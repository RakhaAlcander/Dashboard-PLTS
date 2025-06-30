import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
import json
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
warnings.filterwarnings('ignore')
import google.generativeai as genai
import os
import random
from typing import Dict, Any
import openai
import io

# Page config
st.set_page_config(
    page_title="Dashboard PLTS Atap",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - DIPERBAIKI untuk teks hitam
st.markdown("""
    <style>
    .insight-card {
        background-color: #f8f9fa;
        border-left: 5px solid #1f77b4;
        padding: 20px;
        margin: 20px 0;
        border-radius: 10px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .insight-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .insight-card h4 {
        color: #1f77b4;
        margin-bottom: 15px;
    }
    .insight-card ul {
        color: #000000;
        padding-left: 20px;
    }
    .insight-card li {
        margin-bottom: 8px;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

AI_INSIGHTS_CSS = """
        <style>
        /* CRITICAL: Prevent horizontal overflow completely */
        * {
            box-sizing: border-box !important;
        }
        
        html, body, #root, .stApp {
            overflow-x: hidden !important;
            max-width: 100vw !important;
        }
        
        /* Force full width - Override semua container Streamlit */
        .main > div {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: none !important;
        }
        
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: none !important;
            width: 100% !important;
        }
        
        /* Override sidebar constraints */
        .css-1d391kg, .css-1v0mbdj {
            max-width: none !important;
        }
        
        /* Prevent horizontal overflow */
        html, body {
            overflow-x: hidden !important;
        }
        
        .main {
            overflow-x: hidden !important;
        }
        
        /* Insights container - extend beyond normal bounds */
        .insights-fullwidth-container {
            margin-left: -21rem;
            width: calc(100vw - 2rem);
            max-width: none;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 2rem;
            border-radius: 0;
            position: relative;
            box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05);
            overflow-x: hidden;
        }
        
        /* Alternative: Use calculated width instead of viewport */
        .insights-viewport {
            width: calc(100% + 21rem);
            margin-left: -21rem;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 2rem;
            position: relative;
            overflow-x: hidden;
        }
        
        /* SAFE: Fixed width yang tidak akan overflow */
        .insights-fixed-width {
            width: 100%;
            margin: 0 -1rem;
            padding: 2rem 3rem;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            position: relative;
            overflow-x: hidden;
            box-sizing: border-box;
        }
        
        /* Beautiful gradient cards */
        .insight-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 24px;
            margin: 1.5rem 0;
            box-shadow: 
                0 20px 60px rgba(102, 126, 234, 0.3),
                0 8px 32px rgba(0, 0, 0, 0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(20px);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        
        .insight-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #ffd700, #ff6b6b, #4ecdc4, #45b7d1);
            animation: shimmer 3s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .insight-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 
                0 30px 80px rgba(102, 126, 234, 0.4),
                0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .insight-card h4 {
            color: #ffffff;
            margin-bottom: 1.5rem;
            font-size: 1.6rem;
            font-weight: 700;
            text-shadow: 0 2px 8px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .insight-card ul {
            margin: 0;
            padding-left: 1.5rem;
            list-style: none;
        }
        
        .insight-card li {
            margin: 1rem 0;
            line-height: 1.8;
            font-size: 1.05rem;
            position: relative;
            padding-left: 1.5rem;
        }
        
        .insight-card li::before {
            content: '▶';
            position: absolute;
            left: 0;
            color: #ffd700;
            font-size: 0.8rem;
        }
        
        .insight-card strong {
            color: #ffd700;
            font-weight: 600;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }
        
        /* Spectacular header */
        .insights-header {
            text-align: center;
            margin: 3rem 0 4rem 0;
            position: relative;
        }
        
        .insights-title {
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 4s ease-in-out infinite;
            text-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
            line-height: 1.2;
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .insights-subtitle {
            font-size: 1.2rem;
            color: #64748b;
            margin-top: 1rem;
            font-weight: 400;
        }
        
        /* Grid layout responsif */
        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            max-width: none;
            margin: 0;
            box-sizing: border-box;
        }
        
        /* Tombol refresh yang menarik */
        .refresh-button-container {
            text-align: center;
            margin: 3rem 0 2rem 0;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 50px;
            padding: 1rem 2rem;
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        
        .refresh-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
        }
        
        /* Mode toggle */
        .mode-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            border: none;
            border-radius: 12px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            font-weight: 600;
            color: #475569;
        }
        
        /* Responsive design */
        @media (max-width: 1024px) {
            .insights-fullwidth-container,
            .insights-viewport {
                margin-left: -1rem;
                width: calc(100% + 2rem);
                padding: 1.5rem;
            }
            
            .insights-fixed-width {
                margin: 0 -0.5rem;
                padding: 1.5rem 2rem;
            }
            
            .insights-grid {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }
        }
        
        @media (max-width: 768px) {
            .insight-card {
                padding: 1.5rem;
                margin: 1rem 0;
            }
            
            .insight-card h4 {
                font-size: 1.3rem;
            }
            
            .insights-fullwidth-container,
            .insights-viewport {
                margin-left: -0.5rem;
                width: calc(100% + 1rem);
                padding: 1rem;
            }
            
            .insights-fixed-width {
                margin: 0 -0.5rem;
                padding: 1rem 1.5rem;
            }
        }
        
        /* Loading animation */
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(102, 126, 234, 0.3);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
    """

class PLTSInsightsGenerator:
    def __init__(self):
        pass

    def setup_gemini(self, api_key: str):
        """Setup Gemini client"""
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    
    def calculate_plts_metrics(self, df):
        """Calculate specific PLTS metrics from the dataset"""
        try:
            # Calculate basic metrics
            avg_utilization = df['PERSEN_THD_DAYA'].mean() if 'PERSEN_THD_DAYA' in df.columns else 0
            
            # Performance categories based on utilization
            if 'PERSEN_THD_DAYA' in df.columns:
                excellent_count = len(df[df['PERSEN_THD_DAYA'] > 75])
                needs_improvement = len(df[df['PERSEN_THD_DAYA'] < 25])
            else:
                excellent_count = 0
                needs_improvement = 0
            
            # Capacity and export data
            total_kapasitas_mwp = df['KAPASITAS_MWp'].sum() if 'KAPASITAS_MWp' in df.columns else 0
            total_ekspor = df['Total_Ekspor'].sum() if 'Total_Ekspor' in df.columns else 0
            
            # Top UNITAP analysis
            if 'UNITAP' in df.columns and 'KAPASITAS_MWp' in df.columns:
                unitap_summary = df.groupby('UNITAP').agg({
                    'KAPASITAS_MWp': 'sum',
                    'Total_Ekspor': 'sum',
                    'PERSEN_THD_DAYA': 'mean'
                }).reset_index()
                
                if len(unitap_summary) > 0:
                    top_unitap = unitap_summary.loc[unitap_summary['KAPASITAS_MWp'].idxmax()]
                    top_unitap_name = top_unitap['UNITAP']
                    top_unitap_capacity = top_unitap['KAPASITAS_MWp']
                else:
                    top_unitap_name = "N/A"
                    top_unitap_capacity = 0
            else:
                top_unitap_name = "N/A"
                top_unitap_capacity = 0
            
            # Additional insights
            low_performance_count = len(df[df['PERSEN_THD_DAYA'] < 25]) if 'PERSEN_THD_DAYA' in df.columns else 0
            high_performance_count = len(df[df['PERSEN_THD_DAYA'] > 75]) if 'PERSEN_THD_DAYA' in df.columns else 0
            
            return {
                'avg_utilization': avg_utilization,
                'excellent_count': excellent_count,
                'needs_improvement': needs_improvement,
                'total_kapasitas_mwp': total_kapasitas_mwp,
                'total_ekspor': total_ekspor,
                'top_unitap_name': top_unitap_name,
                'top_unitap_capacity': top_unitap_capacity,
                'low_performance_count': low_performance_count,
                'high_performance_count': high_performance_count,
                'total_customers': len(df),
                'avg_capacity_per_customer': df['KAPASITAS_PLTS_ATAP'].mean() if 'KAPASITAS_PLTS_ATAP' in df.columns else 0,
                'utilization_std': df['PERSEN_THD_DAYA'].std() if 'PERSEN_THD_DAYA' in df.columns else 0
            }
            
        except Exception as e:
            st.error(f"Error calculating metrics: {str(e)}")
            return {}
    
    def generate_ai_insights_gemini(self, metrics, context=""):
        """Generate insights using Gemini"""
        prompt = f"""
        Sebagai konsultan energi terbarukan senior, analisis data performa PLTS Atap di Jawa Timur:

        📊 METRICS KUNCI:
        - Rata-rata Utilisasi: {metrics['avg_utilization']:.1f}%
        - Excellent Performers: {metrics['excellent_count']} pelanggan ({metrics['excellent_count']/metrics['total_customers']*100:.1f}%)
        - Perlu Perbaikan: {metrics['needs_improvement']} pelanggan ({metrics['needs_improvement']/metrics['total_customers']*100:.1f}%)
        - Total Kapasitas: {metrics['total_kapasitas_mwp']:.1f} MWp
        - Total Ekspor: {metrics['total_ekspor']:,.0f} kWh
        - Unit Terbesar: {metrics['top_unitap_name']} ({metrics['top_unitap_capacity']:.1f} MWp)
        - Performa Rendah (<25%): {metrics['low_performance_count']} pelanggan
        - Performa Tinggi (>75%): {metrics['high_performance_count']} pelanggan

        Context: {context}

        Buatlah 5-8 poin Key Insights dan 5-8 poin Rekomendasi Strategis dalam format JSON:
        {{
            "key_insights": [
                "insight 1",
                "insight 2",
                "dst..."
            ],
            "strategic_recommendations": [
                "rekomendasi 1", 
                "rekomendasi 2",
                "dst..."
            ]
        }}
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
        
def add_api_key_sidebar():
    """Tambahkan API key input di sidebar"""
    st.sidebar.header("🤖 AI Configuration")
    gemini_api_key = st.sidebar.text_input(
        "Gemini API Key", 
        type="password",
        help="Dapatkan API key dari https://makersuite.google.com/app/apikey"
    )
    return gemini_api_key

def add_context_input():
    """Tambahkan context input"""
    context = st.text_area(
        "Konteks Tambahan (Opsional)",
        placeholder="Contoh: Data ini mencakup performa PLTS di 16 UNITAP Jawa Timur periode 2024...",
        height=100
    )
    return context

def render_ai_insights_section(df, api_key, context=""):
    """Render AI insights section dengan full width layout yang optimal"""

    # Inject CSS styling
    st.markdown(AI_INSIGHTS_CSS, unsafe_allow_html=True)

    # Stop lebih awal jika tidak ada API key
    if not api_key:
        st.warning("⚠️ Masukkan Gemini API Key di sidebar untuk menggunakan AI Insights")
        return

    # Layout mode selection
    layout_mode = st.selectbox(
        "🎨 Layout Mode",
        ["Fixed Full Width", "Viewport Full Width", "Extended Container", "Standard"],
        index=0,
        key="ai_layout_mode",  # ✅ Hindari error duplicate ID
        help="Pilih mode layout untuk AI Insights"
    )

    # Mapping ke class CSS
    container_class = {
        "Fixed Full Width": "insights-fixed-width",
        "Viewport Full Width": "insights-viewport",
        "Extended Container": "insights-fullwidth-container"
    }.get(layout_mode, "")  # Default "" untuk "Standard"

    # Buka container jika ada class CSS
    if container_class:
        st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)

    # Header utama
    st.markdown("""
        <div class="insights-header">
            <div class="insights-title">
                💡 AI-Generated Insights
            </div>
            <div class="insights-subtitle">
                Rekomendasi Strategis untuk Optimasi PLTS
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Inisialisasi AI
    try:
        ai_generator = PLTSInsightsGenerator()
        ai_generator.setup_gemini(api_key)
    except Exception as e:
        st.error(f"❌ Gagal inisialisasi AI: {str(e)}")
        if container_class:
            st.markdown('</div>', unsafe_allow_html=True)
        return

    # Spinner selama AI generate
    with st.spinner("🤖 AI sedang menganalisis data PLTS Anda..."):
        # Inisialisasi & hitung
        metrics = ai_generator.calculate_plts_metrics(df)
        if not metrics:
            st.error("❌ Gagal menghitung metrik dari data.")
            return

        ai_response = ai_generator.generate_ai_insights_gemini(metrics, context)

    if ai_response.startswith("Error"):
        st.error(f"❌ {ai_response}")
        return

    try:
        json_start = ai_response.find('{')
        json_end = ai_response.rfind('}') + 1
        json_content = ai_response[json_start:json_end]
        insights_data = json.loads(json_content)
    except Exception as e:
        st.error(f"❌ Gagal parsing hasil AI: {str(e)}")
        with st.expander("🔍 Lihat respons mentah"):
            st.text(ai_response)
        return

    # Indikator selesai
    st.success("✅ Analisis selesai!")

    # Grid insights
    st.markdown('<div class="insights-grid">', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f"""
            <div class="insight-card">
                <h4>🔍 Key Insights</h4>
                <ul>
                    {''.join([f'<li>{insight}</li>' for insight in insights_data.get('key_insights', [])])}
                </ul>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="insight-card">
                <h4>📊 Performance Metrics</h4>
                <ul>
                    <li><strong>Rata-rata Utilisasi:</strong> {metrics['avg_utilization']:.1f}%</li>
                    <li><strong>Excellent Performers:</strong> {metrics['excellent_count']} ({metrics['excellent_count']/metrics['total_customers']*100:.1f}%)</li>
                    <li><strong>Total Kapasitas:</strong> {metrics['total_kapasitas_mwp']:.1f} MWp</li>
                    <li><strong>Perlu Perbaikan:</strong> {metrics['needs_improvement']} ({metrics['needs_improvement']/metrics['total_customers']*100:.1f}%)</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="insight-card">
                <h4>📋 Rekomendasi Strategis</h4>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in insights_data.get('strategic_recommendations', [])])}
                </ul>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="insight-card">
                <h4>🎯 Fokus Area</h4>
                <ul>
                    <li><strong>Top UNITAP:</strong> {metrics['top_unitap_name']} ({metrics['top_unitap_capacity']:.1f} MWp)</li>
                    <li><strong>Potensi Ekspor:</strong> {metrics['total_ekspor']:,.0f} kWh</li>
                    <li><strong>Avg Kapasitas:</strong> {metrics['avg_capacity_per_customer']:.1f} kWp/pelanggan</li>
                    <li><strong>Performa Rendah:</strong> {metrics['low_performance_count']} pelanggan perlu inspeksi</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # End insights-grid

    # Refresh Button
    st.markdown('<div class="refresh-button-container">', unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        if st.button("🔄 Generate New Insights", key="refresh_insights"):
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if container_class:
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Close container jika menggunakan full width
    if container_class:
        st.markdown('</div>', unsafe_allow_html=True)


# Alternative: Versi dengan modal/overlay
def render_ai_insights_modal(df, api_key, context=""):
    """Render AI insights dalam modal overlay full screen"""
    
    # Initialize session state
    if 'show_ai_modal' not in st.session_state:
        st.session_state.show_ai_modal = False
    
    # Tombol untuk membuka modal
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Open Full Screen AI Insights", 
                    use_container_width=True,
                    help="Buka AI Insights dalam mode full screen"):
            st.session_state.show_ai_modal = True
            st.rerun()
    
    # Render modal jika aktif
    if st.session_state.show_ai_modal:
        st.markdown("""
            <style>
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0, 0, 0, 0.8);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
            }
            
            .modal-content {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                width: 95vw;
                height: 90vh;
                border-radius: 20px;
                padding: 2rem;
                overflow-y: auto;
                position: relative;
                box-shadow: 0 25px 100px rgba(0, 0, 0, 0.3);
            }
            
            .modal-close {
                position: absolute;
                top: 20px;
                right: 20px;
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                cursor: pointer;
                font-size: 20px;
                z-index: 10000;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Close button
        if st.button("❌", key="close_modal", help="Tutup modal"):
            st.session_state.show_ai_modal = False
            st.rerun()
        
        # Render insights content dalam modal
        render_ai_insights_section(df, api_key, context)


# Versi compact untuk sidebar
def render_ai_insights_sidebar(df, api_key, context=""):
    """Versi compact untuk sidebar"""
    
    st.markdown("""
        <style>
        .sidebar-insight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            color: white;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
        }
        .sidebar-insight h5 {
            color: #ffffff;
            margin-bottom: 0.5rem;
            font-size: 1rem;
            font-weight: 600;
        }
        .sidebar-insight p {
            margin: 0.3rem 0;
            font-size: 0.85rem;
            line-height: 1.4;
        }
        .sidebar-insight strong {
            color: #ffd700;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 AI Insights")
    
    if not api_key:
        st.warning("⚠️ API Key required")
        return
    
    # Compact version of the insights
    with st.spinner('🤖 Analyzing...'):
        try:
            ai_generator = PLTSInsightsGenerator()
            ai_generator.setup_gemini(api_key)
            metrics = ai_generator.calculate_plts_metrics(df)
            
            if not metrics:
                st.error("❌ Failed to calculate metrics")
                return
                
            ai_response = ai_generator.generate_ai_insights_gemini(metrics, context)
            
            # Parse and display compact insights
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end > 0:
                json_content = ai_response[json_start:json_end]
                insights_data = json.loads(json_content)
                
                # Compact cards
                st.markdown(f"""
                    <div class="sidebar-insight">
                        <h5>🔍 Top Insights</h5>
                        {''.join([f'<p>• {insight[:60]}...</p>' for insight in insights_data.get('key_insights', [])[:2]])}
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="sidebar-insight">
                        <h5>📊 Quick Stats</h5>
                        <p><strong>Utilisasi:</strong> {metrics['avg_utilization']:.1f}%</p>
                        <p><strong>Total:</strong> {metrics['total_kapasitas_mwp']:.1f} MWp</p>
                        <p><strong>Perlu Perbaikan:</strong> {metrics['needs_improvement']}</p>
                    </div>
                """, unsafe_allow_html=True)

                if st.button("🔄", key="refresh_sidebar", help="Refresh insights"):
                    st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)[:50]}...")

