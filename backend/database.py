from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Menentukan lokasi file database SQLite
# Ini akan otomatis membuat file bernama 'laporin.db' di dalam folder backend.
SQLALCHEMY_DATABASE_URL = "sqlite:///./laporin.db"

# 2. Membuat "mesin" koneksi ke database
# check_same_thread=False diperlukan agar FastAPI bisa mengakses SQLite dari beberapa thread (proses) sekaligus.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Membuat pabrik sesi (SessionLocal)
# Sesi ini yang akan kita gunakan untuk melakukan transaksi (baca/tulis) ke database nanti.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Membuat Base class
# Nanti, setiap tabel (User, Laporan, dll) akan mewarisi sifat dari Base ini.
Base = declarative_base()