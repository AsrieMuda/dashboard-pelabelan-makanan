import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# 1. KONFIGURASI HALAMAN & TEMA
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Pelabelan Semula Makanan Import 2026",
    page_icon="📊",
    layout="wide"
)

# Muat turun FontAwesome untuk ikon pada kad KPI
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

# CSS Khas Rekaan Kad KPI Berwarna dan Berbayang
st.markdown("""
    <style>
    .kpi-card {
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kpi-blue { background-color: #0d6efd; }
    .kpi-green { background-color: #198754; }
    .kpi-cyan { background-color: #0dcaf0; }
    .kpi-yellow { background-color: #ffc107; color: #212529 !important; }
    
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
        opacity: 0.35;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# FUNGSI MUAT DATA DARI GOOGLE SHEETS (REVISION FIX 404)
# ----------------------------------------------------
@st.cache_data(ttl=60)  # Segarkan data automatik setiap 1 minit
def load_data():
    sheet_id = "13vBLK7XnzhJFKkouzHWg4sBPXwl10WUJKSO638uwjRU"
    
    # URL eksport CSV langsung menggunakan nama tab '2026_Live'
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=2026_Live"
    
    try:
        df = pd.read_csv(url)
        
        # Bersihkan nama lajur daripada ruang kosong
        df.columns = df.columns.str.strip()
        
        # Pembersihan Lajur Tarikh & Tahun
        tarikh_col = [c for c in df.columns if 'TARIKH TERIMA' in c]
        if tarikh_col:
            df['TARIKH_DATETIME'] = pd.to_datetime(df[tarikh_col[0]], errors='coerce')
            df['Tahun'] = df['TARIKH_DATETIME'].dt.year.fillna(2026).astype(int)
        else:
            df['Tahun'] = 2026

        # Pembersihan Lajur Fi Bayaran (RM)
        fi_col = [c for c in df.columns if 'FI' in c]
        if fi_col:
            df['FI_CLEAN'] = pd.to_numeric(df[fi_col[0]], errors='coerce').fillna(0)
        else:
            df['FI_CLEAN'] = 0.0

        return df
    except Exception as e:
        st.error(f"Gagal memuatkan data dari Google Sheets: {e}")
        return pd.DataFrame()

# ----------------------------------------------------
# 3. SEMAKAN DATA & PEMBINAAN DASHBOARD
# ----------------------------------------------------
if not df.empty:
    
    # Kenali nama-nama lajur utama
    col_bulan = 'BULAN' if 'BULAN' in df.columns else df.columns[0]
    col_kod = [c for c in df.columns if 'KOD' in c][0] if any('KOD' in c for c in df.columns) else df.columns[1]
    col_jenis = [c for c in df.columns if 'JENIS PERMOHONAN' in c][0] if any('JENIS PERMOHONAN' in c for c in df.columns) else None
    col_syarikat = [c for c in df.columns if 'SYARIKAT' in c][0] if any('SYARIKAT' in c for c in df.columns) else None

    # ----------------------------------------------------
    # SIDEBAR (PENAPIS DATA INTERAKTIF)
    # ----------------------------------------------------
    st.sidebar.header("🔍 Penapis Data")

    # Penapis 1: Tahun
    senarai_tahun = sorted(list(df['Tahun'].unique()))
    tahun_dipilih = st.sidebar.multiselect("Pilih Tahun:", options=senarai_tahun, default=senarai_tahun)

    # Penapis 2: Bulan
    senarai_bulan = list(df[col_bulan].dropna().unique())
    bulan_dipilih = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan, default=senarai_bulan)

    # Penapis 3: Jenis Permohonan
    if col_jenis:
        senarai_jenis = list(df[col_jenis].dropna().unique())
        jenis_dipilih = st.sidebar.multiselect("Pilih Jenis Permohonan:", options=senarai_jenis, default=senarai_jenis)
    else:
        jenis_dipilih = []

    # Penapis 4: Range Slider Fi (RM)
    min_fi = float(df['FI_CLEAN'].min())
    max_fi = float(df['FI_CLEAN'].max())
    if min_fi == max_fi:
        max_fi += 100.0

    julat_fi = st.sidebar.slider("Pilih Julat Fi (RM):", min_value=min_fi, max_value=max_fi, value=(min_fi, max_fi))

    # TAPIS DATA
    df_filtered = df.copy()
    if tahun_dipilih:
        df_filtered = df_filtered[df_filtered['Tahun'].isin(tahun_dipilih)]
    if bulan_dipilih:
        df_filtered = df_filtered[df_filtered[col_bulan].isin(bulan_dipilih)]
    if jenis_dipilih and col_jenis:
        df_filtered = df_filtered[df_filtered[col_jenis].isin(jenis_dipilih)]
    df_filtered = df_filtered[(df_filtered['FI_CLEAN'] >= julat_fi[0]) & (df_filtered['FI_CLEAN'] <= julat_fi[1])]

    # ----------------------------------------------------
    # PAPARAN UTAMA
    # ----------------------------------------------------
    st.title("📊 Dashboard Pelabelan Semula Makanan Import")
    st.caption("Data Permohonan Integrasi Kebangsaan (2026 Live)")
    st.divider()

    # ----------------------------------------------------
    # KAD KPI BERWARNA (CARD VIEW)
    # ----------------------------------------------------
    total_apps = len(df_filtered)
    total_fees = df_filtered['FI_CLEAN'].sum()
    
    # Anggaran status kelulusan/proses
    lulus_count = total_apps # Boleh disesuaikan mengikut logik lajur status
    kadar_lulus = 100.0 if total_apps > 0 else 0.0

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
                    <div class="kpi-value">{lulus_count:,}</div>
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
    # GRAF INTERAKTIF
    # ----------------------------------------------------
    g_col1, g_col2 = st.columns([2, 1])

    with g_col1:
        st.subheader("📦 Jenis Permohonan")
        if col_jenis and not df_filtered.empty:
            jenis_counts = df_filtered[col_jenis].value_counts().reset_index()
            jenis_counts.columns = ['Jenis', 'Jumlah']
            
            fig_bar = px.bar(
                jenis_counts, 
                x='Jumlah', 
                y='Jenis', 
                orientation='h',
                text='Jumlah',
                color_discrete_sequence=['#0d6efd']
            )
            fig_bar.update_layout(
                yaxis={'categoryorder':'total ascending'},
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Tiada data untuk dipaparkan.")

    with g_col2:
        st.subheader("📌 Agihan Mengikut Bulan")
        if not df_filtered.empty:
            bulan_counts = df_filtered[col_bulan].value_counts().reset_index()
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
        else:
            st.info("Tiada data untuk dipaparkan.")

    # ----------------------------------------------------
    # ENJIN CARIAN & JADUAL DATA
    # ----------------------------------------------------
    st.subheader("🔍 Enjin Carian & Data Permohonan Live")

    search_term = st.text_input("Carian Pantas (Syarikat, Kod Rujukan, dll.):")
    if search_term and not df_filtered.empty:
        # Cari di seluruh lajur string
        mask = df_filtered.astype(str).apply(lambda row: row.str.contains(search_term, case=False, na=False)).any(axis=1)
        df_filtered = df_filtered[mask]

    # Gugurkan lajur bantuan dalam paparan jadual
    display_df = df_filtered.drop(columns=['TARIKH_DATETIME', 'FI_CLEAN', 'Tahun'], errors='ignore')
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("Gagal memuatkan data. Sila pastikan 'gid' tab '2026_Live' dimasukkan dengan betul dalam kod.")
