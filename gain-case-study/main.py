#!/usr/bin/env python3
"""
Gain Enerji Case Study - Ana Çalıştırma Scripti
2024 yılı elektrik piyasası verilerini çeker ve analiz eder.
"""

import sys
import os
from datetime import datetime

# src klasörünü path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api_client import SeffaflikAPIClient
from src.data_collector import DataCollector
from src.data_processor import DataProcessor

def print_banner():
    """Başlık yazdır"""
    print("="*60)
    print("GAIN ENERJİ CASE STUDY 2025")
    print("Türkiye Elektrik Piyasası Şeffaflık Platformu Analizi")
    print("Analiz Dönemi: 2024 Yılı")
    print("="*60)

def check_credentials():
    """Kimlik bilgilerini kontrol et"""
    try:
        from config.credentials import USERNAME, PASSWORD
        
        if not USERNAME or not PASSWORD:
            print("HATA: Kimlik bilgileri eksik!")
            print("Lütfen config/credentials.py dosyasına kullanıcı adı ve şifrenizi girin.")
            print("Kayıt: https://kayit.epias.com.tr/epias-transparency-platform-registration-form")
            return False
        
        print("Kimlik bilgileri bulundu")
        return True
        
    except ImportError:
        print("HATA: config/credentials.py dosyası bulunamadı!")
        return False

def main():
    """Ana fonksiyon"""
    print_banner()
    
    # Kimlik bilgilerini kontrol et
    if not check_credentials():
        return
    
    print("Case Study başlatılıyor...")
    print(f"Başlangıç zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. API Bağlantısını Test Et
        print("\n" + "="*50)
        print("1. API BAĞLANTI TESTİ")
        print("="*50)
        
        client = SeffaflikAPIClient()
        if not client.test_connection():
            print("API bağlantısı başarısız. İşlem durduruluyor.")
            return
        
        # 2. Veri Çekme İşlemi
        print("\n" + "="*50)
        print("2. VERİ ÇEKME İŞLEMİ")
        print("="*50)
        
        print("UYARI: Bu işlem 30-60 dakika sürebilir!")
        print("2024 yılı boyunca 4 santral için tüm veriler çekilecek:")
        print("   - PTF (Piyasa Takas Fiyatı)")
        print("   - SMF (Sistem Marjinal Fiyatı)")
        print("   - KGÜP (Kesinleşmiş Günlük Üretim Programı)")
        print("   - Gerçek Üretim Verileri")
        
        response = input("\nVeri çekme işlemini başlatmak istiyor musunuz? (y/n): ")
        
        if response.lower() == 'y':
            collector = DataCollector()
            collector.collect_all_data()
        else:
            print("Veri çekme atlandı. Mevcut verilerle devam ediliyor...")
        
        # 3. Veri İşleme ve Analiz
        print("\n" + "="*50)
        print("3. VERİ İŞLEME VE ANALİZ")
        print("="*50)
        
        processor = DataProcessor()
        excel_file = processor.create_excel_report()
        
        # 4. Sonuçlar
        print("\n" + "="*50)
        print("4. SONUÇLAR")
        print("="*50)
        
        if excel_file:
            print("Case Study başarıyla tamamlandı!")
            print(f"Excel Raporu: {excel_file}")
            print(f"Ham Veriler: data/raw/")
            print(f"İşlenmiş Veriler: data/processed/")
            
            print("\nRapor İçeriği:")
            print("   - Santral_1: MASLAKTEPE RES analizi")
            print("   - Santral_2: EBER RES analizi") 
            print("   - Santral_3: YANBOLU HES analizi")
            print("   - Santral_4: MELİKOM HES analizi")
            print("   - Karşılaştırma: Santraller arası analiz")
            
        else:
            print("Rapor oluşturulamadı!")
            print("Lütfen veri çekme işleminin başarılı olduğundan emin olun.")
        
        print(f"\nBitiş zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\nİşlem kullanıcı tarafından durduruldu!")
        
    except Exception as e:
        print(f"\nBeklenmeyen hata: {e}")
        print("Lütfen hata detaylarını kontrol edin ve tekrar deneyin.")

if __name__ == "__main__":
    main()
