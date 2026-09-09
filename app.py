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

# Load FontAwesome untuk ikon
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
# 2. FUNGSI MUAT DATA DENGAN PEMETAAN INDEKS N & AC
# ----------------------------------------------------

# (A) Data Live 2026
@st.cache_data(ttl=60)
def load_data_2026():
    sheet_id = "1GCgoOI96Nhaq57ia1CAPG8cWrboBo-kvUlnYSNNVRw8"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=2026"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.astype(str).str.strip()
        
        # Lajur N (Index 13) - Nama Produk & Jenama
        if df.shape[1] > 13:
            df['PRODUK_CLEAN'] = df.iloc[:, 13].fillna('Tidak Diketahui').astype(str).str.strip()
        else:
            df['PRODUK_CLEAN'] = 'Tidak Diketahui'

        # Lajur AC (Index 28) - Kumpulan Makanan
        if df.shape[1] > 28:
            df['KUMPULAN_CLEAN'] = df.iloc[:, 28].fillna('Lain-lain').astype(str).str.strip()
        else:
            df['KUMPULAN_CLEAN'] = 'Lain-lain'

        # Tarikh & Tahun (Index 2 / Tarikh Terima)
        df['Tahun'] = 2026
        fi_cols = [c for c in df.columns if 'FI' in c.upper()]
        df['FI_CLEAN'] = pd.to_numeric(df[fi_cols[0]].astype(str).str.replace('RM','').str.replace(',',''), errors='coerce').fillna(0) if fi_cols else 0.0

        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# (B) Data Arkib MasterData (2023 - 2025)
@st.cache_data(ttl=300)
def load_data_master():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT-az79V0Akfc3S2MR0NdzSiQZlThMAr8JO-CIdkmB3d2yiIA_p-q4bEHCYREVc1VF4gR9qhtPn4Bdy/pub?gid=184868812&single=true&output=csv"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.astype(str).str.strip()

        # Pemetaaan Lajur N (Index 13) - Nama Produk & Jenama
        if df.shape[1] > 13:
            df['PRODUK_CLEAN'] = df.iloc[:, 13].fillna('Tidak Diketahui').astype(str).str.strip()
        else:
            df['PRODUK_CLEAN'] = 'Tidak Diketahui'

        # Pemetaan Lajur AC (Index 28) - Kumpulan Makanan
        if df.shape[1] > 28:
            df['KUMPULAN_CLEAN'] = df.iloc[:, 28].fillna('Lain-lain').astype(str).str.strip()
        else:
            df['KUMPULAN_CLEAN'] = 'Lain-lain'

        # Ekstrak Tahun dari Lajur Index 2 (Tarikh Terima)
        df['Tahun'] = df.iloc[:, 2].astype(str).str.extract(r'(202[3-6])')[0].fillna(2024).astype(int)

        # Pembersihan Fi Bayaran (Index 7)
        df['FI_CLEAN'] = pd.to_numeric(df.iloc[:, 7].astype(str).str.replace('RM','').str.replace(',',''), errors='coerce').fillna(0)

        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# ----------------------------------------------------