# Function untuk memproses file yang diupload
def process_uploaded_file(uploaded_file):
    try:
        # Cek ekstensi file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Format file tidak didukung. Gunakan CSV atau Excel (.xlsx/.xls)")
            return None
        
        return df
    except Exception as e:
        st.error(f"Error memproses file: {str(e)}")
        return None

# Helper function for preparing map data
@st.cache_data
def prepare_map_data_enhanced(df, max_markers=1000, kota_filter='All'):
    """Prepare optimized data for map visualization"""
    if df.empty:
        return pd.DataFrame()
    
    # Check for required coordinate columns
    lat_cols = ['latitude', 'lat', 'LATITUDE', 'LAT']
    lon_cols = ['longitude', 'lon', 'LONGITUDE', 'LON']
    
    lat_col = None
    lon_col = None
    
    for col in lat_cols:
        if col in df.columns:
            lat_col = col
            break
    
    for col in lon_cols:
        if col in df.columns:
            lon_col = col
            break
    
    if not lat_col or not lon_col:
        st.warning("Kolom koordinat (latitude/longitude) tidak ditemukan. Peta tidak dapat ditampilkan.")
        return pd.DataFrame()
    
    # Filter out invalid coordinates
    df_valid = df.dropna(subset=[lat_col, lon_col])
    df_valid = df_valid[
        (df_valid[lat_col] != 0) & 
        (df_valid[lon_col] != 0) &
        (df_valid[lat_col].between(-90, 90)) &
        (df_valid[lon_col].between(-180, 180))
    ]
    
    # Sample data if too many markers
    if max_markers and len(df_valid) > max_markers:
        df_valid = df_valid.sample(n=max_markers, random_state=42)
        st.info(f"Menampilkan {max_markers} dari {len(df)} data untuk performa optimal.")
    
    return df_valid

