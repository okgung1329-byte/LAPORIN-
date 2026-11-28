from pydantic import BaseModel 
from datetime import datetime
from typing import List, Optional

# --- USER SCHEMAS ---
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

# --- REPORT SCHEMAS ---
class ReportHistoryResponse(BaseModel):
    id: int
    status: str
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    id: int
    judul: str
    deskripsi: str
    kategori: str
    lokasi: str
    foto_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    ticket_number: Optional[str] = None
    is_public: bool
    created_at: datetime
    histories: List[ReportHistoryResponse] = []
    pemilik: UserResponse

    class Config:
        from_attributes = True

# --- AUTH SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None