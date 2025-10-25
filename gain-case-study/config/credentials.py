

# Şeffaflık Platformu kayıt: https://kayit.epias.com.tr/epias-transparency-platform-registration-form
USERNAME = "alaaddinkoyuncu1@outlook.com"  # Buraya kullanıcı adınızı girin
PASSWORD = "Mintonette.1"  # Buraya şifrenizi girin

# API Base URLs
TGT_URL = "https://giris.epias.com.tr/cas/v1/tickets"
BASE_API_URL = "https://seffaflik.epias.com.tr/electricity-service/v1"

# API Endpoints
ENDPOINTS = {
    "PTF": f"{BASE_API_URL}/markets/dam/data/mcp",
    "SMF": f"{BASE_API_URL}/markets/bpm/data/system-marginal-price", 
    "KGUP": f"{BASE_API_URL}/generation/data/dpp-first-version",
    "URETIM": f"{BASE_API_URL}/generation/data/realtime-generation"
}

# Santral Bilgileri (pp_list.json'dan)
SANTRALLER = [
    {
        "powerPlantName": "MASLAKTEPE RES",
        "organizationId": 12717,
        "powerPlantId": 2468,
        "uevcbId": 3207214
    },
    {
        "powerPlantName": "EBER RES", 
        "organizationId": 12517,
        "powerPlantId": 2316,
        "uevcbId": 3217197
    },
    {
        "powerPlantName": "YANBOLU HES",
        "organizationId": 8801,
        "powerPlantId": 1884,
        "uevcbId": 2813560
    },
    {
        "powerPlantName": "MELİKOM HES",
        "organizationId": 9709,
        "powerPlantId": 2142,
        "uevcbId": 3196990
    }
]
