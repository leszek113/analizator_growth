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
        
        # Walidacja danych
        df = validate_google_sheet_data(df, config)
        
        logger.info(f"Pobrano {len(df)} spółek z Google Sheet")
        logger.info(f"Kolumny selekcji: {list(config['selection_columns'].values())}")
        logger.info(f"Kolumny informacyjne: {list(config['informational_columns'].values())}")
        
        return df
        
    except Exception as e:
        logger.error(f"Błąd podczas importu danych z Google Sheet: {e}")
        raise

def validate_google_sheet_data(df, config):
    """
    Waliduje dane z Google Sheet
    """
    try:
        # Sprawdź czy DataFrame nie jest pusty
        if df.empty:
            raise ValueError("DataFrame jest pusty")
        
        # Sprawdź wymagane kolumny
        required_columns = []
        required_columns.append(config['ticker_column'])
        required_columns.extend(config['selection_columns'].values())
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Brak wymaganych kolumn: {missing_columns}")
        
        # Usuń wiersze z pustymi tickerami
        initial_count = len(df)
        ticker_col = config['ticker_column']
        df = df.dropna(subset=[ticker_col])
        df = df[df[ticker_col].str.strip() != '']
        
        if len(df) < initial_count:
            logger.info(f"Usunięto {initial_count - len(df)} wierszy z pustymi tickerami")
        
        # Waliduj tickery (tylko litery, cyfry i kropki)
        import re
        valid_ticker_pattern = r'^[A-Za-z0-9.]+$'
        invalid_tickers = df[~df[ticker_col].str.match(valid_ticker_pattern, na=False)]
        
        if not invalid_tickers.empty:
            logger.warning(f"Znaleziono {len(invalid_tickers)} nieprawidłowych tickerów")
            for ticker in invalid_tickers[ticker_col].unique()[:5]:  # Pokaż tylko pierwsze 5
                logger.warning(f"  - {ticker}")
        
        # Waliduj Yield jeśli istnieje
        yield_col = config['selection_columns'].get('yield')
        if yield_col and yield_col in df.columns:
            df[yield_col] = pd.to_numeric(df[yield_col].astype(str).str.replace('%', ''), errors='coerce')
            invalid_yield = df[df[yield_col].isna() | (df[yield_col] < 0) | (df[yield_col] > 100)]
            
            if not invalid_yield.empty:
                logger.warning(f"Znaleziono {len(invalid_yield)} nieprawidłowych wartości Yield")
        
        # Waliduj Quality Rating jeśli istnieje
        quality_col = config['selection_columns'].get('quality_rating')
        if quality_col and quality_col in df.columns:
            df[quality_col] = pd.to_numeric(df[quality_col], errors='coerce')
            invalid_rating = df[df[quality_col].isna() | 
                              (df[quality_col] < 0) | 
                              (df[quality_col] > 13)]
            
            if not invalid_rating.empty:
                logger.warning(f"Znaleziono {len(invalid_rating)} nieprawidłowych wartości Quality Rating")
        
        logger.info(f"Walidacja zakończona. Pozostało {len(df)} wierszy")
        return df
        
    except Exception as e:
        logger.error(f"Błąd podczas walidacji danych: {e}")
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