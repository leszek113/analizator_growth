#!/usr/bin/env python3
"""
Skrypt do czyszczenia danych historycznych z bazy danych
Zachowuje konfigurację, usuwa dane historyczne
"""

import sqlite3
import os
import sys
from datetime import datetime

def cleanup_database():
    """Czyści dane historyczne z bazy danych"""
    
    db_path = 'data/analizator_growth.db'
    
    if not os.path.exists(db_path):
        print("❌ Baza danych nie istnieje!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== CZYSZCZENIE BAZY DANYCH ===")
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Lista tabel do wyczyszczenia (dane historyczne)
        tables_to_clean = [
            'analysis_runs',           # Historia uruchomień analizy
            'stage1_companies',        # Spółki z selekcji
            'auto_schedule_runs',      # Historia uruchomień scheduler
            'flag_history',            # Historia zmian flag
            'company_flags',           # Aktualne flagi spółek
            'company_notes'            # Notatki spółek
        ]
        
        # Lista tabel do zachowania (konfiguracja)
        tables_to_keep = [
            'selection_rules_versions',        # Wersje reguł selekcji
            'informational_columns_versions',  # Wersje kolumn informacyjnych
            'stock_prices'                     # Dane historyczne cen (opcjonalnie)
        ]
        
        print("🗑️  USUWANE TABELE (dane historyczne):")
        for table in tables_to_clean:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count_before = cursor.fetchone()[0]
                
                cursor.execute(f'DELETE FROM {table}')
                deleted_count = cursor.rowcount
                
                print(f"  ✅ {table}: {count_before} → 0 rekordów (usunięto {deleted_count})")
                
            except Exception as e:
                print(f"  ❌ {table}: BŁĄD - {e}")
        
        print()
        print("💾 ZACHOWANE TABELE (konfiguracja):")
        for table in tables_to_keep:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} rekordów (zachowano)")
            except Exception as e:
                print(f"  ❌ {table}: BŁĄD - {e}")
        
        # Resetuj auto-increment ID
        print()
        print("🔄 RESETOWANIE AUTO-INCREMENT ID:")
        for table in tables_to_clean:
            try:
                cursor.execute(f'DELETE FROM sqlite_sequence WHERE name = "{table}"')
                print(f"  ✅ {table}: ID zresetowane")
            except Exception as e:
                print(f"  ❌ {table}: BŁĄD - {e}")
        
        # Zatwierdź zmiany
        conn.commit()
        
        print()
        print("=== PODSUMOWANIE ===")
        print("✅ Baza danych wyczyszczona pomyślnie!")
        print("✅ Konfiguracja zachowana")
        print("✅ Dane historyczne usunięte")
        print("✅ System gotowy do nowego startu")
        
        return True
        
    except Exception as e:
        print(f"❌ BŁĄD podczas czyszczenia bazy danych: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🧹 CZYSZCZENIE BAZY DANYCH - ANALIZATOR GROWTH")
    print("=" * 50)
    
    # Potwierdzenie
    response = input("Czy na pewno chcesz wyczyścić dane historyczne? (tak/nie): ")
    if response.lower() not in ['tak', 'yes', 'y']:
        print("❌ Anulowano czyszczenie bazy danych")
        sys.exit(0)
    
    success = cleanup_database()
    
    if success:
        print("\n🎉 CZYSZCZENIE ZAKOŃCZONE POMYŚLNIE!")
        print("System jest gotowy do nowego startu z czystą bazą danych.")
    else:
        print("\n💥 CZYSZCZENIE NIEUDANE!")
        print("Sprawdź logi błędów powyżej.")
        sys.exit(1)
