import gspread
import pandas as pd
import yaml
from oauth2client.service_account import ServiceAccountCredentials
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data_columns_config():
    """
    Ładuje konfigurację kolumn danych
    """
    try:
        with open('config/data_columns.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logger.error(f"Błąd podczas ładowania konfiguracji kolumn: {e}")
        raise

def import_google_sheet_data():
    """
    Importuje dane z Google Sheet z podziałem na kolumny selekcji i informacyjne
    """
    try:
        # Załaduj konfigurację kolumn
        config = load_data_columns_config()
        
        # Ustawienia dostępu do Google Sheet
        SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        CREDS_PATH = 'secrets/credentials.json'
        SHEET_NAME = '03_DK_Master_XLS_Source'
        WORKSHEET_NAME = 'DK'
        
        # Autoryzacja i połączenie z Google Sheet
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
        client = gspread.authorize(creds)
        
        # Otwórz arkusz i zakładkę
        sheet = client.open(SHEET_NAME)
        worksheet = sheet.worksheet(WORKSHEET_NAME)
        
        # Pobierz wszystkie dane
        data = worksheet.get_all_values()
        
        # Użyj wiersza 4 (indeks 4) jako nagłówków, pomiń pierwsze 5 wierszy
        # Napraw duplikaty nazw kolumn
        headers = data[4]
        unique_headers = []
        for i, header in enumerate(headers):
            if header in unique_headers:
                unique_headers.append(f"{header}_{i}")
            else:
                unique_headers.append(header)
        
        df = pd.DataFrame(data[5:], columns=unique_headers)
        
        # Sprawdź czy wszystkie wymagane kolumny są obecne
        required_columns = []
        required_columns.append(config['ticker_column'])
        required_columns.extend(config['selection_columns'].values())
        required_columns.extend(config['informational_columns'].values())
        
        missing_columns = []
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            logger.warning(f"Brakujące kolumny: {missing_columns}")
            logger.info(f"Dostępne kolumny: {list(df.columns)}")
        
        logger.info(f"Pobrano {len(df)} spółek z Google Sheet")
        logger.info(f"Kolumny selekcji: {list(config['selection_columns'].values())}")
        logger.info(f"Kolumny informacyjne: {list(config['informational_columns'].values())}")
        
        return df
        
    except Exception as e:
        logger.error(f"Błąd podczas importu danych z Google Sheet: {e}")
        raise

def main():
    """Test funkcji importu"""
    print("=== TEST IMPORTU DANYCH Z GOOGLE SHEET ===\n")
    
    df = import_google_sheet_data()
    
    print(f"Zaimportowano {len(df)} spółek z {len(df.columns)} kolumnami")
    print(f"Kolumny: {list(df.columns)[:10]}...")  # Pierwsze 10 kolumn
    print(f"Pierwsze 3 spółki:")
    print(df[['Ticker', 'Company', 'Country']].head(3).to_string(index=False))

if __name__ == "__main__":
    main() 