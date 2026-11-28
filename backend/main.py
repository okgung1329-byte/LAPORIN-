from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import os, shutil, uuid

import models, schemas, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LAPORIN API 2.0")

# PERBAIKAN CORS: allow_credentials diubah menjadi False
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"message": "LAPORIN API 2.0 Aktif"}

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(nama_lengkap=user.nama_lengkap, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/reports", response_model=schemas.ReportResponse)
def create_report(
    judul: str = Form(...), deskripsi: str = Form(...), kategori: str = Form(...),
    lokasi: str = Form(...), latitude: Optional[float] = Form(None), longitude: Optional[float] = Form(None),
    foto: Optional[UploadFile] = File(None), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)
):
    foto_url = None
    if foto:
        file_extension = os.path.splitext(foto.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"uploads/{unique_filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_url = f"/uploads/{unique_filename}"

    new_report = models.Report(
        judul=judul, deskripsi=deskripsi, kategori=kategori, lokasi=lokasi,
        latitude=latitude, longitude=longitude, foto_url=foto_url, owner_id=current_user.id, status="Menunggu verifikasi"
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    tahun = datetime.now().year
    new_report.ticket_number = f"LPR-{tahun}-{new_report.id:05d}"
    
    history = models.ReportHistory(report_id=new_report.id, status="Menunggu verifikasi", note="Laporan berhasil dibuat oleh pelapor.")
    notif = models.Notification(user_id=current_user.id, report_id=new_report.id, message=f"Laporan #{new_report.ticket_number} berhasil dikirim.")
    db.add(history)
    db.add(notif)
    db.commit()
    db.refresh(new_report)
    return new_report

@app.get("/my-reports", response_model=List[schemas.ReportResponse])
def get_my_reports(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    reports = db.query(models.Report).filter(models.Report.owner_id == current_user.id).order_by(models.Report.created_at.desc()).all()
    return reports

@app.get("/reports/{ticket_number}", response_model=schemas.ReportResponse)
def get_report_by_ticket(ticket_number: str, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.ticket_number == ticket_number).first()
    if not report:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    return report

# --- FITUR ADMIN BARU ---
@app.get("/admin/reports", response_model=List[schemas.ReportResponse])
def get_all_reports_admin(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Akses ditolak. Anda bukan admin.")
    return db.query(models.Report).order_by(models.Report.created_at.desc()).all()

@app.put("/admin/reports/{report_id}/status")
def update_report_status(
    report_id: int, status: str = Form(...), note: str = Form(None), 
    db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Akses ditolak.")
    
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    
    report.status = status
    history = models.ReportHistory(report_id=report.id, status=status, note=note or f"Status diperbarui menjadi {status}")
    notif = models.Notification(user_id=report.owner_id, report_id=report.id, message=f"Status laporan {report.ticket_number} diperbarui menjadi {status}.")
    
    db.add(history)
    db.add(notif)
    db.commit()
    return {"message": "Status berhasil diperbarui"} 