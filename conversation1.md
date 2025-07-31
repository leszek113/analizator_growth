# ANALIZATOR RYNKU - DOKUMENTACJA KONWERSACJI #1

## CEL PROJEKTU
Aplikacja do automatycznej selekcji spółek/ETF-ów do ewentualnej inwestycji na podstawie danych z różnych źródeł.

### Główne funkcje:
- Import danych z Google Sheet (duża tabela ~500 wierszy, 135 kolumn)
- Pobieranie danych z Yahoo Finance (cena, dywidendy, yield, wskaźniki techniczne)
- Automatyczna selekcja spółek według zdefiniowanych kryteriów
- Tworzenie shortlisty kandydatów do inwestycji
- Zapisywanie wyników w lokalnej bazie SQLite
- Prezentacja wyników przez interfejs webowy
- Historia selekcji (możliwość sprawdzenia, czy spółka była kiedyś na liście)

## ARCHITEKTURA
- **Język:** Python
- **Baza danych:** SQLite
- **Interfejs webowy:** Flask
- **Konteneryzacja:** Docker (na końcu)
- **Backup:** Możliwość tworzenia kopii zapasowych
- **Automatyzacja:** Uruchamianie raz dziennie

## ŚRODOWISKO
- **Rozwój:** macOS
- **Produkcja:** Linux Ubuntu w chmurze
- **Repozytorium:** GitHub (https://github.com/leszek113/analiza_rynku)

## ŹRÓDŁA DANYCH

### 1. Google Sheet
- **Nazwa arkusza:** "03_DK_Master_XLS_Source"
- **Zakładka:** "DK"
- **Struktura:** ~500 wierszy (dokładnie 487 po import), 135 kolumn
- **Nagłówki:** w 5. wierszu (indeks 4) - struktura została przesunięta w dół
- **Autoryzacja:** Service Account (credentials.json w katalogu secrets/)
- **Udostępnienie:** Arkusz udostępniony do odczytu dla Service Account
- **Selekcja danych:** Pobieramy wszystkie dane, selekcję robimy w Pythonie

### 2. Yahoo Finance
- **Dane:** cena, historia dywidend, yield, wskaźniki techniczne (np. stochastic)
- **Biblioteka:** yfinance
- **Status:** Do implementacji
- **Konto:** Nie ma konta, korzystamy z ogólnodostępnych danych

## REGUŁY SELEKCJI (AKTUALNE - ZWERYFIKOWANE)

### Plik konfiguracyjny: `config/selection_rules.yaml`

1. **Country** = US, UK, Canada
2. **Quality Rating** = 13 lub 12 (w danych jako "1300%", "1200%" z powodu formatowania)
3. **Yield** >= 4% (w formie procentowej)
4. **Dividend Growth Streak (Years)** >= 15
5. **5-Year Dividend Growth Rate CAGR** >= 300% - **TYMCZASOWO WYŁĄCZONE**
6. **S&P Credit Rating** = A* (każda wartość zaczynająca się od A) i tylko BBB+, BBB (bez BBB- i NA)
7. **DK Rating** = "Potential Good Buy or Better"

### Kolejność stosowania reguł:
1. Country → 2. Quality Rating → 3. Yield → 4. Dividend Growth Streak → 5. S&P Credit Rating → 6. DK Rating

### Wyniki selekcji:
- **Początkowa liczba spółek:** 487
- **Po selekcji:** 16 spółek (3.29%)
- **Wybrane spółki:** ARE, BHB, BKH, BMY, BEP, CVX, EMN, EPD, FRT, NNN, NWN, PFE, O, TGT, UPS, VZ

## STRUKTURA PROJEKTU (ZAKTUALIZOWANA - LIPIEC 2025)
```
analizator_rynku/
├── src/
│   ├── stage2_analysis.py        # Główny skrypt analizy dwuetapowej
│   ├── database_manager.py       # Menedżer bazy danych SQLite
│   ├── yahoo_finance_analyzer.py # Analiza Yahoo Finance i Stochastic
│   ├── import_google_sheet.py    # Import danych z Google Sheet
│   ├── stock_selector.py         # Logika selekcji spółek
│   ├── database_test.py          # Test bazy danych
│   └── history_test.py           # Test funkcji historii
├── config/
│   ├── selection_rules.yaml      # Reguły selekcji (edytowalne)
│   └── data_columns.yaml         # Konfiguracja kolumn danych (edytowalne)
├── secrets/
│   └── credentials.json          # Dane logowania Google API
├── static/                       # Pliki statyczne (CSS, JS) - do implementacji
├── templates/                    # Szablony HTML - do implementacji
├── docs/                         # Dokumentacja
├── tests/                        # Testy - do implementacji
├── venv/                         # Wirtualne środowisko Python
├── market_analyzer.db            # Baza danych SQLite
├── requirements.txt              # Zależności Python
└── .gitignore                    # Ignoruje katalog secrets/ i venv/
```

## POSTĘP PROJEKTU

### ✅ ZROBIONE:
1. **Synchronizacja z GitHub** - repozytorium utworzone i połączone
2. **Konfiguracja Google API** - Service Account, credentials.json
3. **Import danych z Google Sheet** - działa, pobiera 487 spółek
4. **Plik konfiguracyjny reguł** - YAML z 6 regułami selekcji (1 wyłączona)
5. **Moduł selekcji spółek** - StockSelector class (poprawiony)
6. **Główny skrypt** - stage2_analysis.py (dwuetapowa analiza)
7. **Wirtualne środowisko Python** - skonfigurowane z wymaganymi bibliotekami
8. **Debugowanie i weryfikacja** - selekcja zweryfikowana z ręczną selekcją użytkownika
9. **Naprawienie problemów z danymi** - obsługa duplikatów kolumn, formatowania procentów
10. **Baza danych SQLite** - implementacja z uproszczoną strukturą
11. **Analiza Yahoo Finance** - pobieranie danych i obliczanie Stochastic Oscillator
12. **Funkcje historii** - możliwość sprawdzenia historii spółek
13. **Czyszczenie projektu** - usunięto niepotrzebne pliki debug

### 🔧 PROBLEMY ROZWIĄZANE:
- **Selekcja nie działała** - wszystkie spółki były odrzucane (0 wyników)
- **Przyczyna:** Nazwy kolumn w danych nie pasowały do tych w konfiguracji
- **Rozwiązanie:** Utworzono debug_columns.py, poprawiono reguły selekcji
- **Problem z formatowaniem:** Quality Rating wyświetlany jako "1200%", "1300%" zamiast 12, 13
- **Problem z Yield:** Początkowo w dolarach ($0.04), potem poprawione na procenty (4%)
- **Problem z duplikatami kolumn:** Naprawiono import danych
- **Problem z przesunięciem danych:** Nagłówki przesunięte z wiersza 3 na wiersz 5
- **Problem z Stochastic Oscillator:** Wartości NaN - rozwiązane przez dostosowanie parametrów
- **Problem z bazą danych:** Złożona struktura - uproszczona do 2 tabel
- **Problem z niepotrzebnymi plikami:** Usunięto 6 plików debug i 5 plików CSV

### 📋 DO ZROBIENIA:
1. **Interfejs webowy (Flask)** - prezentacja wyników i historii
2. **Automatyzacja (cron/systemd)** - uruchamianie raz dziennie
3. **Backup** - możliwość tworzenia kopii zapasowych
4. **Docker** - konteneryzacja aplikacji
5. **Testy jednostkowe** - pokrycie testami
6. **Dokumentacja API** - dokumentacja funkcji

## SZCZEGÓŁY TECHNICZNE

### Biblioteki Python (requirements.txt):
- gspread>=5.12.0 (Google Sheets API)
- pandas>=2.2.0 (analiza danych)
- oauth2client>=4.1.3 (autoryzacja Google)
- PyYAML>=6.0.1 (konfiguracja)
- yfinance>=0.2.28 (Yahoo Finance) - ✅ ZAINSTALOWANE
- Flask>=3.0.0 (interfejs webowy) - do implementacji

### Bezpieczeństwo:
- credentials.json w katalogu secrets/ (ignorowany przez git)
- .gitignore zawiera wpis "secrets/" i "venv/"
- Wirtualne środowisko Python dla izolacji zależności

### Problemy techniczne napotkane i rozwiązane:
- PowerShell powodował błędy wyświetlania w terminalu - rozwiązane przez użycie zsh
- Ostrzeżenie SSL (LibreSSL vs OpenSSL) - nie wpływa na działanie
- Nazwy kolumn w danych nie pasowały do konfiguracji - rozwiązane przez debugowanie
- Formatowanie danych w Google Sheets (procenty, dolary) - rozwiązane przez poprawkę logiki
- Duplikaty nazw kolumn - rozwiązane przez naprawę importu
- Przesunięcie struktury danych w arkuszu - rozwiązane przez aktualizację importu

### Elastyczność:
- Reguły selekcji w pliku YAML (łatwe do edycji)
- Możliwość dodawania/usuwania kryteriów bez wpływu na historię
- W przyszłości: edytor webowy do zmiany reguł

## RÓŻNICE RÓL
- **Użytkownik (CEO):** Definiuje wymagania biznesowe, nie zna programowania
- **AI (Project Manager + Programista):** Odpowiada za implementację techniczną

## KOMUNIKACJA
- **Język:** Polski
- **Styl:** Krok po kroku, z wyjaśnieniami
- **Kontrola:** Użytkownik ma wpływ na każdy szczegół
- **Nauka:** Użytkownik chce się uczyć podczas tworzenia
- **Podejście:** "Lepiej mniej a dobrze niż dużo i z błędami"
- **Interfejs:** Minimalistyczny, prosty, funkcjonalny (wygląd nie jest priorytetem)

## NASTĘPNE KROKI
1. ✅ Uruchomić debug_columns.py aby zdiagnozować problem z nazwami kolumn
2. ✅ Poprawić plik konfiguracyjny reguł selekcji
3. ✅ Przetestować selekcję ponownie
4. ✅ Zweryfikować selekcję z ręczną selekcją użytkownika
5. ✅ Implementacja bazy danych SQLite z uproszczoną strukturą
6. ✅ Analiza Yahoo Finance i Stochastic Oscillator
7. ✅ Funkcje historii spółek
8. ✅ Czyszczenie projektu (usunięto niepotrzebne pliki)
9. 🔄 Implementacja interfejsu webowego Flask

## FUNKCJONALNOŚCI INTERFEJSU WEBOWEGO
- Prezentacja shortlisty i historii selekcji
- Możliwość przeglądania, filtrowania i wyszukiwania spółek/ETF-ów
- **WYŚWIETLANIE WYNIKÓW DLA WYBRANEJ DATY Z PRZESZŁOŚCI** - bardzo ważna funkcja
- Możliwość sprawdzenia, czy spółka XYZ była kiedykolwiek w kręgu zainteresowań i w jakich okresach

## WAŻNE USTALENIA
- **Parametry selekcji:** Kilkadziesiąt parametrów, muszą być elastyczne
- **Historia:** Dodawanie/usuwanie parametrów nie może wpływać na historyczne raportowanie
- **Edycja reguł:** W przyszłości prosty sposób edycji kolumn i wartości decydujących o selekcji
- **Backup:** Możliwość backupowania danych
- **Docker:** Aplikacja ma działać w kontenerze Docker

## WERYFIKACJA SELEKCJI (ZAKTUALIZOWANA)
- **Data:** Lipiec 2025
- **Status:** ✅ ZWERYFIKOWANE
- **Porównanie:** Automatyczna selekcja vs ręczna selekcja użytkownika
- **Wynik:** 17 spółek (po aktualizacji danych)
- **Wybrane spółki:** ARE, BHB, BKH, BMY, BEP, EMN, EPD, FRT, HRL, MAA, NNN, NWN, O, PFE, TGT, UPS, VZ
- **Etap 2:** 5 spółek spełnia warunki Stochastic Oscillator
- **Final Selection:** BHB, BKH, HRL, NNN, NWN

## PLAN DWUETAPOWEJ SELEKCJI
### Koncepcja:
1. **Etap Selekcji 1 - DK Rating xls** - obecne warunki z Google Sheet
2. **Etap Selekcji 2 - Yahoo Finance i obliczenia** - dodatkowe dane i wskaźniki
3. **Etap Selekcji 3 - Ostateczna selekcja** - filtrowanie na podstawie warunków z Etapu 2

### SZCZEGÓŁY ETAPU 2 - YAHOO FINANCE I OBLICZENIA:
#### Stochastic Oscillator:
- **Parametry:** Period 36, Smoothing Factor 12, SMA 12
- **Wykresy:** 1 miesiąc i 1 tydzień
- **Warunek:** Wartości poniżej 30%
- **Logika:** **Przynajmniej jeden** z warunków musi być spełniony:
  - Stochastic 1 miesiąc < 30% **LUB** Stochastic 1 tydzień < 30%
- **Przykłady:**
  ```
  Spółka | Stochastic_1M | Stochastic_1W | Etap2_Status
  ARE    | 25%           | 45%           | ✅ (1M < 30%)
  BHB    | 45%           | 22%           | ✅ (1W < 30%)
  CVX    | 35%           | 40%           | ❌ (oba > 30%)
  ```

### PYTANIA NA NASTĘPNE SPOTKANIE:

#### 1. Zakres Etapu 2:
- Czy Etap 2 ma być wykonywany tylko dla spółek z Etapu 1, czy dla wszystkich spółek z arkusza?

#### 2. Dane z Yahoo Finance:
- Jakie konkretnie dane z Yahoo Finance chcesz pobierać? (np. cena, dywidenda, wskaźniki techniczne, P/E, P/B, etc.)

#### 3. Własne obliczenia:
- Jakie własne obliczenia/wskaźniki chcesz dodawać? (np. średnie kroczące, wskaźniki momentum, etc.)

#### 4. Warunki Etapu 3:
- Czy warunki w Etapie 3 będą podobne do obecnych (YAML), czy inne?
- Jakie konkretnie warunki chcesz stosować?

#### 5. Konfiguracja:
- Czy chcesz mieć możliwość włączenia/wyłączenia Etapu 3, czy zawsze ma być aktywny?

#### 6. Harmonogram:
- Czy wszystkie etapy mają być wykonywane raz dziennie, czy w różnym tempie?

#### 7. Baza danych:
- Jaką strukturę bazy danych preferujesz dla przechowywania wyników wszystkich etapów?

## UPROSZCZONA STRUKTURA BAZY DANYCH (LIPIEC 2025)

### **Tabele:**
1. **`analysis_runs`** - Historia uruchomień analizy
2. **`stage1_companies`** - Spółki Etapu 1 + dane Etapu 2 + status końcowy

### **Usunięte tabele (niepotrzebne):**
- ❌ `stage2_results` - dane przeniesione do `stage1_companies`
- ❌ `final_selection` - status przeniesiony do `stage1_companies`

### **Funkcje historii:**
- ✅ `get_company_history(ticker)` - historia konkretnej spółki
- ✅ `get_companies_by_date(date)` - spółki z konkretnej daty  
- ✅ `get_latest_run_date()` - data najnowszego uruchomienia

### **Przykłady użycia historii:**
```python
# Historia spółki BHB
history = db_manager.get_company_history("BHB")
# Wynik: 2025-07-28: Etap 1 ✅, Stochastic 1M=18.1%, 1W=16.7%

# Spółki z konkretnej daty
companies = db_manager.get_companies_by_date("2025-07-28")
# Wynik: 17 spółek z tej daty
```

## ZAKTUALIZOWANE ETAPY SELEKCJI

### **Etap 1 - Automatyczna selekcja (DK Rating xls)**
- ✅ Import danych z Google Sheet
- ✅ Aplikacja reguł selekcji
- ✅ Zapisywanie wyników do bazy danych

### **Etap 2 - Dodanie danych (Yahoo Finance)**
- ✅ Pobieranie danych z Yahoo Finance
- ✅ Obliczanie Stochastic Oscillator
- ✅ **NIE jest selekcją** - tylko dodanie danych
- ✅ Zapisywanie wyników do bazy danych

### **Etap 3 - Ostateczna selekcja (MANUALNA)**
- ⏳ **Wykonywana przez użytkownika**
- ✅ Dane przygotowane w bazie danych
- ✅ Możliwość analizy historycznej

## AKTUALNY STAN PROJEKTU (LIPIEC 2025)

### **DZIAŁAJĄCE FUNKCJONALNOŚCI:**
✅ **Etap 1:** Automatyczna selekcja z Google Sheet (17 spółek)  
✅ **Etap 2:** Analiza Yahoo Finance + Stochastic Oscillator (5 spółek)  
✅ **Baza danych:** SQLite z uproszczoną strukturą  
✅ **Funkcje historii:** Sprawdzanie historii spółek  
✅ **Dane informacyjne:** Date Edited, Company, Sector z Google Sheet  
✅ **Konfiguracja kolumn:** Edytowalna lista danych informacyjnych  
✅ **Testy:** Skrypty testowe działają poprawnie  

### **GŁÓWNY SKRYPT:**
```bash
python3 src/stage2_analysis.py
```

### **TESTY:**
```bash
python3 src/database_test.py      # Test bazy danych
python3 src/history_test.py       # Test funkcji historii
```

### **STRUKTURA BAZY DANYCH:**
- `analysis_runs` - historia uruchomień
- `stage1_companies` - wszystkie dane w jednym miejscu
  - **Dane selekcji:** country, quality_rating, yield_value, dividend_growth_streak, sp_credit_rating, dk_rating
  - **Dane informacyjne:** date_edited, company_name, sector
  - **Dane Etapu 2:** stochastic_1m, stochastic_1w, stage2_passed, final_selection

### **KONFIGURACJA KOLUMN DANYCH:**
- **Plik:** `config/data_columns.yaml`
- **Kolumny selekcji:** Nie zmieniaj bez konsultacji (country, quality_rating, yield, etc.)
- **Kolumny informacyjne:** Możesz edytować (date_edited, company, sector)
- **Przykład dodania kolumny informacyjnej:**
  ```yaml
  informational_columns:
    date_edited: "Date Edited"
    company: "Company"
    sector: "Sector"
    current_price: "Current Price"  # Dodaj tutaj
  ```

### **NASTĘPNE KROKI:**
1. **Interfejs webowy Flask** - prezentacja wyników
2. **Automatyzacja** - uruchamianie raz dziennie
3. **Backup** - kopie zapasowe
4. **Docker** - konteneryzacja

### **USUNIĘTE PLIKI (CZYSZCZENIE PROJEKTU):**
❌ `debug_yahoo_finance.py` - tymczasowy debug  
❌ `debug_user_stocks.py` - stary debug  
❌ `debug_columns.py` - stary debug  
❌ `debug_arkusz_structure.py` - stary debug  
❌ `debug_specific_stocks.py` - stary debug  
❌ `main_selection.py` - zastąpiony przez `stage2_analysis.py`  
❌ `stage2_results_*.csv` - stare wyniki (dane w bazie)

## **IMPLEMENTACJA WERSJONOWANIA - ZAKOŃCZONA ✅**

### **Zaimplementowane funkcje wersjonowania:**

#### **A. Struktura bazy danych z wersjonowaniem:**
- **Nowe tabele:** `selection_rules_versions`, `informational_columns_versions`
- **Nowe kolumny:** `selection_data` (JSON), `informational_data` (JSON) w `stage1_companies`
- **Wersjonowanie:** `selection_rules_version`, `informational_columns_version` w `analysis_runs`

#### **B. Automatyczne wykrywanie zmian:**
- **`detect_config_changes()`** - wykrywa zmiany w konfiguracji
- **Automatyczne tworzenie wersji** - v1.0, v1.1, v1.2, etc.
- **Integracja z analizą** - sprawdzanie zmian przed każdym uruchomieniem

#### **C. Nowe funkcje raportowania:**
- **`get_company_history_with_versions()`** - historia spółki z wersjami reguł
- **`get_version_details()`** - szczegóły konkretnej wersji
- **`get_all_versions()`** - lista wszystkich wersji
- **`get_analysis_history()`** - historia z wersjonowaniem

#### **D. Przetestowane scenariusze:**
- ✅ **Migracja istniejących danych** do nowej struktury
- ✅ **Wykrywanie zmian** w regułach selekcji
- ✅ **Automatyczne tworzenie wersji** v1.1 po dodaniu reguły
- ✅ **Zapisywanie danych w JSON** z elastyczną strukturą
- ✅ **Raporty z wersjonowaniem** - historia z dokładnymi regułami

#### **E. Przykład działania:**
```
Uruchomienie 1-5: v1.0 (początkowe reguły)
Uruchomienie 6: v1.0 (bez zmian)
Uruchomienie 7: v1.1 (po dodaniu nowej reguły)
```

**System jest gotowy do obsługi częstych zmian reguł (10-20 rocznie) z pełną historią!**

### **NOWE SKRYPTY TESTOWE:**
```bash
python3 src/test_versioning.py      # Test funkcji wersjonowania
python3 src/migrate_to_versioned_schema.py  # Migracja (jednorazowo)
```

---
*Dokumentacja utworzona: 2024*
*Ostatnia aktualizacja: Lipiec 2025*
*Projekt: Analizator Rynku - Selekcja Spółek*
*Status: Projekt z wersjonowaniem - gotowy do implementacji interfejsu webowego* 