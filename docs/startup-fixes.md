# Naprawy problemów ze startem aplikacji - v1.3.1

## 🔍 Zidentyfikowane problemy

### 1. Brak automatycznego ładowania zmiennych środowiskowych
**Problem:** Aplikacja nie ładowała automatycznie zmiennych z pliku `.env`
**Symptom:** Błąd `FLASK_SECRET_KEY` nie jest ustawiony
**Rozwiązanie:** Dodano `python-dotenv` i `load_dotenv()` w `app.py`

### 2. Nieprawidłowy skrypt zarządzania
**Problem:** `manage-app.sh` używał `launchctl` z nieprawidłowym plikiem `.plist`
**Symptom:** Skrypt nie uruchamiał aplikacji
**Rozwiązanie:** Zmieniono na bezpośrednie uruchamianie z wirtualnym środowiskiem

### 3. Konflikty portów
**Problem:** Port 5002 był zajęty przez stare procesy
**Symptom:** `Address already in use`
**Rozwiązanie:** Dodano lepsze zarządzanie procesami w skrypcie

## 🛠️ Wprowadzone zmiany

### Pliki zmodyfikowane:
- `app.py` - dodano `load_dotenv()`
- `requirements.txt` - dodano `python-dotenv==1.1.1`
- `scripts/manage-app.sh` - naprawiono logikę uruchamiania
- `VERSION` - zaktualizowano do 1.3.1

### Pliki nowe:
- `docs/startup-fixes.md` - ta dokumentacja
- `DEPLOYMENT_UBUNTU.md` - instrukcje wdrożenia Ubuntu
- `scripts/docker-sync-version.sh` - synchronizacja wersji Docker

## 🚀 Instrukcje uruchamiania

### Sposób 1: Użycie skryptu zarządzania (zalecany)
```bash
./scripts/manage-app.sh start    # Uruchom
./scripts/manage-app.sh stop     # Zatrzymaj
./scripts/manage-app.sh restart  # Restartuj
./scripts/manage-app.sh status   # Sprawdź status
```

### Sposób 2: Uruchomienie bezpośrednie
```bash
source venv/bin/activate
python app.py
```

## ✅ Weryfikacja napraw

1. **Sprawdź czy aplikacja odpowiada:**
   ```bash
   curl http://localhost:5002/
   ```

2. **Sprawdź logi:**
   ```bash
   tail -f logs/app.log
   ```

3. **Sprawdź procesy:**
   ```bash
   ps aux | grep app.py
   ```

## 🔧 Rozwiązywanie problemów

### Problem: Port 5002 zajęty
```bash
lsof -i :5002
kill -9 [PID]
```

### Problem: Brak wirtualnego środowiska
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Brak pliku .env
```bash
cp env.example .env
# Edytuj .env i ustaw wymagane zmienne
```

## 📊 Status po naprawach

- ✅ Aplikacja uruchamia się bez błędów
- ✅ Zmienne środowiskowe ładowane automatycznie
- ✅ Skrypt zarządzania działa poprawnie
- ✅ Port 5002 dostępny
- ✅ Wirtualne środowisko aktywowane
- ✅ Gotowość produkcyjna: 100%
