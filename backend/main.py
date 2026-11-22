from fastapi import FastAPI, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles # Untuk melayani file gambar
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil # Untuk menyimpan file
import os
import uuid # Untuk membuat nama file unik
from database import engine, Base, SessionLocal
import models
import schemas
from auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
import jwt

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LAPORIN API",
    description="Backend API untuk platform pelaporan publik LAPORIN",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Membuat folder uploads jika belum ada
os.makedirs("uploads", exist_ok=True)
# Mengizinkan frontend mengakses gambar melalui URL /uploads/namafile.jpg
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Akses ditolak. Fitur ini hanya untuk Administrator."
        )
    return current_user

@app.get("/")
def read_root():
    return {"status": "sukses", "pesan": "Selamat datang di API LAPORIN!"}

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")
    
    new_user = models.User(
        nama_lengkap=user.nama_lengkap,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "id": user.id, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}

# --- ENDPOINT BUAT LAPORAN (DIUPDATE UNTUK FILE UPLOAD) ---
@app.post("/reports", response_model=schemas.ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    judul: str = Form(...),
    deskripsi: str = Form(...),
    kategori: str = Form(...),
    lokasi: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    foto: Optional[UploadFile] = File(None), # File bersifat opsional
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    foto_url = None
    
    # Jika user mengupload foto
    if foto:
        # Buat nama file unik untuk menghindari bentrok nama
        file_extension = foto.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"uploads/{file_name}"
        
        # Simpan file ke folder uploads
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
            
        # URL yang akan disimpan di database
        foto_url = f"/uploads/{file_name}"

    new_report = models.Report(
        judul=judul,
        deskripsi=deskripsi,
        kategori=kategori,
        lokasi=lokasi,
        latitude=latitude,
        longitude=longitude,
        foto_url=foto_url,
        owner_id=current_user.id
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@app.get("/reports", response_model=List[schemas.ReportResponse])
def get_all_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reports = db.query(models.Report).order_by(models.Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports

@app.get("/my-reports", response_model=List[schemas.ReportResponse])
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    reports = db.query(models.Report).filter(models.Report.owner_id == current_user.id).order_by(models.Report.created_at.desc()).all()
    return reports

@app.get("/reports/{report_id}", response_model=schemas.ReportResponse)
def get_report_detail(report_id: int, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    return report

@app.put("/reports/{report_id}/status", response_model=schemas.ReportResponse)
def update_report_status(
    report_id: int,
    status_update: schemas.ReportStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    
    report.status = status_update.status
    db.commit()
    db.refresh(report)
    
    return report 