# Helper function to add markers to map
def _add_markers_to_map_helper(map_obj, df, location_name, use_cluster=True, performance_limit=500):
    """Add markers to folium map with performance optimization"""
    if df.empty:
        return
    
    # Determine coordinate columns
    lat_cols = ['latitude', 'lat', 'LATITUDE', 'LAT']
    lon_cols = ['longitude', 'lon', 'LONGITUDE', 'LON']
    
    lat_col = None
    lon_col = None
    
    for col in lat_cols:
        if col in df.columns:
            lat_col = col
            break
    
    for col in lon_cols:
        if col in df.columns:
            lon_col = col
            break
    
    if not lat_col or not lon_col:
        return
    
    # Limit data for performance
    if performance_limit and len(df) > performance_limit:
        df = df.head(performance_limit)
        st.info(f"Menampilkan {performance_limit} marker pertama untuk performa optimal.")
    
    # Add markers
    for idx, row in df.iterrows():
        try:
            lat, lon = row[lat_col], row[lon_col]
            
            # Create popup content
            popup_content = f"""
            <b>PLTS: {row.get('NAMA', 'N/A')}</b><br>
            UNITAP: {row.get('UNITAP', 'N/A')}<br>
            Golongan: {row.get('GOL_TARIF', 'N/A')}<br>
            Kapasitas: {row.get('KAPASITAS_PLTS_ATAP', 0):,.0f} VA<br>
            Daya: {row.get('DAYA', 0):,.0f} VA<br>
            Utilisasi: {row.get('PERSEN_THD_DAYA', 0):.1f}%
            """
            
            # Determine marker color based on utilization
            util = row.get('PERSEN_THD_DAYA', 0)
            if util >= 75:
                color = 'green'
                icon = 'ok-sign'
            elif util >= 50:
                color = 'blue'
                icon = 'info-sign'
            elif util >= 25:
                color = 'orange'
                icon = 'warning-sign'
            else:
                color = 'red'
                icon = 'remove-sign'
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"PLTS: {row.get('NAMA', 'N/A')} - {util:.1f}%",
                icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
            ).add_to(map_obj)
            
        except Exception as e:
            continue  # Skip invalid markers

