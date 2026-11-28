from database import SessionLocal
import models

db = SessionLocal()
reports = db.query(models.Report).filter(models.Report.ticket_number == None).all()
for r in reports:
    r.ticket_number = f"LPR-2026-{r.id:05d}"
db.commit()
db.close()
print(f"Berhasil memperbarui {len(reports)} tiket lama!")
