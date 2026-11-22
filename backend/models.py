from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    laporan = relationship("Report", back_populates="pemilik")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String, index=True)
    deskripsi = Column(String)
    kategori = Column(String)
    lokasi = Column(String)
    foto_url = Column(String, nullable=True)
    
    # --- KOLOM BARU UNTUK PETA ---
    latitude = Column(Float, nullable=True) 
    longitude = Column(Float, nullable=True)
    # -----------------------------

    status = Column(String, default="Menunggu verifikasi") 
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pemilik = relationship("User", back_populates="laporan") 