# Zarządzanie wersjami w Analizator Growth

## 🎯 Przegląd

Analizator Growth używa centralnego systemu zarządzania wersjami, który automatycznie synchronizuje wersje we wszystkich plikach projektu. To eliminuje problemy z niezgodnościami wersji i zapewnia spójność w całym projekcie.

## 📁 Struktura systemu wersjonowania

```
analizator_growth/
├── VERSION                    # Źródło prawdy - aktualna wersja
├── scripts/
│   ├── version_manager.py     # Główny mechanizm zarządzania wersjami
│   ├── update-version.sh      # Skrypt do aktualizacji wersji
│   └── install-plist.sh       # Skrypt do instalacji plist z zastępowaniem ścieżek
└── config/version.yaml        # Szczegółowe informacje o wersji
```

## 🚀 Szybki start

### Aktualizacja wersji

```bash
# Zwiększ patch version (1.2.3 -> 1.2.4)
./scripts/update-version.sh patch

# Zwiększ minor version (1.2.3 -> 1.3.0)
./scripts/update-version.sh minor

# Zwiększ major version (1.2.3 -> 2.0.0)
./scripts/update-version.sh major

# Zwiększ build number (1.2.3 build 0 -> 1.2.3 build 1)
./scripts/update-version.sh build
```

### Synchronizacja wersji

```bash
# Synchronizuj wersje we wszystkich plikach
source venv/bin/activate
python scripts/version_manager.py sync

# Sprawdź spójność wersji
python scripts/version_manager.py validate
```

## 📋 Pliki automatycznie synchronizowane

System automatycznie aktualizuje wersje w następujących plikach:

- `VERSION` - główny plik wersji
- `config/version.yaml` - szczegółowe informacje o wersji
- `README.md` - nagłówek i changelog
- `Dockerfile` - zmienne środowiskowe Docker
- `docker-compose.yml` - konfiguracja kontenera
- `docker-compose-ubuntu.yml` - konfiguracja Ubuntu
- `docker-entrypoint.sh` - komentarze i logi

## 🔧 Użycie zaawansowane

### Ręczne zarządzanie wersjami

```bash
# Aktywuj środowisko wirtualne
source venv/bin/activate

# Synchronizuj wszystkie pliki
python scripts/version_manager.py sync

# Sprawdź spójność
python scripts/version_manager.py validate

# Zwiększ wersję i automatycznie synchronizuj
python scripts/version_manager.py increment-patch
python scripts/version_manager.py increment-minor
python scripts/version_manager.py increment-major
python scripts/version_manager.py increment-build
```

### Instalacja plist z automatycznym zastępowaniem ścieżek

```bash
# Ustaw ścieżkę projektu
export PROJECT_ROOT="/path/to/analizator_growth"

# Zainstaluj plist z zastąpionymi ścieżkami
./scripts/install-plist.sh
```

## 📊 Format wersji

### Plik VERSION
```
1.2.3
```

### Plik config/version.yaml
```yaml
version:
  major: 1
  minor: 2
  patch: 3
  build: 0

info:
  name: "Analizator Growth"
  full_name: "Analizator Growth v1.2.3"
  release_date: "2025-01-15"
```

## 🔍 Walidacja wersji

System automatycznie sprawdza spójność wersji w następujących plikach:

- `config/version.yaml`
- `README.md`
- `Dockerfile`
- `docker-compose.yml`

### Przykład walidacji

```bash
source venv/bin/activate
python scripts/version_manager.py validate
```

**Wynik:**
```
INFO:__main__:Walidacja wersji we wszystkich plikach...
INFO:__main__:✅ Wszystkie wersje są spójne!
✅ Wszystkie wersje są spójne!
```

## 🚨 Rozwiązywanie problemów

### Problem: Niezgodne wersje

**Objawy:**
```
❌ Znaleziono problemy z wersjami:
  - README.md nie zawiera wersji 1.2.3
  - Dockerfile nie zawiera wersji 1.2.3
```

**Rozwiązanie:**
```bash
# Synchronizuj wszystkie pliki
source venv/bin/activate
python scripts/version_manager.py sync

# Sprawdź ponownie
python scripts/version_manager.py validate
```

### Problem: Błąd podczas aktualizacji

**Objawy:**
```
❌ Błąd podczas aktualizacji wersji!
```

**Rozwiązanie:**
1. Sprawdź czy jesteś w katalogu projektu
2. Sprawdź czy venv jest aktywne
3. Sprawdź uprawnienia do plików
4. Uruchom ponownie z `--verbose` jeśli dostępne

## 🔄 Workflow CI/CD

### Przed commitem

```bash
# Zwiększ wersję
./scripts/update-version.sh patch

# Sprawdź spójność
source venv/bin/activate
python scripts/version_manager.py validate

# Commit zmian
git add .
git commit -m "Bump version to $(cat VERSION)"
```

### W CI/CD

```bash
# Sprawdź spójność wersji
source venv/bin/activate
python scripts/version_manager.py validate

# Jeśli błąd, zatrzymaj build
if [ $? -ne 0 ]; then
    echo "❌ Niezgodne wersje - zatrzymuję build"
    exit 1
fi
```

## 📝 Najlepsze praktyki

1. **Zawsze używaj skryptów** - nie edytuj wersji ręcznie
2. **Sprawdzaj spójność** przed commitem
3. **Używaj odpowiedniego typu wersji**:
   - `patch` - bugfixy
   - `minor` - nowe funkcje
   - `major` - breaking changes
   - `build` - rebuild bez zmian funkcjonalnych
4. **Commituj zmiany wersji** razem z kodem
5. **Testuj po aktualizacji** wersji

## 🎯 Korzyści

- ✅ **Eliminuje błędy** - automatyczna synchronizacja
- ✅ **Oszczędza czas** - jeden skrypt zamiast ręcznej edycji
- ✅ **Zapewnia spójność** - wszystkie pliki zawsze zsynchronizowane
- ✅ **Łatwe w użyciu** - proste komendy
- ✅ **Walidacja** - automatyczne sprawdzanie spójności
- ✅ **CI/CD ready** - gotowe do automatyzacji

---

**Ostatnia aktualizacja:** 2025-01-15  
**Wersja dokumentacji:** 1.0.0
