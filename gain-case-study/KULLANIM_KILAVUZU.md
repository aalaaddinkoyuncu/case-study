# 🚀 Gain Enerji Case Study - Kullanım Kılavuzu

Author: alaaddinkoyuncu

## 📋 Hızlı Başlangıç

### 1. Ön Gereksinimler
```bash
# Python 3.8+ gerekli
python3 --version

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 2. Şeffaflık Platformu Kaydı
1. **Kayıt Ol**: https://kayit.epias.com.tr/epias-transparency-platform-registration-form
2. Kullanıcı adı ve şifre belirle
3. `config/credentials.py` dosyasını düzenle:

```python
USERNAME = "your_username"  # Kullanıcı adınız
PASSWORD = "your_password"  # Şifreniz
```

### 3. Projeyi Çalıştır
```bash
# Ana scripti çalıştır
python3 main.py

# Veya adım adım:
# 1. Sadece API test
python3 src/api_client.py

# 2. Sadece veri çekme
python3 src/data_collector.py

# 3. Sadece analiz
python3 src/data_processor.py
```

## 📊 Proje Yapısı

```
gain-case-study/
├── main.py                 # Ana çalıştırma scripti
├── README.md              # Proje dokümantasyonu
├── KULLANIM_KILAVUZU.md   # Bu dosya
├── requirements.txt       # Python bağımlılıkları
├── venv/                  # Virtual environment
├── config/
│   └── credentials.py     # API kimlik bilgileri
├── src/
│   ├── api_client.py      # API bağlantı modülü
│   ├── data_collector.py  # Veri çekme modülü
│   └── data_processor.py  # Veri işleme ve analiz
├── data/
│   ├── raw/              # Ham API verileri (JSON)
│   └── processed/        # İşlenmiş veriler
├── reports/
│   ├── excel_reports/    # Excel raporları
│   └── visualizations/   # Grafikler (gelecekte)
└── notebooks/            # Jupyter notebook'lar (opsiyonel)
```

## 🔧 Modül Detayları

### 1. API Client (`src/api_client.py`)
- **TGT oluşturma**: 2 saatlik geçerlilik
- **API istekleri**: PTF, SMF, KGÜP, Üretim
- **Hata yönetimi**: Otomatik retry ve logging

**Kullanım:**
```python
from src.api_client import SeffaflikAPIClient

client = SeffaflikAPIClient()
client.test_connection()

# PTF verisi çek
data = client.make_api_request(
    "PTF", 
    "2024-01-01T00:00:00+03:00", 
    "2024-01-31T23:59:59+03:00"
)
```

### 2. Data Collector (`src/data_collector.py`)
- **Batch processing**: API kısıtlamaları için tarih aralığı böler
- **Rate limiting**: İstekler arası bekleme
- **JSON kayıt**: Ham verileri data/raw/ klasörüne kaydeder

**Çekilen Veriler:**
- `ptf_2024.json` - Piyasa Takas Fiyatı
- `smf_2024.json` - Sistem Marjinal Fiyatı
- `kgup_SANTRAL_ADI_2024.json` - Her santral için KGÜP
- `uretim_SANTRAL_ADI_2024.json` - Her santral için üretim

### 3. Data Processor (`src/data_processor.py`)
- **Veri temizleme**: Tarih/saat normalizasyonu
- **Veri birleştirme**: PTF, SMF, KGÜP, Üretim
- **Hesaplamalar**: Dengesizlik, gelir, maliyet
- **Excel çıktısı**: Santral bazında sheet'ler

## 📈 Analiz Detayları

### Hesaplanan Metrikler

1. **Dengesizlik Miktarı**
   ```
   Dengesizlik = Gerçek Üretim - KGÜP
   ```

2. **Gün Öncesi Piyasa Geliri**
   ```
   GÖP Geliri = KGÜP × PTF
   ```

3. **Dengesizlik Tutarı**
   ```
   Dengesizlik Tutarı = Dengesizlik × SMF
   ```

4. **Toplam Gelir**
   ```
   Toplam Gelir = GÖP Geliri + Dengesizlik Tutarı
   ```

5. **Birim Gelir**
   ```
   Birim Gelir = Toplam Gelir / Gerçek Üretim
   ```

### Excel Rapor Formatı

**Santral Sheet'leri:**
- Tarih, Ay, Saat
- PTF, SMF
- KGÜP, Gerçek Üretim, Dengesizlik
- Gelir hesaplamaları
- Maliyet analizleri

**Karşılaştırma Sheet'i:**
- Aylık özet veriler
- Santral performans karşılaştırması
- Birim gelir ve maliyet metrikleri

## ⚠️ Önemli Notlar

### API Kısıtlamaları
- **TGT Süresi**: 2 saat (otomatik yenilenir)
- **Rate Limiting**: İstekler arası 1-2 saniye bekleme
- **Tarih Aralığı**: Bazı endpoint'ler için maksimum 30 gün

### Veri Kalitesi
- **Eksik Veriler**: API'den gelen eksik değerler NaN olarak işlenir
- **Tarih Formatı**: Tüm tarihler UTC+3 saat diliminde
- **Santral Kodları**: pp_list.json dosyasından alınır

### Performans
- **Veri Çekme**: ~30-60 dakika (tüm yıl için)
- **İşleme**: ~2-5 dakika
- **Dosya Boyutu**: ~50-100 MB (tüm ham veriler)

## 🐛 Sorun Giderme

### Yaygın Hatalar

1. **"ModuleNotFoundError: No module named 'pandas'"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"TGT oluşturma hatası"**
   - Kullanıcı adı/şifre kontrol et
   - İnternet bağlantısını kontrol et
   - Şeffaflık Platformu erişilebilirliğini kontrol et

3. **"API hatası: 401 Unauthorized"**
   - TGT süresi dolmuş olabilir (otomatik yenilenir)
   - Kimlik bilgilerini kontrol et

4. **"Dosya bulunamadı" hatası**
   - Önce veri çekme işlemini tamamla
   - data/raw/ klasörünü kontrol et

### Debug Modu

```python
# API isteklerini detaylı görmek için
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Destek

Sorun yaşadığınızda:
1. Hata mesajını tam olarak kaydedin
2. Hangi adımda hata aldığınızı belirtin
3. `config/credentials.py` dosyasının doğru doldurulduğundan emin olun
4. İnternet bağlantınızı kontrol edin

## 🎯 Sonraki Adımlar

Projeyi geliştirmek için:
- [ ] Görselleştirme modülü ekle (matplotlib/seaborn)
- [ ] Web dashboard oluştur (Streamlit/Dash)
- [ ] Otomatik raporlama (günlük/haftalık)
- [ ] Makine öğrenmesi tahmin modelleri
- [ ] Real-time veri akışı
