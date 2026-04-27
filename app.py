import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Tampilan
st.set_page_config(page_title="Dashboard Al Wafa Sejahtera", layout="wide")

# Fungsi Membaca Data dari Google Sheets (Link CSV)
def load_data(sheet_id, sheet_name):
    # PERBAIKAN 1: URL harus lengkap agar Streamlit bisa mendownload data CSV dari Sheets
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        # Skip 4 baris pertama karena ringkasan TikTok
        df = pd.read_csv(url, skiprows=4)
        # Bersihkan kolom yang tidak perlu
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        # Format Tanggal
        if 'Tanggal' in df.columns:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        # Bersihkan Persentase Konversi agar jadi angka
        if 'Persentase konversi' in df.columns:
            df['Persentase konversi'] = df['Persentase konversi'].astype(str).str.replace('%', '').astype(float)
        return df
    except Exception as e:
        st.sidebar.error(f"Gagal memuat data: {e}")
        return None

# --- SIDEBAR ---
st.sidebar.image("https://www.gstatic.com/images/branding/product/2x/sheets_2020q4_48dp.png", width=50)
st.sidebar.title("Kontrol Dashboard")

# PERBAIKAN 2: Masukkan ID Sheet Anda di sini
SHEET_ID = "1v6u2kOHdcQ30ONrTSzc-e8e2rFFaRvzn"

list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
bulan_pilihan = st.sidebar.selectbox("Pilih Bulan Analisis:", list_bulan)

# --- MAIN PAGE ---
df = load_data(SHEET_ID, bulan_pilihan)

if df is not None and not df.empty:
    st.title(f"📈 Performa Toko Al Wafa - {bulan_pilihan} 2026")
    
    # Row 1: Metrics
    m1, m2, m3, m4 = st.columns(4)
    total_gmv = df['Nilai Bruto Barang Dagangan (GMV) (Rp)'].sum()
    total_order = df['Pesanan'].sum()
    total_views = df['Tayangan halaman'].sum()
    avg_cr = df['Persentase konversi'].mean()

    m1.metric("Total GMV", f"Rp {total_gmv:,.0f}")
    m2.metric("Total Pesanan", f"{total_order:,}")
    m3.metric("Total Traffic", f"{total_views:,}")
    m4.metric("Avg. Konversi", f"{avg_cr:.2f}%")

    # Row 2: Charts
    c1, c2 = st.columns(2)
    with c1:
        fig_gmv = px.area(df, x='Tanggal', y='Nilai Bruto Barang Dagangan (GMV) (Rp)', 
                          title="Tren Omzet Harian", color_discrete_sequence=['#2ecc71'])
        # PERBAIKAN 3: Nama variabel harus sama (tadi fig_sales, sekarang fig_gmv)
        st.plotly_chart(fig_gmv, use_container_width=True)
    with c2:
        fig_traffic = px.line(df, x='Tanggal', y='Tayangan halaman', 
                             title="Tren Pengunjung", color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig_traffic, use_container_width=True)

    # Row 3: Data Table
    with st.expander("Lihat Data Mentah"):
        st.dataframe(df, use_container_width=True)
else:
    st.error(f"Data untuk bulan {bulan_pilihan} belum ada di Google Sheets atau link tidak bisa diakses.")
