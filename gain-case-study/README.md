# Gain Enerji Intern Analyst Case Study 2025

Author: alaaddinkoyuncu

## 📋 Proje Açıklaması

Bu case study, Türkiye Elektrik Piyasası Şeffaflık Platformu API'sini kullanarak enerji piyasası verilerini çekme, analiz etme ve karşılaştırmalı analiz yapma projesidir.

## 🎯 Ne İsteniyor?

### Ana Hedef
2024 yılı boyunca (01.01.2024 - 31.12.2024) belirli santraller için aşağıdaki verileri çekerek karşılaştırmalı analiz yapmak:

1. **PTF (Piyasa Takas Fiyatı)** - Elektrik piyasasındaki takas fiyatı
2. **SMF (Sistem Marjinal Fiyatı)** - Sistemin marjinal fiyatı
3. **KGÜP (Kesinleşmiş Günlük Üretim Programı)** - Planlanan üretim miktarı
4. **Gerçek Üretim** - Fiili üretim miktarı

### Analiz Edilecek Santraller
```json
1. MASLAKTEPE RES (Rüzgar Enerji Santrali)
2. EBER RES (Rüzgar Enerji Santrali)  
3. YANBOLU HES (Hidroelektrik Santrali)
4. MELİKOM HES (Hidroelektrik Santrali)
```

## 🔧 Teknik Gereksinimler

### 1. Platform Kaydı
- **Kayıt URL**: https://kayit.epias.com.tr/epias-transparency-platform-registration-form
- **Platform URL**: https://seffaflik.epias.com.tr/
- Kullanıcı adı ve şifre gerekli

### 2. API Erişimi
- **TGT (Ticket Granting Ticket)** oluşturulmalı
- TGT geçerlilik süresi: 2 saat
- Her API isteği için TGT header'da gönderilmeli

### 3. Veri Çekme Endpoints

#### PTF (Piyasa Takas Fiyatı)
- **URL**: `https://seffaflik.epias.com.tr/electricity-service/v1/markets/dam/data/mcp`
- **Dönen Veri**: `price` (TL cinsinden PTF)

#### SMF (Sistem Marjinal Fiyatı)
- **URL**: `https://seffaflik.epias.com.tr/electricity-service/v1/markets/bpm/data/system-marginal-price`
- **Dönen Veri**: `systemMarginalPrice` (TL cinsinden SMF)

#### KGÜP (Kesinleşmiş Günlük Üretim Programı)
- **URL**: `https://seffaflik.epias.com.tr/electricity-service/v1/generation/data/dpp-first-version`
- **Dönen Veri**: `toplam` (MW cinsinden planlanan üretim)
- **Gerekli Parametreler**: `organizationId`, `uevcbId`, `region: "TR1"`

#### Gerçek Üretim
- **URL**: `https://seffaflik.epias.com.tr/electricity-service/v1/generation/data/realtime-generation`
- **Dönen Veri**: `total` (MW cinsinden gerçek üretim)
- **Gerekli Parametre**: `powerPlantId`

## 📊 Yapılacaklar Listesi

### Faz 1: Altyapı Kurulumu
- [ ] Şeffaflık Platformuna kayıt ol
- [ ] API bağlantısı için Python environment kurulumu
- [ ] Gerekli kütüphaneleri yükle (`requests`, `pandas`, `matplotlib`, `openpyxl`)
- [ ] TGT oluşturma fonksiyonu geliştir

### Faz 2: Veri Çekme Modülleri
- [ ] PTF verisi çekme fonksiyonu
- [ ] SMF verisi çekme fonksiyonu  
- [ ] KGÜP verisi çekme fonksiyonu (4 santral için)
- [ ] Gerçek üretim verisi çekme fonksiyonu (4 santral için)
- [ ] Tarih aralığı kısıtlaması için batch processing implementasyonu

### Faz 3: Veri İşleme
- [ ] Çekilen verileri temizle ve standardize et
- [ ] Tarih/saat formatlarını normalize et
- [ ] Eksik veri kontrolü ve handling
- [ ] Veriyi pandas DataFrame'e dönüştür

### Faz 4: Analiz ve Karşılaştırma
- [ ] Santral bazında KGÜP vs Gerçek Üretim karşılaştırması
- [ ] PTF ve SMF trend analizi
- [ ] Santral performans metrikleri hesaplama
- [ ] Kaynak tipi bazında (RES vs HES) karşılaştırma

### Faz 5: Raporlama
- [ ] Excel formatında karşılaştırmalı analiz raporu
- [ ] Görselleştirmeler (grafikler, chartlar)
- [ ] Özet istatistikler ve bulgular
- [ ] Sonuç ve öneriler bölümü

### Faz 6: Dokümantasyon
- [ ] Kod dokümantasyonu
- [ ] API kullanım kılavuzu
- [ ] Sonuçların yorumlanması
- [ ] Gelecek geliştirmeler için öneriler

## 📁 Proje Yapısı

```
gain-case-study/
├── README.md
├── requirements.txt
├── config/
│   ├── credentials.py
│   └── api_endpoints.py
├── src/
│   ├── api_client.py
│   ├── data_collector.py
│   ├── data_processor.py
│   └── analyzer.py
├── data/
│   ├── raw/
│   └── processed/
├── reports/
│   ├── excel_reports/
│   └── visualizations/
└── notebooks/
    └── analysis.ipynb
```

## ⚠️ Önemli Notlar

1. **Tarih Formatı**: Tüm tarih parametreleri `"2024-01-01T00:00:00+03:00"` formatında olmalı
2. **API Kısıtlamaları**: Bazı servislerde tarih aralığı kısıtlaması olabilir, batch processing gerekebilir
3. **TGT Yenileme**: 2 saatte bir TGT yenilenmeli
4. **Veri Kalitesi**: API'den dönen verilerde eksik değerler olabilir, kontrol edilmeli
5. **Rate Limiting**: API isteklerinde rate limiting olabilir, uygun bekleme süreleri eklenmelidir

## 🚀 Başlangıç

1. Şeffaflık Platformuna kayıt olun
2. `requirements.txt` dosyasındaki bağımlılıkları yükleyin
3. `config/credentials.py` dosyasına kullanıcı bilgilerinizi ekleyin
4. `src/api_client.py` ile API bağlantısını test edin
5. Veri çekme işlemlerine başlayın

## 📈 Beklenen Çıktılar

- 2024 yılı boyunca 4 santral için saatlik veri seti
- Excel formatında karşılaştırmalı analiz raporu
- Santral performans değerlendirme raporu
- PTF/SMF trend analizi
- Görsel raporlar ve grafikler
