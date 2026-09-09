import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Pelabelan Semula Makanan Import",
    page_icon="📊",
    layout="wide"
)

# 2. Fungsi Muat Data (Simulasi / Integrasi Google Sheet)
@st.cache_data
def load_data():
    # JIKA MENGGUNAKAN CSV BUKAN GOOGLE SHEETS:
    # df = pd.read_csv("data_master.csv")
    
    # CONTOH INTEGRASI GOOGLE SHEETS (Gantikan ID dengan Spreadsheet ID anda):
    # Google Sheet Mesti Ditetapkan kepada "Anyone with link can view"
    sheet_id = "GANTIKAN_DENGAN_SPREADSHEET_ID_ANDA"
    sheet_name = "MasterData"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(url)
    except:
        # Data dummy sekiranya tiada sambungan Google Sheet (Untuk Pengujian)
        data = {
            "Tahun": [2023, 2023, 2024, 2024, 2025, 2025, 2026],
            "Bulan": ["Januari", "Februari", "Mac", "April", "Januari", "Februari", "Mac"],
            "Kod Rujukan": ["KOD001", "KOD002", "KOD003", "KOD004", "KOD005", "KOD006", "KOD007"],
            "Fi": [100.0, 250.0, 150.0, 300.0, 50.0, 200.0, 400.0],
            "Syarikat": ["Syarikat A", "Syarikat B", "Syarikat C", "Syarikat A", "Syarikat D", "Syarikat B", "Syarikat C"],
            "Produk": ["Biskut", "Minuman Juice", "Susu Lapis", "Coklat", "Kerepek", "Roti", "Sos Cili"],
            "Negara": ["Jepun", "China", "Australia", "Jepun", "Thailand", "China", "Korea"],
            "Kumpulan": ["Makanan Kering", "Minuman", "Produk Tenusu", "Makanan Kering", "Makanan Kering", "Makanan Kering", "Sos/Perasa"],
            "Status": ["LULUS", "DALAM PROSES", "LULUS", "TOLAK", "LULUS", "LULUS", "DALAM PROSES"]
        }
        df = pd.DataFrame(data)

    # Pembersihan Data (Data Cleaning)
    if 'Bulan' in df.columns:
        df['Bulan'] = df['Bulan'].astype(str).str.strip()
    if 'Status' in df.columns:
        df['Status'] = df['Status'].astype(str).str.upper()
    if 'Fi' in df.columns:
        df['Fi'] = pd.to_numeric(df['Fi'], errors='coerce').fillna(0)

    return df

# Muat data
df = load_data()

# ----------------------------------------------------
# 3. SIDEBAR (PENAPIS DATA & SLIDER)
# ----------------------------------------------------
st.sidebar.header("🔍 Penapis Data")

# Penapis 1: Pilih Tahun
senarai_tahun = sorted(list(df['Tahun'].unique())) if 'Tahun' in df.columns else []
tahun_dipilih = st.sidebar.multiselect("Pilih Tahun:", options=senarai_tahun, default=senarai_tahun)

# Penapis 2: Pilih Bulan
senarai_bulan = list(df['Bulan'].unique()) if 'Bulan' in df.columns else []
bulan_dipilih = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan, default=senarai_bulan)

# Penapis 3: Status Permohonan
senarai_status = list(df['Status'].unique()) if 'Status' in df.columns else []
status_dipilih = st.sidebar.multiselect("Pilih Status Permohonan:", options=senarai_status, default=senarai_status)

# Penapis 4: SLIDER Julat Fi (RM)
min_fi = float(df['Fi'].min()) if not df.empty else 0.0
max_fi = float(df['Fi'].max()) if not df.empty else 1000.0

if min_fi == max_fi:
    max_fi += 100.0

julat_fi = st.sidebar.slider(
    "Pilih Julat Fi (RM):",
    min_value=min_fi,
    max_value=max_fi,
    value=(min_fi, max_fi)
)

# ----------------------------------------------------
# 4. TAPIS DATA BERDASARKAN PILIHAN
# ----------------------------------------------------
df_filtered = df.copy()

if tahun_dipilih and 'Tahun' in df.columns:
    df_filtered = df_filtered[df_filtered['Tahun'].isin(tahun_dipilih)]

if bulan_dipilih and 'Bulan' in df.columns:
    df_filtered = df_filtered[df_filtered['Bulan'].isin(bulan_dipilih)]

if status_dipilih and 'Status' in df.columns:
    df_filtered = df_filtered[df_filtered['Status'].isin(status_dipilih)]

if 'Fi' in df.columns:
    df_filtered = df_filtered[(df_filtered['Fi'] >= julat_fi[0]) & (df_filtered['Fi'] <= julat_fi[1])]

# ----------------------------------------------------
# 5. PAPARAN UTAMA DASHBOARD
# ----------------------------------------------------
st.title("📊 Dashboard Pelabelan Semula Makanan Import")
st.markdown("Analisis Data Permohonan Integrasi Kebangsaan")

st.divider()

# Kad KPI (Key Performance Indicators)
col1, col2, col3, col4 = st.columns(4)

total_apps = len(df_filtered)
total_fees = df_filtered['Fi'].sum() if not df_filtered.empty else 0
total_lulus = len(df_filtered[df_filtered['Status'].str.contains("LULUS", na=False)]) if not df_filtered.empty else 0
kadar_lulus = (total_lulus / total_apps * 100) if total_apps > 0 else 0

col1.metric("Jumlah Permohonan", f"{total_apps:,}")
col2.metric("Jumlah Kutipan Fi", f"RM {total_fees:,.2f}")
col3.metric("Permohonan Lulus", f"{total_lulus:,}")
col4.metric("Kadar Kelulusan", f"{kadar_lulus:.1f}%")

st.divider()

# ----------------------------------------------------
# 6. GRAF INTERAKTIF (PLOTLY)
# ----------------------------------------------------
g_col1, g_col2 = st.columns([2, 1])

with g_col1:
    st.subheader("📦 Permohonan Mengikut Kumpulan Makanan")
    if not df_filtered.empty:
        kumpulan_counts = df_filtered['Kumpulan'].value_counts().reset_index()
        kumpulan_counts.columns = ['Kumpulan', 'Jumlah']
        
        fig_bar = px.bar(
            kumpulan_counts, 
            x='Jumlah', 
            y='Kumpulan', 
            orientation='h',
            text='Jumlah',
            color='Jumlah',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Tiada data untuk dipaparkan.")

with g_col2:
    st.subheader("📌 Status Kelulusan")
    if not df_filtered.empty:
        status_counts = df_filtered['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        
        fig_pie = px.pie(
            status_counts, 
            values='Jumlah', 
            names='Status', 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Tiada data untuk dipaparkan.")

# ----------------------------------------------------
# 7. JADUAL DATA INTERAKTIF
# ----------------------------------------------------
st.subheader("📋 Enjin Carian & Data Permohonan")

# Carian teks
search_term = st.text_input("🔍 Carian Pantas (Syarikat, Kod, Produk, atau Negara):")
if search_term:
    df_filtered = df_filtered[
        df_filtered['Syarikat'].astype(str).str.contains(search_term, case=False) |
        df_filtered['Kod Rujukan'].astype(str).str.contains(search_term, case=False) |
        df_filtered['Produk'].astype(str).str.contains(search_term, case=False) |
        df_filtered['Negara'].astype(str).str.contains(search_term, case=False)
    ]

st.dataframe(df_filtered, use_container_width=True, hide_index=True)