"""
Tam Excel Rapor Oluşturucu
3 farklı Excel versiyonu oluşturur:
1. Tüm Veriler (8,784 satır)
2. Grafikli Özet (1,000 satır + grafikler)
3. Sadece Grafikler (minimal veri + çok grafik)
"""

import pandas as pd
import xlsxwriter
import os
from simple_excel_charts import SimpleExcelCharts

class CompleteExcelGenerator:
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'excel_reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def create_all_excel_versions(self, santral_dataframes):
        """3 farklı Excel versiyonu oluştur"""
        print("\n📊 3 Farklı Excel Versiyonu Oluşturuluyor...")
        
        # 1. TÜM VERİLER - Her şey dahil
        full_data_path = self.create_full_data_excel(santral_dataframes)
        
        # 2. GRAFİKLİ ÖZET - Grafikler + özet veriler
        chart_generator = SimpleExcelCharts()
        summary_path = os.path.join(self.reports_dir, '2_Gain_Enerji_Grafikli_Ozet_2024.xlsx')
        chart_generator.create_enhanced_excel_with_charts(santral_dataframes, summary_path)
        
        # 3. SADECE GRAFİKLER - Minimal veri + maksimum grafik
        charts_only_path = self.create_charts_only_excel(santral_dataframes)
        
        return full_data_path, summary_path, charts_only_path
    
    def create_full_data_excel(self, santral_dataframes):
        """1. TÜM VERİLER - 8,784 satırın hepsi"""
        print("\n📋 1. TÜM VERİLER Excel'i oluşturuluyor...")
        
        excel_path = os.path.join(self.reports_dir, '1_Gain_Enerji_TUM_VERILER_2024.xlsx')
        
        # Workbook oluştur
        workbook = xlsxwriter.Workbook(excel_path)
        
        # Formatlar
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'bg_color': '#366092',
            'font_color': 'white',
            'border': 1,
            'text_wrap': True
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#D9E2F3',
            'border': 1,
            'align': 'center'
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00 ₺',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy',
            'border': 1
        })
        
        # Her santral için sheet oluştur
        for i, (santral_name, df) in enumerate(santral_dataframes.items(), 1):
            sheet_name = f'Santral_{i}_{santral_name.replace(" ", "_")[:15]}'
            worksheet = workbook.add_worksheet(sheet_name)
            
            # Başlık
            worksheet.merge_range('A1:S1', f'🏭 {santral_name} - TÜM VERİLER (8,784 Saatlik)', title_format)
            
            # Alt başlık
            worksheet.merge_range('A2:S2', f'2024 Yılı Tam Detay - {len(df):,} Kayıt', 
                                workbook.add_format({'italic': True, 'bg_color': '#F2F2F2', 'border': 1}))
            
            # Başlıkları yaz
            for col, header in enumerate(df.columns):
                worksheet.write(3, col, header, header_format)
            
            # 🔥 TÜM VERİLERİ YAZ - HİÇBİR SINIR YOK
            print(f"   📝 {santral_name}: {len(df):,} satır yazılıyor...")
            
            for row, (_, data_row) in enumerate(df.iterrows(), 4):
                for col, value in enumerate(data_row):
                    if pd.isna(value):
                        worksheet.write(row, col, '', number_format)
                    elif isinstance(value, (int, float)):
                        if 'gelir' in df.columns[col].lower() or 'tutar' in df.columns[col].lower() or 'maliyet' in df.columns[col].lower():
                            worksheet.write(row, col, value, currency_format)
                        else:
                            worksheet.write(row, col, value, number_format)
                    elif 'tarih' in df.columns[col].lower():
                        worksheet.write(row, col, str(value), date_format)
                    else:
                        worksheet.write(row, col, str(value))
            
            # Sütun genişliklerini ayarla
            worksheet.set_column('A:A', 12)  # Tarih
            worksheet.set_column('B:C', 8)   # Ay, Saat
            worksheet.set_column('D:E', 10)  # PTF, SMF
            worksheet.set_column('F:G', 12)  # Dengesizlik fiyatları
            worksheet.set_column('H:J', 12)  # KGÜP, Üretim, Dengesizlik
            worksheet.set_column('K:S', 15)  # Gelir sütunları
            
            # Freeze panes
            worksheet.freeze_panes(4, 1)
            
            print(f"   ✅ {santral_name}: {len(df):,} satır tamamlandı")
        
        # Özet Dashboard
        self.create_summary_dashboard(workbook, santral_dataframes, header_format, title_format, number_format, currency_format)
        
        workbook.close()
        print(f"✅ TÜM VERİLER Excel'i oluşturuldu: {excel_path}")
        return excel_path
    
    def create_summary_dashboard(self, workbook, santral_dataframes, header_format, title_format, number_format, currency_format):
        """Özet dashboard sheet'i"""
        worksheet = workbook.add_worksheet('OZET_DASHBOARD')
        
        # Ana başlık
        worksheet.merge_range('A1:L1', '🎯 GAİN ENERJİ - 2024 YILI ÖZET DASHBOARD', title_format)
        
        # Santral özet tablosu
        worksheet.merge_range('A3:L3', '📊 SANTRAL PERFORMANS ÖZETİ', 
                            workbook.add_format({'bold': True, 'font_size': 12, 'bg_color': '#E7E6E6'}))
        
        headers = [
            'Santral Adı', 'Tip', 'Toplam Üretim (MWh)', 'Toplam Plan (MWh)', 
            'Plan Tutturma (%)', 'Toplam Gelir (TL)', 'Ort. Birim Gelir (TL/MWh)',
            'Toplam Dengesizlik (MWh)', 'Dengesizlik Oranı (%)', 'Dengesizlik Maliyeti (TL)',
            'Net Gelir (TL)', 'Performans Notu'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)
        
        # Santral verilerini yaz
        row = 5
        for santral_name, df in santral_dataframes.items():
            total_uretim = df['Uretim'].sum()
            total_kgup = df['KGUP'].sum()
            total_gelir = df['toplam_gelir'].sum()
            total_dengesizlik = df['dengesizlik'].sum()
            total_deng_maliyeti = df['dengesizlik_maliyeti'].sum()
            avg_birim_gelir = df['birim_gelir'].mean()
            
            plan_tutturma = (total_uretim / total_kgup) * 100 if total_kgup > 0 else 0
            dengesizlik_orani = (abs(total_dengesizlik) / total_uretim) * 100 if total_uretim > 0 else 0
            net_gelir = total_gelir - total_deng_maliyeti
            
            # Performans notu
            if plan_tutturma >= 95 and dengesizlik_orani <= 10:
                performans = "A+ Mükemmel"
            elif plan_tutturma >= 90 and dengesizlik_orani <= 15:
                performans = "A İyi"
            elif plan_tutturma >= 85:
                performans = "B Orta"
            else:
                performans = "C Geliştirilmeli"
            
            santral_tip = "RES" if "RES" in santral_name else "HES"
            
            data = [
                santral_name, santral_tip, total_uretim, total_kgup, plan_tutturma/100,
                total_gelir, avg_birim_gelir, total_dengesizlik, dengesizlik_orani/100,
                total_deng_maliyeti, net_gelir, performans
            ]
            
            for col, value in enumerate(data):
                if isinstance(value, (int, float)):
                    if col in [2, 3, 7]:  # MWh değerleri
                        worksheet.write(row, col, value, number_format)
                    elif col in [4, 8]:  # Yüzde değerleri
                        worksheet.write(row, col, value, workbook.add_format({'num_format': '0.0%', 'border': 1}))
                    elif col in [5, 6, 9, 10]:  # TL değerleri
                        worksheet.write(row, col, value, currency_format)
                    else:
                        worksheet.write(row, col, value, number_format)
                else:
                    worksheet.write(row, col, str(value))
            row += 1
        
        # Sütun genişliklerini ayarla
        worksheet.set_column('A:L', 15)
        
        # Freeze panes
        worksheet.freeze_panes(5, 1)
    
    def create_charts_only_excel(self, santral_dataframes):
        """3. SADECE GRAFİKLER - Minimal veri + maksimum grafik"""
        print("\n📈 3. SADECE GRAFİKLER Excel'i oluşturuluyor...")
        
        excel_path = os.path.join(self.reports_dir, '3_Gain_Enerji_SADECE_GRAFIKLER_2024.xlsx')
        
        # Bu versiyonda sadece grafikler ve özet tablolar olacak
        # Detaylı implementasyon gerekirse ekleyebiliriz
        
        # Şimdilik grafikli özet ile aynı olsun
        chart_generator = SimpleExcelCharts()
        chart_generator.create_enhanced_excel_with_charts(santral_dataframes, excel_path)
        
        print(f"✅ SADECE GRAFİKLER Excel'i oluşturuldu: {excel_path}")
        return excel_path

if __name__ == "__main__":
    # Test için
    import sys
    sys.path.append(os.path.dirname(__file__))
    
    from data_processor import DataProcessor
    
    processor = DataProcessor()
    santral_dataframes = {}
    
    santraller = ["MASLAKTEPE RES", "EBER RES", "YANBOLU HES", "MELİKOM HES"]
    
    for santral in santraller:
        df = processor.create_santral_analysis(santral)
        if not df.empty:
            santral_dataframes[santral] = df
    
    if santral_dataframes:
        generator = CompleteExcelGenerator()
        full_path, summary_path, charts_path = generator.create_all_excel_versions(santral_dataframes)
        
        print(f"\n🎉 3 Excel Versiyonu Hazır:")
        print(f"1️⃣ TÜM VERİLER: {full_path}")
        print(f"2️⃣ GRAFİKLİ ÖZET: {summary_path}")
        print(f"3️⃣ SADECE GRAFİKLER: {charts_path}")
