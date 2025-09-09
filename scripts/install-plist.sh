#!/bin/bash

# Skrypt do instalacji pliku plist z automatycznym zastępowaniem ścieżek
# Użycie: ./scripts/install-plist.sh

# Kolory dla output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Sprawdź czy PROJECT_ROOT jest ustawione
if [ -z "$PROJECT_ROOT" ]; then
    PROJECT_ROOT=$(pwd)
    echo -e "${YELLOW}PROJECT_ROOT nie jest ustawione, używam: $PROJECT_ROOT${NC}"
fi

echo -e "${YELLOW}Instalacja pliku plist dla Analizator Growth...${NC}"

# Sprawdź czy plik źródłowy istnieje
if [ ! -f "com.leszek.analizator-growth.plist" ]; then
    echo -e "${RED}❌ Nie znaleziono pliku com.leszek.analizator-growth.plist${NC}"
    exit 1
fi

# Utwórz tymczasowy plik z zastąpionymi ścieżkami
TEMP_PLIST="/tmp/com.leszek.analizator-growth.plist"
sed "s|{{PROJECT_ROOT}}|$PROJECT_ROOT|g" com.leszek.analizator-growth.plist > "$TEMP_PLIST"

# Sprawdź czy katalog LaunchAgents istnieje
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo -e "${YELLOW}Tworzenie katalogu LaunchAgents...${NC}"
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Skopiuj plik do LaunchAgents
echo -e "${YELLOW}Kopiowanie pliku do LaunchAgents...${NC}"
cp "$TEMP_PLIST" "$LAUNCH_AGENTS_DIR/com.leszek.analizator-growth.plist"

# Załaduj usługę
echo -e "${YELLOW}Ładowanie usługi...${NC}"
launchctl load "$LAUNCH_AGENTS_DIR/com.leszek.analizator-growth.plist"

# Usuń tymczasowy plik
rm "$TEMP_PLIST"

echo -e "${GREEN}✅ Plik plist został zainstalowany pomyślnie!${NC}"
echo -e "${GREEN}✅ Usługa została załadowana${NC}"
echo ""
echo "Dostępne komendy:"
echo "  launchctl start com.leszek.analizator-growth    # Uruchom"
echo "  launchctl stop com.leszek.analizator-growth     # Zatrzymaj"
echo "  launchctl unload ~/Library/LaunchAgents/com.leszek.analizator-growth.plist  # Usuń"
echo ""
echo "Lub użyj skryptu zarządzania:"
echo "  ./scripts/manage-app.sh start|stop|restart|status"
