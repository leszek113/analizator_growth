#!/bin/bash

# Skrypt do zarządzania aplikacją Analizator Growth na macOS
# Użycie: ./scripts/manage-app.sh [start|stop|restart|status]

APP_NAME="com.leszek.analizator-growth"
APP_PORT=5002
PROJECT_DIR="${PROJECT_ROOT:-$(pwd)}"

# Kolory dla output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funkcja sprawdzająca czy aplikacja odpowiada
check_app() {
    if curl -f -s http://localhost:$APP_PORT/ > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Funkcja sprawdzająca procesy Python
check_processes() {
    ps aux | grep python | grep app.py | grep -v grep
}

# Funkcja wymuszenia zatrzymania
force_stop() {
    echo -e "${YELLOW}Wymuszanie zatrzymania procesów...${NC}"
    
    # Znajdź i zatrzymaj wszystkie procesy Python app.py
    PIDS=$(ps aux | grep python | grep app.py | grep -v grep | awk '{print $2}')
    
    if [ -n "$PIDS" ]; then
        echo "Znalezione procesy: $PIDS"
        for PID in $PIDS; do
            echo "Zatrzymuję proces $PID..."
            kill -TERM $PID 2>/dev/null
            sleep 2
            if kill -0 $PID 2>/dev/null; then
                echo "Wymuszanie zatrzymania procesu $PID..."
                kill -KILL $PID 2>/dev/null
            fi
        done
    else
        echo "Brak procesów do zatrzymania"
    fi
}

# Funkcja sprawdzenia statusu
status() {
    echo -e "${YELLOW}=== Status aplikacji Analizator Growth ===${NC}"
    
    # Sprawdź status usługi launchd
    echo -e "\n${YELLOW}Status usługi launchd:${NC}"
    launchctl list | grep $APP_NAME || echo "Usługa nie jest załadowana"
    
    # Sprawdź procesy
    echo -e "\n${YELLOW}Procesy Python:${NC}"
    PROCESSES=$(check_processes)
    if [ -n "$PROCESSES" ]; then
        echo "$PROCESSES"
    else
        echo "Brak uruchomionych procesów"
    fi
    
    # Sprawdź czy aplikacja odpowiada
    echo -e "\n${YELLOW}Test odpowiedzi aplikacji:${NC}"
    if check_app; then
        echo -e "${GREEN}✅ Aplikacja odpowiada na http://localhost:$APP_PORT${NC}"
    else
        echo -e "${RED}❌ Aplikacja nie odpowiada na http://localhost:$APP_PORT${NC}"
    fi
}

# Funkcja uruchomienia
start() {
    echo -e "${YELLOW}Uruchamianie aplikacji...${NC}"
    
    # Sprawdź czy już działa
    if check_app; then
        echo -e "${GREEN}Aplikacja już działa!${NC}"
        return 0
    fi
    
    # Zatrzymaj stare procesy jeśli istnieją
    force_stop
    
    # Przejdź do katalogu projektu
    cd "$PROJECT_DIR"
    
    # Aktywuj wirtualne środowisko i uruchom aplikację
    echo "Aktywuję wirtualne środowisko i uruchamiam aplikację..."
    nohup bash -c "source venv/bin/activate && python app.py" > logs/app.log 2>&1 &
    
    # Czekaj na uruchomienie
    echo "Czekam na uruchomienie aplikacji..."
    for i in {1..30}; do
        if check_app; then
            echo -e "${GREEN}✅ Aplikacja uruchomiona pomyślnie!${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Aplikacja nie uruchomiła się w ciągu 30 sekund${NC}"
    return 1
}

# Funkcja zatrzymania
stop() {
    echo -e "${YELLOW}Zatrzymywanie aplikacji...${NC}"
    
    # Sprawdź czy działa
    if ! check_app; then
        echo -e "${GREEN}Aplikacja już zatrzymana!${NC}"
        return 0
    fi
    
    # Zatrzymaj procesy bezpośrednio
    force_stop
    
    # Czekaj na zatrzymanie
    echo "Czekam na zatrzymanie aplikacji..."
    for i in {1..10}; do
        if ! check_app; then
            echo -e "${GREEN}✅ Aplikacja zatrzymana pomyślnie!${NC}"
            return 0
        fi
        sleep 1
    done
    
    # Sprawdź czy się zatrzymała
    if ! check_app; then
        echo -e "${GREEN}✅ Aplikacja zatrzymana pomyślnie!${NC}"
        return 0
    else
        echo -e "${RED}❌ Nie udało się zatrzymać aplikacji${NC}"
        return 1
    fi
}

# Funkcja restartu
restart() {
    echo -e "${YELLOW}Restartowanie aplikacji...${NC}"
    stop
    sleep 2
    start
}

# Główna logika
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Użycie: $0 {start|stop|restart|status}"
        echo ""
        echo "Komendy:"
        echo "  start   - Uruchom aplikację"
        echo "  stop    - Zatrzymaj aplikację"
        echo "  restart - Restartuj aplikację"
        echo "  status  - Pokaż status aplikacji"
        exit 1
        ;;
esac 