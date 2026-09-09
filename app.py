import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Dashboard Pelabelan Semula Makanan Import 2026",
    page_icon="📊",
    layout="wide"
)

# Load FontAwesome untuk ikon pada kad KPI
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

# 2. CSS Khas Rekaan Kad KPI Berwarna
st.markdown("""
    <style>
    .kpi-card {
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kpi-blue { background-color: #0d6efd; }
    .kpi-green { background-color: #198754; }
    .kpi-cyan { background-color: #0dcaf0; }
    .kpi-yellow { background-color: #ffc107; color: #000 !important; }
    
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        opacity: 0.9;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
    }
    .kpi-icon {
        font-size: 2.5rem;
        opacity: 0.4;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Fungsi Muat Data dari Tab '2026_Live'
@st.cache_data(ttl=300) # Data segar setiap 5 menit
def load_data():
    # ID Spreadsheet dari imej anda
    sheet_id = "13vBLK7XnzhJFKkouzHWg4sBPXwl10WUJKSO638uwjRU"
    sheet_name = "2026_Live"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(url)
        
        # Bersihkan nama lajur daripada sebarang ruang kosong
        df.columns = df.columns.str.strip()
        
        # Ekstrak Tahun dari Tarikh Terima / Pembersihan Data
        if 'TARIKH TERIMA PERMOHONAN DI HQ' in df.columns:
            df['TARIKH'] = pd.to_datetime(df['TARIKH TERIMA PERMOHONAN DI HQ'], errors='coerce')
            df['Tahun'] = df['TARIKH'].dt.year.fillna(2026).astype(int)
        else:
            df['Tahun'] = 2026

        # Pembersihan Lajur Fi Bayaran
        if 'FI BAYARAN (RM)' in df.columns:
            df['FI BAYARAN (RM)'] = pd.to_numeric(df['FI BAYARAN (RM)'], errors='coerce').fillna(0)
            
    except Exception as e:
        st.error(f"Gagal memuatkan data dari Google Sheets: {e}")
        return pd.DataFrame()

    return df

df = load_data()

if not df.empty:
    # ----------------------------------------------------
    # 4. SIDEBAR (PENAPIS DATA)
    # ----------------------------------------------------
    st.sidebar.header("🔍 Penapis Data")

    # Penapis Tahun
    senarai_tahun = sorted(list(df['Tahun'].unique())) if 'Tahun' in df.columns else [2026]
    tahun_dipilih = st.sidebar.multiselect("Pilih Tahun:", options=senarai_tahun, default=senarai_tahun)

    # Penapis Bulan
    senarai_bulan = list(df['BULAN'].dropna().unique()) if 'BULAN' in df.columns else []
    bulan_dipilih = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan, default=senarai_bulan)

    # Penapis Jenis Permohonan
    senarai_jenis = list(df['JENIS PERMOHONAN (NRC/RETAIL/ONLINE/POS)'].dropna().unique()) if 'JENIS PERMOHONAN (NRC/RETAIL/ONLINE/POS)' in df.columns else []
    jenis_dipilih = st.sidebar.multiselect("Pilih Jenis Permohonan:", options=senarai_jenis, default=senarai_jenis)

    # Slider Julat Fi
    min_fi = float(df['FI BAYARAN (RM)'].min()) if 'FI BAYARAN (RM)' in df.columns else 0.0
    max_fi = float(df['FI BAYARAN (RM)'].max()) if 'FI BAYARAN (RM)' in df.columns else 1000.0
    if min_fi == max_fi:
        max_fi += 100.0

    julat_fi = st.sidebar.slider("Pilih Julat Fi (RM):", min_value=min_fi, max_value=max_fi, value=(min_fi, max_fi))

    # Tapis Data
    df_filtered = df.copy()
    
    if tahun_dipilih and 'Tahun' in df.columns:
        df_filtered = df_filtered[df_filtered['Tahun'].isin(tahun_dipilih)]
    if bulan_dipilih and 'BULAN' in df.columns:
        df_filtered = df_filtered[df_filtered['BULAN'].isin(bulan_dipilih)]
    if jenis_dipilih and 'JENIS PERMOHONAN (NRC/RETAIL/ONLINE/POS)' in df.columns:
        df_filtered = df_filtered[df_filtered['JENIS PERMOHONAN (NRC/RETAIL/ONLINE/POS)'].isin(jenis_dipilih)]
    if 'FI BAYARAN (RM)' in df.columns:
        df_filtered = df_filtered[(df_filtered['FI BAYARAN (RM)'] >= julat_fi[0]) & (df_filtered['FI BAYARAN (RM)'] <= julat_fi[1])]

    # ----------------------------------------------------
    # 5. HEADER DASHBOARD
    # ----------------------------------------------------
    st.title("📊 Dashboard Pelabelan Semula Makanan Import")
    st.caption("Data Permohonan Integrasi Live (2026)")
    st.divider()

    # ----------------------------------------------------
    # 6. KAD KPI BERWARNA
    # ----------------------------------------------------
    total_apps = len(df_filtered)
    total_fees = df_filtered['FI BAYARAN (RM)'].sum() if 'FI BAYARAN (RM)' in df_filtered.columns else 0
    
    # Kira Lulus (Berdasarkan Kod Kelulusan 'S' / 'K' atau seumpamanya)
    total_lulus = len(df_filtered[df_filtered['JENIS PERMOHONAN (S / K )\n\n- = KELULUSAN RELABEL'].notna()]) if 'JENIS PERMOHONAN (S / K )\n\n- = KELULUSAN RELABEL' in df_filtered.columns else total_apps
    kadar_lulus = (total_lulus / total_apps * 100) if total_apps > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="kpi-card kpi-blue">
                <div>
                    <div class="kpi-title">JUMLAH PERMOHONAN</div>
                    <div class="kpi-value">{total_apps:,}</div>
                </div>
                <div class="kpi-icon"><i class="fa-solid fa-folder-open"></i></div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card kpi-green">
                <div>
                    <div class="kpi-title">JUMLAH KUTIPAN FI</div>
                    <div class="kpi-value">RM {total_fees:,.2f}</div>
                </div>
                <div class="kpi-icon"><i class="fa-solid fa-wallet"></i></div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card kpi-cyan">
                <div>
                    <div class="kpi-title">PERMOHONAN PROSES</div>
                    <div class="kpi-value">{total_lulus:,}</div>
                </div>
                <div class="kpi-icon"><i class="fa-solid fa-circle-check"></i></div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card kpi-yellow">
                <div>
                    <div class="kpi-title">KADAR PROSES</div>
                    <div class="kpi-value">{kadar_lulus:.1f}%</div>
                </div>
                <div class="kpi-icon"><i class="fa-solid fa-percent"></i></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 7. GRAF INTERAKTIF
    # ----------------------------------------------------
    g_col1, g_col2 = st.columns([2, 1])

    with g_col1:
        st.subheader("📦 Jenis Permohonan")
        if 'JENIS PERMOHONAN (NRC/RETAIL/ONLINE/POS)' in df_filtered.columns and not df_filtered.empty:
            jenis_counts = df_filtered['JENIS PERMOHONAN (NRC/RETAIL/ONLINE/POS)'].value_counts().reset_index()
            jenis_counts.columns = ['Jenis', 'Jumlah']
            
            fig_bar = px.bar(
                jenis_counts, 
                x='Jumlah', 
                y='Jenis', 
                orientation='h',
                text='Jumlah',
                color_discrete_sequence=['#0d6efd']
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

    with g_col2:
        st.subheader("📌 Agihan Mengikut Bulan")
        if 'BULAN' in df_filtered.columns and not df_filtered.empty:
            bulan_counts = df_filtered['BULAN'].value_counts().reset_index()
            bulan_counts.columns = ['Bulan', 'Jumlah']
            
            fig_pie = px.pie(
                bulan_counts, 
                values='Jumlah', 
                names='Bulan', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

    # ----------------------------------------------------
    # 8. JADUAL DATA LIVE
    # ----------------------------------------------------
    st.subheader("🔍 Enjin Carian & Data Permohonan Live")
    
    search_term = st.text_input("Carian Pantas (Syarikat, Kod Rujukan, dll.):")
    if search_term and not df_filtered.empty:
        df_filtered = df_filtered[
            df_filtered['NAMA SYARIKAT'].astype(str).str.contains(search_term, case=False, na=False) |
            df_filtered['KOD RUJUKAN PERMOHONAN'].astype(str).str.contains(search_term, case=False, na=False)
        ]

    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
else:
    st.warning("Tiada data ditemui atau tetapan Google Sheets memerlukan kebenaran akses (Public Share).")
