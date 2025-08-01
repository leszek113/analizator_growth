# Analizator Rynku - v1.0 🎯

Automatyczny system analizy i selekcji spółek dywidendowych z integracją Google Sheets i Yahoo Finance.

## 🚀 Funkcjonalności

### 📊 Analiza i Selekcja
- **Etap 1**: Automatyczna selekcja spółek z Google Sheets na podstawie reguł
- **Etap 2**: Analiza Yahoo Finance + Stochastic Oscillator (dane informacyjne)
- **Wersjonowanie**: Pełna historia zmian reguł i danych
- **Baza danych**: SQLite z archiwizacją wszystkich wyników

### 🖥️ Interfejs Webowy
- **Dashboard**: Przegląd najnowszych wyników i statystyk
- **Wyniki**: Tabela z sortowaniem, filtrowaniem i eksportem CSV
- **Konfiguracja**: Edycja reguł selekcji przez UI
- **Notatki**: System notatek dla każdej spółki
- **Dark Mode**: Nowoczesny interfejs z trybem ciemnym

### 🔧 Konfiguracja
- **Reguły selekcji**: Elastyczne kryteria (kraj, rating, yield, etc.)
- **Kolumny informacyjne**: Dodawanie/usuwanie pól z Google Sheets
- **Wersjonowanie**: Automatyczne śledzenie zmian konfiguracji

## 📋 Wymagania

- Python 3.8+
- Google Sheets API (credentials)
- Yahoo Finance API (darmowe)

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

### 4. Konfiguracja Google Sheets
1. Utwórz projekt w [Google Cloud Console](https://console.cloud.google.com/)
2. Włącz Google Sheets API
3. Utwórz Service Account i pobierz `credentials.json`
4. Umieść plik w folderze `secrets/`

### 5. Konfiguracja Google Sheets
1. Utwórz arkusz z danymi spółek
2. Udostępnij arkusz dla Service Account email
3. Zaktualizuj `GOOGLE_SHEET_ID` w `src/import_google_sheet.py`

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

## 🏗️ Architektura

```
analizator_rynku/
├── app.py                 # Główna aplikacja Flask
├── src/
│   ├── database_manager.py      # Zarządzanie bazą danych
│   ├── import_google_sheet.py   # Import z Google Sheets
│   ├── yahoo_finance_analyzer.py # Analiza Yahoo Finance
│   ├── stage2_analysis.py       # Główna logika analizy
│   └── stock_selector.py        # Selekcja spółek
├── config/
│   ├── selection_rules.yaml     # Reguły selekcji
│   └── data_columns.yaml        # Konfiguracja kolumn
├── templates/                   # Szablony HTML
├── static/                      # CSS, JS, obrazy
└── secrets/                     # Pliki konfiguracyjne
```

## 📊 Baza danych

### Tabele
- `stage1_companies` - wyniki selekcji z danymi
- `analysis_runs` - historia uruchomień
- `selection_rules_versions` - wersje reguł
- `informational_columns_versions` - wersje kolumn
- `company_notes` - notatki spółek

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

## 🚀 Funkcje zaawansowane

### Stochastic Oscillator
- Parametry: Period 36, Smoothing 12, SMA 12
- Analiza 1M i 1W wykresów
- Warunek: przynajmniej jeden < 30%

### Yield Netto
- Automatyczne obliczanie: `Yield * 0.81`
- Cena dla 5% yield netto
- Historia cen i yieldów

### Notatki
- Numerowane notatki per spółka
- Edycja i usuwanie
- Historia zmian

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