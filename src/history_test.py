#!/usr/bin/env python3
"""
Skrypt testowy dla funkcji historii spółek
"""

import sys
import os
import pandas as pd

# Dodaj ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager

def test_company_history():
    """
    Testuje funkcje historii spółek
    """
    print("=== TEST FUNKCJI HISTORII SPÓŁEK ===")
    
    try:
        # Inicjalizuj menedżer bazy danych
        db_manager = DatabaseManager()
        print("✅ Baza danych zainicjalizowana")
        
        # Test 1: Historia konkretnej spółki
        print("\n=== TEST 1: Historia spółki BHB ===")
        bhb_history = db_manager.get_company_history("BHB", limit=5)
        
        if not bhb_history.empty:
            print(f"Znaleziono {len(bhb_history)} wpisów dla BHB:")
            for _, row in bhb_history.iterrows():
                print(f"  {row['run_date']}: {row['company_name']}")
                print(f"    Etap 1: Quality={row['quality_rating']}, Yield={row['yield_value']}")
                if row['stochastic_1m'] is not None:
                    print(f"    Etap 2: 1M={row['stochastic_1m']:.1f}%, 1W={row['stochastic_1w']:.1f}%")
                else:
                    print(f"    Etap 2: Błąd - {row['stage2_error']}")
                print()
        else:
            print("Brak historii dla BHB")
        
        # Test 2: Historia spółki która nie ma historii
        print("\n=== TEST 2: Historia spółki AAPL (nie ma w bazie) ===")
        aapl_history = db_manager.get_company_history("AAPL", limit=5)
        
        if not aapl_history.empty:
            print(f"Znaleziono {len(aapl_history)} wpisów dla AAPL")
        else:
            print("AAPL nie ma historii w bazie (oczekiwane)")
        
        # Test 3: Spółki z konkretnej daty
        print("\n=== TEST 3: Spółki z najnowszej daty ===")
        latest_date = db_manager.get_latest_run_date()
        if latest_date:
            print(f"Sprawdzam spółki z daty: {latest_date}")
            companies_by_date = db_manager.get_companies_by_date(latest_date)
            
            if not companies_by_date.empty:
                print(f"Znaleziono {len(companies_by_date)} spółek z {latest_date}:")
                for _, row in companies_by_date.iterrows():
                    print(f"  {row['ticker']}: {row['company_name']}")
            else:
                print(f"Brak spółek z daty {latest_date}")
        else:
            print("Nie udało się pobrać najnowszej daty")
        
        # Test 4: Spółki z nieistniejącej daty
        print("\n=== TEST 4: Spółki z nieistniejącej daty ===")
        fake_date = "2020-01-01"
        companies_fake_date = db_manager.get_companies_by_date(fake_date)
        
        if not companies_fake_date.empty:
            print(f"Znaleziono {len(companies_fake_date)} spółek z {fake_date}")
        else:
            print(f"Brak spółek z daty {fake_date} (oczekiwane)")
        
        print("\n✅ Test funkcji historii zakończony pomyślnie")
        
    except Exception as e:
        print(f"❌ Błąd podczas testu historii: {e}")
        import traceback
        traceback.print_exc()

def show_available_companies():
    """
    Pokazuje dostępne spółki w bazie
    """
    print("\n=== DOSTĘPNE SPÓŁKI W BAZIE ===")
    
    try:
        db_manager = DatabaseManager()
        
        # Pobierz najnowsze wyniki
        latest_results = db_manager.get_latest_results()
        
        if latest_results and 'stage1_companies' in latest_results:
            companies = latest_results['stage1_companies']
            if not companies.empty:
                print(f"Spółki z najnowszego uruchomienia ({len(companies)}):")
                for _, row in companies.iterrows():
                    print(f"  {row['ticker']}: {row['company_name']}")
            else:
                print("Brak spółek w najnowszym uruchomieniu")
        else:
            print("Brak najnowszych wyników")
            
    except Exception as e:
        print(f"❌ Błąd podczas pobierania spółek: {e}")

def main():
    """
    Główna funkcja
    """
    print("=== TEST FUNKCJI HISTORII ANALIZATORA RYNKU ===")
    
    # Pokaż dostępne spółki
    show_available_companies()
    
    # Test funkcji historii
    test_company_history()

if __name__ == "__main__":
    main() 