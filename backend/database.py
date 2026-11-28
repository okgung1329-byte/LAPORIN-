from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Menggunakan SQLite secara default, atau PostgreSQL jika ada DATABASE_URL (seperti di Railway)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./laporin.db")

# Perbaikan khusus untuk SQLite agar bisa berjalan di berbagai thread (FastAPI)
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fungsi untuk mendapatkan sesi database di setiap request API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 