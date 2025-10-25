# Gain Enerji Case Study - Teknik Doküman

Author: alaaddinkoyuncu

## Proje Genel Bakış

Bu proje, Türkiye Elektrik Piyasası Şeffaflık Platformu'ndan 2024 yılı verilerini çekerek, 4 farklı santralın (2 RES + 2 HES) performans analizini yapan kapsamlı bir veri analiz sistemidir.

## Kullanılan Teknolojiler ve Amaçları

### 1. Python Programlama Dili
**Neden Seçildi:** Veri analizi ve API entegrasyonu için en uygun dil
**Kullanım Alanları:** Tüm proje Python ile geliştirildi

### 2. Kütüphaneler ve Amaçları

#### **Veri İşleme Kütüphaneleri**
- **pandas**: Excel benzeri veri tabloları oluşturmak ve işlemek için
- **numpy**: Matematiksel hesaplamalar (dengesizlik fiyatları, gelir hesaplamaları)
- **json**: API'den gelen verileri okumak ve kaydetmek için

#### **API ve Web İstekleri**
- **requests**: Şeffaflık Platformu API'sine bağlanmak için
- **datetime**: Tarih ve saat işlemleri (2024 yılı veri aralıkları)

#### **Excel Rapor Oluşturma**
- **xlsxwriter**: Grafikli Excel dosyaları oluşturmak için
- **openpyxl**: Basit Excel dosyaları okuma/yazma için

#### **Web Arayüzü**
- **streamlit**: Kullanıcı dostu web arayüzü oluşturmak için
- **plotly**: İnteraktif grafikler (çizgi, sütun, karşılaştırma grafikleri)

## Proje Yapısı ve Fonksiyonlar

### 1. API Bağlantı Modülü (`src/api_client.py`)

#### **SeffaflikAPIClient Sınıfı**
```python
class SeffaflikAPIClient:
```

**Ana Fonksiyonlar:**

- **`create_tgt()`**: Şeffaflık Platformu'na giriş yapmak için güvenlik anahtarı oluşturur
- **`make_api_request()`**: PTF, SMF, KGÜP, Üretim verilerini API'den çeker
- **`test_connection()`**: API bağlantısının çalışıp çalışmadığını kontrol eder

**Neden Gerekli:** Şeffaflık Platformu güvenlik protokolü gereği önce TGT (bilet) alınması, sonra bu biletle veri çekilmesi gerekiyor.

### 2. Veri Toplama Modülü (`src/data_collector.py`)

#### **DataCollector Sınıfı**
```python
class DataCollector:
```

**Ana Fonksiyonlar:**

- **`collect_ptf_data()`**: Piyasa Takas Fiyatı verilerini toplar (8,784 saatlik)
- **`collect_smf_data()`**: Sistem Marjinal Fiyatı verilerini toplar
- **`collect_kgup_data()`**: Her santral için planlanan üretim verilerini toplar
- **`collect_uretim_data()`**: Her santral için gerçek üretim verilerini toplar
- **`generate_date_ranges()`**: 2024 yılını küçük parçalara böler (API limiti nedeniyle)

**Neden Parçalara Bölünüyor:** API tek seferde tüm yılı vermiyor, 15-30 günlük parçalar halinde çekmek gerekiyor.

### 3. Veri İşleme Modülü (`src/data_processor.py`)

#### **DataProcessor Sınıfı**
```python
class DataProcessor:
```

**Ana Fonksiyonlar:**

- **`process_ptf_data()`**: Ham PTF verilerini temizler ve düzenler
- **`process_smf_data()`**: Ham SMF verilerini temizler ve düzenler
- **`process_santral_data()`**: Santral verilerini (KGÜP/Üretim) işler
- **`create_santral_analysis()`**: Bir santral için tüm verileri birleştirir ve finansal hesaplamalar yapar

**Finansal Hesaplamalar:**
```python
# PDF'deki formüllere göre
pozitif_dengesizlik_fiyati = Min(PTF, SMF) * 0.97
negatif_dengesizlik_fiyati = Max(PTF, SMF) * 1.03
gop_geliri = KGUP * PTF
toplam_gelir = gop_geliri + dengesizlik_tutari
```

