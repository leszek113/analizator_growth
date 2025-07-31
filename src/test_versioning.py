#!/usr/bin/env python3
"""
Test funkcji wersjonowania w bazie danych
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
import pandas as pd

def test_versioning_functions():
    """
    Testuje funkcje wersjonowania
    """
    print("=== TEST FUNKCJI WERSJONOWANIA ===")
    
    try:
        db_manager = DatabaseManager()
        
        # Test 1: Historia uruchomień z wersjonowaniem
        print("\n1. Historia uruchomień z wersjonowaniem:")
        history = db_manager.get_analysis_history(limit=5)
        if not history.empty:
            print(history[['run_id', 'run_date', 'stage1_count', 'selection_rules_version', 'informational_columns_version']].to_string())
        else:
            print("Brak danych w historii")
        
        # Test 2: Wszystkie wersje reguł selekcji
        print("\n2. Wersje reguł selekcji:")
        selection_versions = db_manager.get_all_versions('selection')
        if not selection_versions.empty:
            print(selection_versions.to_string())
        else:
            print("Brak wersji reguł selekcji")
        
        # Test 3: Wszystkie wersje kolumn informacyjnych
        print("\n3. Wersje kolumn informacyjnych:")
        info_versions = db_manager.get_all_versions('informational')
        if not info_versions.empty:
            print(info_versions.to_string())
        else:
            print("Brak wersji kolumn informacyjnych")
        
        # Test 4: Szczegóły wersji v1.0
        print("\n4. Szczegóły wersji v1.0 (selekcja):")
        version_details = db_manager.get_version_details('selection', 'v1.0')
        if version_details:
            print(f"Wersja: {version_details['version']}")
            print(f"Utworzona: {version_details['created_at']}")
            print(f"Opis: {version_details['description']}")
            print("Reguły:")
            for rule_name, rule_config in version_details['data'].items():
                print(f"  {rule_name}: {rule_config}")
        else:
            print("Nie znaleziono wersji v1.0")
        
        # Test 5: Historia konkretnej spółki z wersjonowaniem
        print("\n5. Historia spółki z wersjonowaniem (pierwsze 3 spółki):")
        companies = db_manager.get_latest_results()
        if companies and 'companies' in companies and not companies['companies'].empty:
            first_companies = companies['companies'].head(3)
            for _, company in first_companies.iterrows():
                ticker = company['ticker']
                print(f"\nHistoria spółki {ticker}:")
                history = db_manager.get_company_history_with_versions(ticker, limit=3)
                if not history.empty:
                    for _, record in history.iterrows():
                        print(f"  {record['run_date']}: v{record['selection_rules_version']} (selekcja), v{record['informational_columns_version']} (info)")
                        if record['selection_data_parsed']:
                            print(f"    Dane selekcji: {record['selection_data_parsed']}")
                        if record['informational_data_parsed']:
                            print(f"    Dane informacyjne: {record['informational_data_parsed']}")
                else:
                    print(f"  Brak historii dla {ticker}")
        
        # Test 6: Wykrywanie zmian w konfiguracji
        print("\n6. Wykrywanie zmian w konfiguracji:")
        changes = db_manager.detect_config_changes()
        print(f"Zmiany w regułach selekcji: {changes['selection_changed']}")
        print(f"Zmiany w kolumnach informacyjnych: {changes['info_changed']}")
        if changes['new_selection_version']:
            print(f"Nowa wersja selekcji: {changes['new_selection_version']}")
        if changes['new_info_version']:
            print(f"Nowa wersja informacyjna: {changes['new_info_version']}")
        
        print("\n✅ Test wersjonowania zakończony pomyślnie!")
        
    except Exception as e:
        print(f"❌ Błąd podczas testowania: {e}")
        import traceback
        traceback.print_exc()

def test_json_data_structure():
    """
    Testuje strukturę danych JSON
    """
    print("\n=== TEST STRUKTURY DANYCH JSON ===")
    
    try:
        db_manager = DatabaseManager()
        
        # Pobierz najnowsze wyniki
        latest_results = db_manager.get_latest_results()
        
        if latest_results and 'companies' in latest_results and not latest_results['companies'].empty:
            print("Przykładowe dane JSON z najnowszego uruchomienia:")
            
            # Pokaż pierwsze 3 spółki
            for i, (_, company) in enumerate(latest_results['companies'].head(3).iterrows()):
                print(f"\nSpółka {i+1}: {company['ticker']}")
                
                # Sprawdź czy są dane JSON
                if 'selection_data' in company and company['selection_data']:
                    import json
                    selection_data = json.loads(company['selection_data'])
                    print(f"  Dane selekcji (JSON): {selection_data}")
                
                if 'informational_data' in company and company['informational_data']:
                    import json
                    info_data = json.loads(company['informational_data'])
                    print(f"  Dane informacyjne (JSON): {info_data}")
                
                # Pokaż też stare kolumny (jeśli istnieją)
                old_columns = ['country', 'quality_rating', 'yield_value', 'company_name', 'sector']
                old_data = {col: company.get(col, 'N/A') for col in old_columns if col in company}
                if old_data:
                    print(f"  Stare kolumny: {old_data}")
        
        print("\n✅ Test struktury JSON zakończony!")
        
    except Exception as e:
        print(f"❌ Błąd podczas testowania JSON: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Główna funkcja
    """
    print("=== TEST WERSJONOWANIA BAZY DANYCH ===")
    
    # Test funkcji wersjonowania
    test_versioning_functions()
    
    # Test struktury JSON
    test_json_data_structure()

if __name__ == "__main__":
    main() 