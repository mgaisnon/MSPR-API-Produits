import os
from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
from . import crud, models, schemas
from .database import SessionLocal, engine
from .rabbitmq import publish_event

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
Instrumentator().instrument(app).expose(app)

API_KEY = os.getenv("API_KEY") 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Clé API invalide")

@app.get("/")
def read_root():
    return {"message": "Bienvenue dans l'API produits."}

@app.get("/products/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product

@app.post("/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    db_product = crud.get_product_by_name(db, name=product.name)
    if db_product:
        raise HTTPException(status_code=400, detail="Nom de produit déjà utilisé")
    new_product = crud.create_product(db, product)
    try:
        event_data = {key: value for key, value in new_product.__dict__.items() if not key.startswith('_')}
        publish_event("product_created", event_data)
    except Exception as e:
        pass
    return new_product

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    db_product = crud.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    if product.name and product.name != db_product.name:
        existing_product = crud.get_product_by_name(db, name=product.name)
        if existing_product and existing_product.id != product_id:
            raise HTTPException(status_code=400, detail="Nom de produit déjà utilisé")
    updated = crud.update_product(db, product_id, product)
    try:
        event_data = {key: value for key, value in updated.__dict__.items() if not key.startswith('_')}
        publish_event("product_updated", event_data)
    except Exception as e:
        pass
    return updated

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    deleted = crud.delete_product(db, product_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    try:
        publish_event("product_deleted", {"id": product_id})
    except Exception as e:
        pass
    return {"detail": "Produit supprimé"}