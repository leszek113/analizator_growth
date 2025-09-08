#!/bin/bash

# Analizator Growth v1.1.2 - Docker Entrypoint
set -e

echo "🚀 Uruchamianie Analizatora Growth v1.1.2..."

# Sprawdzenie czy istnieją pliki konfiguracyjne
if [ ! -f "/app/config/selection_rules.yaml" ]; then
    echo "⚠️  Brak pliku selection_rules.yaml - używam domyślnej konfiguracji"
fi

if [ ! -f "/app/config/data_columns.yaml" ]; then
    echo "⚠️  Brak pliku data_columns.yaml - używam domyślnej konfiguracji"
fi

# Sprawdzenie czy istnieją credentials Google Sheets
if [ ! -f "/app/secrets/credentials.json" ]; then
    echo "⚠️  Brak pliku credentials.json - Google Sheets może nie działać"
fi

# Inicjalizacja bazy danych (jeśli nie istnieje)
echo "📊 Inicjalizacja bazy danych..."
python3 -c "
from src.database_manager import DatabaseManager
db = DatabaseManager()
db.init_database()
print('✅ Baza danych zainicjalizowana')
"

# Uruchomienie aplikacji Flask
echo "🌐 Uruchamianie serwera Flask na porcie 5002..."
exec python3 app.py 