def main():
    st.markdown('<div class="main-header">☀️ Dashboard Analisis PLTS Atap Jawa Timur</div>', unsafe_allow_html=True)
    
    gemini_api_key = add_api_key_sidebar()

    df = None

    st.subheader("Upload File Data")
    uploaded_file = st.file_uploader(
            "Pilih file CSV atau Excel",
            type=['csv', 'xlsx', 'xls'],
            help="Upload file CSV atau Excel yang berisi data PLTS Atap"
        )
        
    if uploaded_file is not None:
            # Tampilkan info file
        st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Proses file
        df = process_uploaded_file(uploaded_file)
            
        if df is not None:
            st.success("File berhasil diupload!")
    else:
        st.warning("Silakan upload file untuk melanjutkan analisis.")

    if df is None or df.empty:
        st.warning("⚠️ Tidak ada data.")
        return


    
    # Jika data tersedia, tampilkan preview dan analisis
    if df is not None and not df.empty:
        st.subheader("Preview Data")
        
        # Tampilkan informasi dasar
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Jumlah Baris", len(df))
        with col2:
            st.metric("Jumlah Kolom", len(df.columns))
        with col3:
            st.metric("Missing Values", df.isnull().sum().sum())
        
        # Tampilkan beberapa baris pertama
        st.write("**Beberapa baris pertama:**")
        st.dataframe(df.head())
        
        # Tampilkan info kolom
        st.write("**Informasi Kolom:**")
        col_info = pd.DataFrame({
            'Kolom': df.columns,
            'Tipe Data': df.dtypes,
            'Jumlah Non-Null': df.count(),
            'Jumlah Null': df.isnull().sum()
        })
        st.dataframe(col_info)
        
        # Opsi untuk download template
        st.subheader("Template File")
        if st.button("Download Template Excel"):
            # Buat template sederhana
            template_data = {
                'Lokasi': ['Contoh Lokasi 1', 'Contoh Lokasi 2'],
                'Kapasitas_kW': [100, 150],
                'Produksi_kWh': [12000, 18000],
                'Tanggal': ['2024-01-01', '2024-01-02']
            }
            template_df = pd.DataFrame(template_data)
            
            # Convert to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                template_df.to_excel(writer, index=False, sheet_name='Template')
            
            st.download_button(
                label="Download Template",
                data=output.getvalue(),
                file_name="template_plts_atap.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    
    unitap_mapping = {
        '51BJN': 'Bojonegoro',
        '51BWG': 'Banyuwangi',
        '51GSK': 'Gresik',
        '51JBR': 'Jember',
        '51KDR': 'Kediri',
        '51MDN': 'Madiun',
        '51MJK': 'Mojokerto',
        '51MLG': 'Malang',
        '51PMK': 'Pamekasan',
        '51PON': 'Ponorogo',
        '51PSR': 'Pasuruan',
        '51SBB': 'Surabaya Barat',
        '51SBS': 'Surabaya Selatan',
        '51SBU': 'Surabaya Utara',
        '51SDA': 'Sidoarjo',
        '51STB': 'Situbondo'
    }
    df['UNITAP'] = df['UNITAP'].replace(unitap_mapping)
    
    # Define pattern columns BEFORE using them
    # Identify and calculate monthly totals dynamically
    # Look for columns that contain 'Impor' or 'Ekspor' patterns
    impor_pattern_cols = [col for col in df.columns if any(month in str(col) for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) and 'Impor' in str(col)]
    ekspor_pattern_cols = [col for col in df.columns if any(month in str(col) for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) and 'Ekspor' in str(col)]
    
    # If no monthly columns found, look for generic patterns
    if not impor_pattern_cols:
        impor_pattern_cols = [col for col in df.columns if 'Impor' in str(col) and col != 'TOTAL']
    if not ekspor_pattern_cols:
        ekspor_pattern_cols = [col for col in df.columns if 'Ekspor' in str(col) and col != 'TOTAL']
    
    # Display data info for debugging
    with st.expander("🔍 Info Dataset"):
        st.write(f"**Jumlah Baris:** {len(df)}")
        st.write(f"**Jumlah Kolom:** {len(df.columns)}")
        st.write("**Kolom yang tersedia:**")
        st.write(df.columns.tolist())
        
        # Show columns that contain Impor/Ekspor
        if impor_pattern_cols:
            st.write(f"**Kolom Impor (dari PLN) ditemukan:** {impor_pattern_cols}")
        if ekspor_pattern_cols:
            st.write(f"**Kolom Ekspor (ke PLN) ditemukan:** {ekspor_pattern_cols}")
            
        st.write("**Data Types:**")
        st.write(df.dtypes)
        st.write("**Preview data:**")
        st.dataframe(df.head(), use_container_width=True)
    
    # Calculate totals if monthly data exists with proper data cleaning
    if impor_pattern_cols:
        # Clean and convert impor columns to numeric
        for col in impor_pattern_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Total_Impor'] = df[impor_pattern_cols].sum(axis=1)
    else:
        df['Total_Impor'] = 0
        
    if ekspor_pattern_cols:
        # Clean and convert ekspor columns to numeric
        for col in ekspor_pattern_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Total_Ekspor'] = df[ekspor_pattern_cols].sum(axis=1)
    else:
        df['Total_Ekspor'] = 0
    
    # Clean and standardize numeric columns
    numeric_columns = ['DAYA', 'KAPASITAS_PLTS_ATAP', 'PERSEN_THD_DAYA']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Handle potential column name variations
    required_columns = {
        'UNITAP': ['UNITAP', 'unitap', 'UNIT UP'],
        'NAMA': ['NAMA', 'nama', 'NAMA PELANGGAN'],
        'GOL_TARIF': ['GOL_TARIF', 'GOL TARIF', 'GOLONGAN TARIF', 'KATEGORI GOLONGAN'],
        'KATEGORI_KAPASITAS': ['KATEGORI_KAPASITAS', 'KATEGORI KAPASITAS', '% THD DAYA'],
        'PERSEN_THD_DAYA': ['PERSEN_THD_DAYA', '% THD DAYA', 'PERSEN THD DAYA'],
        'KAPASITAS_PLTS_ATAP': ['KAPASITAS_PLTS_ATAP', 'KAPASITAS PLTS ATAP', 'KAPASITAS'],
        'DAYA': ['DAYA', 'daya']
    }
    
    # Map column names to standard names
    for standard_name, possible_names in required_columns.items():
        for possible_name in possible_names:
            if possible_name in df.columns and standard_name not in df.columns:
                df[standard_name] = df[possible_name]
                break
    
    # Check for missing critical columns and provide defaults
    if 'GOL_TARIF' not in df.columns:
        df['GOL_TARIF'] = 'TIDAK DIKETAHUI'
    
    if 'KATEGORI_KAPASITAS' not in df.columns:
        df['KATEGORI_KAPASITAS'] = 'BELUM DIKATEGORIKAN'
    
    # Calculate PERSEN_THD_DAYA if not exists (Utilisasi = % Kapasitas PLTS terhadap Daya Tersambung)
    if 'PERSEN_THD_DAYA' not in df.columns and 'KAPASITAS_PLTS_ATAP' in df.columns and 'DAYA' in df.columns:
        kapasitas = pd.to_numeric(df['KAPASITAS_PLTS_ATAP'], errors='coerce').fillna(0)
        daya = pd.to_numeric(df['DAYA'], errors='coerce').fillna(1)  # Use 1 to avoid division by zero
        df['PERSEN_THD_DAYA'] = (kapasitas / daya * 100).fillna(0)
    elif 'PERSEN_THD_DAYA' in df.columns:
        df['PERSEN_THD_DAYA'] = pd.to_numeric(df['PERSEN_THD_DAYA'], errors='coerce').fillna(0)
    
    # Convert kapasitas to MWp
    df['KAPASITAS_MWp'] = df['KAPASITAS_PLTS_ATAP'] / 1000000  # Convert VA to MWp
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    unitap_filter = st.sidebar.multiselect(
        "Pilih UNITAP:",
        options=df['UNITAP'].unique(),
        default=df['UNITAP'].unique()
    )
    
    golongan_filter = st.sidebar.multiselect(
        "Pilih Golongan Tarif:",
        options=df['GOL_TARIF'].unique(),
        default=df['GOL_TARIF'].unique()
    )
    
    kategori_filter = st.sidebar.multiselect(
        "Pilih Kategori Kapasitas:",
        options=df['KATEGORI_KAPASITAS'].unique(),
        default=df['KATEGORI_KAPASITAS'].unique()
    )
    
    # Filter data with error handling
    try:
        if (len(unitap_filter) > 0 and 'UNITAP' in df.columns and 
            len(golongan_filter) > 0 and 'GOL_TARIF' in df.columns and 
            len(kategori_filter) > 0 and 'KATEGORI_KAPASITAS' in df.columns):
            
            filtered_df = df[
                (df['UNITAP'].isin(unitap_filter)) &
                (df['GOL_TARIF'].isin(golongan_filter)) &
                (df['KATEGORI_KAPASITAS'].isin(kategori_filter))
            ]
        else:
            filtered_df = df.copy()
            
    except Exception as e:
        filtered_df = df.copy()
        st.warning(f"⚠️ Menggunakan semua data karena ada masalah dengan filter: {str(e)}")
    
    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih.")
        return
    
    # Key Metrics - UTILISASI DIPERBESAR
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
        total_kapasitas_mwp = filtered_df['KAPASITAS_MWp'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_kapasitas_mwp:.1f} MWp</h3>
            <p>Total Kapasitas PLTS</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Rata-rata Utilisasi = rata-rata dari PERSEN_THD_DAYA - DIPERBESAR
        avg_utilization = filtered_df['PERSEN_THD_DAYA'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="utilization-display">{avg_utilization:.1f}%</div>
            <p><b>Rata-rata Utilisasi PLTS</b><br><small>(% Kapasitas vs Daya Tersambung)</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_ekspor = filtered_df['Total_Ekspor'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_ekspor:,.0f} kWh</h3>
            <p>Total Ekspor ke PLN</p>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("---")
    
    # BAGIAN PETA - MENGGANTI VISUALISASI LAMA
    st.divider()
    st.subheader("🗺️ Peta Lokasi PLTS Atap")

    # Show filtering info
    st.info(f"📍 Menampilkan peta untuk {len(filtered_df):,} pelanggan PLTS")

    # Performance toggle
    col_map1, col_map2, col_map3 = st.columns([2, 1, 1])
    with col_map1:
        nama_search = st.text_input(
            "Cari Nama Pelanggan (kosongkan untuk melihat semua):", 
            key="map_nama_search"
        ).strip()
    with col_map2:
        show_map = st.checkbox("Tampilkan Peta", value=True,
                               help="Uncheck to skip map loading for faster page load")
    with col_map3:
        show_all_data = st.checkbox("Tampilkan Semua Data", value=False,
                                    help="⚠️ PERINGATAN: Menampilkan semua data dapat memperlambat loading")

    if not show_map:
        st.info("🚀 Peta dinonaktifkan untuk performa yang lebih cepat. Centang kotak 'Tampilkan Peta' untuk melihat peta.")
    else:
        # Dynamic marker limits based on user choice
        if show_all_data:
            st.warning("⚠️ *Mode Semua Data Aktif*: Rendering mungkin membutuhkan waktu lebih lama untuk dataset besar (>1,000 markers)")
            max_markers_limit = None
            performance_limit = None
        else:
            max_markers_limit = 500
            performance_limit = 300

        # Prepare data for mapping
        df_for_map = filtered_df.copy()
        
        # Add dummy coordinates if not present (for demonstration)
        if 'latitude' not in df_for_map.columns:
            # Generate random coordinates around East Java
            np.random.seed(42)
            df_for_map['latitude'] = np.random.uniform(-8.5, -6.5, len(df_for_map))
            df_for_map['longitude'] = np.random.uniform(111.0, 114.5, len(df_for_map))
            st.warning("⚠️ Koordinat tidak ditemukan, menggunakan koordinat dummy untuk demonstrasi")

        with st.spinner("Mempersiapkan data peta yang dioptimalkan..."):
            df_map_ready = prepare_map_data_enhanced(
                df_for_map,
                max_markers=max_markers_limit,
                kota_filter='All'
            )

        if df_map_ready.empty:
            st.info("Tidak ada data dengan koordinat valid untuk peta.")
        else:
            # Initialize map with better performance settings
            map_center_default = [-7.5, 112.7]  # East Java
            map_zoom_default = 8

            # Calculate optimal center based on data
            if not df_map_ready.empty:
                map_center_default = [
                    df_map_ready['latitude'].mean(),
                    df_map_ready['longitude'].mean()
                ]

            with st.spinner("Memuat peta..."):
                m = folium.Map(
                    location=map_center_default,
                    zoom_start=map_zoom_default,
                    tiles="OpenStreetMap",
                    prefer_canvas=True
                )

                if nama_search:
                    # Search functionality
                    df_search_result = df_map_ready[
                        df_map_ready['NAMA'].astype(str).str.contains(
                            nama_search, case=False, na=False)
                    ]

                    if not df_search_result.empty:
                        st.success(f"Ditemukan {len(df_search_result)} pelanggan dengan nama mengandung: '{nama_search}'")

                        # Center on first result
                        first_asset = df_search_result.iloc[0]
                        m.location = [first_asset['latitude'], first_asset['longitude']]
                        m.zoom_start = 12

                        # Add search result markers
                        _add_markers_to_map_helper(m, df_search_result.head(50), f"search: {nama_search}", use_cluster=False, performance_limit=50)
                    else:
                        st.warning(f"Nama '{nama_search}' tidak ditemukan. Menampilkan peta umum.")
                        # Fall back to general view
                        if len(df_map_ready) > 100:
                            marker_cluster = MarkerCluster(
                                name="PLTS Assets",
                                options={'maxClusterRadius': 50, 'spiderfyOnMaxZoom': False}
                            ).add_to(m)
                            _add_markers_to_map_helper(marker_cluster, df_map_ready, 'All', performance_limit=performance_limit)
                        else:
                            _add_markers_to_map_helper(m, df_map_ready, 'All', use_cluster=False, performance_limit=performance_limit)
                else:
                    # General view with clustering for performance
                    if len(df_map_ready) > 100:
                        marker_cluster = MarkerCluster(
                            name="PLTS Assets",
                            options={'maxClusterRadius': 50, 'spiderfyOnMaxZoom': False}
                        ).add_to(m)
                        _add_markers_to_map_helper(marker_cluster, df_map_ready, 'All', performance_limit=performance_limit)
                        st.success(f"✅ Peta berhasil dimuat dengan {len(df_map_ready)} aset PLTS (dengan clustering)")
                    else:
                        _add_markers_to_map_helper(m, df_map_ready, 'All', use_cluster=False, performance_limit=performance_limit)
                        st.success(f"✅ Peta berhasil dimuat dengan {len(df_map_ready)} aset PLTS")

                # Display map
                folium_static(m, width=None, height=600)

                # Add marker status summary after the map
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    excellent_count = len(df_map_ready[df_map_ready['PERSEN_THD_DAYA'] >= 75])
                    st.metric("🟢 Excellent (≥75%)", excellent_count, help="PLTS dengan utilisasi sangat baik")
                with col2:
                    good_count = len(df_map_ready[(df_map_ready['PERSEN_THD_DAYA'] >= 50) & (df_map_ready['PERSEN_THD_DAYA'] < 75)])
                    st.metric("🔵 Good (50-74%)", good_count, help="PLTS dengan utilisasi baik")
                with col3:
                    fair_count = len(df_map_ready[(df_map_ready['PERSEN_THD_DAYA'] >= 25) & (df_map_ready['PERSEN_THD_DAYA'] < 50)])
                    st.metric("🟠 Fair (25-49%)", fair_count, help="PLTS dengan utilisasi cukup")
                with col4:
                    poor_count = len(df_map_ready[df_map_ready['PERSEN_THD_DAYA'] < 25])
                    st.metric("🔴 Poor (<25%)", poor_count, help="PLTS dengan utilisasi rendah")

    # Charts Section - DIPERBESAR
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribusi Golongan Tarif")
        
        # Hitung jumlah per golongan
        gol_counts = filtered_df['GOL_TARIF'].value_counts()
        
        # Buat labels dengan jumlah
        labels_with_count = [f"{gol}<br>({count} pelanggan)" for gol, count in zip(gol_counts.index, gol_counts.values)]
        
        fig_pie = px.pie(
            values=gol_counts.values,
            names=labels_with_count,
            title="Jumlah Pelanggan per Golongan Tarif",
            color_discrete_sequence=px.colors.qualitative.Set3,
            height=500
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
        fig_pie.update_layout(font=dict(size=14))
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("⚡ Hubungan Daya Tersambung vs Kapasitas PLTS")
        st.info("**Penjelasan:** Grafik ini menunjukkan hubungan antara daya listrik yang tersambung dari PLN (sumbu X) dengan kapasitas PLTS yang dipasang (sumbu Y). Setiap titik adalah satu pelanggan.")
        
        fig_scatter = px.scatter(
            filtered_df,
            x='DAYA',
            y='KAPASITAS_PLTS_ATAP',
            color='GOL_TARIF',
            hover_data={
                'NAMA': True,
                'PERSEN_THD_DAYA': ':.1f',
                'DAYA': ':,.0f',
                'KAPASITAS_PLTS_ATAP': ':,.0f'
            },
            title="Daya Tersambung vs Kapasitas PLTS (Per Pelanggan)",
            labels={
                'DAYA': 'Daya Tersambung (VA)', 
                'KAPASITAS_PLTS_ATAP': 'Kapasitas PLTS (VA)',
                'GOL_TARIF': 'Golongan Tarif'
            },
            height=500
        )
        
        fig_scatter.update_xaxes(tickformat=',.0f')
        fig_scatter.update_yaxes(tickformat=',.0f')
        fig_scatter.update_layout(
            font=dict(size=12),
            hovermode='closest'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    if not filtered_df.empty:
        # Context input
        context = add_context_input()
        
        # AI Insights - BAGIAN BARU INI
        render_ai_insights_section(filtered_df, gemini_api_key, context)
    
    # Performance Analysis
    st.subheader("📈 Sebaran Pelanggan PLTS Atap")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Sebaran Tingkat Utilisasi PLTS")
        st.info("**Penjelasan:** Utilisasi adalah persentase kapasitas PLTS dibanding daya tersambung. Grafik ini menunjukkan berapa banyak pelanggan di setiap rentang utilisasi.")

        # Filter Data Anomali (Outlier)
        UTILIZATION_CAP = 1.5 
        plot_df = filtered_df[filtered_df['PERSEN_THD_DAYA'] <= UTILIZATION_CAP]
        outlier_count = len(filtered_df) - len(plot_df)
        
        if outlier_count > 0:
            st.warning(f"**Info:** Terdapat **{outlier_count} pelanggan** dengan utilisasi di atas {UTILIZATION_CAP*100:.0f}% yang tidak ditampilkan pada grafik agar lebih mudah dibaca.")

        # --- PERBAIKAN 2: Visualisasi yang Lebih Baik ---
        fig_hist = px.histogram(
            plot_df,  # Gunakan dataframe yang sudah bersih
            x='PERSEN_THD_DAYA',
            title="Distribusi Utilisasi PLTS (0% - 150%)",
            labels={'PERSEN_THD_DAYA': 'Tingkat Utilisasi', 'count': 'Jumlah Pelanggan'},
            height=500,
            range_x=[0, UTILIZATION_CAP]  # Paksa sumbu-X memiliki rentang tetap
        )

        # Atur lebar bin secara manual agar rapi
        fig_hist.update_traces(xbins=dict(
            start=0.0,
            size=0.05  # Lebar setiap bin adalah 5%
        ))
        
        # --- PERBAIKAN 3: Penyempurnaan Tampilan ---
        fig_hist.update_layout(
            bargap=0.1,
            font=dict(size=12),
            xaxis_title="Tingkat Utilisasi", # Judul sumbu X yang lebih jelas
            yaxis_title="Jumlah Pelanggan", # Judul sumbu Y
            xaxis_tickformat='.0%'  # Tampilkan label sumbu X sebagai persentase
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Impor vs Ekspor Energi per UNITAP")
        st.info("**Penjelasan:** \n- **Impor (Merah)** = energi yang dibeli dari PLN oleh pelanggan PLTS \n- **Ekspor (Hijau)** = energi surplus PLTS yang dijual kembali ke PLN")
        
        # Group by UNITAP untuk analisis per UP3
        unitap_energy = filtered_df.groupby('UNITAP').agg({
            'Total_Impor': 'sum',
            'Total_Ekspor': 'sum',
            'NAMA': 'count'
        }).reset_index()
        unitap_energy.columns = ['UNITAP', 'Total_Impor_kWh', 'Total_Ekspor_kWh', 'Jumlah_Pelanggan']
        
        fig_bar = px.bar(
            unitap_energy,
            y='UNITAP',
            x=['Total_Impor_kWh', 'Total_Ekspor_kWh'],
            title="Total Impor vs Ekspor Energi per UNITAP",
            barmode='group',
            labels={
                'value': 'Energi (kWh)', 
                'variable': 'Jenis Transaksi Energi',
                'Total_Impor_kWh': 'Impor dari PLN',
                'Total_Ekspor_kWh': 'Ekspor ke PLN'
            },
            height=500,  # Diperbesar
            color_discrete_map={
                'Total_Impor_kWh': '#FF6B6B', 
                'Total_Ekspor_kWh': '#4ECDC4'
            }
        )
    if not unitap_energy.empty:
        fig_bar.update_xaxes(tickangle=90)
        fig_bar.update_layout(
            font=dict(size=12),
            legend=dict(
                title="Jenis Transaksi:",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Geographic Analysis - PETA JAWA TIMUR
    
    # st.subheader("📈 Analisis Kinerja Geografis PLTS Atap")

    # --- BAGIAN 1: PERSIAPAN DATA AGREGRAT DENGAN TRY-EXCEPT SENDIRI ---
    try:
        # Agregasi data per UNITAP
        unitap_summary = filtered_df.groupby('UNITAP').agg(
            Jumlah_Pelanggan=('NO', 'count'),
            Total_Kapasitas_kWp=('KAPASITAS PLTS ATAP', lambda x: x.sum() / 1000),
            Avg_Utilisasi=('% THD DAYA', 'mean')
        ).reset_index()
        # Membuat kolom MWp untuk tabel
        unitap_summary['Total_Kapasitas_MWp'] = (unitap_summary['Total_Kapasitas_kWp'] / 1000).round(4)

    except KeyError as e:
        st.error(f"Gagal melakukan agregasi data. Kolom berikut tidak ditemukan: {e}. Mohon periksa nama kolom di kode.")
        st.stop() # Hentikan eksekusi jika agregasi gagal

    # --- BAGIAN 2: MEMUAT FILE GEOJSON DENGAN TRY-EXCEPT SENDIRI ---
    try:
        # Memuat file GeoJSON dari lokal
        with open('peta_jatim.json', 'r') as f:
            geojson_jatim = json.load(f)
    except FileNotFoundError:
        st.error("Gagal memuat file peta 'peta_jatim.json'. Pastikan file tersebut ada di folder yang sama dengan skrip Python Anda.")
        st.stop() # Hentikan eksekusi jika file peta tidak ada


    # --- BAGIAN 3: PROSES PEMETAAN NAMA DAN VISUALISASI ---
    # Blok try-except umum untuk menangkap error lain yang mungkin terjadi saat plotting
    try:
        # Kamus untuk memetakan nama UNITAP ke nama di GeoJSON
        unitap_to_geojson_map = {
            'SURABAYA BARAT': 'KOTA SURABAYA', 'SURABAYA SELATAN': 'KOTA SURABAYA',
            'SURABAYA UTARA': 'KOTA SURABAYA', 'MALANG': 'KOTA MALANG',
            'BOJONEGORO': 'KABUPATEN BOJONEGORO', 'BANYUWANGI': 'KABUPATEN BANYUWANGI',
            'GRESIK': 'KABUPATEN GRESIK', 'JEMBER': 'KABUPATEN JEMBER',
            'KEDIRI': 'KOTA KEDIRI', 'MADIUN': 'KOTA MADIUN',
            'MOJOKERTO': 'KOTA MOJOKERTO', 'PAMEKASAN': 'KABUPATEN PAMEKASAN',
            'PONOROGO': 'KABUPATEN PONOROGO', 'PASURUAN': 'KOTA PASURUAN',
            'SIDOARJO': 'KABUPATEN SIDOARJO', 'SITUBONDO': 'KABUPATEN SITUBONDO'
        }
        unitap_summary['NAMA_PETA'] = unitap_summary['UNITAP'].str.upper().map(unitap_to_geojson_map)
        
        # Filter baris yang tidak berhasil dipetakan untuk menghindari error pada peta
        mappable_summary = unitap_summary.dropna(subset=['NAMA_PETA'])


        # TANPA LAYOUT KOLOM
        st.subheader("📋 Ringkasan per UNITAP")

        summary_display = unitap_summary.copy()
        summary_display['Avg_Utilisasi'] = summary_display['Avg_Utilisasi'].map('{:.1%}'.format)

        st.dataframe(
            summary_display[['UNITAP', 'Jumlah_Pelanggan', 'Total_Kapasitas_MWp', 'Avg_Utilisasi']],
            use_container_width=True,
            height=580,
            hide_index=True
        )


    except Exception as e:
        st.error(f"Terjadi error yang tidak terduga saat memetakan nama atau membuat visualisasi. Error: {e}")


        
        # Performance Categories - DIPERBAIKI
        st.subheader("🎯 Kategori Performa Pelanggan PLTS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Kategorisasi Berdasarkan Utilisasi & Ekspor")
            
            def categorize_by_quadrant(row):
                util_threshold = 0.50  # 50%
                ekspor_threshold = 200 # 200 kWh
                
                utilisasi = row['PERSEN_THD_DAYA']
                ekspor = row['Total_Ekspor']
                
                # Kuadran 1: Utilisasi Tinggi, Ekspor Tinggi
                if utilisasi >= util_threshold and ekspor >= ekspor_threshold:
                    return 'Produsen Super (Utilisasi Tinggi, Ekspor Tinggi)'
                
                # Kuadran 2: Utilisasi Tinggi, Ekspor Rendah
                elif utilisasi >= util_threshold and ekspor < ekspor_threshold:
                    return 'Konsumen Mandiri (Utilisasi Tinggi, Ekspor Rendah)'
                    
                # Kuadran 3: Utilisasi Rendah, Ekspor Tinggi
                elif utilisasi < util_threshold and ekspor >= ekspor_threshold:
                    return 'Si Pengekspor (Utilisasi Rendah, Ekspor Tinggi)'
                
                # Kuadran 4: Utilisasi Rendah, Ekspor Rendah
                else:
                    return 'Kinerja Rendah (Utilisasi Rendah, Ekspor Rendah)'

            filtered_df['Performance_Category'] = filtered_df.apply(categorize_by_quadrant, axis=1)
            
            perf_dist = filtered_df['Performance_Category'].value_counts()
            
            # Buat labels dengan jumlah
            perf_labels = [f"{cat}<br>({count} pelanggan)" for cat, count in zip(perf_dist.index, perf_dist.values)]
            
            fig_perf = px.pie(
                values=perf_dist.values,
                names=perf_labels,
                title="Distribusi Kategori Performa",
                color_discrete_sequence=['#2E8B57', '#4169E1', '#FFD700', '#DC143C'],
                height=500  # Diperbesar
            )
            fig_perf.update_traces(textposition='inside', textinfo='percent', textfont_size=12)
            fig_perf.update_layout(font=dict(size=11))
            st.plotly_chart(fig_perf, use_container_width=True)
        
        with col2:
            st.subheader("📊 Analisis Agregat per Golongan Tarif")
            st.info("Tabel dan grafik di bawah ini merupakan ringkasan data yang dikelompokkan berdasarkan Golongan Tarif.")

            # Membungkus semua proses dalam satu blok try-except untuk penanganan error yang baik
            try:
                # --- BAGIAN 1: AGREGRASI DATA DENGAN NAMA KOLOM YANG BENAR ---
                df_agregat = filtered_df.groupby('GOL TARIF').agg(
                    # Menghitung Rata-rata
                    Avg_Utilisasi=('% THD DAYA', 'mean'),
                    Avg_Daya_Tersambung=('DAYA', 'mean'),
                    
                    # Menghitung Total Kapasitas. Unit diubah dari Watt ke kWp.
                    Total_Kapasitas_kWp=('KAPASITAS PLTS ATAP', lambda x: x.sum() / 1000),
                    
                    # Menghitung Jumlah Pelanggan menggunakan kolom 'NO'
                    Jumlah_Pelanggan=('NO', 'count')
                ).reset_index()

                # Merapikan nama kolom hasil agregasi agar lebih mudah dipanggil
                df_agregat = df_agregat.rename(columns={
                    'GOL TARIF': 'Golongan_Tarif',
                    'Avg_Utilisasi': 'Utilisasi_Rata_Rata',
                    'Avg_Daya_Tersambung': 'Daya_Tersambung_Rata_Rata',
                    'Total_Kapasitas_kWp': 'Total_Kapasitas_kWp',
                    'Jumlah_Pelanggan': 'Jumlah_Pelanggan'
                })

                # --- BAGIAN 2: MENAMPILKAN HASIL AGREGRASI & VISUALISASI ---
                st.write("### Data Hasil Agregasi:")
                st.dataframe(df_agregat)

                # Visualisasi 2: Scatter/Bubble Chart Analisis Segmen
                st.write("### Analisis Segmen Golongan Tarif")
                fig_scatter = px.scatter(
                    df_agregat,
                    x='Daya_Tersambung_Rata_Rata', # Menggunakan nama kolom yang sudah dirapikan
                    y='Utilisasi_Rata_Rata',      # Menggunakan nama kolom yang sudah dirapikan
                    size='Total_Kapasitas_kWp',     # Menggunakan nama kolom yang sudah dirapikan
                    color='Golongan_Tarif',         # Menggunakan 'Golongan_Tarif' untuk warna
                    hover_name='Golongan_Tarif',    # Menggunakan nama kolom yang sudah dirapikan
                    text='Golongan_Tarif',          # Menggunakan nama kolom yang sudah dirapikan
                    size_max=60,
                    log_x=True,
                    title="Perbandingan Utilisasi vs Daya Tersambung per Golongan Tarif"
                )
                fig_scatter.update_traces(textposition='top center')
                fig_scatter.update_layout(
                    xaxis_title="Daya Tersambung Rata-Rata (Watt)",
                    yaxis_title="Utilisasi Rata-Rata (%)",
                    showlegend=True # Tampilkan legenda agar warna bisa diidentifikasi
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

            # Blok except yang diletakkan dengan benar (di luar 'try')
            except KeyError as e:
                st.error(f"Terjadi KeyError. Sepertinya ada nama kolom di dalam .agg() yang tidak ditemukan di data Anda. Cek kembali nama kolom berikut: {e}")
            except Exception as e:
                st.error(f"Terjadi error yang tidak terduga saat memproses data: {e}")


    # st.info("Mengkategorikan performa pelanggan...")

    # Definisikan fungsi untuk mengkategorikan setiap pelanggan
    def categorize_performance(row):
        # Asumsikan kolom '% THD DAYA' dan 'Total_Ekspor' ada di filtered_df
        # Jika tidak ada 'Total_Ekspor', Anda bisa menyederhanakan logikanya
        try:
            utilisasi = row['% THD DAYA']
            ekspor = row.get('Total_Ekspor', 0) # Gunakan .get() agar tidak error jika kolom tidak ada
        except KeyError:
            return 'Data Tidak Lengkap'

        if utilisasi >= 0.75:
            return 'Excellent'
        elif utilisasi >= 0.50:
            return 'Good'
        elif utilisasi >= 0.25:
            return 'Average'
        else:
            return 'Needs Improvement'

    # Terapkan fungsi ke setiap baris untuk membuat kolom baru
    filtered_df['Performance_Category'] = filtered_df.apply(categorize_performance, axis=1)


if __name__ == "__main__":
    main()