"""
Basit Excel Grafik Oluşturucu
Web arayüzündeki grafiklerin basit versiyonlarını Excel'e ekler
"""

import pandas as pd
import xlsxwriter
import os

class SimpleExcelCharts:
    def __init__(self):
        pass
    
    def create_enhanced_excel_with_charts(self, santral_dataframes, output_path):
        """Grafikli Excel raporu oluştur"""
        print("\n📊 Grafikli Excel raporu oluşturuluyor...")
        
        # Workbook oluştur
        workbook = xlsxwriter.Workbook(output_path)
        
        # Format tanımlamaları
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'bg_color': '#D9E2F3',
            'border': 1
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00 ₺',
            'border': 1
        })
        
        # Her santral için sheet oluştur
        for i, (santral_name, df) in enumerate(santral_dataframes.items(), 1):
            sheet_name = f'Santral_{i}'
            worksheet = workbook.add_worksheet(sheet_name)
            
            # Başlık
            worksheet.merge_range('A1:P1', f'🏭 {santral_name} - Detaylı Analiz', title_format)
            
            # Veri tablosunu yaz
            self.write_data_to_sheet(worksheet, df, header_format, number_format, currency_format, workbook)
            
            # Aylık özet için veri hazırla
            monthly_data = df.groupby('ay').agg({
                'Uretim': 'sum',
                'KGUP': 'sum',
                'dengesizlik': 'sum',
                'toplam_gelir': 'sum',
                'birim_gelir': 'mean'
            }).reset_index()
            
            # Aylık özet tablosunu ekle
            self.add_monthly_summary_with_chart(worksheet, monthly_data, santral_name, workbook)
        
        # Dashboard sheet'i
        self.create_dashboard_sheet(workbook, santral_dataframes, header_format, title_format, number_format, currency_format)
        
        # Karşılaştırma sheet'i
        self.create_comparison_sheet(workbook, santral_dataframes, header_format, title_format, number_format)
        
        workbook.close()
        print(f"✅ Grafikli Excel raporu oluşturuldu: {output_path}")
        return output_path
    
    def write_data_to_sheet(self, worksheet, df, header_format, number_format, currency_format, workbook):
        """Veri tablosunu sheet'e yaz"""
        # Başlıkları yaz
        for col, header in enumerate(df.columns):
            worksheet.write(2, col, header, header_format)
        
        # 🔄 TÜM VERİLERİ YAZ (performans için maksimum 1000 satır)
        # Analiz tüm verilerden yapılır, sadece Excel gösterimi sınırlanır
        max_rows = min(len(df), 1000)  # Excel performansı için maksimum 1000 satır
        sample_df = df.head(max_rows)
        
        for row, (_, data_row) in enumerate(sample_df.iterrows(), 3):
            for col, value in enumerate(data_row):
                if pd.isna(value):
                    worksheet.write(row, col, '', number_format)
                elif isinstance(value, (int, float)):
                    if 'gelir' in df.columns[col].lower() or 'tutar' in df.columns[col].lower():
                        worksheet.write(row, col, value, currency_format)
                    else:
                        worksheet.write(row, col, value, number_format)
                else:
                    worksheet.write(row, col, str(value))
        
        # Veri sayısı bilgisi ekle
        if len(df) > max_rows:
            worksheet.write(max_rows + 4, 0, f"📊 Not: Toplam {len(df):,} kayıt var, Excel'de ilk {max_rows:,} kayıt gösteriliyor.", 
                          workbook.add_format({'italic': True, 'font_color': '#666666'}))
            worksheet.write(max_rows + 5, 0, f"📈 Aylık özet ve grafikler TÜM VERİLERDEN hesaplanmıştır.", 
                          workbook.add_format({'bold': True, 'font_color': '#0066CC'}))
        
        # Sütun genişliklerini ayarla
        worksheet.set_column('A:P', 12)
    
    def add_monthly_summary_with_chart(self, worksheet, monthly_data, santral_name, workbook):
        """Aylık özet ve grafik ekle"""
        # Aylık özet tablosunu ekle
        start_row = 110
        
        # Başlık
        worksheet.merge_range(f'A{start_row}:F{start_row}', f'📊 {santral_name} - Aylık Özet', 
                            workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#E7E6E6'}))
        
        # Aylık veri tablosu
        headers = ['Ay', 'Üretim (MWh)', 'Plan (MWh)', 'Dengesizlik (MWh)', 'Toplam Gelir (TL)', 'Birim Gelir (TL/MWh)']
        
        for col, header in enumerate(headers):
            worksheet.write(start_row + 1, col, header, 
                          workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1}))
        
        # Aylık verileri yaz
        for row, (_, data) in enumerate(monthly_data.iterrows(), start_row + 2):
            worksheet.write(row, 0, int(data['ay']))
            worksheet.write(row, 1, data['Uretim'])
            worksheet.write(row, 2, data['KGUP'])
            worksheet.write(row, 3, data['dengesizlik'])
            worksheet.write(row, 4, data['toplam_gelir'])
            worksheet.write(row, 5, data['birim_gelir'])
        
        # Basit sütun grafiği ekle
        chart = workbook.add_chart({'type': 'column'})
        
        # Veri aralığını belirle
        data_range = f'A{start_row + 2}:C{start_row + 1 + len(monthly_data)}'
        
        chart.add_series({
            'name': 'Plan (KGÜP)',
            'categories': [worksheet.name, start_row + 1, 0, start_row + len(monthly_data), 0],
            'values': [worksheet.name, start_row + 1, 2, start_row + len(monthly_data), 2],
            'fill': {'color': '#5B9BD5'}
        })
        
        chart.add_series({
            'name': 'Gerçek Üretim',
            'categories': [worksheet.name, start_row + 1, 0, start_row + len(monthly_data), 0],
            'values': [worksheet.name, start_row + 1, 1, start_row + len(monthly_data), 1],
            'fill': {'color': '#70AD47'}
        })
        
        chart.set_title({'name': f'{santral_name} - Plan vs Gerçek Üretim'})
        chart.set_x_axis({'name': 'Ay'})
        chart.set_y_axis({'name': 'Üretim (MWh)'})
        chart.set_size({'width': 500, 'height': 300})
        
        # Grafiği ekle
        worksheet.insert_chart(f'H{start_row}', chart)
    
    def create_dashboard_sheet(self, workbook, santral_dataframes, header_format, title_format, number_format, currency_format):
        """Dashboard sheet'i oluştur"""
        worksheet = workbook.add_worksheet('Dashboard')
        
        # Başlık
        worksheet.merge_range('A1:H1', '🎯 Gain Enerji - Executive Dashboard', title_format)
        
        # Özet tablo
        headers = ['Santral', 'Toplam Üretim (MWh)', 'Toplam Gelir (TL)', 'Ort. Birim Gelir (TL/MWh)', 'Plan Tutturma (%)']
        
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)
        
        # Santral verilerini yaz
        row = 4
        for santral_name, df in santral_dataframes.items():
            total_uretim = df['Uretim'].sum()
            total_kgup = df['KGUP'].sum()
            total_gelir = df['toplam_gelir'].sum()
            avg_birim_gelir = df['birim_gelir'].mean()
            plan_tutturma = (total_uretim / total_kgup) * 100 if total_kgup > 0 else 0
            
            worksheet.write(row, 0, santral_name)
            worksheet.write(row, 1, total_uretim, number_format)
            worksheet.write(row, 2, total_gelir, currency_format)
            worksheet.write(row, 3, avg_birim_gelir, currency_format)
            worksheet.write(row, 4, plan_tutturma, workbook.add_format({'num_format': '0.0%'}))
            row += 1
        
        # Sütun genişliklerini ayarla
        worksheet.set_column('A:H', 18)
    
    def create_comparison_sheet(self, workbook, santral_dataframes, header_format, title_format, number_format):
        """Karşılaştırma sheet'i oluştur"""
        worksheet = workbook.add_worksheet('Karşılaştırma')
        
        # Başlık
        worksheet.merge_range('A1:G1', '📊 Santral Karşılaştırma Analizi', title_format)
        
        # Karşılaştırma verileri hazırla
        comparison_data = []
        
        for santral_name, df in santral_dataframes.items():
            monthly_summary = df.groupby('ay').agg({
                'Uretim': 'sum',
                'dengesizlik': 'sum',
                'toplam_gelir': 'sum',
                'birim_gelir': 'mean'
            }).reset_index()
            
            monthly_summary['santral'] = santral_name
            comparison_data.append(monthly_summary)
        
        if comparison_data:
            combined_df = pd.concat(comparison_data, ignore_index=True)
            
            # Başlıkları yaz
            for col, header in enumerate(combined_df.columns):
                worksheet.write(3, col, header, header_format)
            
            # Verileri yaz
            for row, (_, data_row) in enumerate(combined_df.iterrows(), 4):
                for col, value in enumerate(data_row):
                    if isinstance(value, (int, float)):
                        worksheet.write(row, col, value, number_format)
                    else:
                        worksheet.write(row, col, str(value))
        
        # Sütun genişliklerini ayarla
        worksheet.set_column('A:G', 15)

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
        excel_path = "/Users/aldn/Desktop/gain-case-study/reports/excel_reports/Gain_Enerji_Grafikli_Analiz_2024.xlsx"
        chart_generator = SimpleExcelCharts()
        chart_generator.create_enhanced_excel_with_charts(santral_dataframes, excel_path)
