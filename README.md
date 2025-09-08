# Analizator Growth - v1.2.0 🎯

Automatyczny system analizy i selekcji spółek dywidendowych z integracją Google Sheets i Yahoo Finance.

## 🆕 Co nowego w v1.2.0

- **🔒 BEZPIECZEŃSTWO: Pełna walidacja danych wejściowych API** - ochrona przed atakami XSS i injection
- **🔒 BEZPIECZEŃSTWO: Rate limiting dla endpointów API** - ochrona przed DDoS i nadużyciami
- **🔒 BEZPIECZEŃSTWO: Usunięto hardcoded API keys** - dodano zmienne środowiskowe
- **⚡ WYDAJNOŚĆ: System cache dla często używanych danych** - szybsze ładowanie wyników
- **⚡ WYDAJNOŚĆ: Optymalizacja zapytań do bazy danych** - mniejsze obciążenie
- **🔧 STABILNOŚĆ: Naprawiono niezgodności wersji pakietów** - spójne zależności
- **🔧 STABILNOŚĆ: Wyeliminowano duplikację kodu** - czystszy, bardziej utrzymywalny kod
- **🔧 STABILNOŚĆ: Lepsze error handling i logowanie** - bardziej niezawodna aplikacja
- **📚 DOKUMENTACJA: Uzupełniono dokumentację API i konfiguracji** - łatwiejsze wdrożenie
- **🚀 PRODUKCJA: Aplikacja gotowa do wdrożenia produkcyjnego** - pełne zabezpieczenia

## 🆕 Co nowego w v1.1.2

- **📊 Nowe kolumny informacyjne** - Current Price, Historical Fair Value, Market Cap z Google Sheets
- **🧮 Obliczanie Discount to Fair Value** - automatyczne obliczanie w procentach (np. +13.89%)
- **💰 Formatowanie Market Cap** - wyświetlanie w miliardach dolarów (np. $15.2 B)
- **🔧 Naprawa sortowania** - wszystkie kolumny sortowalne, w tym "Sto 36,12,12 1M" i "Sto 36,12,12 1W"
- **📈 Poprawka obliczeń** - Historical Fair Value (60205.16% = $602.05)
- **🗑️ Czyszczenie bazy** - funkcja czyszczenia bazy przed nową analizą
- **📚 Ulepszona dokumentacja** - zaktualizowane instrukcje użytkowania

## 🆕 Co nowego w v1.1.1

- **🎯 Zmiana nazwy projektu** - z "analizator_rynku" na "Analizator Growth"
- **📊 Nowe reguły selekcji** - bardzo restrykcyjne warunki dla spółek typu growth
- **🔧 Opcja B dla Stochastic** - N/A dla spółek z < 60 dni danych historycznych
- **🐛 Naprawa wyświetlania** - poprawione wyświetlanie N/A zamiast nan% w UI
- **🔐 Bezpieczeństwo** - zaktualizowane klucze API na bezpieczniejsze placeholder'y
- **📝 Debug logging** - dodane logi debugowania dla lepszego śledzenia procesu selekcji
- **📚 Dokumentacja** - zaktualizowana dokumentacja deployment'u

## 🆕 Co nowego w v1.1.0

- **📈 Nowy system danych historycznych** - inteligentne pobieranie i przechowywanie danych
- **⚡ Lokalne obliczanie Stochastic** - szybsze i niezawodne obliczenia wskaźników
- **💾 Optymalizacja bazy danych** - tylko dane dzienne z agregacją do tygodniowych/miesięcznych
- **🔄 Inteligentna aktualizacja** - pobieranie tylko nowych danych, oszczędność API calls
- **📊 5-letnia historia** - pełne dane historyczne dla precyzyjnych obliczeń
- **🐛 Naprawa błędów** - poprawione obliczanie Stochastic dla wszystkich spółek
- **🐳 Wersja wbudowana w Docker** - automatyczne przenoszenie wersji z obrazem
- **🔧 Multi-arch support** - obsługa linux/amd64 i linux/arm64

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
git clone https://github.com/leszek113/analizator_growth.git
cd analizator_growth
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
Aplikacja będzie dostępna pod adresem: `http://localhost:5002`

