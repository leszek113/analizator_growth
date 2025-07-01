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
- **Struktura:** ~500 wierszy (dokładnie 488 po import), 135 kolumn
- **Nagłówki:** w 3. wierszu (indeks 2) - początkowo były w 1. wierszu, ale użytkownik poprawił arkusz
- **Autoryzacja:** Service Account (credentials.json w katalogu secrets/)
- **Udostępnienie:** Arkusz udostępniony do odczytu dla Service Account
- **Selekcja danych:** Pobieramy wszystkie dane, selekcję robimy w Pythonie

### 2. Yahoo Finance
- **Dane:** cena, historia dywidend, yield, wskaźniki techniczne (np. stochastic)
- **Biblioteka:** yfinance
- **Status:** Do implementacji
- **Konto:** Nie ma konta, korzystamy z ogólnodostępnych danych

## REGUŁY SELEKCJI (aktualne)

### Plik konfiguracyjny: `config/selection_rules.yaml`

1. **Country** = US, UK, CA
2. **Quality Rating** = 13 lub 12
3. **Yield** >= 4% brutto
4. **Dividend Growth Streak (Years)** >= 15
5. **5-Year Dividend Growth Rate CAGR** >= 300%
6. **S&P Credit Rating** = A* (każda wartość zaczynająca się od A) i tylko BBB+, BBB (bez BBB-)
7. **DK Rating** = "Potential Good to buy or better"

## STRUKTURA PROJEKTU
```
analizator_rynku/
├── src/
│   ├── import_google_sheet.py    # Import danych z Google Sheet
│   ├── stock_selector.py         # Logika selekcji spółek
│   ├── main_selection.py         # Główny skrypt selekcji
│   └── debug_columns.py          # Debug kolumn i wartości
├── config/
│   └── selection_rules.yaml      # Reguły selekcji (edytowalne)
├── secrets/
│   └── credentials.json          # Dane logowania Google API
├── static/                       # Pliki statyczne (CSS, JS)
├── templates/                    # Szablony HTML
├── docs/                         # Dokumentacja
├── tests/                        # Testy
└── .gitignore                    # Ignoruje katalog secrets/
```

## POSTĘP PROJEKTU

### ✅ ZROBIONE:
1. **Synchronizacja z GitHub** - repozytorium utworzone i połączone
2. **Konfiguracja Google API** - Service Account, credentials.json
3. **Import danych z Google Sheet** - działa, pobiera 488 spółek
4. **Plik konfiguracyjny reguł** - YAML z 7 regułami selekcji
5. **Moduł selekcji spółek** - StockSelector class
6. **Główny skrypt** - main_selection.py

### 🔧 PROBLEM DO ROZWIĄZANIA:
- **Selekcja nie działa** - wszystkie spółki są odrzucane (0 wyników)
- **Przyczyna:** Nazwy kolumn w danych nie pasują do tych w konfiguracji
- **Status:** Utworzony debug_columns.py do diagnozy

### 📋 DO ZROBIENIA:
1. **Naprawić selekcję** - dopasować nazwy kolumn
2. **Baza danych SQLite** - projekt i implementacja
3. **Pobieranie danych z Yahoo Finance**
4. **Interfejs webowy (Flask)**
5. **Automatyzacja (cron/systemd)**
6. **Backup**
7. **Docker**

## SZCZEGÓŁY TECHNICZNE

### Biblioteki Python:
- gspread (Google Sheets API)
- pandas (analiza danych)
- oauth2client (autoryzacja Google)
- yaml (konfiguracja)
- yfinance (Yahoo Finance) - do instalacji

### Bezpieczeństwo:
- credentials.json w katalogu secrets/ (ignorowany przez git)
- .gitignore zawiera wpis "secrets/"
- PowerShell odinstalowany z systemu (nie był potrzebny na macOS)

### Problemy techniczne napotkane:
- PowerShell powodował błędy wyświetlania w terminalu
- Ostrzeżenie SSL (LibreSSL vs OpenSSL) - nie wpływa na działanie
- Nazwy kolumn w danych nie pasują do konfiguracji - wymaga debugowania

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
1. Uruchomić debug_columns.py aby zdiagnozować problem z nazwami kolumn
2. Poprawić plik konfiguracyjny reguł selekcji
3. Przetestować selekcję ponownie
4. Przejść do implementacji bazy danych SQLite

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

---
*Dokumentacja utworzona: 2024*
*Projekt: Analizator Rynku - Selekcja Spółek*
*Status: W trakcie implementacji - problem z nazwami kolumn do rozwiązania* 