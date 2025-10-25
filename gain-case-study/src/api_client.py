"""
Şeffaflık Platformu API Client
Bu modül TGT oluşturma ve API istekleri için kullanılır.
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys
import os

# Config dosyasını import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from config.credentials import USERNAME, PASSWORD, TGT_URL, ENDPOINTS
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location("credentials", 
                                                  os.path.join(os.path.dirname(__file__), '..', 'config', 'credentials.py'))
    credentials = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(credentials)
    USERNAME = credentials.USERNAME
    PASSWORD = credentials.PASSWORD
    TGT_URL = credentials.TGT_URL
    ENDPOINTS = credentials.ENDPOINTS

class SeffaflikAPIClient:
    def __init__(self):
        self.username = USERNAME
        self.password = PASSWORD
        self.tgt_url = TGT_URL
        self.endpoints = ENDPOINTS
        self.tgt = None
        self.tgt_created_time = None
        
        if not self.username or not self.password:
            raise ValueError("Kullanıcı adı ve şifre config/credentials.py dosyasında tanımlanmalı!")
    
    def create_tgt(self):
        """TGT (Ticket Granting Ticket) oluştur"""
        print("TGT oluşturuluyor...")
        
        headers = {
            "Accept": "text/plain", 
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        body = {
            "username": self.username,
            "password": self.password,
        }
        
        try:
            response = requests.post(self.tgt_url, data=body, headers=headers)
            response.raise_for_status()
            
            self.tgt = response.text.strip()
            self.tgt_created_time = datetime.now()
            
            print(f"TGT başarıyla oluşturuldu: {self.tgt[:50]}...")
            return self.tgt
            
        except requests.exceptions.RequestException as e:
            print(f"TGT oluşturma hatası: {e}")
            raise
    
    def is_tgt_valid(self):
        """TGT geçerliliğini kontrol et - 2 saat süreli"""
        if not self.tgt or not self.tgt_created_time:
            return False
        
        elapsed = datetime.now() - self.tgt_created_time
        return elapsed.total_seconds() < 7200
    
    def get_valid_tgt(self):
        """Geçerli TGT döndür, gerekirse yenile"""
        if not self.is_tgt_valid():
            self.create_tgt()
        return self.tgt
    
    def make_api_request(self, endpoint_name, start_date, end_date, **kwargs):
        """
        API isteği yap
        
        Args:
            endpoint_name: 'PTF', 'SMF', 'KGUP', 'URETIM'
            start_date: Başlangıç tarihi (string format: "2024-01-01T00:00:00+03:00")
            end_date: Bitiş tarihi (string format: "2024-01-31T00:00:00+03:00")
            **kwargs: Ek parametreler (organizationId, uevcbId, powerPlantId vs.)
        """
        
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Geçersiz endpoint: {endpoint_name}")
        
        url = self.endpoints[endpoint_name]
        tgt = self.get_valid_tgt()
        
        headers = {
            "TGT": tgt,
            "Accept-Language": "en",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        body = {
            "startDate": start_date,
            "endDate": end_date,
        }
        
        if endpoint_name == "KGUP":
            body.update({
                "organizationId": kwargs.get("organizationId"),
                "uevcbId": kwargs.get("uevcbId"),
                "region": "TR1"
            })
        elif endpoint_name == "URETIM":
            body["powerPlantId"] = kwargs.get("powerPlantId")
        
        print(f"{endpoint_name} verisi çekiliyor: {start_date} - {end_date}")
        
        try:
            response = requests.post(url=url, headers=headers, json=body)
            response.raise_for_status()
            
            data = response.json()
            print(f"{endpoint_name} verisi başarıyla çekildi: {len(data.get('items', []))} kayıt")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"{endpoint_name} API hatası: {e}")
            if hasattr(e.response, 'text'):
                print(f"Hata detayı: {e.response.text}")
            raise
    
    def test_connection(self):
        """API bağlantısını test et"""
        print("API bağlantısı test ediliyor...")
        
        try:
            self.create_tgt()
            
            test_start = "2024-01-01T00:00:00+03:00"
            test_end = "2024-01-01T23:59:59+03:00"
            
            result = self.make_api_request("PTF", test_start, test_end)
            
            print("API bağlantısı başarılı!")
            print(f"Test verisi: {len(result.get('items', []))} PTF kaydı çekildi")
            
            return True
            
        except Exception as e:
            print(f"API bağlantı testi başarısız: {e}")
            return False

if __name__ == "__main__":
    # Test için
    client = SeffaflikAPIClient()
    client.test_connection()
