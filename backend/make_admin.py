from database import SessionLocal
import models

db = SessionLocal()
email_target = "Agung@gmail.com" # <--- Target email diubah
user = db.query(models.User).filter(models.User.email == email_target).first()

if user:
    user.is_admin = True
    db.commit()
    print(f"✅ BERHASIL! Akun {user.email} sekarang berstatus sebagai Admin.")
else:
    print(f"❌ GAGAL! Akun {user.email} tidak ditemukan di database.")

db.close() 