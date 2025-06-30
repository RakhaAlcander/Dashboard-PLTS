import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Dashboard PLTS Atap",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #f0f8ff;
        border-left: 5px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Sample data (expanded based on the provided structure)
@st.cache_data
def load_sample_data():
    return pd.read_excel("C:/Users/RAKHA ALCANDER/OneDrive/Documents/MAGANG PLN/PLTS  ATAP.xlsx")

def main():
    st.markdown('<div class="main-header">☀️ Dashboard Analisis PLTS Atap</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_sample_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    
    unitap_filter = st.sidebar.multiselect(
        "Pilih UNITAP:",
        options=df['UNITAP'].unique(),
        default=df['UNITAP'].unique()
    )
    
    golongan_filter = st.sidebar.multiselect(
        "Pilih Golongan Tarif:",
        options=df['GOL TARIF'].unique(),
        default=df['GOL TARIF'].unique()
    )
    
    kategori_filter = st.sidebar.multiselect(
        "Pilih Kategori Kapasitas:",
        options=df['KATEGORI KAPASITAS'].unique(),
        default=df['KATEGORI KAPASITAS'].unique()
    )
    
    # Filter data
    filtered_df = df[
        (df['UNITAP'].isin(unitap_filter)) &
        (df['GOL TARIF'].isin(golongan_filter)) &
        (df['KATEGORI KAPASITAS'].isin(kategori_filter))
    ]
    
    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih.")
        return
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pelanggan = len(filtered_df)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_pelanggan}</h3>
            <p>Total Pelanggan PLTS</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_kapasitas = filtered_df['KAPASITAS PLTS ATAP'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_kapasitas:,.0f} VA</h3>
            <p>Total Kapasitas PLTS</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_utilization = filtered_df['% THD DAYA'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{avg_utilization:.1f}%</h3>
            <p>Rata-rata Utilisasi</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_ekspor = filtered_df['Total_Ekspor'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_ekspor:,.0f} kWh</h3>
            <p>Total Ekspor Energi</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribusi Golongan Tarif")
        fig_pie = px.pie(
            filtered_df, 
            names='GOL_TARIF', 
            title="Distribusi Pelanggan per Golongan Tarif",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("⚡ Kapasitas vs Daya Terpasang")
        fig_scatter = px.scatter(
            filtered_df,
            x='DAYA',
            y='KAPASITAS_PLTS_ATAP',
            size='Total_Ekspor',
            color='GOL_TARIF',
            hover_data=['NAMA', 'PERSEN_THD_DAYA'],
            title="Hubungan Daya vs Kapasitas PLTS"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Performance Analysis
    st.subheader("📈 Analisis Kinerja PLTS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Utilization Analysis
        fig_hist = px.histogram(
            filtered_df,
            x='PERSEN_THD_DAYA',
            nbins=10,
            title="Distribusi Tingkat Utilisasi PLTS",
            labels={'PERSEN_THD_DAYA': 'Utilisasi (%)', 'count': 'Jumlah Pelanggan'}
        )
        fig_hist.update_layout(bargap=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Import vs Export
        filtered_df['Net_Export'] = filtered_df['Total_Ekspor'] - filtered_df['Total_Impor']
        fig_bar = px.bar(
            filtered_df.head(10),
            x='NAMA',
            y=['Total_Impor', 'Total_Ekspor'],
            title="Top 10 Pelanggan: Impor vs Ekspor Energi",
            barmode='group'
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Geographic Analysis
    st.subheader("🗺️ Analisis Geografis")
    
    unitup_summary = filtered_df.groupby('UNITUP').agg({
        'KAPASITAS_PLTS_ATAP': 'sum',
        'Total_Ekspor': 'sum',
        'PERSEN_THD_DAYA': 'mean',
        'NAMA': 'count'
    }).round(2)
    unitup_summary.columns = ['Total Kapasitas', 'Total Ekspor', 'Avg Utilisasi', 'Jumlah Pelanggan']
    
    fig_geo = px.bar(
        unitup_summary.reset_index(),
        x='UNITUP',
        y=['Total Kapasitas', 'Total Ekspor'],
        title="Perbandingan Kinerja per UNITUP",
        barmode='group'
    )
    st.plotly_chart(fig_geo, use_container_width=True)
    
    # Efficiency Analysis
    st.subheader("🎯 Analisis Efisiensi")
    
    filtered_df['Efficiency_Ratio'] = filtered_df['Total_Ekspor'] / (filtered_df['KAPASITAS_PLTS_ATAP'] / 1000)
    filtered_df['ROI_Indicator'] = filtered_df['PERSEN_THD_DAYA'] * filtered_df['Total_Ekspor'] / 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_efficiency = px.scatter(
            filtered_df,
            x='PERSEN_THD_DAYA',
            y='Efficiency_Ratio',
            color='GOL_TARIF',
            size='KAPASITAS_PLTS_ATAP',
            title="Efisiensi vs Utilisasi",
            labels={'PERSEN_THD_DAYA': 'Utilisasi (%)', 'Efficiency_Ratio': 'Rasio Efisiensi'}
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)
    
    with col2:
        # Performance Categories
        def categorize_performance(row):
            if row['PERSEN_THD_DAYA'] >= 80 and row['Total_Ekspor'] > 100:
                return 'High Performer'
            elif row['PERSEN_THD_DAYA'] >= 60 and row['Total_Ekspor'] > 50:
                return 'Good Performer'
            elif row['PERSEN_THD_DAYA'] >= 40:
                return 'Average Performer'
            else:
                return 'Needs Attention'
        
        filtered_df['Performance_Category'] = filtered_df.apply(categorize_performance, axis=1)
        
        perf_dist = filtered_df['Performance_Category'].value_counts()
        fig_perf = px.pie(
            values=perf_dist.values,
            names=perf_dist.index,
            title="Kategori Performa Pelanggan",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_perf, use_container_width=True)
    
    # Insights and Recommendations
    st.subheader("💡 Insights & Rekomendasi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
            <h4>🔍 Key Insights:</h4>
            <ul>
                <li><strong>Utilisasi Rata-rata:</strong> {:.1f}% - Masih ada ruang untuk optimalisasi</li>
                <li><strong>Top Performer:</strong> Pelanggan dengan utilisasi >80% menghasilkan ekspor tertinggi</li>
                <li><strong>Segmen Rumah Tangga:</strong> Dominasi dalam adopsi PLTS Atap</li>
                <li><strong>Potensi Ekspor:</strong> {:.0f} kWh total energi diekspor ke grid</li>
            </ul>
        </div>
        """.format(
            avg_utilization,
            total_ekspor
        ), unsafe_allow_html=True)
    
    with col2:
        needs_attention = filtered_df[filtered_df['Performance_Category'] == 'Needs Attention']
        high_performers = filtered_df[filtered_df['Performance_Category'] == 'High Performer']
        
        st.markdown("""
        <div class="insight-box">
            <h4>📋 Rekomendasi Strategis:</h4>
            <ul>
                <li><strong>Optimalisasi:</strong> {} pelanggan perlu perhatian khusus</li>
                <li><strong>Best Practice:</strong> Replikasi strategi dari {} high performers</li>
                <li><strong>Ekspansi:</strong> Fokus pengembangan di area dengan utilisasi rendah</li>
                <li><strong>Maintenance:</strong> Program maintenance rutin untuk efisiensi optimal</li>
            </ul>
        </div>
        """.format(
            len(needs_attention),
            len(high_performers)
        ), unsafe_allow_html=True)
    
    # Detailed Data Table
    with st.expander("📋 Lihat Data Detail"):
        st.subheader("Data Pelanggan PLTS Atap")
        
        # Add performance indicators to display
        display_df = filtered_df[[
            'NAMA', 'UNITUP', 'GOL_TARIF', 'DAYA', 'KAPASITAS_PLTS_ATAP',
            'PERSEN_THD_DAYA', 'Total_Impor', 'Total_Ekspor', 'Performance_Category'
        ]].round(2)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data CSV",
            data=csv,
            file_name=f"plts_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()