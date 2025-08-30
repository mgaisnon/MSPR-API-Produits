from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_product(db: Session, product_id: int):
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        logger.info(f"Recherche du produit avec ID {product_id}: {'trouvé' if product else 'non trouvé'}")
        return product
    except Exception as e:
        logger.error(f"Erreur lors de la recherche du produit avec ID {product_id}: {str(e)}")
        raise

def get_products(db: Session, skip: int = 0, limit: int = 100):
    try:
        products = db.query(models.Product).offset(skip).limit(limit).all()
        logger.info(f"Récupération des produits (skip={skip}, limit={limit}): {len(products)} trouvés")
        return products
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des produits: {str(e)}")
        raise

def create_product(db: Session, product: schemas.ProductCreate):
    try:
        db_product = models.Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Produit créé avec ID {db_product.id} et nom {db_product.name}")
        print(f"Débogage: created_at après refresh = {db_product.created_at}")
        return db_product
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Tentative de création d'un produit avec un nom existant: {product.name}")
        raise ValueError("Le produit existe déjà")
    except Exception as e:
        logger.error(f"Erreur lors de la création du produit: {str(e)}")
        raise

def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    try:
        db_product = get_product(db, product_id)
        if not db_product:
            logger.info(f"Produit avec ID {product_id} non trouvé pour la mise à jour")
            return None
        if product.name and product.name != db_product.name:
            existing_product = get_product_by_name(db, product.name)
            if existing_product and existing_product.id != product_id:
                logger.warning(f"Tentative de mise à jour avec un nom déjà utilisé: {product.name}")
                raise ValueError("Le produit existe déjà")
        if product.price is not None and product.price < 0:
            logger.warning(f"Tentative de mise à jour avec un prix négatif: {product.price}")
            raise ValueError("Le prix ne peut pas être négatif")
        if product.stock is not None and product.stock < 0:
            logger.warning(f"Tentative de mise à jour avec un stock négatif: {product.stock}")
            raise ValueError("Le stock ne peut pas être négatif")
        for key, value in product.dict(exclude_unset=True).items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Produit avec ID {product_id} mis à jour avec succès")
        return db_product
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Tentative de mise à jour avec un nom déjà utilisé: {product.name}")
        raise ValueError("Le produit existe déjà")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du produit avec ID {product_id}: {str(e)}")
        raise

def delete_product(db: Session, product_id: int):
    try:
        db_product = get_product(db, product_id)
        if db_product:
            db.delete(db_product)
            db.commit()
            logger.info(f"Produit avec ID {product_id} supprimé avec succès")
            return db_product
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du produit avec ID {product_id}: {str(e)}")
        raise

def get_product_by_name(db: Session, name: str):
    try:
        product = db.query(models.Product).filter(models.Product.name == name).first()
        logger.info(f"Recherche du produit par nom {name}: {'trouvé' if product else 'non trouvé'}")
        return product
    except Exception as e:
        logger.error(f"Erreur lors de la recherche du produit par nom {name}: {str(e)}")
        raise