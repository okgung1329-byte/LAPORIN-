from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- SKEMA PENGGUNA (USER) ---
class UserBase(BaseModel):
    nama_lengkap: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- SKEMA LAPORAN (REPORT) ---
class ReportBase(BaseModel):
    judul: str
    deskripsi: str
    kategori: str
    lokasi: str
    foto_url: Optional[str] = None
    latitude: Optional[float] = None # Tambahan untuk peta
    longitude: Optional[float] = None # Tambahan untuk peta

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: int
    status: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReportStatusUpdate(BaseModel):
    status: str
    tanggapan_admin: Optional[str] = None 