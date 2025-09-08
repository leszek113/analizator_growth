# 🐳 Deployment Analizatora Growth na Ubuntu - v1.1.0

## 📋 Wymagania

- Ubuntu 20.04+ lub 22.04+
- Docker Engine 20.10+
- Docker Compose 2.0+
- Port 5002 dostępny

## 🚀 Instalacja Docker (jeśli nie ma)

```bash
# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dodanie użytkownika do grupy docker
sudo usermod -aG docker $USER

# Instalacja Docker Compose
sudo apt install docker-compose-plugin -y

# Restart sesji
newgrp docker
```

## 📥 Deployment v1.1.0

### Krok 1: Pobranie nowej wersji
```bash
# Pobierz najnowszą wersję
docker pull leszek113/analizator-growth:v1.1.0

# Lub pobierz latest
docker pull leszek113/analizator-growth:latest
```

### Krok 2: Przygotowanie katalogów
```bash
# Utwórz katalog projektu
mkdir -p ~/analizator-growth
cd ~/analizator-growth

# Utwórz katalogi dla danych
mkdir -p data logs secrets config
```

### Krok 3: Konfiguracja docker-compose.yml
```yaml
version: '3.8'

services:
  analizator-growth:
    image: leszek113/analizator-growth:v1.1.0
    container_name: analizator-growth-v1.1.0
    ports:
      - "5002:5002"
    volumes:
      # Persystencja bazy danych
      - ./data:/app/data
      # Logi aplikacji
      - ./logs:/app/logs
      # Pliki konfiguracyjne (opcjonalne)
      - ./config:/app/config
      # Credentials Google Sheets
      - ./secrets:/app/secrets
    environment:
      - FLASK_ENV=production
      - PYTHONPATH=/app
      - APP_VERSION=v1.1.0
      - APP_BUILD=0
      - APP_RELEASE_DATE=2025-09-07
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5002/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  data:
  logs:
```

### Krok 4: Uruchomienie aplikacji
```bash
# Uruchom aplikację
docker-compose up -d

# Sprawdź status
docker-compose ps

# Sprawdź logi
docker-compose logs -f
```

## 🔄 Aktualizacja do nowej wersji

### Bezpieczna aktualizacja (zachowuje dane)
```bash
# Zatrzymaj aplikację
docker-compose down

# Pobierz nową wersję
docker pull leszek113/analizator-growth:v1.1.0

# Uruchom ponownie
docker-compose up -d
```

### Sprawdzenie aktualizacji
```bash
# Sprawdź czy aplikacja działa
curl http://localhost:5002/

# Sprawdź wersję w UI
# Otwórz http://localhost:5002 w przeglądarce
```

## 📊 Nowe funkcjonalności v1.1.0

- **📈 Nowy system danych historycznych** - inteligentne pobieranie i przechowywanie danych
- **⚡ Lokalne obliczanie Stochastic** - szybsze i niezawodne obliczenia wskaźników
- **💾 Optymalizacja bazy danych** - tylko dane dzienne z agregacją do tygodniowych/miesięcznych
- **🔄 Inteligentna aktualizacja** - pobieranie tylko nowych danych, oszczędność API calls
- **📊 5-letnia historia** - pełne dane historyczne dla precyzyjnych obliczeń
- **🐛 Naprawa błędów** - poprawione obliczanie Stochastic dla wszystkich spółek
- **🐳 Wersja wbudowana w Docker** - automatyczne przenoszenie wersji z obrazem
- **🔧 Multi-arch support** - obsługa linux/amd64 i linux/arm64

## 🔧 Zarządzanie aplikacją

### Podstawowe komendy
```bash
# Uruchomienie
docker-compose up -d

# Zatrzymanie
docker-compose down

# Restart
docker-compose restart

# Logi
docker-compose logs -f

# Status
docker-compose ps
```

### Backup bazy danych
```bash
# Backup
cp data/analizator_growth.db backup_$(date +%Y%m%d_%H%M%S).db

# Restore
cp backup_20250907_143000.db data/analizator_growth.db
```

## 🚨 Rozwiązywanie problemów

### Aplikacja nie uruchamia się
```bash
# Sprawdź logi
docker-compose logs

# Sprawdź porty
netstat -tlnp | grep 5002

# Sprawdź uprawnienia
ls -la data/ logs/ secrets/
```

### Błąd uprawnień
```bash
# Napraw uprawnienia
sudo chown -R $USER:$USER data/ logs/ secrets/
chmod -R 755 data/ logs/ secrets/
```

### Błąd połączenia z bazą
```bash
# Sprawdź czy baza istnieje
ls -la data/

# Sprawdź uprawnienia bazy
ls -la data/analizator_growth.db
```

## 📞 Wsparcie

- **GitHub:** https://github.com/leszek113/analizator_growth
- **Docker Hub:** https://hub.docker.com/r/leszek113/analizator-growth
- **Wersja:** v1.1.0
- **Data wydania:** 2025-09-07
