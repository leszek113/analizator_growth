# 🚀 Instrukcja Deployment na Ubuntu 24x7

## 📋 Wymagania systemowe

- Ubuntu 20.04+ lub 22.04+
- Docker i Docker Compose
- Minimum 2GB RAM
- 10GB wolnego miejsca na dysku

## 🔧 Instalacja

### 1. Instalacja Docker

```bash
# Aktualizuj system
sudo apt update && sudo apt upgrade -y

# Instalacja Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dodaj użytkownika do grupy docker
sudo usermod -aG docker $USER

# Zainstaluj Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Wyloguj się i zaloguj ponownie
exit
```

### 2. Przygotowanie aplikacji

```bash
# Sklonuj repozytorium
git clone https://github.com/leszek113/analizator_growth.git
cd analizator_growth

# Skopiuj plik konfiguracyjny
cp env.example .env

# Edytuj konfigurację
nano .env
```

### 3. Konfiguracja zmiennych środowiskowych

**WAŻNE:** Ustaw te zmienne w pliku `.env`:

```bash
# WYMAGANE - Bezpieczeństwo
API_KEY=twoj_bardzo_silny_klucz_api_tutaj
FLASK_SECRET_KEY=twoj_bardzo_silny_secret_key_tutaj

# WYMAGANE - Google Sheets
GOOGLE_CREDENTIALS_PATH=secrets/credentials.json
GOOGLE_SHEET_ID=twoj_google_sheet_id
GOOGLE_SHEET_NAME=03_DK_Master_XLS_Source
GOOGLE_WORKSHEET_NAME=DK

# OPCJONALNE - Yahoo Finance
YAHOO_FINANCE_API_KEY=twoj_yahoo_api_key

# Środowisko
FLASK_ENV=production
DEBUG=false
```

### 4. Przygotowanie Google Sheets

```bash
# Utwórz katalog na credentials
mkdir -p secrets

# Skopiuj plik credentials.json do secrets/
# (Pobierz z Google Cloud Console)
cp /ścieżka/do/credentials.json secrets/
```

### 5. Uruchomienie aplikacji

```bash
# Uruchom aplikację
docker-compose -f docker-compose-ubuntu.yml up -d

# Sprawdź status
docker-compose -f docker-compose-ubuntu.yml ps

# Sprawdź logi
docker-compose -f docker-compose-ubuntu.yml logs -f
```

## 🔍 Weryfikacja

### Sprawdź czy aplikacja działa:

```bash
# Sprawdź status kontenera
docker ps

# Sprawdź logi
docker logs analizator-growth-1.3.0

# Test połączenia
curl http://localhost:5002/
```

### Sprawdź w przeglądarce:

- Otwórz: `http://twoj-serwer:5002`
- Sprawdź czy ładuje się dashboard
- Sprawdź czy działa konfiguracja

## 🔄 Zarządzanie aplikacją

### Restart aplikacji:
```bash
docker-compose -f docker-compose-ubuntu.yml restart
```

### Zatrzymanie:
```bash
docker-compose -f docker-compose-ubuntu.yml down
```

### Aktualizacja:
```bash
# Pobierz najnowszą wersję
git pull

# Zatrzymaj aplikację
docker-compose -f docker-compose-ubuntu.yml down

# Uruchom ponownie
docker-compose -f docker-compose-ubuntu.yml up -d
```

## 📊 Monitoring

### Sprawdź logi:
```bash
# Wszystkie logi
docker-compose -f docker-compose-ubuntu.yml logs

# Logi w czasie rzeczywistym
docker-compose -f docker-compose-ubuntu.yml logs -f

# Logi aplikacji
tail -f logs/analizator-growth.log
```

### Sprawdź zużycie zasobów:
```bash
# Zużycie CPU i RAM
docker stats analizator-growth-1.3.0

# Rozmiar bazy danych
du -sh data/
```

## 🛡️ Bezpieczeństwo

### Firewall:
```bash
# Zezwól tylko na port 5002
sudo ufw allow 5002/tcp

# Włącz firewall
sudo ufw enable
```

### Backup:
```bash
# Backup bazy danych
cp data/analizator_growth.db backup/analizator_growth_$(date +%Y%m%d).db

# Backup konfiguracji
tar -czf backup/config_$(date +%Y%m%d).tar.gz config/ secrets/
```

## 🚨 Rozwiązywanie problemów

### Aplikacja się nie uruchamia:
1. Sprawdź logi: `docker-compose logs`
2. Sprawdź zmienne środowiskowe w `.env`
3. Sprawdź czy plik `credentials.json` istnieje

### Błąd "API_KEY nie jest ustawiony":
1. Ustaw zmienną `API_KEY` w pliku `.env`
2. Restart aplikacji: `docker-compose restart`

### Błąd połączenia z Google Sheets:
1. Sprawdź czy `credentials.json` jest w `secrets/`
2. Sprawdź czy arkusz jest udostępniony dla Service Account
3. Sprawdź `GOOGLE_SHEET_ID` w `.env`

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź logi aplikacji
2. Sprawdź status kontenera Docker
3. Sprawdź konfigurację zmiennych środowiskowych

---

**Aplikacja będzie działać 24x7 automatycznie!** 🎯
