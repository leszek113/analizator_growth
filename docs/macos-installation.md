# Instalacja i zarządzanie na macOS 🍎

## 🚀 Uruchamianie aplikacji w tle (launchd)

### Krok 1: Przygotowanie pliku konfiguracyjnego

Plik `com.leszek.analizator-rynku.plist` jest już przygotowany w katalogu projektu z następującymi ustawieniami:

- ✅ **Ręczne uruchamianie** - `RunAtLoad: false`
- ✅ **Warunkowe restartowanie** - `KeepAlive` z warunkami sieciowymi
- ✅ **Logi do plików** - `StandardOutPath` i `StandardErrorPath`
- ✅ **Tryb produkcyjny** - `FLASK_ENV: production`

**Ważne:** Konfiguracja `KeepAlive` została zmieniona z `true` na warunkową, żeby umożliwić niezawodne zatrzymanie aplikacji przez `launchctl stop`.

Utwórz plik `com.leszek.analizator-rynku.plist` w katalogu projektu:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.leszek.analizator-rynku</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/leszek/00_SynDrive/01d_Leszek/02d_LSTstuff/cursor/analizator_rynku/venv/bin/python</string>
        <string>/Users/leszek/00_SynDrive/01d_Leszek/02d_LSTstuff/cursor/analizator_rynku/app.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/leszek/00_SynDrive/01d_Leszek/02d_LSTstuff/cursor/analizator_rynku</string>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>KeepAlive</key>
    <dict>
        <key>NetworkState</key>
        <true/>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>ProcessType</key>
    <string>Background</string>
    
    <key>ThrottleInterval</key>
    <integer>10</integer>
    
    <key>StandardOutPath</key>
    <string>/Users/leszek/00_SynDrive/01d_Leszek/02d_LSTstuff/cursor/analizator_rynku/logs/analizator-rynku.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/leszek/00_SynDrive/01d_Leszek/02d_LSTstuff/cursor/analizator_rynku/logs/analizator-rynku-error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>FLASK_ENV</key>
        <string>production</string>
        <key>PYTHONPATH</key>
        <string>/Users/leszek/00_SynDrive/01d_Leszek/02d_LSTstuff/cursor/analizator_rynku</string>
    </dict>
</dict>
</plist>
```

### Krok 2: Instalacja usługi

```bash
# Skopiuj plik do katalogu LaunchAgents
cp com.leszek.analizator-rynku.plist ~/Library/LaunchAgents/

# Załaduj usługę (nie uruchamia automatycznie)
launchctl load ~/Library/LaunchAgents/com.leszek.analizator-rynku.plist
```

## 🎮 Zarządzanie aplikacją

### Metoda 1: Skrypt zarządzania (ZALECANE)

Dla niezawodnego zarządzania aplikacją użyj skryptu `scripts/manage-app.sh`:

```bash
# Sprawdź status aplikacji
./scripts/manage-app.sh status

# Uruchom aplikację
./scripts/manage-app.sh start

# Zatrzymaj aplikację
./scripts/manage-app.sh stop

# Restartuj aplikację
./scripts/manage-app.sh restart
```

**Zalety skryptu:**
- ✅ **Niezawodne zatrzymanie** - automatyczne wymuszenie jeśli launchd nie zadziała
- ✅ **Sprawdzanie statusu** - test odpowiedzi aplikacji
- ✅ **Kolorowy output** - łatwe rozpoznanie statusu
- ✅ **Obsługa błędów** - automatyczne czyszczenie procesów

### Metoda 2: Bezpośrednie komendy launchd

```bash
# Uruchom usługę
launchctl start com.leszek.analizator-rynku

# Zatrzymaj usługę
launchctl stop com.leszek.analizator-rynku

# Sprawdź status
launchctl list | grep analizator-rynku

# Usuń usługę (wyładuj)
launchctl unload ~/Library/LaunchAgents/com.leszek.analizator-rynku.plist
```

## 📊 Logi i monitoring

### Sprawdzenie logów aplikacji
```bash
tail -f logs/analizator-rynku.log
```

### Sprawdzenie logów błędów
```bash
tail -f logs/analizator-rynku-error.log
```

### Sprawdzenie czy aplikacja działa
```bash
curl -f http://localhost:5001/ || echo "Aplikacja nie odpowiada"
```

## 🔧 Konfiguracja

### Automatyczne restartowanie
- `KeepAlive: true` - aplikacja automatycznie się restartuje przy awarii
- `RunAtLoad: false` - aplikacja NIE uruchamia się automatycznie przy logowaniu

### Logi
- Logi aplikacji: `logs/analizator-rynku.log`
- Logi błędów: `logs/analizator-rynku-error.log`

## 🚨 Rozwiązywanie problemów

### Aplikacja nie uruchamia się
```bash
# Sprawdź logi błędów
tail -20 logs/analizator-rynku-error.log

# Sprawdź status usługi
launchctl list | grep analizator-rynku

# Restart usługi
launchctl stop com.leszek.analizator-rynku
launchctl start com.leszek.analizator-rynku
```

### Port 5001 zajęty
```bash
# Sprawdź co używa portu 5001
lsof -i :5001

# Zatrzymaj proces używający port
kill -9 <PID>
```

## 📝 Uwagi

- Aplikacja uruchamia się **ręcznie** przez `launchctl start`
- Automatyczne restartowanie przy awarii jest **włączone**
- Logi są zapisywane do plików w katalogu `logs/`
- Aplikacja działa na porcie **5001**
- Dostęp przez przeglądarkę: `http://localhost:5001` 