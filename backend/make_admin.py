from database import SessionLocal
import models, auth

def make_admin(email: str, password: str):
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if user:
        user.is_admin = True
        db.commit()
        print(f"SUKSES: Akun {email} sudah ada dan sekarang memiliki akses Admin!")
    else:
        # Jika belum ada, buat akun baru otomatis
        hashed_password = auth.get_password_hash(password)
        new_admin = models.User(
            nama_lengkap="Agung (Admin)",
            email=email,
            hashed_password=hashed_password,
            is_admin=True
        )
        db.add(new_admin)
        db.commit()
        print(f"SUKSES: Akun {email} berhasil DIBUAT dan diberikan akses Admin!")
        
    db.close()

if __name__ == "__main__":
    email_anda = "ok.gung1329@gmail.com" 
    password_anda = "Agung#1329"
    make_admin(email_anda, password_anda) 