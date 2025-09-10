# Changelog

Wszystkie znaczące zmiany w projekcie Analizator Growth będą udokumentowane w tym pliku.

Format jest oparty na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt używa [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2025-09-10

### 🔧 Naprawione - Problemy ze startem aplikacji
- **Dodano python-dotenv** - automatyczne ładowanie zmiennych środowiskowych z pliku .env
- **Naprawiono skrypt zarządzania** - `manage-app.sh` teraz używa wirtualnego środowiska
- **Rozwiązano konflikty portów** - lepsze zarządzanie procesami Python
- **Poprawiono ładowanie konfiguracji** - aplikacja uruchamia się bez błędów

### 📚 Dodane - Dokumentacja
- **DEPLOYMENT_UBUNTU.md** - szczegółowe instrukcje wdrożenia na Ubuntu
- **docker-sync-version.sh** - skrypt synchronizacji wersji w Docker

### 🚀 Ulepszone - Stabilność
- **Aplikacja uruchamia się poprawnie** - wszystkie problemy ze startem rozwiązane
- **Gotowość produkcyjna** - system gotowy do wdrożenia

## [1.3.0] - 2025-09-09

### 🚀 Ulepszone - System zarządzania czasami
- **Timezone Best Practices** - implementacja międzynarodowych standardów zarządzania czasami
- **UTC w bazie danych** - wszystkie czasy zapisywane w UTC dla uniwersalności
- **CET w interfejsie** - automatyczna konwersja na czas polski dla użytkowników
- **Centralne utility functions** - `timezone_utils.py` z funkcjami do zarządzania czasami
- **Spójność czasów** - ujednolicone podejście w całym systemie

### 🧹 Zoptymalizowane - System
- **Usunięto generowanie CSV** - eliminacja niepotrzebnych plików CSV z selekcji
- **Czysta baza danych** - skrypt do czyszczenia danych historycznych
- **Zachowana konfiguracja** - reguły selekcji i ustawienia scheduler pozostają
- **Optymalizacja dysku** - brak śmiecenia po dysku niepotrzebnymi plikami

### ⏰ Zmienione - Scheduler
- **Czas selekcji** - zmieniono z 10:00 na 08:00 CET
- **Codzienne wykonywanie** - zadanie uruchamia się codziennie o 08:00 CET
- **Czas snapshot flag** - pozostaje 23:30 CET
- **Timezone handling** - poprawne zarządzanie strefami czasowymi

### 🔧 Naprawione - Timezone
- **Naprawiono 29 miejsc** z mieszanymi podejściami do czasu
- **Usunięto CURRENT_TIMESTAMP** - wszystkie timestampy explicit UTC
- **Zamieniono datetime.now()** - na get_utc_now() lub get_local_now()
- **Import handling** - naprawiono problemy z relative/absolute imports

### 📚 Dodane - Dokumentacja
- **docs/timezone-best-practices.md** - kompletna dokumentacja zarządzania czasami
- **README.md** - dodano sekcję o timezone practices
- **scripts/cleanup_database.py** - skrypt do czyszczenia bazy danych
- **Przykłady użycia** - jak prawidłowo używać funkcji timezone

## [1.2.4] - 2025-01-15

### 🚀 Ulepszone - Interfejs użytkownika
- **Natychmiastowa aktualizacja flag** - flagi zmieniają się od razu po zapisaniu
- **Invalidacja cache** - dodano automatyczne czyszczenie cache po zmianie flagi
- **Szybsze odświeżanie** - skrócono opóźnienie odświeżania strony z 1000ms na 200ms
- **Lepsze UX** - użytkownicy widzą zmiany flag natychmiast

### 🔧 Naprawione - Cache
- Naprawiono problem z opóźnionym wyświetlaniem flag w interfejsie
- Cache `latest_results` jest teraz invalidowany po każdej zmianie flagi
- Eliminuje problem z wyświetlaniem starych danych przez 5 minut

## [1.2.3] - 2025-01-15

### 🔧 Naprawione - Funkcjonalność
- Naprawiono obliczanie YieldNet 5% Price
- Dodano fallback na cenę z Google Sheets gdy Yahoo Finance nie działa
- Poprawiono logikę pobierania current_price
- YieldNet 5% Price teraz działa poprawnie
- Dodano szczegółowe logi procesu obliczeń

## [1.2.2] - 2025-01-15

### 📊 Dodane - Interfejs
- Dodano kolumnę DK VR do tabeli wyników
- Skrócone wartości: UVB (Ultra Value Buy), VSB (Very Strong Buy)
- Kolorowe badge dla lepszej czytelności (zielone dla UVB, niebieskie dla VSB)
- Zaktualizowano eksport CSV z nową kolumną DK VR
- Poprawiono sortowanie w DataTables po dodaniu nowej kolumny

## [1.2.1] - 2025-01-15

### 📈 Zmienione - Selekcja
- Zmieniono warunek selekcji z "DK Rating" na "DK Valuation Rating"
- Nowe wartości: "Ultra Value Buy", "Very Strong Buy" (zamiast "Potential Good Buy or Better")
- Bardziej restrykcyjne kryteria - tylko najlepsze okazje inwestycyjne
- Zaktualizowano konfigurację reguł selekcji i kolumn danych
- Zaktualizowano dokumentację z nowymi warunkami selekcji

## [1.2.0] - 2025-01-15

### 🔒 Dodane - Bezpieczeństwo
- Pełna walidacja danych wejściowych API (tickery, notatki, flagi, daty)
- Rate limiting dla endpointów API (100/h dla notatek, 50/h dla flag, 200/h ogólnie)
- Usunięto hardcoded API keys - dodano zmienne środowiskowe
- Ochrona przed atakami XSS i injection
- Walidacja formatów danych (regex dla tickerów, długość notatek)

### ⚡ Dodane - Wydajność
- System cache dla często używanych danych (TTL: 5 minut)
- Optymalizacja zapytań do bazy danych
- Automatyczne invalidowanie cache po zapisie nowych danych
- Indeksy SQL dla lepszej wydajności zapytań
- Metryki wydajności (cache hit rate, query time, memory usage)

### 🔧 Zmienione - Stabilność
- Naprawiono niezgodności wersji pakietów w requirements.txt
- Wyeliminowano duplikację kodu w modułach analizy
- Dodano funkcje pomocnicze w stage2_analysis.py
- Lepsze error handling i logowanie
- Spójne wersje zależności

### 📚 Dodane - Dokumentacja
- Uzupełniono dokumentację API i konfiguracji
- Dodano sekcję o bezpieczeństwie i wydajności
- Zaktualizowano README.md z nowymi funkcjami
- Dodano przykłady użycia zmiennych środowiskowych

### 🚀 Dodane - Produkcja
- Aplikacja gotowa do wdrożenia produkcyjnego
- Pełne zabezpieczenia i optymalizacje
- Rate limiting i walidacja danych
- System cache i monitoring wydajności

## [1.1.2] - 2025-09-08

### Dodane
- Nowe kolumny informacyjne: Current Price, Historical Fair Value, Market Cap z Google Sheets
- Implementacja obliczania 'Discount to Fair Value' w procentach
- Poprawka formatowania Market Cap w miliardach dolarów (np. $15.2 B)
- Naprawa sortowania kolumn 'Sto 36,12,12 1M' i 'Sto 36,12,12 1W'
- Aktualizacja konfiguracji DataTable z nowymi indeksami kolumn
- Poprawka obliczania Historical Fair Value (60205.16% = $602.05)
- Dodano funkcję czyszczenia bazy danych przed nową analizą
- Ulepszona dokumentacja i instrukcje użytkowania

## [1.1.1] - 2025-09-08

### Zmienione
- Zmiana nazwy projektu z 'analizator_rynku' na 'Analizator Growth'
- Nowe reguły selekcji dla spółek typu growth (bardzo restrykcyjne)
- Opcja B: N/A dla spółek z < 60 dni danych historycznych
- Naprawa wyświetlania N/A zamiast nan% w UI
- Zaktualizowane klucze API na bezpieczniejsze placeholder'y
- Dodane logi debugowania dla lepszego śledzenia procesu selekcji
- Zaktualizowana dokumentacja deployment'u

## [1.1.0] - 2025-09-07

### Dodane
- Nowy system danych historycznych
- Inteligentna aktualizacja danych (tylko nowe)
- Lokalne obliczanie Stochastic 36,12,12
- Agregacja danych dziennych do tygodniowych i miesięcznych
- Optymalizacja bazy danych (tylko dane dzienne)
- 5-letnia historia danych
- Naprawa błędów w obliczaniu Stochastic
- System wersjonowania aplikacji
- Ulepszone logowanie i monitoring
- Wersja wbudowana w obraz Docker
- Multi-arch support (linux/amd64 + linux/arm64)
- Automatyczne przenoszenie wersji z obrazem

## [1.0.0] - 2024-01-15

### Dodane
- Pierwsza wersja produkcyjna
- System selekcji spółek
- Analiza Stage 1 i Stage 2
- Interfejs webowy
- Integracja z Yahoo Finance
- System flag i notatek
- Automatyczne uruchamianie
- Eksport do CSV
