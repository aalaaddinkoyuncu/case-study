"""
Veri Toplama Modülü
2024 yılı boyunca tüm santraller için PTF, SMF, KGÜP ve Üretim verilerini çeker.
"""

import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os
from api_client import SeffaflikAPIClient
from config.credentials import SANTRALLER

class DataCollector:
    def __init__(self):
        self.client = SeffaflikAPIClient()
        self.santraller = SANTRALLER
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        
        # Data dizinini oluştur
        os.makedirs(self.data_dir, exist_ok=True)
    
    def generate_date_ranges(self, start_date="2024-01-01", end_date="2024-12-31", chunk_days=30):
        """
        Tarih aralığını küçük parçalara böl (API kısıtlamaları için)
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        date_ranges = []
        current = start
        
        while current <= end:
            chunk_end = min(current + timedelta(days=chunk_days-1), end)
            
            start_str = current.strftime("%Y-%m-%dT00:00:00+03:00")
            end_str = chunk_end.strftime("%Y-%m-%dT23:59:59+03:00")
            
            date_ranges.append((start_str, end_str))
            current = chunk_end + timedelta(days=1)
        
        return date_ranges
    
    def collect_ptf_data(self):
        """PTF (Piyasa Takas Fiyatı) verilerini çek"""
        print("\nPTF verileri çekiliyor...")
        
        date_ranges = self.generate_date_ranges()
        all_data = []
        
        for i, (start_date, end_date) in enumerate(date_ranges, 1):
            print(f"PTF Batch {i}/{len(date_ranges)}: {start_date[:10]} - {end_date[:10]}")
            
            try:
                response = self.client.make_api_request("PTF", start_date, end_date)
                
                if 'items' in response:
                    all_data.extend(response['items'])
                
                # API rate limiting için bekle
                time.sleep(1)
                
            except Exception as e:
                print(f"PTF batch {i} hatası: {e}")
                continue
        
        # DataFrame'e dönüştür ve kaydet
        if all_data:
            df = pd.DataFrame(all_data)
            file_path = os.path.join(self.data_dir, 'ptf_2024.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"PTF verileri kaydedildi: {len(all_data)} kayıt - {file_path}")
            return df
        
        return pd.DataFrame()
    
    def collect_smf_data(self):
        """SMF (Sistem Marjinal Fiyatı) verilerini çek"""
        print("\nSMF verileri çekiliyor...")
        
        date_ranges = self.generate_date_ranges()
        all_data = []
        
        for i, (start_date, end_date) in enumerate(date_ranges, 1):
            print(f"SMF Batch {i}/{len(date_ranges)}: {start_date[:10]} - {end_date[:10]}")
            
            try:
                response = self.client.make_api_request("SMF", start_date, end_date)
                
                if 'items' in response:
                    all_data.extend(response['items'])
                
                time.sleep(1)
                
            except Exception as e:
                print(f"SMF batch {i} hatası: {e}")
                continue
        
        if all_data:
            df = pd.DataFrame(all_data)
            file_path = os.path.join(self.data_dir, 'smf_2024.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"SMF verileri kaydedildi: {len(all_data)} kayıt - {file_path}")
            return df
        
        return pd.DataFrame()
    
    def collect_kgup_data(self, santral):
        """Belirli bir santral için KGÜP verilerini çek"""
        santral_name = santral['powerPlantName']
        print(f"\n{santral_name} KGÜP verileri çekiliyor...")
        
        date_ranges = self.generate_date_ranges(chunk_days=15)  # KGÜP için daha küçük batch
        all_data = []
        
        for i, (start_date, end_date) in enumerate(date_ranges, 1):
            print(f"{santral_name} KGÜP Batch {i}/{len(date_ranges)}: {start_date[:10]} - {end_date[:10]}")
            
            try:
                response = self.client.make_api_request(
                    "KGUP", 
                    start_date, 
                    end_date,
                    organizationId=santral['organizationId'],
                    uevcbId=santral['uevcbId']
                )
                
                if 'items' in response:
                    # Santral bilgisini her kayda ekle
                    for item in response['items']:
                        item['santral_name'] = santral_name
                        item['power_plant_id'] = santral['powerPlantId']
                    
                    all_data.extend(response['items'])
                
                time.sleep(2)  # KGÜP için biraz daha uzun bekle
                
            except Exception as e:
                print(f"{santral_name} KGÜP batch {i} hatası: {e}")
                continue
        
        if all_data:
            # Santral adına göre dosya kaydet
            safe_name = santral_name.replace(' ', '_').replace('İ', 'I')
            file_path = os.path.join(self.data_dir, f'kgup_{safe_name}_2024.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"{santral_name} KGÜP verileri kaydedildi: {len(all_data)} kayıt")
            return pd.DataFrame(all_data)
        
        return pd.DataFrame()
    
    def collect_uretim_data(self, santral):
        """Belirli bir santral için Üretim verilerini çek"""
        santral_name = santral['powerPlantName']
        print(f"\n{santral_name} Üretim verileri çekiliyor...")
        
        date_ranges = self.generate_date_ranges(chunk_days=20)
        all_data = []
        
        for i, (start_date, end_date) in enumerate(date_ranges, 1):
            print(f"{santral_name} Üretim Batch {i}/{len(date_ranges)}: {start_date[:10]} - {end_date[:10]}")
            
            try:
                response = self.client.make_api_request(
                    "URETIM", 
                    start_date, 
                    end_date,
                    powerPlantId=santral['powerPlantId']
                )
                
                if 'items' in response:
                    # Santral bilgisini her kayda ekle
                    for item in response['items']:
                        item['santral_name'] = santral_name
                        item['power_plant_id'] = santral['powerPlantId']
                    
                    all_data.extend(response['items'])
                
                time.sleep(1.5)
                
            except Exception as e:
                print(f"{santral_name} Üretim batch {i} hatası: {e}")
                continue
        
        if all_data:
            safe_name = santral_name.replace(' ', '_').replace('İ', 'I')
            file_path = os.path.join(self.data_dir, f'uretim_{safe_name}_2024.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"{santral_name} Üretim verileri kaydedildi: {len(all_data)} kayıt")
            return pd.DataFrame(all_data)
        
        return pd.DataFrame()
    
    def collect_all_data(self):
        """Tüm verileri topla"""
        print("2024 yılı için tüm veriler çekiliyor...")
        print(f"Analiz edilecek santraller: {len(self.santraller)}")
        
        # 1. PTF ve SMF verilerini çek (tüm piyasa için)
        ptf_data = self.collect_ptf_data()
        smf_data = self.collect_smf_data()
        
        # 2. Her santral için KGÜP ve Üretim verilerini çek
        for i, santral in enumerate(self.santraller, 1):
            print(f"\nSantral {i}/{len(self.santraller)}: {santral['powerPlantName']}")
            
            kgup_data = self.collect_kgup_data(santral)
            uretim_data = self.collect_uretim_data(santral)
        
        print("\nTüm veri çekme işlemi tamamlandı!")
        print(f"Veriler şu dizinde: {self.data_dir}")
        
        # Özet bilgi
        files = os.listdir(self.data_dir)
        print(f"Oluşturulan dosyalar: {len(files)}")
        for file in files:
            print(f"  - {file}")

if __name__ == "__main__":
    # Test için
    collector = DataCollector()
    
    # Önce API bağlantısını test et
    if collector.client.test_connection():
        print("UYARI: Bu işlem uzun sürebilir (30-60 dakika)")
        print("Lütfen kullanıcı adı ve şifrenizi config/credentials.py dosyasına girin!")
        
        response = input("\nDevam etmek istiyor musunuz? (y/n): ")
        if response.lower() == 'y':
            collector.collect_all_data()
        else:
            print("İşlem iptal edildi.")
    else:
        print("API bağlantısı başarısız. Lütfen kimlik bilgilerinizi kontrol edin.")
