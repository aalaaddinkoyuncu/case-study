"""
Veri İşleme ve Analiz Modülü
Çekilen ham verileri temizler, birleştirir ve Excel formatına dönüştürür.
"""

import pandas as pd
import json
import os
from datetime import datetime
import numpy as np

class DataProcessor:
    def __init__(self):
        self.raw_data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        self.processed_data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
        self.reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'excel_reports')
        
        # Dizinleri oluştur
        os.makedirs(self.processed_data_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def load_json_data(self, filename):
        """JSON dosyasından veri yükle"""
        file_path = os.path.join(self.raw_data_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠️  Dosya bulunamadı: {filename}")
            return pd.DataFrame()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            print(f"{filename} yüklendi: {len(df)} kayıt")
            return df
            
        except Exception as e:
            print(f"{filename} yükleme hatası: {e}")
            return pd.DataFrame()
    
    def process_ptf_data(self):
        """PTF verilerini işle"""
        print("\nPTF verileri işleniyor...")
        
        df = self.load_json_data('ptf_2024.json')
        if df.empty:
            return df
        
        # Tarih ve saat sütunlarını düzenle
        # API'den gelen date zaten tam format: "2024-01-01T00:00:00+03:00"
        df['datetime'] = pd.to_datetime(df['date'])
        df['ay'] = df['datetime'].dt.month
        df['gun'] = df['datetime'].dt.day
        df['saat'] = df['datetime'].dt.hour
        
        # Sadece gerekli sütunları al
        df_clean = df[['datetime', 'ay', 'gun', 'saat', 'price']].copy()
        df_clean.rename(columns={'price': 'PTF'}, inplace=True)
        
        # Sırala
        df_clean = df_clean.sort_values('datetime').reset_index(drop=True)
        
        print(f"PTF verileri işlendi: {len(df_clean)} kayıt")
        return df_clean
    
    def process_smf_data(self):
        """SMF verilerini işle"""
        print("\nSMF verileri işleniyor...")
        
        df = self.load_json_data('smf_2024.json')
        if df.empty:
            return df
        
        # Tarih ve saat sütunlarını düzenle
        # API'den gelen date zaten tam format: "2024-01-01T00:00:00+03:00"
        df['datetime'] = pd.to_datetime(df['date'])
        df['ay'] = df['datetime'].dt.month
        df['gun'] = df['datetime'].dt.day
        df['saat'] = df['datetime'].dt.hour
        
        # Sadece gerekli sütunları al
        df_clean = df[['datetime', 'ay', 'gun', 'saat', 'systemMarginalPrice']].copy()
        df_clean.rename(columns={'systemMarginalPrice': 'SMF'}, inplace=True)
        
        # Sırala
        df_clean = df_clean.sort_values('datetime').reset_index(drop=True)
        
        print(f"SMF verileri işlendi: {len(df_clean)} kayıt")
        return df_clean
    
    def process_santral_data(self, santral_name, data_type='kgup'):
        """Santral verilerini işle (KGÜP veya Üretim)"""
        safe_name = santral_name.replace(' ', '_').replace('İ', 'I')
        filename = f'{data_type}_{safe_name}_2024.json'
        
        print(f"\n{santral_name} {data_type.upper()} verileri işleniyor...")
        
        df = self.load_json_data(filename)
        if df.empty:
            return df
        
        # Tarih ve saat işleme
        if data_type == 'kgup':
            # KGÜP için 'date' ve 'time' sütunları
            df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
            value_col = 'toplam'
            new_col_name = 'KGUP'
        else:
            # Üretim için 'date' zaten tam format: "2024-01-01T00:00:00+03:00"
            df['datetime'] = pd.to_datetime(df['date'])
            value_col = 'total'
            new_col_name = 'Uretim'
        
        df['ay'] = df['datetime'].dt.month
        df['gun'] = df['datetime'].dt.day
        df['saat'] = df['datetime'].dt.hour
        
        # Sadece gerekli sütunları al
        columns_to_keep = ['datetime', 'ay', 'gun', 'saat', value_col, 'santral_name']
        df_clean = df[columns_to_keep].copy()
        df_clean.rename(columns={value_col: new_col_name}, inplace=True)
        
        # Sırala
        df_clean = df_clean.sort_values('datetime').reset_index(drop=True)
        
        print(f"{santral_name} {data_type.upper()} verileri işlendi: {len(df_clean)} kayıt")
        return df_clean
    
    def create_santral_analysis(self, santral_name):
        """Bir santral için tüm verileri birleştir ve analiz et"""
        print(f"\n{santral_name} için analiz oluşturuluyor...")
        
        # PTF ve SMF verilerini yükle
        ptf_df = self.process_ptf_data()
        smf_df = self.process_smf_data()
        
        # Santral KGÜP ve Üretim verilerini yükle
        kgup_df = self.process_santral_data(santral_name, 'kgup')
        uretim_df = self.process_santral_data(santral_name, 'uretim')
        
        if kgup_df.empty or uretim_df.empty:
            print(f"{santral_name} için yeterli veri yok")
            return pd.DataFrame()
        
        # Tüm verileri birleştir
        # Önce PTF ve SMF'yi birleştir
        if not ptf_df.empty and not smf_df.empty:
            piyasa_df = pd.merge(ptf_df, smf_df[['datetime', 'SMF']], on='datetime', how='outer')
        elif not ptf_df.empty:
            piyasa_df = ptf_df.copy()
            piyasa_df['SMF'] = np.nan
        elif not smf_df.empty:
            piyasa_df = smf_df.copy()
            piyasa_df['PTF'] = np.nan
        else:
            piyasa_df = pd.DataFrame()
        
        # KGÜP ve Üretim verilerini birleştir
        santral_df = pd.merge(kgup_df, uretim_df[['datetime', 'Uretim']], on='datetime', how='outer')
        
        # Piyasa verileri ile santral verilerini birleştir
        if not piyasa_df.empty:
            final_df = pd.merge(piyasa_df, santral_df, on='datetime', how='outer')
        else:
            final_df = santral_df.copy()
            final_df['PTF'] = np.nan
            final_df['SMF'] = np.nan
        
        # Tarih bilgilerini düzenle
        final_df['tarih'] = final_df['datetime'].dt.date
        final_df['ay'] = final_df['datetime'].dt.month
        final_df['saat'] = final_df['datetime'].dt.hour
        
        # Dengesizlik hesapla
        final_df['dengesizlik'] = final_df['Uretim'] - final_df['KGUP']
        
        # 🆕 PDF'DEKİ FORMÜLLERE GÖRE DENGESİZLİK FİYATLARI
        # Pozitif Dengesizlik Fiyatı = Min(PTF, SMF) * 0.97
        final_df['pozitif_dengesizlik_fiyati'] = np.minimum(final_df['PTF'], final_df['SMF']) * 0.97
        
        # Negatif Dengesizlik Fiyatı = Max(PTF, SMF) * 1.03  
        final_df['negatif_dengesizlik_fiyati'] = np.maximum(final_df['PTF'], final_df['SMF']) * 1.03
        
        # 🆕 GÖP GELİRİ (Gün Öncesi Piyasa Geliri)
        final_df['gop_geliri'] = final_df['KGUP'] * final_df['PTF']
        
        # 🆕 DOĞRU DENGESİZLİK TUTARI HESAPLAMA
        # Dengesizlik > 0 → Pozitif Dengesizlik Tutarı = Dengesizlik * Pozitif Dengesizlik Fiyatı
        # Dengesizlik < 0 → Negatif Dengesizlik Tutarı = Dengesizlik * Negatif Dengesizlik Fiyatı
        final_df['dengesizlik_tutari'] = np.where(
            final_df['dengesizlik'] > 0,
            final_df['dengesizlik'] * final_df['pozitif_dengesizlik_fiyati'],  # Pozitif dengesizlik
            final_df['dengesizlik'] * final_df['negatif_dengesizlik_fiyati']   # Negatif dengesizlik
        )
        
        # 🆕 TOPLAM (NET) ÜRETİM (SATIŞ) GELİRİ
        final_df['toplam_gelir'] = final_df['gop_geliri'] + final_df['dengesizlik_tutari']
        
        # 🆕 BİRİM GELİR (TL/MWh)
        final_df['birim_gelir'] = final_df['toplam_gelir'] / final_df['Uretim'].replace(0, np.nan)
        
        # 🆕 DENGESİZLİK MALİYETİ (Sadece negatif dengesizlik için)
        final_df['dengesizlik_maliyeti'] = np.where(
            final_df['dengesizlik'] < 0, 
            abs(final_df['dengesizlik_tutari']),  # Negatif dengesizlik tutarının mutlak değeri
            0
        )
        
        # 🆕 BİRİM DENGESİZLİK MALİYETİ (TL/MWh)
        final_df['birim_dengesizlik_maliyeti'] = final_df['dengesizlik_maliyeti'] / final_df['Uretim'].replace(0, np.nan)
        
        # 🆕 GÜNCEL SÜTUN SIRALAMASI (PDF formüllerine göre)
        columns_order = [
            'tarih', 'ay', 'saat', 'PTF', 'SMF', 
            'pozitif_dengesizlik_fiyati', 'negatif_dengesizlik_fiyati',  # 🆕 Yeni dengesizlik fiyatları
            'KGUP', 'Uretim', 'dengesizlik',
            'gop_geliri', 'dengesizlik_tutari', 'toplam_gelir', 'birim_gelir',
            'dengesizlik_maliyeti', 'birim_dengesizlik_maliyeti'
        ]
        
        final_df = final_df[columns_order].copy()
        final_df = final_df.sort_values(['tarih', 'saat']).reset_index(drop=True)
        
        print(f"{santral_name} analizi tamamlandı: {len(final_df)} kayıt")
        return final_df
    
    def create_comparison_analysis(self, santral_dataframes):
        """Santraller arası karşılaştırma analizi"""
        print("\nKarşılaştırma analizi oluşturuluyor...")
        
        comparison_data = []
        
        for santral_name, df in santral_dataframes.items():
            if df.empty:
                continue
            
            # Aylık özet
            monthly_summary = df.groupby('ay').agg({
                'Uretim': 'sum',
                'dengesizlik': 'sum', 
                'gop_geliri': 'sum',
                'dengesizlik_tutari': 'sum',
                'toplam_gelir': 'sum',
                'dengesizlik_maliyeti': 'sum'
            }).reset_index()
            
            monthly_summary['santral'] = santral_name
            monthly_summary['birim_gelir'] = monthly_summary['toplam_gelir'] / monthly_summary['Uretim']
            monthly_summary['birim_deng_maliyeti'] = monthly_summary['dengesizlik_maliyeti'] / monthly_summary['Uretim']
            
            comparison_data.append(monthly_summary)
        
        if comparison_data:
            comparison_df = pd.concat(comparison_data, ignore_index=True)
            print(f"Karşılaştırma analizi tamamlandı: {len(comparison_df)} kayıt")
            return comparison_df
        
        return pd.DataFrame()
    
    def create_excel_report(self, with_charts=True):
        """Excel raporu oluştur"""
        print(f"\nExcel raporu oluşturuluyor... (Grafikler: {'Evet' if with_charts else 'Hayır'})")
        
        # Santral listesi
        santraller = [
            "MASLAKTEPE RES",
            "EBER RES", 
            "YANBOLU HES",
            "MELİKOM HES"
        ]
        
        # Her santral için analiz oluştur
        santral_dataframes = {}
        
        for santral in santraller:
            df = self.create_santral_analysis(santral)
            if not df.empty:
                santral_dataframes[santral] = df
        
        if not santral_dataframes:
            print("Hiçbir santral için veri bulunamadı")
            return
        
        # Karşılaştırma analizi
        comparison_df = self.create_comparison_analysis(santral_dataframes)
        
        if with_charts:
            # 🆕 GRAFİKLİ EXCEL RAPORU
            try:
                from src.excel_chart_generator import ExcelChartGenerator
            except ImportError:
                import sys
                sys.path.append(os.path.dirname(__file__))
                from excel_chart_generator import ExcelChartGenerator
            
            excel_file = os.path.join(self.reports_dir, 'Gain_Enerji_Grafikli_Analiz_2024.xlsx')
            chart_generator = ExcelChartGenerator(excel_file)
            chart_generator.create_enhanced_excel_report(santral_dataframes)
            
        else:
            # Basit Excel raporu (eski versiyon)
            excel_file = os.path.join(self.reports_dir, 'Gain_Enerji_Case_Study_Analiz_2024.xlsx')
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                
                # Her santral için ayrı sheet
                for i, (santral_name, df) in enumerate(santral_dataframes.items(), 1):
                    sheet_name = f'Santral_{i}'
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Sheet'e santral adını ekle
                    worksheet = writer.sheets[sheet_name]
                    worksheet['A1'] = santral_name
                
                # Karşılaştırma sheet'i
                if not comparison_df.empty:
                    comparison_df.to_excel(writer, sheet_name='Karşılaştırma', index=False)
            
            print(f"Excel raporu oluşturuldu: {excel_file}")
        
        # Özet bilgi
        print(f"\nRapor Özeti:")
        print(f"  - Analiz edilen santral sayısı: {len(santral_dataframes)}")
        for santral, df in santral_dataframes.items():
            print(f"  - {santral}: {len(df)} saatlik veri")
        
        return excel_file

if __name__ == "__main__":
    processor = DataProcessor()
    
    # Excel raporu oluştur
    excel_file = processor.create_excel_report()
    
    if excel_file:
        print(f"\nAnaliz tamamlandı!")
        print(f"Excel dosyası: {excel_file}")
    else:
        print("Rapor oluşturulamadı. Önce veri çekme işlemini tamamlayın.")
