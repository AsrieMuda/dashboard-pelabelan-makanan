import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# 1. KONFIGURASI HALAMAN & TEMA
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Pelabelan Semula Makanan Import",
    page_icon="📊",
    layout="wide"
)

# Muat turun FontAwesome
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
# 2. FUNGSI MUAT DATA (2 SUMBER ASING)
# ----------------------------------------------------

# (A) Data Live 2026 dari Sheet Asal
@st.cache_data(ttl=60)
def load_data_2026():
    sheet_id = "1GCgoOI96Nhaq57ia1CAPG8cWrboBo-kvUlnYSNNVRw8"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=2026"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.astype(str).str.strip()
        
        tarikh_cols = [c for c in df.columns if 'TARIKH' in c.upper()]
        if tarikh_cols:
            df['TARIKH_DATETIME'] = pd.to_datetime(df[tarikh_cols[0]], errors='coerce')
            df['Tahun'] = df['TARIKH_DATETIME'].dt.year.fillna(2026).astype(int)
        else:
            df['Tahun'] = 2026

        fi_cols = [c for c in df.columns if 'FI' in c.upper()]
        df['FI_CLEAN'] = pd.to_numeric(df[fi_cols[0]], errors='coerce').fillna(0) if fi_cols else 0.0

        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# (B) Data Arkib MasterData (2023 - 2025)
@st.cache_data(ttl=300)
def load_data_master():
    sheet_id = "13vBLK7XnzhJFKkouzHWg4sBPXwl10WUJKSO638uwjRU"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=MasterData"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.astype(str).str.strip()
        
        # Kesan lajur tahun atau tarikh
        tarikh_cols = [c for c in df.columns if 'TARIKH' in c.upper() or 'TAHUN' in c.upper()]
        if tarikh_cols:
            df['TARIKH_DATETIME'] = pd.to_datetime(df[tarikh_cols[0]], errors='coerce')
            df['Tahun'] = df['TARIKH_DATETIME'].dt.year.fillna(2024).astype(int)
        else:
            df['Tahun'] = 2024

        fi_cols = [c for c in df.columns if 'FI' in c.upper()]
        df['FI_CLEAN'] = pd.to_numeric(df[fi_cols[0]], errors='coerce').fillna(0) if fi_cols else 0.0

        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# ----------------------------------------------------
# 3. SIDEBAR NAVIGATION (PILIH PAGE)
# ----------------------------------------------------
st.sidebar.title("📌 Menu Halaman")
menu_pilihan = st.sidebar.radio(
    "Pilih Paparan Data:",
    ["🚀 Data Live (2026)", "📚 Data Arkib (2023 - 2025)"]
)

st.sidebar.divider()

