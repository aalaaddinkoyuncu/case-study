"""
Gain Enerji Case Study - Streamlit Web Arayüzü
Elektrik Piyasası Santral Analiz Platformu
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import numpy as np

# src klasörünü path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_processor import DataProcessor
from src.simple_comparison_excel import SimpleComparisonExcel
from config.credentials import SANTRALLER

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Gain Enerji - Santral Analiz Platformu",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .santral-info {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def load_processed_data():
    """İşlenmiş verileri yükle"""
    processor = DataProcessor()
    
    # Santral listesi
    santraller = [
        "MASLAKTEPE RES",
        "EBER RES", 
        "YANBOLU HES",
        "MELİKOM HES"
    ]
    
    santral_dataframes = {}
    
    for santral in santraller:
        try:
            df = processor.create_santral_analysis(santral)
            if not df.empty:
                santral_dataframes[santral] = df
        except Exception as e:
            st.error(f"{santral} verisi yüklenemedi: {e}")
    
    return santral_dataframes

def create_comparison_chart(santral_dataframes, selected_santraller):
    """Karşılaştırma grafikleri oluştur"""
    
    # Aylık özet veriler
    monthly_data = []
    
    for santral_name in selected_santraller:
        if santral_name in santral_dataframes:
            df = santral_dataframes[santral_name]
            
            monthly_summary = df.groupby('ay').agg({
                'Uretim': 'sum',
                'KGUP': 'sum', 
                'dengesizlik': 'sum',
                'toplam_gelir': 'sum',
                'birim_gelir': 'mean'
            }).reset_index()
            
            monthly_summary['santral'] = santral_name
            monthly_summary['santral_tipi'] = 'RES' if 'RES' in santral_name else 'HES'
            
            monthly_data.append(monthly_summary)
    
    if not monthly_data:
        return None, None
    
    combined_df = pd.concat(monthly_data, ignore_index=True)
    
    # Grafik 1: Aylık Üretim Karşılaştırması (Düzeltilmiş)
    fig1 = px.bar(
        combined_df, 
        x='ay', 
        y='Uretim', 
        color='santral',
        title="Aylık Üretim Karşılaştırması (MWh)",
        labels={'ay': 'Ay', 'Uretim': 'Üretim (MWh)'},
        color_discrete_sequence=['#2E8B57', '#FF6347'],  # Yeşil ve Turuncu
        barmode='group'  # Yan yana barlar
    )
    
    # Y ekseni formatını düzelt
    fig1.update_layout(
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(title='Üretim (MWh)', tickformat='.0f'),
        showlegend=True
    )
    
    # Grafik 2: Birim Gelir Karşılaştırması
    fig2 = px.line(
        combined_df, 
        x='ay', 
        y='birim_gelir', 
        color='santral',
        title="Aylık Birim Gelir Trendi (TL/MWh)",
        labels={'ay': 'Ay', 'birim_gelir': 'Birim Gelir (TL/MWh)'},
        markers=True,
        color_discrete_sequence=['#2E8B57', '#FF6347']
    )
    
    fig2.update_layout(
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(title='Birim Gelir (TL/MWh)', tickformat='.2f')
    )
    
    return fig1, fig2

def create_santral_detail_charts(df, santral_name):
    """Santral detay grafikleri - Düzeltilmiş"""
    
    # Aylık özet
    monthly = df.groupby('ay').agg({
        'Uretim': 'sum',
        'KGUP': 'sum', 
        'dengesizlik': 'sum',
        'toplam_gelir': 'sum'
    }).reset_index()
    
    # Grafik 1: Plan vs Gerçek (Düzeltilmiş)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=monthly['ay'], 
        y=monthly['KGUP'], 
        mode='lines+markers', 
        name='Plan (KGÜP)', 
        line=dict(color='#1f77b4', dash='dash', width=3),
        marker=dict(size=8)
    ))
    fig1.add_trace(go.Scatter(
        x=monthly['ay'], 
        y=monthly['Uretim'], 
        mode='lines+markers', 
        name='Gerçek Üretim',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=8)
    ))
    
    fig1.update_layout(
        title=f"{santral_name} - Plan vs Gerçek Üretim",
        xaxis=dict(
            title="Ay",
            tickmode='linear', 
            tick0=1, 
            dtick=1,
            range=[0.5, 12.5]
        ),
        yaxis=dict(
            title="Üretim (MWh)",
            tickformat='.0f'
        ),
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    # Grafik 2: Dengesizlik Analizi (Düzeltilmiş)
    # Pozitif ve negatif dengesizlikleri farklı renklerle göster
    colors = ['#d62728' if x < 0 else '#2ca02c' for x in monthly['dengesizlik']]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=monthly['ay'],
        y=monthly['dengesizlik'],
        marker_color=colors,
        name='Dengesizlik',
        text=[f"{x:.1f}" for x in monthly['dengesizlik']],
        textposition='outside'
    ))
    
    fig2.update_layout(
        title=f"{santral_name} - Aylık Dengesizlik Analizi",
        xaxis=dict(
            title="Ay",
            tickmode='linear',
            tick0=1,
            dtick=1,
            range=[0.5, 12.5]
        ),
        yaxis=dict(
            title="Dengesizlik (MWh)",
            tickformat='.0f'
        ),
        showlegend=False,
        height=400
    )
    
    # Sıfır çizgisi ekle
    fig2.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
    
    return fig1, fig2

def main():
    """Ana uygulama"""
    
    # Header
    st.markdown('<h1 class="main-header">⚡ Gain Enerji - Santral Analiz Platformu</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div class="santral-info">
    <h3>Elektrik Piyasası Santral Performans Analizi</h3>
    <p>2024 yılı boyunca rüzgar ve hidroelektrik santrallerin piyasa performansını analiz edin.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Santral Seçimi
    st.sidebar.header("Santral Seçimi")
    
    # Mevcut santraller
    available_santraller = [
        "MASLAKTEPE RES",
        "EBER RES", 
        "YANBOLU HES",
        "MELİKOM HES"
    ]
    
    # Santral seçim dropdown'ları
    st.sidebar.subheader("Birinci Santral")
    santral_1 = st.sidebar.selectbox(
        "Santral seçin:",
        available_santraller,
        key="santral_1"
    )
    
    st.sidebar.subheader("İkinci Santral")
    santral_2 = st.sidebar.selectbox(
        "Santral seçin:",
        [s for s in available_santraller if s != santral_1],
        key="santral_2"
    )
    
    # Çalıştırma butonu
    st.sidebar.markdown("---")
    run_analysis = st.sidebar.button(
        "Analizi Çalıştır", 
        type="primary",
        use_container_width=True
    )
    
    if run_analysis:
        selected_santraller = [santral_1, santral_2]
        
        with st.spinner('Veriler yükleniyor ve analiz ediliyor...'):
            # Verileri yükle
            santral_dataframes = load_processed_data()
            
            if not santral_dataframes:
                st.error("Veri bulunamadı! Önce veri çekme işlemini tamamlayın.")
                st.stop()
            
            # Başarı mesajı
            st.success(f"Analiz tamamlandı! Seçilen santraller: {santral_1} vs {santral_2}")
            
            # Ana metrikler
            col1, col2 = st.columns(2)
            
            for i, santral in enumerate(selected_santraller):
                if santral in santral_dataframes:
                    df = santral_dataframes[santral]
                    
                    with col1 if i == 0 else col2:
                        st.subheader(f" {santral}")
                        
                        # Temel metrikler
                        total_uretim = df['Uretim'].sum()
                        total_kgup = df['KGUP'].sum()
                        avg_birim_gelir = df['birim_gelir'].mean()
                        total_gelir = df['toplam_gelir'].sum()
                        
                        st.metric("Toplam Üretim", f"{total_uretim:,.0f} MWh")
                        st.metric("Ortalama Birim Gelir", f"{avg_birim_gelir:.2f} TL/MWh")
                        st.metric("Toplam Gelir", f"{total_gelir:,.0f} TL")
                        st.metric("Plan Tutturma", f"{(total_uretim/total_kgup*100):.1f}%")
            
            # Karşılaştırma grafikleri
            st.markdown("---")
            st.header("Karşılaştırmalı Analizler")
            
            fig1, fig2 = create_comparison_chart(santral_dataframes, selected_santraller)
            
            if fig1 and fig2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Santral detay analizleri
            st.markdown("---")
            st.header("Detaylı Santral Analizleri")
            
            for santral in selected_santraller:
                if santral in santral_dataframes:
                    st.subheader(f"{santral} Detay Analizi")
                    
                    df = santral_dataframes[santral]
                    fig1, fig2 = create_santral_detail_charts(df, santral)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        st.plotly_chart(fig2, use_container_width=True)
            
            # Excel Raporu Oluşturma
            st.markdown("---")
            st.header("Excel Raporu Oluştur")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Seçilen Santraller için Excel Raporu")
                
                # Excel oluşturma ve indirme
                try:
                    santral1_name = selected_santraller[0]
                    santral2_name = selected_santraller[1]
                    santral1_data = santral_dataframes[santral1_name]
                    santral2_data = santral_dataframes[santral2_name]
                    
                    excel_gen = SimpleComparisonExcel()
                    excel_path = excel_gen.create_simple_comparison_excel(
                        santral1_name, santral1_data,
                        santral2_name, santral2_data
                    )
                    
                    # Dosyayı oku ve direkt indirme butonu göster
                    with open(excel_path, "rb") as file:
                        excel_data = file.read()
                        
                    st.download_button(
                        label=f"{santral1_name} vs {santral2_name} Excel İndir",
                        data=excel_data,
                        file_name=f"Karsilastirma_{santral1_name.replace(' ', '_')}_vs_{santral2_name.replace(' ', '_')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.success("Excel hazır! Yukarıdaki butona basarak indirebilirsiniz.")
                    
                except Exception as e:
                    st.error(f"Excel oluşturma hatası: {e}")
                    st.error(f"Hata detayı: {str(e)}")
            
            with col2:
                st.subheader("Rapor İçeriği")
                st.info(f"""
                **3 Sheet'li Tam Excel Raporu**: 
                
                **Santral_1 Sheet**: {selected_santraller[0]}
                - TÜM 8,784 saatlik detay veri
                - 16 sütun (Tarih, PTF, SMF, KGÜP, Üretim, Gelirler vb.)
                
                **Santral_2 Sheet**: {selected_santraller[1]}
                - TÜM 8,784 saatlik detay veri  
                - 16 sütun (Tarih, PTF, SMF, KGÜP, Üretim, Gelirler vb.)
                
                **Karşılaştırma Sheet**: 
                - 12 aylık özet karşılaştırma
                - İstenen özel format
                """)
                
                st.warning(" Excel raporu dinamik olarak oluşturulur ve seçtiğiniz santrallere göre değişir.")
    
    else:
        # Başlangıç ekranı
        st.info(" Lütfen yan menüden 2 santral seçin ve 'Analizi Çalıştır' butonuna basın.")
        
        # Santral bilgileri
        st.markdown("---")
        st.header("Mevcut Santraller")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Rüzgar Enerji Santralleri (RES)")
            st.write("• **MASLAKTEPE RES** - Organizasyon ID: 12717")
            st.write("• **EBER RES** - Organizasyon ID: 12517")
        
        with col2:
            st.subheader("Hidroelektrik Santralleri (HES)")
            st.write("• **YANBOLU HES** - Organizasyon ID: 8801")
            st.write("• **MELİKOM HES** - Organizasyon ID: 9709")
        
        st.markdown("---")
        st.markdown("""
        ### Analiz Kapsamı
        - **Veri Dönemi**: 2024 tam yılı (8,784 saatlik veri)
        - **Piyasa Verileri**: PTF, SMF, Dengesizlik Fiyatları
        - **Santral Verileri**: KGÜP, Gerçek Üretim, Dengesizlik
        - **Finansal Analiz**: Gelir, Maliyet, Birim Değerler
        """)

if __name__ == "__main__":
    main()