# 3. NAVIGATION SIDEBAR
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
        col_bulan = df.columns[0]

        # Penapis Sidebar
        st.sidebar.header("🔍 Penapis Data 2026")
        senarai_bulan = [b for b in df[col_bulan].dropna().unique() if str(b).strip() != '']
        bulan_dipilih = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan, default=senarai_bulan)

        senarai_kumpulan = [k for k in df['KUMPULAN_CLEAN'].dropna().unique() if str(k).strip() != '']
        kumpulan_dipilih = st.sidebar.multiselect("Pilih Kumpulan Makanan (Lajur AC):", options=senarai_kumpulan, default=senarai_kumpulan)

        min_fi = float(df['FI_CLEAN'].min())
        max_fi = float(df['FI_CLEAN'].max())
        julat_fi = st.sidebar.slider("Pilih Julat Fi (RM):", min_value=min_fi, max_value=max_fi if max_fi > min_fi else min_fi + 100.0, value=(min_fi, max_fi if max_fi > min_fi else min_fi + 100.0))

        # Tapis
        df_filtered = df.copy()
        if bulan_dipilih:
            df_filtered = df_filtered[df_filtered[col_bulan].isin(bulan_dipilih)]
        if kumpulan_dipilih:
            df_filtered = df_filtered[df_filtered['KUMPULAN_CLEAN'].isin(kumpulan_dipilih)]
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

        # GRAF UNTUK LAJUR AC & LAJUR N
        g_col1, g_col2 = st.columns([1, 1])
        
        with g_col1:
            st.subheader("Top Kumpulan Makanan")
            if not df_filtered.empty:
                counts_ac = df_filtered['KUMPULAN_CLEAN'].value_counts().head(10).reset_index()
                counts_ac.columns = ['Kumpulan Makanan', 'Jumlah']
                fig_bar_ac = px.bar(counts_ac, x='Jumlah', y='Kumpulan Makanan', orientation='h', text='Jumlah', color_discrete_sequence=['#0d6efd'])
                fig_bar_ac.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_bar_ac, use_container_width=True)

        with g_col2:
            st.subheader("Top Produk & Jenama")
            if not df_filtered.empty:
                counts_n = df_filtered['PRODUK_CLEAN'].value_counts().head(10).reset_index()
                counts_n.columns = ['Nama Produk & Jenama', 'Jumlah']
                fig_bar_n = px.bar(counts_n, x='Jumlah', y='Nama Produk & Jenama', orientation='h', text='Jumlah', color_discrete_sequence=['#0dcaf0'])
                fig_bar_n.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_bar_n, use_container_width=True)

        # Jadual Data
        st.subheader("🔍 Enjin Carian & Data Permohonan Live 2026")
        search_term = st.text_input("Carian Pantas (Syarikat, Produk, Kumpulan):")
        display_df = df_filtered.drop(columns=['PRODUK_CLEAN', 'KUMPULAN_CLEAN', 'FI_CLEAN', 'Tahun'], errors='ignore')
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
        col_bulan_m = df_m.columns[0]

        # Penapis Sidebar Arkib
        st.sidebar.header("🔍 Penapis Data Arkib")
        senarai_tahun_m = sorted(list(df_m['Tahun'].unique()))
        tahun_dipilih_m = st.sidebar.multiselect("Pilih Tahun:", options=senarai_tahun_m, default=senarai_tahun_m)

        senarai_bulan_m = [b for b in df_m[col_bulan_m].dropna().unique() if str(b).strip() != '']
        bulan_dipilih_m = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan_m, default=senarai_bulan_m)

        senarai_kumpulan_m = [k for k in df_m['KUMPULAN_CLEAN'].dropna().unique() if str(k).strip() != '']
        kumpulan_dipilih_m = st.sidebar.multiselect("Pilih Kumpulan Makanan (Lajur AC):", options=senarai_kumpulan_m, default=senarai_kumpulan_m)

        min_fi_m = float(df_m['FI_CLEAN'].min())
        max_fi_m = float(df_m['FI_CLEAN'].max())
        julat_fi_m = st.sidebar.slider("Pilih Julat Fi (RM):", min_value=min_fi_m, max_value=max_fi_m if max_fi_m > min_fi_m else min_fi_m + 100.0, value=(min_fi_m, max_fi_m if max_fi_m > min_fi_m else min_fi_m + 100.0))

        # Tapis
        df_filtered_m = df_m.copy()
        if tahun_dipilih_m:
            df_filtered_m = df_filtered_m[df_filtered_m['Tahun'].isin(tahun_dipilih_m)]
        if bulan_dipilih_m:
            df_filtered_m = df_filtered_m[df_filtered_m[col_bulan_m].isin(bulan_dipilih_m)]
        if kumpulan_dipilih_m:
            df_filtered_m = df_filtered_m[df_filtered_m['KUMPULAN_CLEAN'].isin(kumpulan_dipilih_m)]
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

        # GRAF UNTUK LAJUR AC & LAJUR N (ARKIB)
        g_col1, g_col2 = st.columns([1, 1])
        
        with g_col1:
            st.subheader("📦 Kumpulan Makanan (Lajur AC)")
            if not df_filtered_m.empty:
                counts_ac_m = df_filtered_m['KUMPULAN_CLEAN'].value_counts().head(10).reset_index()
                counts_ac_m.columns = ['Kumpulan Makanan', 'Jumlah']
                fig_bar_ac_m = px.bar(counts_ac_m, x='Jumlah', y='Kumpulan Makanan', orientation='h', text='Jumlah', color_discrete_sequence=['#198754'])
                fig_bar_ac_m.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_bar_ac_m, use_container_width=True)

        with g_col2:
            st.subheader("🏷️ Top Produk & Jenama (Lajur N)")
            if not df_filtered_m.empty:
                counts_n_m = df_filtered_m['PRODUK_CLEAN'].value_counts().head(10).reset_index()
                counts_n_m.columns = ['Nama Produk & Jenama', 'Jumlah']
                fig_bar_n_m = px.bar(counts_n_m, x='Jumlah', y='Nama Produk & Jenama', orientation='h', text='Jumlah', color_discrete_sequence=['#ffc107'])
                fig_bar_n_m.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_bar_n_m, use_container_width=True)

        # Jadual Data Arkib
        st.subheader("🔍 Enjin Carian Data MasterData")
        search_term_m = st.text_input("Carian Pantas MasterData:")
        display_df_m = df_filtered_m.drop(columns=['PRODUK_CLEAN', 'KUMPULAN_CLEAN', 'FI_CLEAN'], errors='ignore')
        if search_term_m and not display_df_m.empty:
            mask_m = display_df_m.astype(str).apply(lambda row: row.str.contains(search_term_m, case=False, na=False)).any(axis=1)
            display_df_m = display_df_m[mask_m]
        st.dataframe(display_df_m, use_container_width=True, hide_index=True)