# ----------------------------------------------------
# 4. HALAMAN 1: DATA LIVE 2026
# ----------------------------------------------------
if menu_pilihan == "🚀 Data Live (2026)":
    df, error_msg = load_data_2026()
    
    if error_msg:
        st.error(f"❌ Ralat membaca data 2026: {error_msg}")
    elif df.empty:
        st.warning("⚠️ Data 2026 kosong.")
    else:
        col_bulan = 'BULAN' if 'BULAN' in df.columns else df.columns[0]
        col_jenis = [c for c in df.columns if 'JENIS' in c.upper()]
        jenis_field = col_jenis[0] if col_jenis else None

        # Penapis Sidebar
        st.sidebar.header("🔍 Penapis Data 2026")
        senarai_bulan = [b for b in df[col_bulan].dropna().unique() if str(b).strip() != '']
        bulan_dipilih = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan, default=senarai_bulan)

        if jenis_field:
            senarai_jenis = [j for j in df[jenis_field].dropna().unique() if str(j).strip() != '']
            jenis_dipilih = st.sidebar.multiselect("Pilih Jenis Permohonan:", options=senarai_jenis, default=senarai_jenis)
        else:
            jenis_dipilih = []

        min_fi = float(df['FI_CLEAN'].min())
        max_fi = float(df['FI_CLEAN'].max())
        julat_fi = st.sidebar.slider("Pilih Julat Fi (RM):", min_value=min_fi, max_value=max_fi if max_fi > min_fi else min_fi + 100.0, value=(min_fi, max_fi if max_fi > min_fi else min_fi + 100.0))

        # Tapis
        df_filtered = df.copy()
        if bulan_dipilih:
            df_filtered = df_filtered[df_filtered[col_bulan].isin(bulan_dipilih)]
        if jenis_dipilih and jenis_field:
            df_filtered = df_filtered[df_filtered[jenis_field].isin(jenis_dipilih)]
        df_filtered = df_filtered[(df_filtered['FI_CLEAN'] >= julat_fi[0]) & (df_filtered['FI_CLEAN'] <= julat_fi[1])]

        # Header & KPI
        st.title("📊 Dashboard Pelabelan Semula Makanan Import")
        st.caption("Data Permohonan Live Terus Dari Sumber Asal (2026)")
        st.divider()

        total_apps = len(df_filtered)
        total_fees = df_filtered['FI_CLEAN'].sum()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="kpi-card kpi-blue"><div><div class="kpi-title">JUMLAH PERMOHONAN</div><div class="kpi-value">{total_apps:,}</div></div><div class="kpi-icon"><i class="fa-solid fa-folder-open"></i></div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card kpi-green"><div><div class="kpi-title">JUMLAH KUTIPAN FI</div><div class="kpi-value">RM {total_fees:,.2f}</div></div><div class="kpi-icon"><i class="fa-solid fa-wallet"></i></div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card kpi-cyan"><div><div class="kpi-title">PERMOHONAN PROSES</div><div class="kpi-value">{total_apps:,}</div></div><div class="kpi-icon"><i class="fa-solid fa-circle-check"></i></div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="kpi-card kpi-yellow"><div><div class="kpi-title">KADAR PROSES</div><div class="kpi-value">100.0%</div></div><div class="kpi-icon"><i class="fa-solid fa-percent"></i></div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Graf
        g_col1, g_col2 = st.columns([2, 1])
        with g_col1:
            st.subheader("📦 Jenis Permohonan")
            if jenis_field and not df_filtered.empty:
                jenis_counts = df_filtered[jenis_field].value_counts().reset_index()
                jenis_counts.columns = ['Jenis', 'Jumlah']
                fig_bar = px.bar(jenis_counts, x='Jumlah', y='Jenis', orientation='h', text='Jumlah', color_discrete_sequence=['#0d6efd'])
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_bar, use_container_width=True)
        with g_col2:
            st.subheader("📌 Agihan Mengikut Bulan")
            if not df_filtered.empty:
                bulan_counts = df_filtered[col_bulan].value_counts().reset_index()
                bulan_counts.columns = ['Bulan', 'Jumlah']
                fig_pie = px.pie(bulan_counts, values='Jumlah', names='Bulan', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
                fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_pie, use_container_width=True)

        # Jadual Data
        st.subheader("🔍 Enjin Carian & Data Permohonan Live 2026")
        search_term = st.text_input("Carian Pantas:")
        display_df = df_filtered.drop(columns=['TARIKH_DATETIME', 'FI_CLEAN', 'Tahun'], errors='ignore')
        if search_term and not display_df.empty:
            mask = display_df.astype(str).apply(lambda row: row.str.contains(search_term, case=False, na=False)).any(axis=1)
            display_df = display_df[mask]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ----------------------------------------------------
