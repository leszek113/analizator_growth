#!/usr/bin/env python3
"""
Skrypt testowy do sprawdzenia działania bazy danych
"""

import sys
import os
import pandas as pd

# Dodaj ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager

def test_database():
    """
    Testuje funkcjonalność bazy danych
    """
    print("=== TEST BAZY DANYCH ===")
    
    try:
        # Inicjalizuj menedżer bazy danych
        db_manager = DatabaseManager()
        print("✅ Baza danych zainicjalizowana")
        
        # Sprawdź historię uruchomień
        print("\n=== HISTORIA URUCHOMIEŃ ===")
        history = db_manager.get_analysis_history(limit=5)
        
        if history.empty:
            print("Brak historii uruchomień")
        else:
            print(f"Znaleziono {len(history)} uruchomień:")
            for _, row in history.iterrows():
                print(f"  ID: {row['run_id']}, Data: {row['run_date']}")
                print(f"    Etap 1: {row['stage1_count']}, Etap 2: {row['stage2_count']}, Final: {row['final_count']}")
                print(f"    Status: {row['status']}, Notatki: {row['notes']}")
                print()
        
        # Sprawdź najnowsze wyniki
        print("=== NAJNOWSZE WYNIKI ===")
        latest_results = db_manager.get_latest_results()
        
        if not latest_results:
            print("Brak najnowszych wyników")
        else:
            run_info = latest_results['run_info']
            print(f"Ostatnie uruchomienie (ID: {run_info['run_id']}):")
            print(f"  Data: {run_info['run_date']}")
            print(f"  Etap 1: {run_info['stage1_count']} spółek")
            print(f"  Etap 2: {run_info['stage2_count']} spółek")
            print(f"  Final: {run_info['final_count']} spółek")
            
            # Spółki Etapu 1 z danymi selekcji i informacjami o Etapie 2
            stage1_companies = latest_results['stage1_companies']
            if not stage1_companies.empty:
                print(f"\n  Spółki Etapu 1 z danymi selekcji ({len(stage1_companies)}):")
                for _, row in stage1_companies.iterrows():
                    stage2_status = "✅" if row['stage2_passed'] else "❌"
                    final_status = "🎯" if row['final_selection'] else ""
                    print(f"    {row['ticker']}: {row['company_name']} {final_status}")
                    print(f"      Etap 1: Quality={row['quality_rating']}, Yield={row['yield_value']}, DK={row['dk_rating']}")
                    if row['stochastic_1m'] is not None:
                        print(f"      Etap 2: 1M={row['stochastic_1m']:.1f}%, 1W={row['stochastic_1w']:.1f}% {stage2_status}")
                    else:
                        print(f"      Etap 2: Błąd - {row['stage2_error']}")
                    print()
            
            # Ostateczna selekcja
            final_selection = latest_results['final_selection']
            if not final_selection.empty:
                print(f"\n  🎯 Ostateczna selekcja ({len(final_selection)} spółek):")
                for _, row in final_selection.iterrows():
                    print(f"    {row['ticker']}: {row['company_name']}")
                    print(f"      Stochastic: 1M={row['stochastic_1m']:.1f}%, 1W={row['stochastic_1w']:.1f}%")
            else:
                print(f"\n  🎯 Ostateczna selekcja: Brak spółek")
            
            # Podsumowanie Etapu 2
            stage2_passed = stage1_companies[stage1_companies['stage2_passed'] == True]
            if not stage2_passed.empty:
                print(f"\n  Etap 2 - Spółki które przeszły ({len(stage2_passed)}):")
                for _, row in stage2_passed.iterrows():
                    print(f"    {row['ticker']}: 1M={row['stochastic_1m']:.1f}%, 1W={row['stochastic_1w']:.1f}%")
        
        print("\n✅ Test bazy danych zakończony pomyślnie")
        
    except Exception as e:
        print(f"❌ Błąd podczas testu bazy danych: {e}")
        import traceback
        traceback.print_exc()

def show_database_structure():
    """
    Pokazuje strukturę bazy danych
    """
    print("=== STRUKTURA BAZY DANYCH ===")
    
    try:
        import sqlite3
        
        with sqlite3.connect("market_analyzer.db") as conn:
            cursor = conn.cursor()
            
            # Pokaż wszystkie tabele
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"Znalezione tabele ({len(tables)}):")
            for table in tables:
                table_name = table[0]
                print(f"\n📋 Tabela: {table_name}")
                
                # Pokaż strukturę tabeli
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    pk_mark = " 🔑" if pk else ""
                    not_null_mark = " NOT NULL" if not_null else ""
                    print(f"    {col_name}: {col_type}{not_null_mark}{pk_mark}")
                
                # Pokaż liczbę wierszy
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"    Liczba wierszy: {count}")
        
        print("\n✅ Struktura bazy danych wyświetlona")
        
    except Exception as e:
        print(f"❌ Błąd podczas wyświetlania struktury: {e}")

def main():
    """
    Główna funkcja
    """
    print("=== TEST BAZY DANYCH ANALIZATORA RYNKU ===")
    
    # Pokaż strukturę bazy danych
    show_database_structure()
    
    # Test funkcjonalności
    test_database()

if __name__ == "__main__":
    main() 