### Ubuntu/Docker (Środowisko testowe)
Szczegółowa instrukcja dla środowiska Docker znajduje się w pliku: [docs/docker-installation.md](docs/docker-installation.md)

**Szybki start:**
```bash
# Uruchomienie kontenera
docker run -d --name analizator-growth-v1 -p 5002:5002 leszek113/analizator-growth:v1.1.1
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
analizator_growth/
├── app.py                 # Główna aplikacja Flask
├── src/
│   ├── database_manager.py      # Zarządzanie bazą danych + cache
│   ├── import_google_sheet.py   # Import z Google Sheets
│   ├── yahoo_finance_analyzer.py # Analiza Yahoo Finance
│   ├── stage2_analysis.py       # Główna logika analizy
│   ├── stock_selector.py        # Selekcja spółek
│   ├── auto_scheduler.py        # Automatyczne uruchamianie
│   ├── cache_manager.py         # System cache
│   └── rate_limiter.py          # Rate limiting API
├── config/
│   ├── selection_rules.yaml     # Reguły selekcji
│   ├── data_columns.yaml        # Kolumny danych
│   └── auto_schedule.yaml       # Konfiguracja automatycznego uruchamiania
├── templates/                   # Szablony HTML
├── static/                      # CSS, JS, obrazy
├── data/                        # Baza danych SQLite
├── logs/                        # Logi aplikacji
│   ├── analizator-growth.log     # Główne logi
│   ├── analizator-growth-error.log # Logi błędów
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
# Reguły selekcji spółek GROWTH - Etap 1 (GŁÓWNA SELEKCJA)
# Bardzo restrykcyjne warunki dla spółek typu growth
# Wszystkie spółki które przejdą Etap 1 trafiają do finalnej listy

selection_rules:
  quality_rating:
    column: "Quality Rating (out Of 13)"
    operator: "in"
    values: ["13.00", "12.00"]
    description: "Tylko spółki z najwyższymi ocenami jakości (12 lub 13 na 13)"

  sp_credit_rating:
    column: "S&P Credit Rating"
    operator: "complex"
    allowed_patterns: ["A*", "BBB+", "BBB"]
    excluded_values: ["BBB-", "NA"]
    description: "Ratingi A (A+, A, A-) oraz BBB+ i BBB. Wykluczone BBB- i NA"

  dk_rating:
    column: "DK Rating"
    operator: "in"
    values: ["Potential Good Buy or Better"]
    description: "Tylko spółki z pozytywną oceną DK - Potential Good Buy or Better"
```

### Kolumny informacyjne (`config/data_columns.yaml`)
```yaml
selection_columns:
  country: "Country"
  quality_rating: "Quality Rating (out Of 13)"
  yield: "Yield"
  dividend_growth_streak: "Dividend Growth Streak (Years)"
  sp_credit_rating: "S&P Credit Rating"
  dk_rating: "DK Rating"

informational_columns:
  date_edited: "Date Edited"
  company: "Company"
  sector: "Sector"
  current_price: "Current Price"  # Cena aktualna w dolarach
  historical_fair_value: "Historical Fair Value"  # Historical Fair Value w procentach (ale to są dolary)
  market_cap_billion: "Market Cap (Billion)"  # Market Cap w miliardach dolarów
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

## ⚡ Wydajność

### System Cache
- **Cache Manager**: Automatyczne cache'owanie często używanych danych
- **TTL**: Konfigurowalny czas życia cache (domyślnie 5 minut)
- **Auto-invalidation**: Automatyczne czyszczenie po zapisie nowych danych
- **Memory-based**: Szybki dostęp do danych w pamięci

### Optymalizacje
- **Zapytania SQL**: Indeksy na kluczowych kolumnach
- **Batch operations**: Masowe operacje na bazie danych
- **Lazy loading**: Ładowanie danych tylko gdy potrzebne
- **Connection pooling**: Optymalne zarządzanie połączeniami

### Metryki wydajności
- **Cache hit rate**: Procent trafień w cache
- **Query time**: Czas wykonania zapytań
- **Memory usage**: Zużycie pamięci przez cache
- **Response time**: Czas odpowiedzi API

## 🚀 Funkcje zaawansowane

### Stochastic Oscillator (Etap 2 - dane informacyjne)
- Parametry: Period 36, Smoothing 12, SMA 12
- Analiza 1M i 1W wykresów
- Warunek: przynajmniej jeden < 30%
- **Opcja B**: N/A dla spółek z < 60 dni danych historycznych
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

### Walidacja danych wejściowych
- **Tickery**: Tylko litery, cyfry i kropki (regex: `^[A-Za-z0-9.]+$`)
- **Notatki**: Max 1000 znaków, ochrona przed XSS
- **Flagi**: Walidacja kolorów i długości notatek
- **Daty**: Format YYYY-MM-DD z walidacją

### Rate Limiting
- **API Notes**: 100 żądań/godzinę
- **API Flags**: 50 żądań/godzinę  
- **API General**: 200 żądań/godzinę
- **Sliding window**: Automatyczne czyszczenie starych żądań

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

### Zmienne środowiskowe
```bash
# API Security
API_KEY=your_secret_api_key_here

