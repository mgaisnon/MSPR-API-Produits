import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

url = os.getenv("DATABASE_URL")

if not url:
    raise RuntimeError("❌ DATABASE_URL is not set in environment variables")

if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)


engine = create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
