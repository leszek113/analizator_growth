#!/bin/bash

# Skrypt do aktualizacji wersji projektu
# Użycie: ./scripts/update-version.sh [patch|minor|major|build]

# Kolory dla output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Sprawdź czy podano argument
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Użycie: $0 [patch|minor|major|build]${NC}"
    echo ""
    echo "Przykłady:"
    echo "  $0 patch    # 1.2.3 -> 1.2.4"
    echo "  $0 minor    # 1.2.3 -> 1.3.0"
    echo "  $0 major    # 1.2.3 -> 2.0.0"
    echo "  $0 build    # 1.2.3 build 0 -> 1.2.3 build 1"
    exit 1
fi

VERSION_TYPE=$1

# Sprawdź czy jesteśmy w katalogu projektu
if [ ! -f "VERSION" ]; then
    echo -e "${RED}❌ Nie znaleziono pliku VERSION. Uruchom skrypt z katalogu projektu.${NC}"
    exit 1
fi

# Sprawdź czy Python i venv są dostępne
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Nie znaleziono katalogu venv. Uruchom najpierw: python3 -m venv venv${NC}"
    exit 1
fi

echo -e "${YELLOW}Aktualizacja wersji: $VERSION_TYPE${NC}"

# Aktywuj venv i uruchom version_manager
source venv/bin/activate

# Uruchom odpowiednią komendę
case $VERSION_TYPE in
    patch)
        echo -e "${YELLOW}Zwiększanie patch version...${NC}"
        python scripts/version_manager.py increment-patch
        ;;
    minor)
        echo -e "${YELLOW}Zwiększanie minor version...${NC}"
        python scripts/version_manager.py increment-minor
        ;;
    major)
        echo -e "${YELLOW}Zwiększanie major version...${NC}"
        python scripts/version_manager.py increment-major
        ;;
    build)
        echo -e "${YELLOW}Zwiększanie build number...${NC}"
        python scripts/version_manager.py increment-build
        ;;
    *)
        echo -e "${RED}❌ Nieznany typ wersji: $VERSION_TYPE${NC}"
        echo "Dostępne opcje: patch, minor, major, build"
        exit 1
        ;;
esac

# Sprawdź czy aktualizacja się powiodła
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Wersja została zaktualizowana pomyślnie!${NC}"
    
    # Pokaż aktualną wersję
    CURRENT_VERSION=$(cat VERSION)
    echo -e "${GREEN}Aktualna wersja: $CURRENT_VERSION${NC}"
    
    # Waliduj spójność
    echo -e "${YELLOW}Walidacja spójności wersji...${NC}"
    python scripts/version_manager.py validate
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Wszystkie wersje są spójne!${NC}"
    else
        echo -e "${RED}❌ Znaleziono problemy ze spójnością wersji!${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Błąd podczas aktualizacji wersji!${NC}"
    exit 1
fi
