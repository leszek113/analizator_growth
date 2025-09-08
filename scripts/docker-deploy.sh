#!/bin/bash

# Skrypt do deployment na Docker Hub
# Użycie: ./scripts/docker-deploy.sh [build|push|deploy]

# Konfiguracja
DOCKER_USERNAME="leszek113"
IMAGE_NAME="analizator-growth"
VERSION="v1.1.0"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
LATEST_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:latest"

# Kolory dla output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funkcja logowania
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Funkcja sprawdzania Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker nie jest zainstalowany${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker nie jest uruchomiony${NC}"
        exit 1
    fi
    
    log "✅ Docker jest dostępny"
}

# Funkcja logowania do Docker Hub
docker_login() {
    log "Sprawdzam logowanie do Docker Hub..."
    
    if docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
        log "✅ Już zalogowany do Docker Hub"
    else
        log "Logowanie do Docker Hub..."
        docker login
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Błąd logowania do Docker Hub${NC}"
            exit 1
        fi
    fi
}

# Funkcja budowania obrazu
build_image() {
    log "Budowanie obrazu Docker..."
    
    # Sprawdź czy Dockerfile istnieje
    if [ ! -f "Dockerfile" ]; then
        echo -e "${RED}❌ Dockerfile nie istnieje${NC}"
        exit 1
    fi
    
    # Build obrazu
    docker build -t $FULL_IMAGE_NAME -t $LATEST_IMAGE_NAME .
    
    if [ $? -eq 0 ]; then
        log "✅ Obraz zbudowany pomyślnie: $FULL_IMAGE_NAME"
        log "✅ Obraz zbudowany pomyślnie: $LATEST_IMAGE_NAME"
    else
        echo -e "${RED}❌ Błąd budowania obrazu${NC}"
        exit 1
    fi
}

# Funkcja push do Docker Hub
push_image() {
    log "Wysyłanie obrazu do Docker Hub..."
    
    # Push wersji
    docker push $FULL_IMAGE_NAME
    if [ $? -eq 0 ]; then
        log "✅ Wersja $VERSION wysłana pomyślnie"
    else
        echo -e "${RED}❌ Błąd wysyłania wersji $VERSION${NC}"
        exit 1
    fi
    
    # Push latest
    docker push $LATEST_IMAGE_NAME
    if [ $? -eq 0 ]; then
        log "✅ Wersja latest wysłana pomyślnie"
    else
        echo -e "${RED}❌ Błąd wysyłania wersji latest${NC}"
        exit 1
    fi
}

# Funkcja pełnego deployment
deploy() {
    log "Rozpoczynam pełny deployment..."
    
    check_docker
    docker_login
    build_image
    push_image
    
    log "🎉 Deployment zakończony pomyślnie!"
    log "Obrazy dostępne na Docker Hub:"
    log "  - $FULL_IMAGE_NAME"
    log "  - $LATEST_IMAGE_NAME"
    
    echo -e "\n${GREEN}📋 Instrukcje deployment na Ubuntu:${NC}"
    echo "1. docker pull $FULL_IMAGE_NAME"
    echo "2. docker-compose down"
    echo "3. docker-compose up -d"
}

# Funkcja wyświetlania pomocy
show_help() {
    echo "Użycie: $0 {build|push|deploy|help}"
    echo ""
    echo "Komendy:"
    echo "  build  - Zbuduj obraz Docker"
    echo "  push   - Wyślij obraz do Docker Hub"
    echo "  deploy - Pełny deployment (build + push)"
    echo "  help   - Pokaż tę pomoc"
    echo ""
    echo "Przykład:"
    echo "  $0 deploy"
}

# Główna logika
case "$1" in
    build)
        check_docker
        build_image
        ;;
    push)
        check_docker
        docker_login
        push_image
        ;;
    deploy)
        deploy
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Nieznana komenda: $1${NC}"
        show_help
        exit 1
        ;;
esac
