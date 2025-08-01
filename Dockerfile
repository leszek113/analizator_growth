# Analizator Rynku v1.0 - Docker Image
FROM python:3.11-slim

# Ustawienie zmiennych środowiskowych
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Ustawienie katalogu roboczego
WORKDIR /app

# Instalacja systemowych zależności
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie plików requirements
COPY requirements.txt .

# Instalacja zależności Python
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu aplikacji
COPY . .

# Tworzenie katalogów dla danych
RUN mkdir -p /app/data /app/logs /app/secrets

# Ustawienie uprawnień
RUN chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 5001

# Entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"] 