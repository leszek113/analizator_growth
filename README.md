# Analizator Rynku - v1.1.0 🎯

Automatyczny system analizy i selekcji spółek dywidendowych z integracją Google Sheets i Yahoo Finance.

## 🆕 Co nowego w v1.1.0

- **📈 Nowy system danych historycznych** - inteligentne pobieranie i przechowywanie danych
- **⚡ Lokalne obliczanie Stochastic** - szybsze i niezawodne obliczenia wskaźników
- **💾 Optymalizacja bazy danych** - tylko dane dzienne z agregacją do tygodniowych/miesięcznych
- **🔄 Inteligentna aktualizacja** - pobieranie tylko nowych danych, oszczędność API calls
- **📊 5-letnia historia** - pełne dane historyczne dla precyzyjnych obliczeń
- **🐛 Naprawa błędów** - poprawione obliczanie Stochastic dla wszystkich spółek

## 🚀 Funkcjonalności

### 📊 Analiza i Selekcja
- **Etap 1**: Automatyczna selekcja spółek z Google Sheets na podstawie reguł (JEDYNA SELEKCJA)
- **Etap 2**: Analiza Yahoo Finance + Stochastic Oscillator (DODATKOWE DANE INFORMACYJNE)
- **Dane historyczne**: 5-letnia historia cen z inteligentną aktualizacją
- **Stochastic 36,12,12**: Lokalne obliczanie dla 1M i 1W z pełnej historii
- **Wersjonowanie**: Pełna historia zmian reguł i danych
- **Baza danych**: SQLite z archiwizacją wszystkich wyników

### 🖥️ Interfejs Webowy
- **Dashboard**: Przegląd najnowszych wyników i statystyk
- **Wyniki**: Tabela z sortowaniem, filtrowaniem i eksportem CSV
- **Konfiguracja**: Edycja reguł selekcji przez UI
- **Notatki**: System notatek dla każdej spółki
- **Flagi**: System kolorowych flag z notatkami dla spółek
- **Dark Mode**: Nowoczesny interfejs z trybem ciemnym

### 🔧 Konfiguracja
- **Reguły selekcji**: Elastyczne kryteria (kraj, rating, yield, etc.)
- **Kolumny informacyjne**: Dodawanie/usuwanie pól z Google Sheets
- **Wersjonowanie**: Automatyczne śledzenie zmian konfiguracji

## 📋 Wymagania

- Python 3.8+
- Google Sheets API (credentials)
- Yahoo Finance API (darmowe)
- APScheduler 3.10.4+

## 🛠️ Instalacja

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/leszek113/analizator_rynku.git
cd analizator_rynku
```

### 2. Środowisko wirtualne
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate     # Windows
```

### 3. Zależności
```bash
pip install -r requirements.txt
```

### 4. Konfiguracja zmiennych środowiskowych
1. Skopiuj plik `env.example` do `.env`
2. Ustaw odpowiednie wartości w pliku `.env`:
   ```bash
   cp env.example .env
   # Edytuj .env i ustaw API_KEY i inne wartości
   ```