### 4. Excel Rapor Modülleri

#### **SimpleExcelCharts (`src/simple_excel_charts.py`)**
- Grafikli Excel raporları oluşturur
- Plan vs Gerçek üretim grafikleri
- Aylık özet tabloları
- Dashboard sayfası

#### **CompleteExcelGenerator (`src/complete_excel_generator.py`)**
- 3 farklı Excel versiyonu oluşturur:
  1. **Tüm Veriler**: 8,784 satırın hepsi
  2. **Grafikli Özet**: İlk 1,000 satır + grafikler
  3. **Sadece Grafikler**: Minimal veri + maksimum grafik

### 5. Web Arayüzü (`streamlit_app.py`)

**Ana Fonksiyonlar:**

- **`load_processed_data()`**: İşlenmiş verileri yükler
- **`create_comparison_chart()`**: Santral karşılaştırma grafikleri oluşturur
- **`create_santral_detail_charts()`**: Detaylı santral analiz grafikleri

**Kullanıcı Özellikleri:**
- 2 santral seçme dropdown'ları
- Karşılaştırmalı grafikler
- Excel indirme butonları
- Responsive tasarım

## Veri Akışı

```
1. API Bağlantısı (TGT oluşturma)
   ↓
2. Veri Çekme (PTF, SMF, KGÜP, Üretim)
   ↓
3. Veri Temizleme ve İşleme
   ↓
4. Finansal Hesaplamalar (PDF formüllerine göre)
   ↓
5. Excel Raporları Oluşturma
   ↓
6. Web Arayüzünde Görselleştirme
```

## Analiz Edilen Santraller

1. **MASLAKTEPE RES** (Rüzgar) - Organizasyon ID: 12717
2. **EBER RES** (Rüzgar) - Organizasyon ID: 12517
3. **YANBOLU HES** (Hidroelektrik) - Organizasyon ID: 8801
4. **MELİKOM HES** (Hidroelektrik) - Organizasyon ID: 9709

## Çıktılar

### Excel Raporları
- **1_Gain_Enerji_TUM_VERILER_2024.xlsx**: Tüm 8,784 saatlik veri
- **2_Gain_Enerji_Grafikli_Ozet_2024.xlsx**: Grafikler + özet
- **3_Gain_Enerji_SADECE_GRAFIKLER_2024.xlsx**: Sadece grafikler

### Web Arayüzü
- İnteraktif santral karşılaştırması
- Gerçek zamanlı grafikler
- Excel indirme özelliği

### Yönetici Raporu
- **Gain_Enerji_Yonetici_Ozet_Raporu.md**: İş geliştirme önerileri

## Performans Metrikleri

**Hesaplanan Değerler:**
- Plan Tutturma Oranı: (Gerçek Üretim / KGÜP) × 100
- Dengesizlik Oranı: (|Toplam Dengesizlik| / Toplam Üretim) × 100
- Birim Gelir: Toplam Gelir / Toplam Üretim (TL/MWh)
- Net Gelir: Toplam Gelir - Dengesizlik Maliyeti

**Performans Notları:**
- **A+ Mükemmel**: Plan tutturma ≥95% ve Dengesizlik ≤10%
- **A İyi**: Plan tutturma ≥90% ve Dengesizlik ≤15%
- **B Orta**: Plan tutturma ≥85%
- **C Geliştirilmeli**: Plan tutturma <85%

## Güvenlik ve Kimlik Doğrulama

- Kullanıcı bilgileri `config/credentials.py` dosyasında saklanır
- TGT (Ticket Granting Ticket) sistemi ile güvenli API erişimi
- 2 saatlik oturum süresi, otomatik yenileme

## Hata Yönetimi

- API bağlantı hataları için retry mekanizması
- Eksik veri kontrolü ve uyarıları
- Kullanıcı dostu hata mesajları
- Graceful degradation (bir santral verisi yoksa diğerleriyle devam)

Bu doküman, projenin teknik altyapısını ve her komponentin amacını açıklamaktadır. Herhangi bir teknik detay için ek bilgi gerekirse, kod içindeki yorumlar ve docstring'ler referans alınabilir.
