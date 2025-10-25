"""
Basit Karşılaştırmalı Excel Oluşturucu
Sadece tablo - grafik yok
"""

import pandas as pd
import xlsxwriter
import os
from datetime import datetime
import numpy as np

class SimpleComparisonExcel:
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'excel_reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def create_simple_comparison_excel(self, santral1_name, santral1_data, santral2_name, santral2_data):
        """Basit karşılaştırmalı Excel oluştur - sadece tablo"""
        
        # Dosya adı
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = os.path.join(
            self.reports_dir, 
            f'Karsilastirma_{santral1_name.replace(" ", "_")}_vs_{santral2_name.replace(" ", "_")}_{timestamp}.xlsx'
        )
        
        print(f"Excel oluşturuluyor: {excel_path}")
        
        # Workbook oluştur
        workbook = xlsxwriter.Workbook(excel_path)
        
        # Formatlar
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'bg_color': '#366092',
            'font_color': 'white',
            'border': 1,
            'text_wrap': True,
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
        
        # Santral 1 detay sheet'i
        self.create_santral_detail_sheet(
            workbook, santral1_name, santral1_data, 'Santral_1',
            header_format, number_format, currency_format
        )
        
        # Santral 2 detay sheet'i
        self.create_santral_detail_sheet(
            workbook, santral2_name, santral2_data, 'Santral_2',
            header_format, number_format, currency_format
        )
        
        # Karşılaştırma sheet'i oluştur
        self.create_comparison_table(
            workbook, santral1_name, santral1_data, santral2_name, santral2_data,
            header_format, number_format, currency_format
        )
        
        workbook.close()
        print(f"Excel oluşturuldu: {excel_path}")
        return excel_path
    
    def create_santral_detail_sheet(self, workbook, santral_name, df, sheet_name,
                                  header_format, number_format, currency_format):
        """Santral detay sheet'i oluştur - tüm saatlik veriler"""
        
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Başlık
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#D9E2F3',
            'border': 1,
            'align': 'center'
        })
        worksheet.merge_range('A1:P1', santral_name, title_format)
        
        # Sütun başlıkları
        headers = [
            'Tarih', 'Ay', 'Saat', 'PTF', 'SMF', 
            'Pozitif Den. Fiyatı', 'Negatif Den. Fiyatı',
            'KGÜP', 'Üretim', 'Dengesizlik',
            'GÖP Geliri', 'Dengesizlik Tutarı', 'Toplam Gelir', 'Birim Gelir',
            'Dengesizlik Maliyeti', 'Birim Deng. Maliyeti'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(1, col, header, header_format)
        
        # Veri sütunlarını eşleştir
        data_columns = [
            'tarih', 'ay', 'saat', 'PTF', 'SMF',
            'pozitif_dengesizlik_fiyati', 'negatif_dengesizlik_fiyati',
            'KGUP', 'Uretim', 'dengesizlik',
            'gop_geliri', 'dengesizlik_tutari', 'toplam_gelir', 'birim_gelir',
            'dengesizlik_maliyeti', 'birim_dengesizlik_maliyeti'
        ]
        
        # TÜM VERİLERİ YAZ - HİÇBİR SINIR YOK
        print(f"   {santral_name}: {len(df):,} satır yazılıyor...")
        
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy hh:mm',
            'border': 1
        })
        
        for row_idx, (_, row_data) in enumerate(df.iterrows(), 2):
            for col_idx, col_name in enumerate(data_columns):
                if col_name in df.columns:
                    value = row_data[col_name]
                    
                    if pd.isna(value):
                        worksheet.write(row_idx, col_idx, '', number_format)
                    elif col_name == 'tarih':
                        worksheet.write(row_idx, col_idx, value, date_format)
                    elif col_name in ['ay', 'saat']:
                        worksheet.write(row_idx, col_idx, int(value) if not pd.isna(value) else '', number_format)
                    elif 'gelir' in col_name or 'maliyet' in col_name or 'tutar' in col_name:
                        worksheet.write(row_idx, col_idx, float(value) if not pd.isna(value) else 0, currency_format)
                    else:
                        worksheet.write(row_idx, col_idx, float(value) if not pd.isna(value) else 0, number_format)
        
        print(f"   {santral_name}: {len(df):,} satır tamamlandı")
        
        # Sütun genişliklerini ayarla
        worksheet.set_column('A:A', 16)  # Tarih
        worksheet.set_column('B:C', 8)   # Ay, Saat
        worksheet.set_column('D:G', 12)  # Fiyatlar
        worksheet.set_column('H:J', 15)  # Üretim verileri
        worksheet.set_column('K:P', 18)  # Gelir verileri
        
        # Freeze panes
        worksheet.freeze_panes(2, 1)
    
    def create_comparison_table(self, workbook, santral1_name, santral1_data, 
                              santral2_name, santral2_data, 
                              header_format, number_format, currency_format):
        """Karşılaştırma tablosu oluştur"""
        
        worksheet = workbook.add_worksheet('Karşılaştırma')
        
        # Santral 1 başlığı (A2)
        santral1_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#FF6B6B',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        worksheet.write('A2', 'Santral 1', santral1_format)
        
        # Başlıklar (3. satır)
        headers = [
            'Ay', 'Gerçekleşen Üretim (MWh)', 'Dengesizlik Miktarı (MWh)', 
            'GÖP Geliri (TL)', 'Dengesizlik Tutarı (TL)', 'Toplam Gelir (TL)', 
            'Birim Gelir (TL/MWh)', 'Dengesizlik Maliyeti (TL)', 'Birim Deng Mal. (TL/MWh)'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)
        
        # Santral 1 aylık verileri
        monthly_1 = santral1_data.groupby('ay').agg({
            'Uretim': 'sum',
            'dengesizlik': 'sum', 
            'gop_geliri': 'sum',
            'dengesizlik_tutari': 'sum',
            'toplam_gelir': 'sum',
            'dengesizlik_maliyeti': 'sum'
        }).reset_index()
        
        monthly_1['birim_gelir'] = monthly_1['toplam_gelir'] / monthly_1['Uretim']
        monthly_1['birim_deng_mal'] = monthly_1['dengesizlik_maliyeti'] / monthly_1['Uretim']
        
        # Santral 1 verilerini yaz (4-15. satırlar)
        for i in range(12):
            ay = i + 1
            row_idx = 3 + i
            
            if ay in monthly_1['ay'].values:
                row_data = monthly_1[monthly_1['ay'] == ay].iloc[0]
                data_values = [
                    ay, row_data['Uretim'], row_data['dengesizlik'],
                    row_data['gop_geliri'], row_data['dengesizlik_tutari'], row_data['toplam_gelir'],
                    row_data['birim_gelir'], row_data['dengesizlik_maliyeti'], row_data['birim_deng_mal']
                ]
            else:
                data_values = [ay, 0, 0, 0, 0, 0, 0, 0, 0]
            
            for col_idx, value in enumerate(data_values):
                if col_idx == 0:  # Ay
                    worksheet.write(row_idx, col_idx, int(value), number_format)
                elif col_idx in [3, 4, 5, 7]:  # TL değerleri
                    worksheet.write(row_idx, col_idx, float(value), currency_format)
                else:
                    worksheet.write(row_idx, col_idx, float(value), number_format)
        
        # Santral 1 Toplam
        worksheet.write(15, 0, 'Toplam', workbook.add_format({'bold': True, 'border': 1}))
        total_1 = monthly_1.sum()
        total_values_1 = [
            '', total_1['Uretim'], total_1['dengesizlik'], total_1['gop_geliri'],
            total_1['dengesizlik_tutari'], total_1['toplam_gelir'], 
            total_1['toplam_gelir'] / total_1['Uretim'] if total_1['Uretim'] > 0 else 0,
            total_1['dengesizlik_maliyeti'], 
            total_1['dengesizlik_maliyeti'] / total_1['Uretim'] if total_1['Uretim'] > 0 else 0
        ]
        
        for col_idx, value in enumerate(total_values_1[1:], 1):
            if col_idx in [3, 4, 5, 7]:  # TL değerleri (GÖP, Dengesizlik Tutarı, Toplam Gelir, Dengesizlik Maliyeti)
                worksheet.write(15, col_idx, float(value), currency_format)
            else:
                worksheet.write(15, col_idx, float(value), number_format)
        
        # Santral 2 başlığı (A18)
        santral2_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#4ECDC4',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        worksheet.write('A18', 'Santral 2', santral2_format)
        
        # Santral 2 başlıkları (19. satır)
        for col, header in enumerate(headers):
            worksheet.write(18, col, header, header_format)
        
        # Santral 2 aylık verileri
        monthly_2 = santral2_data.groupby('ay').agg({
            'Uretim': 'sum',
            'dengesizlik': 'sum',
            'gop_geliri': 'sum', 
            'dengesizlik_tutari': 'sum',
            'toplam_gelir': 'sum',
            'dengesizlik_maliyeti': 'sum'
        }).reset_index()
        
        monthly_2['birim_gelir'] = monthly_2['toplam_gelir'] / monthly_2['Uretim']
        monthly_2['birim_deng_mal'] = monthly_2['dengesizlik_maliyeti'] / monthly_2['Uretim']
        
        # Santral 2 verilerini yaz (20-31. satırlar)
        for i in range(12):
            ay = i + 1
            row_idx = 19 + i
            
            if ay in monthly_2['ay'].values:
                row_data = monthly_2[monthly_2['ay'] == ay].iloc[0]
                data_values = [
                    ay, row_data['Uretim'], row_data['dengesizlik'],
                    row_data['gop_geliri'], row_data['dengesizlik_tutari'], row_data['toplam_gelir'],
                    row_data['birim_gelir'], row_data['dengesizlik_maliyeti'], row_data['birim_deng_mal']
                ]
            else:
                data_values = [ay, 0, 0, 0, 0, 0, 0, 0, 0]
            
            for col_idx, value in enumerate(data_values):
                if col_idx == 0:  # Ay
                    worksheet.write(row_idx, col_idx, int(value), number_format)
                elif col_idx in [3, 4, 5, 7]:  # TL değerleri
                    worksheet.write(row_idx, col_idx, float(value), currency_format)
                else:
                    worksheet.write(row_idx, col_idx, float(value), number_format)
        
        # Santral 2 Toplam
        worksheet.write(31, 0, 'Toplam', workbook.add_format({'bold': True, 'border': 1}))
        total_2 = monthly_2.sum()
        total_values_2 = [
            '', total_2['Uretim'], total_2['dengesizlik'], total_2['gop_geliri'],
            total_2['dengesizlik_tutari'], total_2['toplam_gelir'], 
            total_2['toplam_gelir'] / total_2['Uretim'] if total_2['Uretim'] > 0 else 0,
            total_2['dengesizlik_maliyeti'], 
            total_2['dengesizlik_maliyeti'] / total_2['Uretim'] if total_2['Uretim'] > 0 else 0
        ]
        
        for col_idx, value in enumerate(total_values_2[1:], 1):
            if col_idx in [3, 4, 5, 7]:  # TL değerleri (GÖP, Dengesizlik Tutarı, Toplam Gelir, Dengesizlik Maliyeti)
                worksheet.write(31, col_idx, float(value), currency_format)
            else:
                worksheet.write(31, col_idx, float(value), number_format)
        
        # Sütun genişlikleri
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:C', 18)
        worksheet.set_column('D:F', 15)
        worksheet.set_column('G:I', 18)
        
        # Freeze panes
        worksheet.freeze_panes(3, 1)

if __name__ == "__main__":
    # Test
    import sys
    sys.path.append('.')
    from src.data_processor import DataProcessor
    
    processor = DataProcessor()
    santral1_data = processor.create_santral_analysis("MASLAKTEPE RES")
    santral2_data = processor.create_santral_analysis("EBER RES")
    
    if not santral1_data.empty and not santral2_data.empty:
        excel_gen = SimpleComparisonExcel()
        excel_path = excel_gen.create_simple_comparison_excel(
            "MASLAKTEPE RES", santral1_data,
            "EBER RES", santral2_data
        )
        print(f"Test Excel oluşturuldu: {excel_path}")
    else:
        print("Test verileri bulunamadı!")
