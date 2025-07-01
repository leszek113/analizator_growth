import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Ustawienia dostępu do Google Sheet
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_PATH = 'secrets/credentials.json'  # Ścieżka do pliku z danymi logowania
SHEET_NAME = '03_DK_Master_XLS_Source'  # Nazwa Twojego arkusza Google Sheet
WORKSHEET_NAME = 'DK'                   # Nazwa zakładki

# Autoryzacja i połączenie z Google Sheet
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
client = gspread.authorize(creds)

# Otwórz arkusz i zakładkę
sheet = client.open(SHEET_NAME)
worksheet = sheet.worksheet(WORKSHEET_NAME)

# Pobierz wszystkie dane jako listę list
data = worksheet.get_all_values()

# Użyj trzeciego wiersza jako nagłówków, pomiń pierwsze trzy wiersze
df = pd.DataFrame(data[3:], columns=data[2])  # Wiersz 3 (indeks 2) to nagłówki

# Wyświetl informacje o danych
print(f"Liczba wierszy: {len(df)}")
print(f"Liczba kolumn: {len(df.columns)}")
print("\nPierwsze 10 wierszy:")
print(df.head(10))

print("\nNazwy kolumn (pierwsze 20):")
print(df.columns[:20].tolist()) 