"""
Excel Grafik Oluşturucu
Web arayüzündeki grafikleri Excel'e ekler
"""

import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import os

class ExcelChartGenerator:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.workbook = None
        self.worksheets = {}
    
    def create_enhanced_excel_report(self, santral_dataframes):
        """Grafikli Excel raporu oluştur"""
        print("\n📊 Grafikli Excel raporu oluşturuluyor...")
        
        # Workbook oluştur
        self.workbook = xlsxwriter.Workbook(self.excel_path)
        
        # Format tanımlamaları
        self.define_formats()
        
        # Her santral için sheet ve grafikler
        for i, (santral_name, df) in enumerate(santral_dataframes.items(), 1):
            sheet_name = f'Santral_{i}'
            self.create_santral_sheet_with_charts(sheet_name, santral_name, df)
        
        # Karşılaştırma sheet'i
        self.create_comparison_sheet_with_charts(santral_dataframes)
        
        # Dashboard sheet'i
        self.create_dashboard_sheet(santral_dataframes)
        
        # Workbook'u kapat
        self.workbook.close()
        print(f"✅ Grafikli Excel raporu oluşturuldu: {self.excel_path}")
    
    def define_formats(self):
        """Excel formatlarını tanımla"""
        self.formats = {
            'header': self.workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            }),
            'title': self.workbook.add_format({
                'bold': True,
                'font_size': 16,
                'bg_color': '#D9E2F3',
                'border': 1
            }),
            'number': self.workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1
            }),
            'currency': self.workbook.add_format({
                'num_format': '#,##0.00 ₺',
                'border': 1
            }),
            'percentage': self.workbook.add_format({
                'num_format': '0.0%',
                'border': 1
            })
        }
    
    def create_santral_sheet_with_charts(self, sheet_name, santral_name, df):
        """Santral sheet'i grafiklerle oluştur"""
        worksheet = self.workbook.add_worksheet(sheet_name)
        self.worksheets[sheet_name] = worksheet
        
        # Santral adını başlık olarak ekle
        worksheet.merge_range('A1:P1', f'🏭 {santral_name} - Detaylı Analiz', self.formats['title'])
        
        # Veri tablosunu ekle
        self.write_data_table(worksheet, df, start_row=2)
        
        # Aylık özet veriler
        monthly_data = self.prepare_monthly_data(df)
        
        # Grafikleri ekle
        self.add_production_chart(worksheet, monthly_data, santral_name, 'S3')
        self.add_revenue_chart(worksheet, monthly_data, santral_name, 'S20')
        self.add_imbalance_chart(worksheet, monthly_data, santral_name, 'S37')
        
        # Sütun genişliklerini ayarla
        worksheet.set_column('A:P', 12)
    
    def write_data_table(self, worksheet, df, start_row=0):
        """Veri tablosunu Excel'e yaz"""
        # Başlıkları yaz
        for col, header in enumerate(df.columns):
            worksheet.write(start_row, col, header, self.formats['header'])
        
        # Verileri yaz
        for row, (_, data_row) in enumerate(df.iterrows(), start_row + 1):
            for col, value in enumerate(data_row):
                if pd.isna(value):
                    worksheet.write(row, col, '', self.formats['number'])
                elif isinstance(value, (int, float)):
                    if 'gelir' in df.columns[col].lower() or 'tutar' in df.columns[col].lower():
                        worksheet.write(row, col, value, self.formats['currency'])
                    else:
                        worksheet.write(row, col, value, self.formats['number'])
                else:
                    worksheet.write(row, col, str(value))
    
    def prepare_monthly_data(self, df):
        """Aylık özet veriler hazırla"""
        monthly = df.groupby('ay').agg({
            'Uretim': 'sum',
            'KGUP': 'sum',
            'dengesizlik': 'sum',
            'toplam_gelir': 'sum',
            'birim_gelir': 'mean',
            'dengesizlik_maliyeti': 'sum'
        }).reset_index()
        
        return monthly
    
    def add_production_chart(self, worksheet, monthly_data, santral_name, position):
        """Üretim grafiği ekle"""
        # Grafik oluştur
        chart = self.workbook.add_chart({'type': 'column'})
        
        # Veri aralığını belirle (aylık veriler için)
        chart.add_series({
            'name': 'Plan (KGÜP)',
            'categories': ['Dashboard', 1, 0, len(monthly_data), 0],  # Ay sütunu
            'values': ['Dashboard', 1, 1, len(monthly_data), 1],      # KGÜP sütunu
            'fill': {'color': '#5B9BD5'},
            'gap': 150
        })
        
        chart.add_series({
            'name': 'Gerçek Üretim',
            'categories': ['Dashboard', 1, 0, len(monthly_data), 0],  # Ay sütunu  
            'values': ['Dashboard', 1, 2, len(monthly_data), 2],      # Üretim sütunu
            'fill': {'color': '#70AD47'}
        })
        
        # Grafik ayarları
        chart.set_title({'name': f'{santral_name} - Plan vs Gerçek Üretim'})
        chart.set_x_axis({'name': 'Ay'})
        chart.set_y_axis({'name': 'Üretim (MWh)'})
        chart.set_size({'width': 480, 'height': 288})
        
        # Grafiği worksheet'e ekle
        worksheet.insert_chart(position, chart)
    
    def add_revenue_chart(self, worksheet, monthly_data, santral_name, position):
        """Gelir grafiği ekle"""
        chart = self.workbook.add_chart({'type': 'line'})
        
        chart.add_series({
            'name': 'Birim Gelir (TL/MWh)',
            'categories': ['Dashboard', 1, 0, len(monthly_data), 0],
            'values': ['Dashboard', 1, 4, len(monthly_data), 4],  # birim_gelir sütunu
            'line': {'color': '#FFC000', 'width': 3},
            'marker': {'type': 'circle', 'size': 6}
        })
        
        chart.set_title({'name': f'{santral_name} - Birim Gelir Trendi'})
        chart.set_x_axis({'name': 'Ay'})
        chart.set_y_axis({'name': 'Birim Gelir (TL/MWh)'})
        chart.set_size({'width': 480, 'height': 288})
        
        worksheet.insert_chart(position, chart)
    
    def add_imbalance_chart(self, worksheet, monthly_data, santral_name, position):
        """Dengesizlik grafiği ekle"""
        chart = self.workbook.add_chart({'type': 'column'})
        
        chart.add_series({
            'name': 'Dengesizlik (MWh)',
            'categories': ['Dashboard', 1, 0, len(monthly_data), 0],
            'values': ['Dashboard', 1, 3, len(monthly_data), 3],  # dengesizlik sütunu
            'fill': {'color': '#E74C3C'},
            'data_labels': {'value': True}
        })
        
        chart.set_title({'name': f'{santral_name} - Aylık Dengesizlik'})
        chart.set_x_axis({'name': 'Ay'})
        chart.set_y_axis({'name': 'Dengesizlik (MWh)'})
        chart.set_size({'width': 480, 'height': 288})
        
        worksheet.insert_chart(position, chart)
    
    def create_comparison_sheet_with_charts(self, santral_dataframes):
        """Karşılaştırma sheet'i grafiklerle"""
        worksheet = self.workbook.add_worksheet('Karşılaştırma')
        
        # Başlık
        worksheet.merge_range('A1:H1', '📊 Santral Karşılaştırma Analizi', self.formats['title'])
        
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
            
            # Veriyi yaz
            self.write_data_table(worksheet, combined_df, start_row=2)
            
            # Karşılaştırma grafiği ekle
            self.add_comparison_chart(worksheet, combined_df, 'J3')
    
    def add_comparison_chart(self, worksheet, combined_df, position):
        """Karşılaştırma grafiği ekle"""
        chart = self.workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
        
        # Her santral için seri ekle
        santraller = combined_df['santral'].unique()
        colors = ['#5B9BD5', '#70AD47', '#FFC000', '#E74C3C']
        
        for i, santral in enumerate(santraller):
            chart.add_series({
                'name': santral,
                'categories': ['Karşılaştırma', 3, 0, len(combined_df)+2, 0],  # Ay sütunu
                'values': ['Karşılaştırma', 3, 1, len(combined_df)+2, 1],      # Üretim sütunu
                'fill': {'color': colors[i % len(colors)]}
            })
        
        chart.set_title({'name': 'Santral Üretim Karşılaştırması'})
        chart.set_x_axis({'name': 'Ay'})
        chart.set_y_axis({'name': 'Üretim (MWh)'})
        chart.set_size({'width': 600, 'height': 400})
        
        worksheet.insert_chart(position, chart)
    
    def create_dashboard_sheet(self, santral_dataframes):
        """Dashboard sheet'i oluştur"""
        worksheet = self.workbook.add_worksheet('Dashboard')
        
        # Başlık
        worksheet.merge_range('A1:L1', '🎯 Gain Enerji - Executive Dashboard', self.formats['title'])
        
        # Özet metrikler
        row = 3
        worksheet.write(row, 0, 'Santral', self.formats['header'])
        worksheet.write(row, 1, 'Toplam Üretim (MWh)', self.formats['header'])
        worksheet.write(row, 2, 'Toplam Gelir (TL)', self.formats['header'])
        worksheet.write(row, 3, 'Ort. Birim Gelir (TL/MWh)', self.formats['header'])
        worksheet.write(row, 4, 'Plan Tutturma (%)', self.formats['header'])
        
        row += 1
        for santral_name, df in santral_dataframes.items():
            total_uretim = df['Uretim'].sum()
            total_kgup = df['KGUP'].sum()
            total_gelir = df['toplam_gelir'].sum()
            avg_birim_gelir = df['birim_gelir'].mean()
            plan_tutturma = (total_uretim / total_kgup) * 100 if total_kgup > 0 else 0
            
            worksheet.write(row, 0, santral_name)
            worksheet.write(row, 1, total_uretim, self.formats['number'])
            worksheet.write(row, 2, total_gelir, self.formats['currency'])
            worksheet.write(row, 3, avg_birim_gelir, self.formats['currency'])
            worksheet.write(row, 4, plan_tutturma/100, self.formats['percentage'])
            row += 1
        
        # Dashboard grafiği
        self.add_dashboard_chart(worksheet, santral_dataframes, 'A12')
        
        # Sütun genişliklerini ayarla
        worksheet.set_column('A:L', 15)
    
    def add_dashboard_chart(self, worksheet, santral_dataframes, position):
        """Dashboard grafiği ekle"""
        chart = self.workbook.add_chart({'type': 'pie'})
        
        # Toplam üretim verilerini hazırla
        santral_names = []
        total_productions = []
        
        for santral_name, df in santral_dataframes.items():
            santral_names.append(santral_name)
            total_productions.append(df['Uretim'].sum())
        
        # Pie chart için veri ekle
        chart.add_series({
            'name': 'Toplam Üretim Dağılımı',
            'categories': santral_names,
            'values': total_productions,
            'data_labels': {'percentage': True, 'value': True}
        })
        
        chart.set_title({'name': '2024 Yılı Toplam Üretim Dağılımı'})
        chart.set_size({'width': 500, 'height': 350})
        
        worksheet.insert_chart(position, chart)

if __name__ == "__main__":
    # Test için
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
        chart_generator = ExcelChartGenerator(excel_path)
        chart_generator.create_enhanced_excel_report(santral_dataframes)
