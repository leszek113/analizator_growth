#!/usr/bin/env python3
"""
Skrypt do analizy Etapu 2 - Yahoo Finance i obliczenia
Analizuje spółki z Etapu 1 pod kątem warunków Stochastic Oscillator
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Dodaj ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from import_google_sheet import import_google_sheet_data
from stock_selector import StockSelector
from yahoo_finance_analyzer import YahooFinanceAnalyzer
from database_manager import DatabaseManager

def get_stage1_stocks():
    """
    Pobiera spółki z Etapu 1 (DK Rating xls)
    """
    print("=== ETAP 1 - Pobieranie spółek z Google Sheet ===")
    
    try:
        # Import danych z Google Sheet
        df = import_google_sheet_data()
        print(f"Pobrano {len(df)} spółek z Google Sheet")
        
        # Zastosuj reguły selekcji
        selector = StockSelector()
        selected_df = selector.select_stocks(df)
        
        # Wyciągnij listę tickerów
        if 'Ticker' in selected_df.columns:
            tickers = selected_df['Ticker'].tolist()
        elif 'Ticker_3' in selected_df.columns:  # W przypadku duplikatów kolumn
            tickers = selected_df['Ticker_3'].tolist()
        else:
            print("Błąd: Nie znaleziono kolumny z tickerami")
            return [], selected_df
        
        print(f"Etap 1: Wybrano {len(tickers)} spółek")
        print(f"Spółki z Etapu 1: {', '.join(tickers)}")
        
        return tickers, selected_df
        
    except Exception as e:
        print(f"Błąd podczas Etapu 1: {e}")
        return [], pd.DataFrame()

def analyze_stage2(stage1_stocks):
    """
    Analizuje spółki z Etapu 1 pod kątem warunków Etapu 2
    """
    print("\n=== ETAP 2 - Analiza Yahoo Finance i Stochastic Oscillator ===")
    
    if not stage1_stocks:
        print("Brak spółek z Etapu 1 do analizy")
        return pd.DataFrame()
    
    try:
        # Inicjalizuj analizator
        analyzer = YahooFinanceAnalyzer()
        
        # Analizuj wszystkie spółki
        results_df = analyzer.analyze_stage2_stocks(stage1_stocks)
        
        # Wyświetl wyniki
        print(f"\nWyniki analizy Etapu 2:")
        print(f"Przeanalizowano {len(results_df)} spółek")
        
        # Spółki z dobrymi warunkami Stochastic (dane informacyjne)
        stage2_passed = results_df[results_df['stage2_passed'] == True]
        print(f"Etap 2: {len(stage2_passed)} spółek ma dobre warunki Stochastic")
        
        if not stage2_passed.empty:
            print("\nSpółki z dobrymi warunkami Stochastic:")
            for _, row in stage2_passed.iterrows():
                ticker = row['ticker']
                stoch_1m = row['stochastic_1m']
                stoch_1w = row['stochastic_1w']
                condition_1m = "✅" if row['condition_1m'] else "❌"
                condition_1w = "✅" if row['condition_1w'] else "❌"
                
                print(f"  {ticker}: 1M={stoch_1m:.1f}% {condition_1m}, 1W={stoch_1w:.1f}% {condition_1w}")
        
        # Spółki z gorszymi warunkami Stochastic (dane informacyjne)
        stage2_failed = results_df[results_df['stage2_passed'] == False]
        if not stage2_failed.empty:
            print(f"\nSpółki z gorszymi warunkami Stochastic ({len(stage2_failed)}):")
            for _, row in stage2_failed.iterrows():
                ticker = row['ticker']
                stoch_1m = row['stochastic_1m']
                stoch_1w = row['stochastic_1w']
                error = row['error']
                
                if error:
                    print(f"  {ticker}: BŁĄD - {error}")
                else:
                    print(f"  {ticker}: 1M={stoch_1m:.1f}%, 1W={stoch_1w:.1f}% (oba > 30%)")
        
        return results_df
        
    except Exception as e:
        print(f"Błąd podczas Etapu 2: {e}")
        return pd.DataFrame()

def get_final_selection(stage1_stocks, stage2_results):
    """
    Zwraca listę spółek które przeszły Etap 1 (jedyna prawdziwa selekcja)
    Etap 2 to tylko dane informacyjne
    """
    print("\n=== WYNIK KOŃCOWY - Spółki które przeszły Etap 1 ===")
    
    # Etap 1 to jedyna prawdziwa selekcja
    final_stocks = stage1_stocks.copy()
    
    print(f"Spółki które przeszły Etap 1 (selekcja): {len(final_stocks)}")
    if final_stocks:
        print(f"Lista: {', '.join(final_stocks)}")
    else:
        print("Brak spółek spełniających Etap 1")
    
    # Dodatkowe informacje o Etapie 2 (tylko informacyjne)
    if not stage2_results.empty:
        stage2_passed = stage2_results[stage2_results['stage2_passed'] == True]
        print(f"\nDodatkowe informacje - Etap 2 (dane informacyjne):")
        print(f"Spółki z dobrymi warunkami Stochastic: {len(stage2_passed)}")
        if not stage2_passed.empty:
            stage2_tickers = stage2_passed['ticker'].tolist()
            print(f"Lista: {', '.join(stage2_tickers)}")
    
    return final_stocks

def save_results(stage1_stocks, stage2_results, final_stocks):
    """
    Zapisuje wyniki do pliku CSV
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stage2_results_{timestamp}.csv"
    
    try:
        # Przygotuj dane do zapisu
        results_to_save = stage2_results.copy()
        results_to_save['stage1_passed'] = results_to_save['ticker'].isin(stage1_stocks)
        results_to_save['final_selection'] = results_to_save['ticker'].isin(final_stocks)  # Etap 1 to finalna selekcja
        
        # Dodaj timestamp
        results_to_save['analysis_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zapisz do CSV
        results_to_save.to_csv(filename, index=False)
        print(f"\nWyniki zapisane do: {filename}")
        
    except Exception as e:
        print(f"Błąd podczas zapisywania wyników: {e}")

def main():
    """
    Główna funkcja z wersjonowaniem
    """
    print("=== ANALIZATOR RYNKU - ETAP 2 (Z WERSJONOWANIEM) ===")
    print(f"Data analizy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Inicjalizuj menedżer bazy danych
    db_manager = DatabaseManager()
    
    # Sprawdź zmiany w konfiguracji
    print("\n0. SPRAWDZANIE ZMIAN W KONFIGURACJI...")
    changes = db_manager.detect_config_changes()
    if changes['selection_changed']:
        print(f"⚠️  Wykryto zmiany w regułach selekcji - utworzono wersję: {changes['new_selection_version']}")
    if changes['info_changed']:
        print(f"⚠️  Wykryto zmiany w kolumnach informacyjnych - utworzono wersję: {changes['new_info_version']}")
    if not changes['selection_changed'] and not changes['info_changed']:
        print("✅ Brak zmian w konfiguracji")
    
    # Etap 1 - Pobierz spółki
    stage1_stocks, stage1_df = get_stage1_stocks()
    
    if not stage1_stocks:
        print("Brak spółek z Etapu 1. Kończę analizę.")
        return
    
    # Etap 2 - Analizuj Yahoo Finance
    stage2_results = analyze_stage2(stage1_stocks)
    
    if stage2_results.empty:
        print("Brak wyników z Etapu 2. Kończę analizę.")
        return
    
    # Wynik końcowy
    final_stocks = get_final_selection(stage1_stocks, stage2_results)
    
    # Zapisz wyniki do bazy danych
    try:
        # Utwórz nowe uruchomienie analizy (z wersjonowaniem)
        run_id = db_manager.create_analysis_run(
            selected_count=len(final_stocks),  # Etap 1 to jedyna selekcja
            notes="Analiza: Etap 1 (selekcja) + Etap 2 (dane informacyjne)"
        )
        
        # Zapisz spółki Etapu 1 z danymi selekcji i informacjami o Etapie 2 (z JSON)
        db_manager.save_stage1_companies(run_id, stage1_df, stage2_results)
        
        print(f"\n✅ Wszystkie wyniki zapisane do bazy danych (run_id: {run_id})")
        
    except Exception as e:
        print(f"❌ Błąd podczas zapisywania do bazy danych: {e}")
    
    # Zapisz wyniki do CSV (dodatkowo)
    save_results(stage1_stocks, stage2_results, final_stocks)
    
    print("\n=== ANALIZA ZAKOŃCZONA ===")

if __name__ == "__main__":
    main() 