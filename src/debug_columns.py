import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def import_google_sheet_data():
    """Importuje dane z Google Sheet"""
    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    CREDS_PATH = 'secrets/credentials.json'
    SHEET_NAME = '03_DK_Master_XLS_Source'
    WORKSHEET_NAME = 'DK'
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
    client = gspread.authorize(creds)
    
    sheet = client.open(SHEET_NAME)
    worksheet = sheet.worksheet(WORKSHEET_NAME)
    
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[3:], columns=data[2])
    
    return df

def main():
    print("=== DEBUG - SPRAWDZANIE KOLUMN I WARTOŚCI ===\n")
    
    df = import_google_sheet_data()
    
    # Sprawdź kolumny związane z naszymi regułami
    target_columns = [
        'Country',
        'Quality Rating (out Of 13)',
        'Yield',
        'Dividend Growth Streak (Years)',
        '5-Year Dividend Growth Rate CAGR',
        'S&P Credit Rating',
        'DK Rating'
    ]
    
    print("Kolumny w danych:")
    for i, col in enumerate(df.columns):
        if any(target in col for target in ['Country', 'Quality', 'Yield', 'Dividend', 'S&P', 'DK']):
            print(f"  {i}: '{col}'")
    
    print("\nSprawdzenie konkretnych kolumn:")
    for col in target_columns:
        if col in df.columns:
            print(f"\n'{col}':")
            print(f"  Typ danych: {df[col].dtype}")
            print(f"  Unikalne wartości (pierwsze 10): {df[col].unique()[:10]}")
            print(f"  Przykładowe wartości (pierwsze 5): {df[col].head().tolist()}")
        else:
            print(f"\n'{col}': NIE ZNALEZIONA")
            # Szukaj podobnych nazw
            similar = [c for c in df.columns if any(word in c for word in col.split())]
            if similar:
                print(f"  Podobne kolumny: {similar}")
    
    # Sprawdź pierwsze kilka wierszy dla kluczowych kolumn
    print("\n=== PIERWSZE 5 WIERSZY DLA KLUCZOWYCH KOLUMN ===")
    key_cols = ['Ticker', 'Company', 'Country']
    available_key_cols = [col for col in key_cols if col in df.columns]
    if available_key_cols:
        print(df[available_key_cols].head())

if __name__ == "__main__":
    main() 