### 5. Konfiguracja Google Sheets
1. Utwórz projekt w [Google Cloud Console](https://console.cloud.google.com/)
2. Włącz Google Sheets API
3. Utwórz Service Account i pobierz `credentials.json`
4. Umieść plik w folderze `secrets/`
5. Utwórz arkusz z danymi spółek
6. Udostępnij arkusz dla Service Account email
7. Zaktualizuj `GOOGLE_SHEET_ID` w `src/import_google_sheet.py`

## 🚀 Uruchomienie

### macOS (Środowisko deweloperskie)
Szczegółowa instrukcja instalacji i zarządzania aplikacją na macOS znajduje się w pliku: [docs/macos-installation.md](docs/macos-installation.md)

**Szybki start:**
```bash
# Aktywacja środowiska wirtualnego
source venv/bin/activate

# Uruchomienie aplikacji
python app.py
```
Aplikacja będzie dostępna pod adresem: `http://localhost:5001`

### Ubuntu/Docker (Środowisko testowe)
Szczegółowa instrukcja dla środowiska Docker znajduje się w pliku: [docs/docker-installation.md](docs/docker-installation.md)

**Szybki start:**
```bash
# Uruchomienie kontenera
docker run -d --name analizator-rynku-v1 -p 5001:5001 leszek113/analizator-rynku:v1.0-amd64-fixed2
```

## 📖 Użycie

### 1. Konfiguracja reguł selekcji
- Przejdź do `/config`
- Edytuj reguły w sekcji "Reguły Selekcji"
- Dodaj/usuń kolumny informacyjne

### 2. Uruchomienie analizy
- Kliknij "Uruchom Analizę" na dashboardzie
- System pobierze dane z Google Sheets
- Przeprowadzi selekcję według reguł
- Pobierze dodatkowe dane z Yahoo Finance

### 3. Przeglądanie wyników
- `/results` - najnowsze wyniki
- Filtrowanie po dacie i tickerze
- Sortowanie kolumn
- Eksport do CSV

### 4. Notatki
- Kliknij "N-XX" przy spółce
- Dodawaj, edytuj, usuwaj notatki
- Historia notatek dla każdej spółki

### 5. Flagi spółek
- Kliknij na flagę przy spółce (⚪🔴🟢🟡🔵)
- Wybierz kolor flagi i dodaj notatkę (max 40 znaków)
- Tooltip pokazuje notatkę po najechaniu na flagę
- Historia flag zapisywana automatycznie raz dziennie

### 6. Przeglądanie wyników
- **Domyślnie**: pokazuje najnowszą selekcję z datą w nagłówku
- **Filtrowanie po dacie**: pokazuje selekcję z tej daty
- **Przycisk "Wszystko"**: pokazuje wszystkie selekcje ze wszystkich dat
- **Sortowanie**: domyślnie po "Yield Netto" malejąco

### 7. Automatyczne uruchamianie
- Przejdź do `/config`
- W sekcji "Automatyczne Uruchamianie Analizy":
  - Włącz/wyłącz automatyczne uruchamianie
  - Ustaw godzinę i strefę czasową
  - Sprawdź status schedulera
  - Przeglądaj historię uruchomień
  - Uruchom analizę natychmiast

### 8. Zapis flag tickerów
- W sekcji "Zapis flag tickerów":
  - Włącz/wyłącz automatyczny zapis historii flag
  - Ustaw godzinę zapisu (domyślnie 23:30)
  - Sprawdź status i historię zapisów
  - Uruchom zapis natychmiast

## 🏗️ Architektura

```
analizator_rynku/
├── app.py                 # Główna aplikacja Flask
├── src/
│   ├── database_manager.py      # Zarządzanie bazą danych
│   ├── import_google_sheet.py   # Import z Google Sheets
│   ├── yahoo_finance_analyzer.py # Analiza Yahoo Finance
│   ├── stage2_analysis.py       # Główna logika analizy
│   ├── stock_selector.py        # Selekcja spółek
│   └── auto_scheduler.py        # Automatyczne uruchamianie
├── config/
│   ├── selection_rules.yaml     # Reguły selekcji
│   ├── data_columns.yaml        # Kolumny danych
│   └── auto_schedule.yaml       # Konfiguracja automatycznego uruchamiania
├── templates/                   # Szablony HTML
├── static/                      # CSS, JS, obrazy
├── data/                        # Baza danych SQLite
├── logs/                        # Logi aplikacji
│   ├── analizator-rynku.log     # Główne logi
│   ├── analizator-rynku-error.log # Logi błędów
│   ├── auto_schedule.log        # Logi automatycznego uruchamiania
│   └── auto_schedule_monitoring.json # JSON logi monitoringu
└── secrets/                     # Pliki konfiguracyjne
```

## 📊 Baza danych

### Tabele
- `stage1_companies` - wyniki selekcji z danymi
- `analysis_runs` - historia uruchomień
- `selection_rules_versions` - wersje reguł
- `informational_columns_versions` - wersje kolumn
- `company_notes` - notatki spółek
- `auto_schedule_runs` - historia automatycznych uruchomień
- `company_flags` - aktualne flagi spółek
- `flag_history` - historia zmian flag (dzienne snapshoty)

### Wersjonowanie
- Każde uruchomienie ma przypisaną wersję reguł
- Pełna historia zmian konfiguracji
- Możliwość odtworzenia wyników z dowolnej daty

## 🔧 Konfiguracja

### Reguły selekcji (`config/selection_rules.yaml`)
```yaml
country:
  operator: "in"
  values: ["USA", "Canada"]
  
yield:
  operator: ">="
  value: 4.0
  
quality_rating:
  operator: "in"
  values: ["13.00", "12.00"]
```

### Kolumny informacyjne (`config/data_columns.yaml`)
```yaml
selection_columns:
  - "Country"
  - "Yield"
  - "Quality Rating (out Of 13)"

informational_columns:
  - "Company"
  - "Sector"
  - "Date Edited"
```

### Automatyczne uruchamianie (`config/auto_schedule.yaml`)
```yaml
auto_schedule:
  enabled: false
  time: "09:00"
  timezone: "Europe/Warsaw"
  interval_hours: 24

flag_snapshot:
  enabled: true
  time: "23:30"
  timezone: "Europe/Warsaw"
```

## 🎯 Logika Analizy

### Etap 1 - Selekcja (JEDYNA SELEKCJA)
- Pobieranie danych z Google Sheets
- Aplikowanie reguł selekcji (kraj, rating, yield, etc.)
- **Wszystkie spółki które przejdą Etap 1 są w finalnej selekcji**

### Etap 2 - Dane Informacyjne (NIE SELEKCJA)
- Pobieranie dodatkowych danych z Yahoo Finance
- Obliczanie Stochastic Oscillator
- Obliczanie cen i yieldów netto
- **Etap 2 NIE eliminuje spółek z selekcji - to tylko dodatkowe informacje**

## 🚀 Funkcje zaawansowane

### Stochastic Oscillator (Etap 2 - dane informacyjne)
- Parametry: Period 36, Smoothing 12, SMA 12
- Analiza 1M i 1W wykresów
- Warunek: przynajmniej jeden < 30%
- **UWAGA**: To są tylko dane informacyjne, nie wpływają na selekcję

### Yield Netto
- Automatyczne obliczanie: `Yield * 0.81`
- Cena dla 5% yield netto
- Historia cen i yieldów

### Notatki
- Numerowane notatki per spółka
- Edycja i usuwanie
- Historia zmian

### Flagi spółek
- **5 kolorów**: 🔴 Czerwony, 🟢 Zielony, 🟡 Żółty, 🔵 Niebieski, ⚪ Brak flagi
- **Notatki**: Do 40 znaków per flaga
- **UI**: Emoji z tooltipem na hover
- **Historia**: Automatyczny dzienny zapis o 23:30
- **Konfiguracja**: Zarządzanie w sekcji "Zapis flag tickerów"

### 🔄 Automatyczne Uruchamianie Analizy
- **APScheduler**: Codzienne uruchamianie o zdefiniowanej godzinie
- **Konfiguracja**: Włącz/wyłącz, czas, strefa czasowa
- **Dual Logging**: Czytelne logi + JSON dla monitoringu
- **Historia**: Pełna historia uruchomień w bazie danych
- **API Endpointy**: Status, health check, konfiguracja
- **UI**: Sekcja w Konfiguracji z zarządzaniem
- **Metryki**: Czas wykonania, liczba spółek, status błędów

## 🔐 Bezpieczeństwo

### API Key
Aplikacja używa API Key do autoryzacji chronionych endpointów. Ustaw zmienną środowiskową:
```bash
export API_KEY="your_secret_api_key_here"
```

### Chronione endpointy
Wszystkie endpointy z `POST` metodami wymagają nagłówka:
```
X-API-Key: your_secret_api_key_here
```

## 🌐 API Endpointy

### Automatyczne uruchamianie
- `GET /api/auto-schedule/status` - Status schedulera (publiczny)
- `GET /api/auto-schedule/health` - Health check (publiczny)
- `GET /api/auto-schedule/history` - Historia uruchomień (publiczny)
- `POST /api/auto-schedule/configure` - Konfiguracja (chroniony, X-API-Key)
- `POST /api/auto-schedule/run-now` - Uruchom teraz (chroniony, X-API-Key)

### Notatki
- `GET /api/notes/<ticker>` - Pobierz notatki spółki
- `POST /api/notes/<ticker>` - Dodaj notatkę
- `PUT /api/notes/<ticker>/<number>` - Edytuj notatkę
- `DELETE /api/notes/<ticker>/<number>` - Usuń notatkę

### Flagi
- `GET /api/flags/<ticker>` - Pobierz flagę spółki
- `POST /api/flags/<ticker>` - Ustaw flagę spółki
- `GET /api/flags/history/<ticker>` - Historia flag spółki
- `GET /api/flags/report` - Raport wszystkich flag
- `GET /api/flag-snapshot/status` - Status zapisu flag (publiczny)
- `GET /api/flag-snapshot/history` - Historia zapisu flag (publiczny)
- `POST /api/flag-snapshot/configure` - Konfiguracja zapisu flag (chroniony)
- `POST /api/flag-snapshot/run-now` - Uruchom zapis flag teraz (chroniony)

## 📝 Logowanie

### Logi aplikacji
- `logs/analizator-rynku.log` - Główne logi aplikacji
- `logs/analizator-rynku-error.log` - Logi błędów

### Logi automatycznego uruchamiania
- `logs/auto_schedule.log` - Czytelne logi (debugowanie)
- `logs/auto_schedule_monitoring.json` - JSON logi (monitoring)

### Format JSON logów
```json
{
  "timestamp": "2025-08-01T17:18:00.649062",
  "event": "auto_analysis_started",
  "run_id": "auto_20250801_171842",
  "status": "success",
  "execution_time_seconds": 930,
  "companies_count": 24
}
```

## 🔍 Monitoring i Alerty

### Metryki dostępne
- **Status uruchomienia**: success/error/timeout
- **Czas wykonania**: w sekundach
- **Liczba spółek**: przetworzonych
- **Błędy szczegółowe**: typ, wiadomość, recoverable
- **Historia uruchomień**: pełna w bazie danych

### Przygotowanie dla przyszłych alertów
- JSON logi gotowe do parsowania
- API endpointy dla health check
- Struktura metryk zdefiniowana
- Historia błędów w bazie danych

### Przykłady użycia
```bash
# Sprawdzenie statusu
curl http://localhost:5001/api/auto-schedule/health

# Pobranie historii
curl http://localhost:5001/api/auto-schedule/history?limit=5

# Konfiguracja (wymaga API key)
curl -X POST -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "time": "09:00"}' \
  http://localhost:5001/api/auto-schedule/configure

# Pobranie flag spółki
curl http://localhost:5001/api/flags/AAPL

# Ustawienie flagi (wymaga API key)
curl -X POST -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"flag_color": "green", "flag_notes": "Dobra spółka"}' \
  http://localhost:5001/api/flags/AAPL

# Status zapisu flag
curl http://localhost:5001/api/flag-snapshot/status

# Historia zapisu flag
curl http://localhost:5001/api/flag-snapshot/history
```

## 📝 Licencja

MIT License - zobacz plik [LICENSE](LICENSE)

## 🤝 Współpraca

1. Fork projektu
2. Utwórz branch dla nowej funkcjonalności
3. Commit zmian
4. Push do branch
5. Utwórz Pull Request

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź [Issues](https://github.com/leszek113/analizator_rynku/issues)
2. Utwórz nowy Issue z opisem problemu
3. Dołącz logi i konfigurację

---

**Analizator Rynku v1.0** - Automatyczna selekcja spółek dywidendowych 🎯 