# Google Sheets
GOOGLE_CREDENTIALS_PATH=secrets/credentials.json
GOOGLE_SHEET_NAME=03_DK_Master_XLS_Source
GOOGLE_WORKSHEET_NAME=DK

# Yahoo Finance (opcjonalne)
YAHOO_FINANCE_API_KEY=your_yahoo_api_key
```

## 🌐 API Endpointy

### Automatyczne uruchamianie
- `GET /api/auto-schedule/status` - Status schedulera (publiczny)
- `GET /api/auto-schedule/health` - Health check (publiczny)
- `GET /api/auto-schedule/history` - Historia uruchomień (publiczny)
- `POST /api/auto-schedule/configure` - Konfiguracja (chroniony, X-API-Key)
- `POST /api/auto-schedule/run-now` - Uruchom teraz (chroniony, X-API-Key)

### Notatki (z walidacją i rate limiting)
- `GET /api/notes/<ticker>` - Pobierz notatki spółki
- `POST /api/notes/<ticker>` - Dodaj notatkę (rate limit: 100/h)
- `PUT /api/notes/<ticker>/<number>` - Edytuj notatkę
- `DELETE /api/notes/<ticker>/<number>` - Usuń notatkę

### Flagi (z walidacją i rate limiting)
- `GET /api/flags/<ticker>` - Pobierz flagę spółki
- `POST /api/flags/<ticker>` - Ustaw flagę spółki (rate limit: 50/h)
- `GET /api/flags/history/<ticker>` - Historia flag spółki
- `GET /api/flags/report` - Raport wszystkich flag
- `GET /api/flag-snapshot/status` - Status zapisu flag (publiczny)
- `GET /api/flag-snapshot/history` - Historia zapisu flag (publiczny)
- `POST /api/flag-snapshot/configure` - Konfiguracja zapisu flag (chroniony)
- `POST /api/flag-snapshot/run-now` - Uruchom zapis flag teraz (chroniony)

## 📝 Logowanie

### Logi aplikacji
- `logs/analizator-growth.log` - Główne logi aplikacji
- `logs/analizator-growth-error.log` - Logi błędów

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
curl http://localhost:5002/api/auto-schedule/health

# Pobranie historii
curl http://localhost:5002/api/auto-schedule/history?limit=5

# Konfiguracja (wymaga API key)
curl -X POST -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "time": "09:00"}' \
  http://localhost:5002/api/auto-schedule/configure

# Pobranie flag spółki
curl http://localhost:5002/api/flags/AAPL

# Ustawienie flagi (wymaga API key)
curl -X POST -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"flag_color": "green", "flag_notes": "Dobra spółka"}' \
  http://localhost:5002/api/flags/AAPL

# Status zapisu flag
curl http://localhost:5002/api/flag-snapshot/status

# Historia zapisu flag
curl http://localhost:5002/api/flag-snapshot/history
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
1. Sprawdź [Issues](https://github.com/leszek113/analizator_growth/issues)
2. Utwórz nowy Issue z opisem problemu
3. Dołącz logi i konfigurację

---

**Analizator Growth v1.2.0** - Automatyczna selekcja spółek dywidendowych 🎯 