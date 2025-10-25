"""
4 Santral için Tüm Kombinasyonları Excel Oluştur
6 farklı karşılaştırmalı Excel dosyası oluşturur
"""

import sys
import os
sys.path.append('src')

from src.data_processor import DataProcessor
from src.simple_comparison_excel import SimpleComparisonExcel
from itertools import combinations

def create_all_combination_excels():
    """Tüm santral kombinasyonları için Excel oluştur"""
    
    # Santraller
    santraller = [
        "MASLAKTEPE RES",
        "EBER RES", 
        "YANBOLU HES",
        "MELİKOM HES"
    ]
    
    print("🚀 4 Santral için Tüm Kombinasyonları Oluşturuluyor...")
    print(f"📊 Toplam kombinasyon: {len(list(combinations(santraller, 2)))} adet")
    print("=" * 60)
    
    # Veri işleyici
    processor = DataProcessor()
    excel_gen = SimpleComparisonExcel()
    
    # Tüm santral verilerini önceden yükle
    print("📥 Santral verileri yükleniyor...")
    santral_data = {}
    
    for santral in santraller:
        print(f"   {santral} yükleniyor...")
        df = processor.create_santral_analysis(santral)
        if not df.empty:
            santral_data[santral] = df
            print(f"   ✅ {santral}: {len(df):,} kayıt")
        else:
            print(f"   ❌ {santral}: Veri bulunamadı!")
    
    print("\n" + "=" * 60)
    print("📊 Excel dosyaları oluşturuluyor...")
    
    # Tüm kombinasyonları oluştur
    created_files = []
    
    for i, (santral1, santral2) in enumerate(combinations(santraller, 2), 1):
        print(f"\n{i}/6: {santral1} vs {santral2}")
        
        if santral1 in santral_data and santral2 in santral_data:
            try:
                excel_path = excel_gen.create_simple_comparison_excel(
                    santral1, santral_data[santral1],
                    santral2, santral_data[santral2]
                )
                created_files.append(excel_path)
                print(f"   ✅ Excel oluşturuldu: {os.path.basename(excel_path)}")
                
            except Exception as e:
                print(f"   ❌ Hata: {e}")
        else:
            print(f"   ❌ Veri eksik: {santral1} veya {santral2}")
    
    # Özet
    print("\n" + "=" * 60)
    print("🎉 TÜM KOMBİNASYONLAR TAMAMLANDI!")
    print(f"📁 Oluşturulan dosya sayısı: {len(created_files)}")
    
    print("\n📋 Oluşturulan Excel Dosyaları:")
    for i, file_path in enumerate(created_files, 1):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024*1024)  # MB
        print(f"   {i}. {file_name} ({file_size:.1f} MB)")
    
    return created_files

if __name__ == "__main__":
    created_files = create_all_combination_excels()
    print(f"\n🚀 {len(created_files)} Excel dosyası hazır!")
