import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from . import crud, schemas, models

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

def init_data():
    db = SessionLocal()
    response = requests.get("https://615f5fb4f7254d0017068109.mockapi.io/api/v1/products")
    data = response.json()
    for item in data:
        existing = db.query(models.Product).filter(models.Product.name == item['name']).first()
        if not existing:
            try:
                price = float(item['price'])
            except (KeyError, ValueError):
                continue

            try:
                stock = int(item['stock']) if item['stock'] != "rupture" else 0
            except (KeyError, ValueError):
                stock = 0

            product_data = schemas.ProductCreate(
                name=item['name'],
                description=item['description'],
                price=price,
                stock=stock,
                origin=item['origin']
            )
            crud.create_product(db, product_data)
    db.close()

if __name__ == "__main__":
    init_data()