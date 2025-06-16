# MSPR - API Produits

![Build](https://img.shields.io/github/actions/workflow/status/mgaisnon/MSPR-API-Produits/ci.yml?branch=main)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![Docker Image](https://img.shields.io/docker/image-size/mgaisnon/mspr-api-produits/latest)

API REST pour la gestion des produits de l'application PayeTonKawa.

## 🚀 Stack technique
- Langage : Python 3.11
- Framework : FastAPI
- Base de données : MySQL
- ORM : SQLAlchemy + Pydantic
- Conteneurisation : Docker

## 🔧 Installation locale
```bash
docker compose up --build
````

API accessible sur : [http://localhost:8002/docs](http://localhost:8002/docs)

## 🔍 Endpoints principaux

* `GET /produits` : Liste des produits
* `POST /produits` : Création d'un produit
* `GET /produits/{id}` : Détails d'un produit
* `PUT /produits/{id}` : Mise à jour d'un produit
* `DELETE /produits/{id}` : Suppression d'un produit

## ⚙️ Variables d'environnement

```env
DATABASE_URL=mysql+pymysql://user:password@db-produits:3306/produits_db
```

## 📉 Tests

```bash
pytest --cov=app
```
