import os
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# Muat data dengan path relatif yang aman untuk lokal dan Streamlit Cloud
path_data = os.path.join(os.path.dirname(__file__), "main_data.csv")
if not os.path.exists(path_data):
    st.error("File main_data.csv tidak ditemukan. Jalankan notebook.ipynb sampai selesai terlebih dulu.")
    st.stop()

hour_df = pd.read_csv(path_data)
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])


# Fungsi sederhana untuk membuat bar chart dengan prinsip color highlighting
def buat_bar_chart(data, judul, label_x, label_y):
    data = data.sort_values(ascending=False)  # urutkan dari tertinggi ke terendah
    warna = ["#1f77b4" if i == 0 else "#d3d3d3" for i in range(len(data))]
    fig, ax = plt.subplots(figsize=(7, 5))
    batang = ax.bar(data.index.astype(str), data.values, color=warna)
    ax.bar_label(batang, fmt="%.0f", padding=3)  # angka di atas batang
    ax.set_ylim(0, data.max() * 1.15)  # sumbu Y mulai dari 0
    ax.set_title(judul)
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    sns.despine(ax=ax)
    plt.tight_layout()
    return fig


# ------------------------------------------------------------ Sidebar
st.sidebar.header("Filter Data")

tanggal_min = hour_df["dteday"].min().date()
tanggal_maks = hour_df["dteday"].max().date()

rentang = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(tanggal_min, tanggal_maks),
    min_value=tanggal_min,
    max_value=tanggal_maks
)

# Penanganan jika user baru memilih 1 tanggal
if isinstance(rentang, (tuple, list)):
    if len(rentang) == 2:
        tanggal_awal, tanggal_akhir = rentang
    elif len(rentang) == 1:
        tanggal_awal = rentang[0]
        tanggal_akhir = rentang[0]
    else:
        tanggal_awal, tanggal_akhir = tanggal_min, tanggal_maks
else:
    tanggal_awal = rentang
    tanggal_akhir = rentang

daftar_musim = ["Spring", "Summer", "Fall", "Winter"]
musim_pilihan = st.sidebar.multiselect("Musim", options=daftar_musim, default=daftar_musim)

daftar_cuaca = [c for c in ["Cerah/Berawan", "Berkabut/Mendung", "Hujan/Salju Ringan", "Cuaca Ekstrem"]
                if c in hour_df["weathersit"].unique()]
cuaca_pilihan = st.sidebar.multiselect("Kondisi Cuaca", options=daftar_cuaca, default=daftar_cuaca)

# Terapkan filter ke data
data_filter = hour_df[
    (hour_df["dteday"].dt.date >= tanggal_awal)
    & (hour_df["dteday"].dt.date <= tanggal_akhir)
    & (hour_df["season"].isin(musim_pilihan))
    & (hour_df["weathersit"].isin(cuaca_pilihan))
]

# ------------------------------------------------------------ Halaman utama
st.title("Bike Sharing Dashboard")
st.caption("Analisis penyewaan sepeda Capital Bikeshare tahun 2011 sampai 2012")

if data_filter.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah filter di sidebar.")
    st.stop()

# Baris KPI
kol1, kol2, kol3 = st.columns(3)
kol1.metric("Total Penyewaan", f"{data_filter['cnt'].sum():,}")
kol2.metric("Total Pengguna Registered", f"{data_filter['registered'].sum():,}")
kol3.metric("Total Pengguna Casual", f"{data_filter['casual'].sum():,}")

st.divider()

# ------------------------------------------------------------ Visualisasi 1
st.subheader("1. Pengaruh Musim dan Cuaca terhadap Rata-rata Penyewaan")
st.write("Rata-rata penyewaan dihitung per jam (data dashboard berasal dari data per jam). Batang biru tua menandai nilai tertinggi.")

rata_season = data_filter.groupby("season")["cnt"].mean()
rata_cuaca = data_filter.groupby("weathersit")["cnt"].mean()

kiri, kanan = st.columns(2)
with kiri:
    fig1 = buat_bar_chart(rata_season, "Rata-rata Penyewaan per Jam berdasarkan Musim",
                          "Musim", "Rata-rata Penyewaan per Jam")
    st.pyplot(fig1)
with kanan:
    fig2 = buat_bar_chart(rata_cuaca, "Rata-rata Penyewaan per Jam berdasarkan Cuaca",
                          "Kondisi Cuaca", "Rata-rata Penyewaan per Jam")
    st.pyplot(fig2)

st.divider()

# ------------------------------------------------------------ Visualisasi 2
st.subheader("2. Tren Penyewaan per Jam")

cnt_jam = data_filter.groupby(["hr", "workingday"])["cnt"].mean().unstack()
cnt_jam = cnt_jam.reindex(range(24))  # pastikan jam 0 sampai 23 selalu ada
reg_jam = data_filter.groupby(["hr", "workingday"])["registered"].mean().unstack().reindex(range(24))
cas_jam = data_filter.groupby(["hr", "workingday"])["casual"].mean().unstack().reindex(range(24))

kiri, kanan = st.columns(2)

