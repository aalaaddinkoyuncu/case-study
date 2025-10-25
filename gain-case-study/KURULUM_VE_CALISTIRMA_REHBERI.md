# Gain Enerji Case Study - Kurulum ve Çalıştırma Rehberi

## Sistem Gereksinimleri

- **İşletim Sistemi**: Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **Python**: 3.8 veya üzeri

## Adım 1: Python Kurulumu

### Windows için:
1. https://python.org adresinden Python 3.8+ indirin
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
3. Komut istemini açın ve `python --version` yazarak kontrol edin

### macOS için:
```bash
# Homebrew ile (önerilen)
brew install python

# Veya python.org'dan indirin
```

### Linux için:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## Adım 2: Proje Dosyalarını İndirme

1. Proje klasörünü bilgisayarınıza kopyalayın
2. Terminal/Komut İstemi'ni açın
3. Proje klasörüne gidin:
```bash
cd /path/to/gain-case-study
```

## Adım 3: Sanal Ortam Oluşturma

```bash
# Sanal ortam oluştur
python -m venv venv

# Sanal ortamı aktifleştir
# Windows için:
venv\Scripts\activate

# macOS/Linux için:
source venv/bin/activate
```

**Not**: Sanal ortam aktifleştiğinde terminal başında `(venv)` yazısını göreceksiniz.

## Adım 4: Gerekli Kütüphaneleri Kurma

```bash
pip install -r requirements.txt
```

**Kurulacak kütüphaneler:**
- pandas (veri işleme)
- numpy (matematiksel hesaplamalar)
- requests (API bağlantısı)
- streamlit (web arayüzü)
- plotly (grafikler)
- xlsxwriter (Excel raporları)
- openpyxl (Excel okuma/yazma)

## Adım 5: Kimlik Bilgilerini Ayarlama

### 5.1 Şeffaflık Platformu Hesabı
1. https://kayit.epias.com.tr/epias-transparency-platform-registration-form adresine gidin
2. Ücretsiz hesap oluşturun
3. Email doğrulamasını tamamlayın

### 5.2 Kimlik Bilgilerini Girme
1. `config/credentials.py` dosyasını açın
2. Aşağıdaki bilgileri girin:

```python
# Şeffaflık Platformu kimlik bilgileri
USERNAME = "sizin_email_adresiniz@domain.com"
PASSWORD = "sizin_sifreniz"

# API URL'leri (değiştirmeyin)
TGT_URL = "https://giris.epias.com.tr/cas/v1/tickets"
ENDPOINTS = {
    "PTF": "https://seffaflik.epias.com.tr/electricity-service/v1/markets/dam/data/mcp",
    "SMF": "https://seffaflik.epias.com.tr/electricity-service/v1/markets/bpm/data/system-marginal-price",
    "KGUP": "https://seffaflik.epias.com.tr/electricity-service/v1/generation/data/dpp",
    "URETIM": "https://seffaflik.epias.com.tr/electricity-service/v1/generation/data/realtime-generation"
}

# Santral bilgileri (değiştirmeyin)
SANTRALLER = [
    {
        "powerPlantName": "MASLAKTEPE RES",
        "powerPlantId": 2346,
        "organizationId": 12717,
        "uevcbId": 12717
    },
    # ... diğer santraller
]
```

## Adım 6: Projeyi Çalıştırma

### Seçenek 1: Komple Analiz (Önerilen)

```bash
python main.py
```

**Bu komut:**
1. API bağlantısını test eder
2. 2024 yılı verilerini çeker (30-60 dakika sürer)
3. Verileri işler ve analiz eder
4. Excel raporlarını oluşturur

### Seçenek 2: Sadece Web Arayüzü

Eğer veriler zaten çekilmişse:

```bash
streamlit run streamlit_app.py
```

Tarayıcınızda otomatik olarak açılacak adres: http://localhost:8501

### Seçenek 3: Sadece Veri Çekme

```bash
python src/data_collector.py
```

### Seçenek 4: Sadece Analiz ve Rapor

```bash
python src/data_processor.py
```

## Adım 7: Çıktıları İnceleme

### Excel Raporları
Raporlar `reports/excel_reports/` klasöründe oluşur:

1. **1_Gain_Enerji_TUM_VERILER_2024.xlsx**
   - Tüm 8,784 saatlik veri
   - 4 santral için ayrı sheet'ler
   - Özet dashboard

2. **2_Gain_Enerji_Grafikli_Ozet_2024.xlsx**
   - Grafikler + özet veriler
   - Plan vs Gerçek üretim grafikleri
   - Aylık analiz tabloları

3. **3_Gain_Enerji_SADECE_GRAFIKLER_2024.xlsx**
   - Minimal veri + maksimum grafik
   - Sunum amaçlı

### Web Arayüzü
- Santral seçimi ve karşılaştırma
- İnteraktif grafikler
- Excel indirme butonları

### Ham Veriler
`data/raw/` klasöründe JSON formatında:
- `ptf_2024.json` (Piyasa Takas Fiyatı)
- `smf_2024.json` (Sistem Marjinal Fiyatı)
- `kgup_SANTRAL_ADI_2024.json` (Plan verileri)
- `uretim_SANTRAL_ADI_2024.json` (Gerçek üretim)

## Sorun Giderme

### Yaygın Hatalar ve Çözümleri

#### 1. "ModuleNotFoundError"
```bash
# Çözüm: Sanal ortamın aktif olduğundan emin olun
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Kütüphaneleri tekrar kurun
pip install -r requirements.txt
```

#### 2. "401 Unauthorized" API Hatası
```bash
# Çözüm: Kimlik bilgilerini kontrol edin
# config/credentials.py dosyasında:
# - Email adresinin doğru olduğundan emin olun
# - Şifrenin doğru olduğundan emin olun
# - Şeffaflık Platformu'na web'den giriş yapabildiğinizi test edin
```

#### 3. "Connection Error"
```bash
# Çözüm: İnternet bağlantısını kontrol edin
# Firewall/proxy ayarlarını kontrol edin
```

#### 4. "Permission Denied" Hatası
```bash
# Windows için: Komut İstemi'ni "Yönetici olarak çalıştır"
# macOS/Linux için: sudo kullanmayın, kullanıcı yetkilerinizi kontrol edin
```

#### 5. Streamlit Açılmıyor
```bash
# Tarayıcıyı manuel açın ve şu adrese gidin:
http://localhost:8501

# Veya farklı port kullanın:
streamlit run streamlit_app.py --server.port 8502
```


### Veri Güncelleme

Yeni veriler için:
```bash
# Eski verileri silin
rm -rf data/raw/*

# Yeni verileri çekin
python src/data_collector.py
```

Bu rehber, projeyi sıfırdan kurmanız ve çalıştırmanız için gereken tüm adımları içermektedir.
