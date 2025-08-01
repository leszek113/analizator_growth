# Instalacja i zarządzanie na Ubuntu/Docker 🐳

## 🚀 Uruchamianie aplikacji w kontenerze Docker

### Krok 1: Przygotowanie środowiska

Upewnij się, że masz zainstalowany Docker na Ubuntu:

```bash
# Sprawdź wersję Docker
docker --version

# Sprawdź czy Docker działa
docker ps
```

### Krok 2: Pobranie obrazu z Docker Hub

```bash
# Pobierz najnowszą wersję obrazu
docker pull leszek113/analizator-rynku:v1.0-amd64-fixed2

# Sprawdź dostępne obrazy
docker images | grep analizator-rynku
```

### Krok 3: Uruchomienie kontenera

```bash
# Uruchom kontener z aplikacją
docker run -d \
  --name analizator-rynku-v1 \
  -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/secrets:/app/secrets \
  leszek113/analizator-rynku:v1.0-amd64-fixed2
```

## 🎮 Zarządzanie aplikacją

### Uruchomienie aplikacji
```bash
# Uruchom istniejący kontener
docker start analizator-rynku-v1
```

### Zatrzymanie aplikacji
```bash
# Zatrzymaj kontener
docker stop analizator-rynku-v1
```

### Restart aplikacji
```bash
# Restart kontenera
docker restart analizator-rynku-v1
```

### Sprawdzenie statusu
```bash
# Sprawdź czy kontener działa
docker ps | grep analizator-rynku

# Sprawdź wszystkie kontenery (włącznie ze zatrzymanymi)
docker ps -a | grep analizator-rynku
```

### Usunięcie kontenera
```bash
# Zatrzymaj i usuń kontener
docker stop analizator-rynku-v1
docker rm analizator-rynku-v1
```

## 📊 Logi i monitoring

### Sprawdzenie logów aplikacji
```bash
# Wyświetl logi kontenera
docker logs analizator-rynku-v1

# Śledź logi na żywo
docker logs -f analizator-rynku-v1

# Wyświetl ostatnie 50 linii logów
docker logs --tail 50 analizator-rynku-v1
```

### Sprawdzenie czy aplikacja działa
```bash
# Sprawdź czy aplikacja odpowiada
curl -f http://localhost:5001/ || echo "Aplikacja nie odpowiada"

# Sprawdź porty
netstat -tlnp | grep 5001
```

## 🔄 Aktualizacja do nowej wersji

### Krok 1: Zatrzymanie starej wersji
```bash
# Zatrzymaj obecny kontener
docker stop analizator-rynku-v1

# Usuń stary kontener
docker rm analizator-rynku-v1
```

### Krok 2: Pobranie nowej wersji
```bash
# Pobierz nową wersję
docker pull leszek113/analizator-rynku:v1.0-amd64-fixed2
```

### Krok 3: Uruchomienie nowej wersji
```bash
# Uruchom z nową wersją
docker run -d \
  --name analizator-rynku-v1 \
  -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/secrets:/app/secrets \
  leszek113/analizator-rynku:v1.0-amd64-fixed2
```

## 🔧 Konfiguracja

### Volumes (persystencja danych)
- `./data:/app/data` - baza danych SQLite
- `./logs:/app/logs` - logi aplikacji
- `./config:/app/config` - pliki konfiguracyjne
- `./secrets:/app/secrets` - credentials Google Sheets

### Porty
- `5001:5001` - aplikacja dostępna na porcie 5001

### Automatyczne restartowanie
```bash
# Uruchom z automatycznym restartowaniem
docker run -d \
  --name analizator-rynku-v1 \
  --restart unless-stopped \
  -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/secrets:/app/secrets \
  leszek113/analizator-rynku:v1.0-amd64-fixed2
```

## 🚨 Rozwiązywanie problemów

### Kontener nie uruchamia się
```bash
# Sprawdź logi błędów
docker logs analizator-rynku-v1

# Sprawdź status kontenera
docker ps -a | grep analizator-rynku

# Sprawdź użycie zasobów
docker stats analizator-rynku-v1
```

### Port 5001 zajęty
```bash
# Sprawdź co używa portu 5001
sudo netstat -tlnp | grep 5001

# Lub użyj lsof
sudo lsof -i :5001
```

### Problemy z volumes
```bash
# Sprawdź czy katalogi istnieją
ls -la data/ logs/ config/ secrets/

# Utwórz brakujące katalogi
mkdir -p data logs config secrets
```

### Reset kontenera
```bash
# Pełny reset (usuwa dane!)
docker stop analizator-rynku-v1
docker rm analizator-rynku-v1
docker run -d --name analizator-rynku-v1 -p 5001:5001 leszek113/analizator-rynku:v1.0-amd64-fixed2
```

## 📝 Uwagi

- **Dane są zachowywane** w volume `./data`
- **Logi aplikacji** są w volume `./logs`
- **Aplikacja działa na porcie 5001**
- **Dostęp przez przeglądarkę**: `http://localhost:5001`
- **Automatyczne restartowanie** można włączyć przez `--restart unless-stopped`
- **Aktualizacje** wymagają zatrzymania i usunięcia starego kontenera 