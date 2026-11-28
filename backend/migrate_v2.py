from sqlalchemy import text
from database import engine # Pastikan sesuai dengan file koneksi Anda

def run_migration():
    with engine.connect() as conn:
        # 1. Tambah kolom ticket_number (Tanpa UNIQUE dulu)
        try:
            conn.execute(text("ALTER TABLE reports ADD COLUMN ticket_number VARCHAR;"))
            conn.commit()
            print("Kolom ticket_number BERHASIL ditambahkan.")
        except Exception as e:
            print(f"Info ticket_number: {e}")
            conn.rollback()

        # 2. Tambah kolom is_public
        try:
            conn.execute(text("ALTER TABLE reports ADD COLUMN is_public BOOLEAN DEFAULT 0;"))
            conn.commit()
            print("Kolom is_public BERHASIL ditambahkan.")
        except Exception as e:
            print(f"Info is_public: {e}")
            conn.rollback()

        # 3. Buat Unique Index secara terpisah untuk ticket_number
        try:
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_reports_ticket_number ON reports (ticket_number);"))
            conn.commit()
            print("Unique index ticket_number BERHASIL dibuat.")
        except Exception as e:
            print(f"Info index: {e}")
            conn.rollback()

if __name__ == "__main__":
    run_migration()