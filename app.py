import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Dashboard Pelabelan Semula Makanan Import",
    page_icon="📊",
    layout="wide"
)

# Load FontAwesome untuk ikon pada kad
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

# 2. CSS Khas Untuk Menjadikan Kad Berwarna-warni Persis Rekaan Asal
st.markdown("""
    <style>
    /* Styling Kad KPI */
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
    
    /* Kemaskan Padding Container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Fungsi Muat Data
@st.cache_data
def load_data():
    sheet_id = "GANTIKAN_DENGAN_SPREADSHEET_ID_ANDA"
    sheet_name = "MasterData"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(url)
    except:
        # Data Simulasi jika Google Sheet tiada
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

    if 'Bulan' in df.columns:
        df['Bulan'] = df['Bulan'].astype(str).str.strip()
    if 'Status' in df.columns:
        df['Status'] = df['Status'].astype(str).str.upper()
    if 'Fi' in df.columns:
        df['Fi'] = pd.to_numeric(df['Fi'], errors='coerce').fillna(0)

    return df

df = load_data()

# ----------------------------------------------------
# 4. SIDEBAR (PENAPIS DATA)
# ----------------------------------------------------
st.sidebar.header("🔍 Penapis Data")

senarai_tahun = sorted(list(df['Tahun'].unique())) if 'Tahun' in df.columns else []
tahun_dipilih = st.sidebar.multiselect("Pilih Tahun:", options=senarai_tahun, default=senarai_tahun)

senarai_bulan = list(df['Bulan'].unique()) if 'Bulan' in df.columns else []
bulan_dipilih = st.sidebar.multiselect("Pilih Bulan:", options=senarai_bulan, default=senarai_bulan)

senarai_status = list(df['Status'].unique()) if 'Status' in df.columns else []
status_dipilih = st.sidebar.multiselect("Pilih Status Permohonan:", options=senarai_status, default=senarai_status)

min_fi = float(df['Fi'].min()) if not df.empty else 0.0
max_fi = float(df['Fi'].max()) if not df.empty else 1000.0
if min_fi == max_fi:
    max_fi += 100.0

julat_fi = st.sidebar.slider("Pilih Julat Fi (RM):", min_value=min_fi, max_value=max_fi, value=(min_fi, max_fi))

# Tapis Data
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
# 5. HEADER DASHBOARD
# ----------------------------------------------------
st.title("📊 Dashboard Pelabelan Semula Makanan Import")
st.caption("Analisis Data Permohonan Integrasi (2023 - 2026)")
st.divider()

# ----------------------------------------------------
# 6. KAD KPA BERWARNA (CARD VIEW)
# ----------------------------------------------------
total_apps = len(df_filtered)
total_fees = df_filtered['Fi'].sum() if not df_filtered.empty else 0
total_lulus = len(df_filtered[df_filtered['Status'].str.contains("LULUS", na=False)]) if not df_filtered.empty else 0
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
                <div class="kpi-title">PERMOHONAN LULUS</div>
                <div class="kpi-value">{total_lulus:,}</div>
            </div>
            <div class="kpi-icon"><i class="fa-solid fa-circle-check"></i></div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card kpi-yellow">
            <div>
                <div class="kpi-title">KADAR KELULUSAN</div>
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
    st.subheader(" Graf Jenis Produk (Kumpulan Makanan)")
    if not df_filtered.empty:
        kumpulan_counts = df_filtered['Kumpulan'].value_counts().reset_index()
        kumpulan_counts.columns = ['Kumpulan', 'Jumlah']
        
        fig_bar = px.bar(
            kumpulan_counts, 
            x='Jumlah', 
            y='Kumpulan', 
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
        st.info("Tiada data ditemui.")

with g_col2:
    st.subheader(" Status Kelulusan")
    if not df_filtered.empty:
        status_counts = df_filtered['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        
        fig_pie = px.pie(
            status_counts, 
            values='Jumlah', 
            names='Status', 
            hole=0.5,
            color_discrete_sequence=['#198754', '#dc3545', '#ffc107', '#6c757d']
        )
        fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Tiada data ditemui.")

# ----------------------------------------------------
# 8. JADUAL DATA
# ----------------------------------------------------
st.subheader("🔍 Enjin Carian & Data Permohonan")

search_term = st.text_input("Carian Pantas (Syarikat, Kod, Produk, atau Negara):")
if search_term:
    df_filtered = df_filtered[
        df_filtered['Syarikat'].astype(str).str.contains(search_term, case=False) |
        df_filtered['Kod Rujukan'].astype(str).str.contains(search_term, case=False) |
        df_filtered['Produk'].astype(str).str.contains(search_term, case=False) |
        df_filtered['Negara'].astype(str).str.contains(search_term, case=False)
    ]

st.dataframe(df_filtered, use_container_width=True, hide_index=True)
