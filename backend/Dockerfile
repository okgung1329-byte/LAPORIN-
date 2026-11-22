# Gunakan image Python versi ringan
FROM python:3.11-slim

# Tentukan direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt terlebih dahulu agar proses instalasi lebih cepat di masa depan
COPY requirements.txt .

# Instal semua library Python yang dibutuhkan
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke dalam container
COPY . .

# Hugging Face Spaces menggunakan port 7860 secara default[reference:0]
ENV PORT=7860
EXPOSE 7860

# Perintah untuk menjalankan server FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"] 