# 5. HALAMAN 2: DATA ARKIB MASTERDATA (2023 - 2025)
# ----------------------------------------------------
else:
    df_m, error_msg_m = load_data_master()
    
    if error_msg_m:
        st.error(f"❌ Ralat membaca data MasterData: {error_msg_m}")
    elif df_m.empty:
        st.warning("⚠️ Data MasterData kosong.")
    else:
        col_bulan_m = 'BULAN' if 'BULAN' in df_m.columns else df_m.columns[0]
        col_jenis_m = [c for c in df_m.columns if 'KUMPULAN' in c.upper() or 'JENIS' in c.upper()]
        jenis_field_m = col_jenis_m[0] if col_jenis_m else None

        # Penapis Sidebar Arkib
        st.sidebar.header("🔍 Penapis Data Arkib")
        senarai_tahun_m = sorted(list(df_m['Tahun'].unique()))
        tahun_dipilih_m = st.sidebar.multiselect("Pilih Tahun:", options=senarai_tahun_m, default=senarai_tahun_m)

        senarai_bulan_m = [b for b in df_m[col_bulan_m].dropna().unique() if str(b).strip() != '']
        bulan_dipilih_m = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan_m, default=senarai_bulan_m)

        min_fi_m = float(df_m['FI_CLEAN'].min())
        max_fi_m = float(df_m['FI_CLEAN'].max())
        julat_fi_m = st.sidebar.slider("Pilih Julat Fi (RM):", min_value=min_fi_m, max_value=max_fi_m if max_fi_m > min_fi_m else min_fi_m + 100.0, value=(min_fi_m, max_fi_m if max_fi_m > min_fi_m else min_fi_m + 100.0))

        # Tapis
        df_filtered_m = df_m.copy()
        if tahun_dipilih_m:
            df_filtered_m = df_filtered_m[df_filtered_m['Tahun'].isin(tahun_dipilih_m)]
        if bulan_dipilih_m:
            df_filtered_m = df_filtered_m[df_filtered_m[col_bulan_m].isin(bulan_dipilih_m)]
        df_filtered_m = df_filtered_m[(df_filtered_m['FI_CLEAN'] >= julat_fi_m[0]) & (df_filtered_m['FI_CLEAN'] <= julat_fi_m[1])]

        # Header & KPI Arkib
        st.title("📚 Arkib Data MasterData (2023 - 2025)")
        st.caption("Rekod Terkumpul Permohonan Integrasi Terdahulu")
        st.divider()

        total_apps_m = len(df_filtered_m)
        total_fees_m = df_filtered_m['FI_CLEAN'].sum()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="kpi-card kpi-blue"><div><div class="kpi-title">JUMLAH PERMOHONAN</div><div class="kpi-value">{total_apps_m:,}</div></div><div class="kpi-icon"><i class="fa-solid fa-box-archive"></i></div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card kpi-green"><div><div class="kpi-title">KUTIPAN FI TERKUMPUL</div><div class="kpi-value">RM {total_fees_m:,.2f}</div></div><div class="kpi-icon"><i class="fa-solid fa-coins"></i></div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card kpi-cyan"><div><div class="kpi-title">REKOD DITERIMA</div><div class="kpi-value">{total_apps_m:,}</div></div><div class="kpi-icon"><i class="fa-solid fa-list-check"></i></div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="kpi-card kpi-yellow"><div><div class="kpi-title">STATUS REKOD</div><div class="kpi-value">LENGKAP</div></div><div class="kpi-icon"><i class="fa-solid fa-database"></i></div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Graf Arkib
        g_col1, g_col2 = st.columns([2, 1])
        with g_col1:
            st.subheader("📦 Kumpulan Produk / Makanan")
            if jenis_field_m and not df_filtered_m.empty:
                counts_m = df_filtered_m[jenis_field_m].value_counts().reset_index()
                counts_m.columns = ['KUMPULAN', 'Jumlah']
                fig_bar_m = px.bar(counts_m, x='Jumlah', y='KUMPULAN', orientation='h', text='Jumlah', color_discrete_sequence=['#198754'])
                fig_bar_m.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_bar_m, use_container_width=True)
        with g_col2:
            st.subheader("📊 Agihan Mengikut Tahun")
            if not df_filtered_m.empty:
                tahun_counts = df_filtered_m['Tahun'].value_counts().reset_index()
                tahun_counts.columns = ['Tahun', 'Jumlah']
                fig_pie_m = px.pie(tahun_counts, values='Jumlah', names='Tahun', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie_m.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_pie_m, use_container_width=True)

        # Jadual Data Arkib
        st.subheader("🔍 Enjin Carian Data MasterData")
        search_term_m = st.text_input("Carian Pantas MasterData:")
        display_df_m = df_filtered_m.drop(columns=['TARIKH_DATETIME', 'FI_CLEAN'], errors='ignore')
        if search_term_m and not display_df_m.empty:
            mask_m = display_df_m.astype(str).apply(lambda row: row.str.contains(search_term_m, case=False, na=False)).any(axis=1)
            display_df_m = display_df_m[mask_m]
        st.dataframe(display_df_m, use_container_width=True, hide_index=True)
