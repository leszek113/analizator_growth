import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from stock_selector import StockSelector

def import_google_sheet_data():
    """Importuje dane z Google Sheet"""
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
    
    # Użyj trzeciego wiersza jako nagłówków, pomiń pierwsze trzy wiersze
    df = pd.DataFrame(data[3:], columns=data[2])
    
    return df

def main():
    """Główna funkcja - import danych i selekcja spółek"""
    print("=== ANALIZATOR RYNKU - SELEKCJA SPÓŁEK ===\n")
    
    # 1. Import danych z Google Sheet
    print("1. Importuję dane z Google Sheet...")
    df = import_google_sheet_data()
    print(f"   Zaimportowano {len(df)} spółek z {len(df.columns)} kolumnami\n")
    
    # 2. Selekcja spółek
    print("2. Rozpoczynam selekcję spółek...")
    selector = StockSelector()
    selected_stocks = selector.select_stocks(df)
    
    # 3. Podsumowanie
    summary = selector.get_selection_summary(df, selected_stocks)
    print(f"\n=== PODSUMOWANIE SELEKCJI ===")
    print(f"Początkowa liczba spółek: {summary['original_count']}")
    print(f"Spółek po selekcji: {summary['filtered_count']}")
    print(f"Usunięto spółek: {summary['removed_count']}")
    print(f"Procent przejścia selekcji: {summary['selection_rate']}%")
    
    # 4. Wyświetlenie wyników
    if len(selected_stocks) > 0:
        print(f"\n=== WYBRANE SPÓŁKI ({len(selected_stocks)}) ===")
        # Wyświetl podstawowe informacje o wybranych spółkach
        display_columns = ['Ticker', 'Company', 'Country', 'Yield', 'Quality Rating (out Of 13)', 
                          'Dividend Growth Streak (Years)', '5-Year Dividend Growth Rate CAGR', 
                          'S&P Credit Rating', 'DK Rating']
        
        # Sprawdź które kolumny istnieją
        available_columns = [col for col in display_columns if col in selected_stocks.columns]
        
        print(selected_stocks[available_columns].to_string(index=False))
    else:
        print("\nBrak spółek spełniających kryteria selekcji.")
    
    return selected_stocks

if __name__ == "__main__":
    main() 