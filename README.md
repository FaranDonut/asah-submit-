# Proyek Analisis Data: Bike Sharing Dataset ✨

Proyek ini menganalisis data penyewaan sepeda Capital Bikeshare tahun 2011 sampai 2012 dari [Bike Sharing Dataset](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset). Analisis menjawab dua pertanyaan bisnis:

1. Berapa rata-rata dan total penyewaan harian berdasarkan cuaca dan musim, serta kondisi apa yang menyebabkan penurunan terbesar?
2. Pada jam berapa terjadi puncak dan titik terendah penyewaan dari pengguna registered dan casual pada Hari Kerja dibandingkan Akhir Pekan/Libur?

Analisis lanjutan memakai Manual Grouping (`waktu_hari`) dan Binning (`kategori_suhu`, `kategori_permintaan`) tanpa machine learning. Hasilnya ditampilkan di dashboard Streamlit.

## Struktur Direktori

```text
submission
├───dashboard
│   ├───main_data.csv
│   └───dashboard.py
├───data
│   ├───day.csv
│   └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment - Anaconda

```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Menjalankan Notebook

Letakkan `day.csv` dan `hour.csv` di folder `data/`, lalu jalankan semua cell di `notebook.ipynb` dari folder `submission`. Notebook akan membuat `dashboard/main_data.csv`.

## Run Streamlit App

Jalankan perintah ini dari folder `submission`:

```bash
streamlit run dashboard/dashboard.py
```

## Deploy ke Streamlit Cloud

1. Upload folder `submission` ke repository GitHub (pastikan `dashboard/main_data.csv` dan `requirements.txt` ikut ter-upload).
2. Buka [share.streamlit.io](https://share.streamlit.io) dan login dengan akun GitHub.
3. Klik **New app**, pilih repository dan branch.
4. Isi **Main file path** dengan `dashboard/dashboard.py`, lalu klik **Deploy**.
5. Salin link aplikasi yang dihasilkan ke `url.txt`.
