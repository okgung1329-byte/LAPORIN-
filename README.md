import# LAPORIN - Platform Pelaporan Publik

LAPORIN adalah platform digital berbasis web yang membantu masyarakat menyampaikan laporan mengenai permasalahan di lingkungan sekitar, fasilitas umum, dan infrastruktur secara mudah, transparan, dan terpantau.

## Teknologi yang Digunakan
- **Frontend:** HTML5, CSS3, JavaScript Vanilla, Leaflet (Peta)
- **Backend:** Python, FastAPI, Uvicorn
- **Database:** SQLite, SQLAlchemy
- **Keamanan:** JWT (JSON Web Token), Passlib (Bcrypt/PBKDF2)

## Struktur Folder
```text
LAPORIN/
├── backend/            # Kode Python (FastAPI)
│   ├── .env            # Kunci rahasia (Jangan di-upload ke GitHub!)
│   ├── auth.py         # Logika keamanan & token
│   ├── database.py     # Konfigurasi database
│   ├── main.py         # Endpoint API utama
│   ├── models.py       # Cetak biru tabel database
│   ├── schemas.py      # Validasi data
│   └── requirements.txt# Daftar library Python
└── frontend/           # Kode antarmuka (HTML/CSS/JS)
    ├── css/
    │   └── style.css
    ├── index.html      # Beranda
    ├── login.html      # Halaman Masuk
    ├── register.html   # Halaman Daftar
    ├── map.html        # Peta Laporan
    ├── create_report.html # Form Buat Laporan
    └── my-reports.html # Daftar Laporan Pengguna