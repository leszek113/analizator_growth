# Security Policy

## 🔒 Bezpieczeństwo Analizator Growth

### Wspierane wersje

| Wersja | Wsparcie bezpieczeństwa |
| ------- | ----------------------- |
| 1.2.x   | ✅ Pełne wsparcie       |
| 1.1.x   | ⚠️ Ograniczone wsparcie |
| < 1.1   | ❌ Brak wsparcia        |

### Zgłaszanie luk bezpieczeństwa

Jeśli znalazłeś lukę bezpieczeństwa w Analizator Growth, proszę:

1. **NIE** publikuj jej publicznie
2. Wyślij email na: security@analizator-growth.com
3. Opisz szczegółowo problem
4. Dołącz kroki reprodukcji (jeśli możliwe)

Odpowiemy w ciągu 48 godzin.

### Zabezpieczenia w wersji 1.2.0+

#### Walidacja danych wejściowych
- **Tickery**: Regex `^[A-Za-z0-9.]+$` - tylko litery, cyfry i kropki
- **Notatki**: Max 1000 znaków, ochrona przed XSS
- **Flagi**: Walidacja kolorów i długości notatek (max 40 znaków)
- **Daty**: Format YYYY-MM-DD z walidacją
- **API**: Wszystkie dane wejściowe są walidowane

#### Rate Limiting
- **API Notes**: 100 żądań/godzinę na IP
- **API Flags**: 50 żądań/godzinę na IP
- **API General**: 200 żądań/godzinę na IP
- **Sliding window**: Automatyczne czyszczenie starych żądań

#### Autoryzacja
- **API Key**: Wymagany dla chronionych endpointów
- **Zmienne środowiskowe**: Wszystkie klucze w zmiennych środowiskowych
- **Brak hardcoded credentials**: Usunięto wszystkie hardcoded klucze

#### Ochrona przed atakami
- **XSS**: Walidacja i escapowanie danych wejściowych
- **Injection**: Parametryzowane zapytania SQL
- **CSRF**: Tokeny CSRF w formularzach
- **DDoS**: Rate limiting i monitoring

### Najlepsze praktyki

#### Dla deweloperów
1. **Zawsze waliduj dane wejściowe**
2. **Używaj parametrów w zapytaniach SQL**
3. **Escape'uj dane wyjściowe**
4. **Regularnie aktualizuj zależności**
5. **Używaj HTTPS w produkcji**

#### Dla administratorów
1. **Ustaw silne API keys**
2. **Regularnie rotuj klucze**
3. **Monitoruj logi aplikacji**
4. **Używaj firewall**
5. **Regularnie aktualizuj aplikację**

### Konfiguracja bezpieczeństwa

#### Zmienne środowiskowe
```bash
# API Security
API_KEY=your_very_strong_secret_key_here

# Google Sheets (bezpieczne)
GOOGLE_CREDENTIALS_PATH=secrets/credentials.json
GOOGLE_SHEET_NAME=your_sheet_name
GOOGLE_WORKSHEET_NAME=your_worksheet_name

# Yahoo Finance (opcjonalne)
YAHOO_FINANCE_API_KEY=your_yahoo_api_key
```

#### Firewall
```bash
# Zezwól tylko na port 5002
ufw allow 5002/tcp

# Blokuj dostęp z zewnątrz (opcjonalne)
ufw deny from any to any port 5002
```

#### HTTPS (produkcja)
```bash
# Użyj reverse proxy (nginx/apache)
# z certyfikatem SSL
```

### Monitoring bezpieczeństwa

#### Logi do monitorowania
- `logs/analizator-growth-error.log` - Błędy aplikacji
- `logs/analizator-growth.log` - Główne logi
- Rate limiting logs - w logach aplikacji

#### Metryki bezpieczeństwa
- Liczba odrzuconych żądań (rate limiting)
- Błędy walidacji danych
- Nieudane próby autoryzacji
- Czas odpowiedzi API

### Aktualizacje bezpieczeństwa

#### Automatyczne
- Rate limiting działa automatycznie
- Walidacja danych jest wbudowana
- Cache automatycznie się czyści

#### Ręczne
- Regularnie aktualizuj zależności
- Monitoruj logi błędów
- Sprawdzaj nowe wersje aplikacji

### Kontakt

- **Email**: security@analizator-growth.com
- **GitHub Issues**: Tylko dla problemów nie-bezpieczeństwa
- **Discord**: #security channel

---

**Ostatnia aktualizacja**: 2025-01-15
**Wersja**: 1.2.0
