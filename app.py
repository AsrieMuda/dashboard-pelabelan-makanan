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

# Muat turun FontAwesome untuk ikon kad
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

# Styling Kad KPI Berwarna
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
# 2. FUNGSI MUAT DATA DIRECT DARI FAIL ASAL
# ----------------------------------------------------
@st.cache_data(ttl=60) # Segarkan data automatik setiap 1 minit
def load_data():
    # ID Sheet Asal dari formula IMPORTRANGE anda
    original_sheet_id = "1GCgoOI96Nhaq57ia1CAPG8cWrboBo-kvUlnYSNNVRw8"
    original_tab_name = "2026"
    
    # URL GViz Export terus dari sumber asal
    url = f"https://docs.google.com/spreadsheets/d/{original_sheet_id}/gviz/tq?tqx=out:csv&sheet={original_tab_name}"
    
    try:
        df_raw = pd.read_csv(url)
        
        if df_raw.empty:
            return pd.DataFrame(), "Fail Google Sheets asal adalah kosong."
            
        # Bersihkan nama lajur
        df_raw.columns = df_raw.columns.astype(str).str.strip()
        
        # Ekstrak Tarikh & Tahun
        tarikh_cols = [c for c in df_raw.columns if 'TARIKH' in c.upper()]
        if tarikh_cols:
            df_raw['TARIKH_DATETIME'] = pd.to_datetime(df_raw[tarikh_cols[0]], errors='coerce')
            df_raw['Tahun'] = df_raw['TARIKH_DATETIME'].dt.year.fillna(2026).astype(int)
        else:
            df_raw['Tahun'] = 2026

        # Ekstrak & Bersihkan Lajur Fi Bayaran (RM)
        fi_cols = [c for c in df_raw.columns if 'FI' in c.upper()]
        if fi_cols:
            df_raw['FI_CLEAN'] = pd.to_numeric(df_raw[fi_cols[0]], errors='coerce').fillna(0)
        else:
            df_raw['FI_CLEAN'] = 0.0

        return df_raw, None
        
    except Exception as err:
        return pd.DataFrame(), str(err)

# Panggilan muat data
df, error_msg = load_data()

# ----------------------------------------------------
# 3. SEMAKAN DATA & PAPARAN DASHBOARD
# ----------------------------------------------------
if error_msg:
    st.error(f"❌ Ralat membaca fail asal: {error_msg}")
    st.info("💡 **Langkah Penting:** Sila pastikan FAIL ASAL (`1GCgoOI96Nhaq57ia1CAPG8cWrboBo-kvUlnYSNNVRw8`) juga mempunyai tetapan perkongsian **'Anyone with the link can view'**.")

elif df.empty:
    st.warning("⚠️ Data ditemui tetapi helaian asal adalah kosong.")

else:
    # Kenal pasti nama lajur
    col_bulan = 'BULAN' if 'BULAN' in df.columns else df.columns[0]
    col_jenis = [c for c in df.columns if 'JENIS' in c.upper()]
    jenis_field = col_jenis[0] if col_jenis else None

    # ----------------------------------------------------
    # SIDEBAR (PENAPIS DATA INTERAKTIF)
    # ----------------------------------------------------
    st.sidebar.header("🔍 Penapis Data")

    # Penapis Tahun
    senarai_tahun = sorted(list(df['Tahun'].unique()))
    tahun_dipilih = st.sidebar.multiselect("Pilih Tahun:", options=senarai_tahun, default=senarai_tahun)

    # Penapis Bulan
    senarai_bulan = [b for b in df[col_bulan].dropna().unique() if str(b).strip() != '']
    bulan_dipilih = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan, default=senarai_bulan)

    # Penapis Jenis Permohonan
    if jenis_field:
        senarai_jenis = [j for j in df[jenis_field].dropna().unique() if str(j).strip() != '']
        jenis_dipilih = st.sidebar.multiselect("Pilih Jenis Permohonan:", options=senarai_jenis, default=senarai_jenis)
    else:
        jenis_dipilih = []

    # Slider Julat Fi
    min_fi = float(df['FI_CLEAN'].min())
    max_fi = float(df['FI_CLEAN'].max())
    if min_fi == max_fi:
        max_fi += 100.0

    julat_fi = st.sidebar.slider("Pilih Julat Fi (RM):", min_value=min_fi, max_value=max_fi, value=(min_fi, max_fi))

    # LOGIK TAPISAN DATA
    df_filtered = df.copy()
    if tahun_dipilih:
        df_filtered = df_filtered[df_filtered['Tahun'].isin(tahun_dipilih)]
    if bulan_dipilih:
        df_filtered = df_filtered[df_filtered[col_bulan].isin(bulan_dipilih)]
    if jenis_dipilih and jenis_field:
        df_filtered = df_filtered[df_filtered[jenis_field].isin(jenis_dipilih)]
    
    df_filtered = df_filtered[(df_filtered['FI_CLEAN'] >= julat_fi[0]) & (df_filtered['FI_CLEAN'] <= julat_fi[1])]

    # ----------------------------------------------------
    # HEADER DASHBOARD
    # ----------------------------------------------------
    st.title("📊 Dashboard Pelabelan Semula Makanan Import")
    st.caption("Data Permohonan Live Terus Dari Sumber Asal (2026)")
    st.divider()

    # ----------------------------------------------------
    # KAD KPI BERWARNA (CARD VIEW)
    # ----------------------------------------------------
    total_apps = len(df_filtered)
    total_fees = df_filtered['FI_CLEAN'].sum()
    total_proses = total_apps
    kadar_proses = 100.0 if total_apps > 0 else 0.0

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
                    <div class="kpi-value">{total_proses:,}</div>
                </div>
                <div class="kpi-icon"><i class="fa-solid fa-circle-check"></i></div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card kpi-yellow">
                <div>
                    <div class="kpi-title">KADAR PROSES</div>
                    <div class="kpi-value">{kadar_proses:.1f}%</div>
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
        if jenis_field and not df_filtered.empty:
            jenis_counts = df_filtered[jenis_field].value_counts().reset_index()
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
    # JADUAL DATA LIVE & CARIAN
    # ----------------------------------------------------
    st.subheader("🔍 Enjin Carian & Data Permohonan Live")

    search_term = st.text_input("Carian Pantas (Syarikat, Kod Rujukan, dll.):")
    
    display_df = df_filtered.drop(columns=['TARIKH_DATETIME', 'FI_CLEAN', 'Tahun'], errors='ignore')
    
    if search_term and not display_df.empty:
        mask = display_df.astype(str).apply(lambda row: row.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, hide_index=True)
