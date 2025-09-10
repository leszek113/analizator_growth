#!/bin/bash
# Skrypt do automatycznej synchronizacji wersji Docker z VERSION

set -e

# Pobierz wersję z VERSION
VERSION=$(cat VERSION)
echo "🔄 Synchronizuję wersję Docker: $VERSION"

# Funkcja do aktualizacji pliku
update_docker_file() {
    local file=$1
    local pattern=$2
    local replacement=$3
    
    if [ -f "$file" ]; then
        echo "  📝 Aktualizuję $file"
        sed -i.bak "s/$pattern/$replacement/g" "$file"
        rm -f "$file.bak"
    else
        echo "  ⚠️  Plik $file nie istnieje"
    fi
}

# Aktualizuj docker-compose.yml
update_docker_file "docker-compose.yml" \
    "container_name: analizator-growth-[0-9]\+\.[0-9]\+\.[0-9]\+" \
    "container_name: analizator-growth-$VERSION"

# Aktualizuj docker-compose-ubuntu.yml
update_docker_file "docker-compose-ubuntu.yml" \
    "container_name: analizator-growth-[0-9]\+\.[0-9]\+\.[0-9]\+" \
    "container_name: analizator-growth-$VERSION"

# Aktualizuj Dockerfile
update_docker_file "Dockerfile" \
    "ENV APP_VERSION=\"v[0-9]\+\.[0-9]\+\.[0-9]\+\"" \
    "ENV APP_VERSION=\"v$VERSION\""

echo "✅ Synchronizacja wersji Docker zakończona: $VERSION"