with kiri:
    # Line chart Hari Kerja vs Akhir Pekan/Libur
    fig3, ax3 = plt.subplots(figsize=(7, 5))
    warna_hari = {"Hari Kerja": "#1f77b4", "Akhir Pekan/Libur": "#ff7f0e"}
    for jenis_hari in cnt_jam.columns:
        seri = cnt_jam[jenis_hari]
        ax3.plot(seri.index, seri.values, marker="o", markersize=4, color=warna_hari[jenis_hari], label=jenis_hari)
        jam_puncak = seri.idxmax()
        ax3.scatter(jam_puncak, seri.max(), s=120, color="red", zorder=5)  # titik puncak
        ax3.annotate(f"{jam_puncak:02d}:00", xy=(jam_puncak, seri.max()), xytext=(5, 8), textcoords="offset points")
    ax3.set_title("Rata-rata Penyewaan per Jam: Hari Kerja vs Akhir Pekan/Libur")
    ax3.set_xlabel("Jam (0-23)")
    ax3.set_ylabel("Rata-rata Penyewaan")
    ax3.set_xticks(range(0, 24))
    ax3.tick_params(axis="x", labelsize=7)
    ax3.set_ylim(0, np.nanmax(cnt_jam.values) * 1.2)
    ax3.legend()
    sns.despine(ax=ax3)
    plt.tight_layout()
    st.pyplot(fig3)

with kanan:
    # Line chart registered vs casual
    fig4, ax4 = plt.subplots(figsize=(7, 5))
    gaya = [("Registered", reg_jam, "#1f77b4"), ("Casual", cas_jam, "#ff7f0e")]
    for tipe, tabel, warna in gaya:
        for jenis_hari in tabel.columns:
            garis = "-" if jenis_hari == "Hari Kerja" else "--"
            seri = tabel[jenis_hari]
            ax4.plot(seri.index, seri.values, color=warna, linestyle=garis, marker="o", markersize=3,
                     label=f"{tipe} - {jenis_hari}")
            jam_puncak = seri.idxmax()
            ax4.scatter(jam_puncak, seri.max(), s=100, color="red", zorder=5)  # titik puncak
    ax4.set_title("Rata-rata Penyewaan per Jam: Registered vs Casual")
    ax4.set_xlabel("Jam (0-23)")
    ax4.set_ylabel("Rata-rata Penyewaan")
    ax4.set_xticks(range(0, 24))
    ax4.tick_params(axis="x", labelsize=7)
    ax4.set_ylim(0, np.nanmax(reg_jam.values) * 1.2)
    ax4.legend(fontsize=8)
    sns.despine(ax=ax4)
    plt.tight_layout()
    st.pyplot(fig4)

st.divider()

# ------------------------------------------------------------ Visualisasi 3
st.subheader("3. Analisis Lanjutan: Manual Grouping dan Binning")
st.write("Jam dikelompokkan menjadi Pagi (05-10), Siang (11-14), Sore (15-18), dan Malam (19-04). "
         "Suhu dibagi menjadi Dingin (di bawah 15°C), Sejuk (15°C sampai 25°C), dan Panas (di atas 25°C).")

rata_waktu = data_filter.groupby("waktu_hari")["cnt"].mean()
rata_suhu = data_filter.groupby("kategori_suhu")["cnt"].mean()

kiri, kanan = st.columns(2)
with kiri:
    fig5 = buat_bar_chart(rata_waktu, "Rata-rata Penyewaan per Jam berdasarkan Waktu Operasional",
                          "Waktu Operasional", "Rata-rata Penyewaan per Jam")
    st.pyplot(fig5)
with kanan:
    fig6 = buat_bar_chart(rata_suhu, "Rata-rata Penyewaan per Jam berdasarkan Kategori Suhu",
                          "Kategori Suhu", "Rata-rata Penyewaan per Jam")
    st.pyplot(fig6)

st.divider()

# ------------------------------------------------------------ Kesimpulan
st.subheader("Kesimpulan")

musim_tertinggi = rata_season.idxmax()
cuaca_tertinggi = rata_cuaca.idxmax()
waktu_tertinggi = rata_waktu.idxmax()
suhu_tertinggi = rata_suhu.idxmax()
rata_jam_total = data_filter.groupby("hr")["cnt"].mean()
jam_puncak_total = rata_jam_total.idxmax()

st.write(f"Pada data yang sedang difilter, musim dengan rata-rata penyewaan tertinggi adalah **{musim_tertinggi}**, "
         f"kondisi cuaca tertinggi adalah **{cuaca_tertinggi}**, jam puncak ada di **{jam_puncak_total:02d}:00**, "
         f"waktu operasional tertinggi adalah **{waktu_tertinggi}**, dan kategori suhu tertinggi adalah **{suhu_tertinggi}**.")

st.markdown("""
- Penyewaan paling tinggi pada musim Fall dan cuaca cerah, dan paling rendah pada musim Spring dan saat hujan atau salju ringan.
- Hari kerja punya dua puncak (sekitar jam 08:00 dan 17:00), sedangkan akhir pekan punya satu puncak lebar di siang hari. Pengguna casual lebih aktif di akhir pekan.
- Waktu Sore dan suhu Panas menghasilkan rata-rata penyewaan tertinggi, sedangkan waktu Malam dan suhu Dingin paling rendah.
- Rekomendasi: tambah stok pada jam sibuk, lakukan perawatan armada saat Spring dan malam hari, dan buat promo konversi casual ke registered pada akhir pekan.
""")
