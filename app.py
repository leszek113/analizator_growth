#!/usr/bin/env python3
"""
Główna aplikacja Flask dla Analizatora Rynku
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os
import pandas as pd
import yaml
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database_manager import DatabaseManager
from src.stage2_analysis import main as run_analysis
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'analizator_rynku_secret_key'

# Inicjalizacja menedżera bazy danych
db_manager = DatabaseManager()

def load_config_files():
    """
    Ładuje pliki konfiguracyjne
    """
    try:
        logger.info("Ładowanie pliku selection_rules.yaml...")
        with open('config/selection_rules.yaml', 'r', encoding='utf-8') as f:
            selection_rules = yaml.safe_load(f)
        logger.info("Plik selection_rules.yaml załadowany pomyślnie")
        
        logger.info("Ładowanie pliku data_columns.yaml...")
        with open('config/data_columns.yaml', 'r', encoding='utf-8') as f:
            data_columns = yaml.safe_load(f)
        logger.info("Plik data_columns.yaml załadowany pomyślnie")
        
        return selection_rules, data_columns
    except FileNotFoundError as e:
        logger.error(f"Plik konfiguracyjny nie znaleziony: {e}")
        return None, None
    except yaml.YAMLError as e:
        logger.error(f"Błąd parsowania YAML: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
        return None, None

def save_config_files(selection_rules, data_columns):
    """
    Zapisuje pliki konfiguracyjne
    """
    try:
        with open('config/selection_rules.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(selection_rules, f, default_flow_style=False, allow_unicode=True)
        
        with open('config/data_columns.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(data_columns, f, default_flow_style=False, allow_unicode=True)
        
        return True
    except Exception as e:
        logger.error(f"Błąd podczas zapisywania konfiguracji: {e}")
        return False

@app.route('/')
def dashboard():
    """
    Strona główna z dashboardem
    """
    try:
        # Pobierz historię uruchomień
        history = db_manager.get_analysis_history(limit=10)
        
        # Pobierz najnowsze wyniki
        latest_results = db_manager.get_latest_results()
        
        # Pobierz statystyki
        today_run_info = db_manager.get_today_run_info()
        has_today_run = db_manager.has_today_run()
        
        stats = {
            'total_runs': len(history) if not history.empty else 0,
            'latest_run_date': history.iloc[0]['run_date'] if not history.empty else 'Brak',
            'latest_companies_count': len(latest_results) if not latest_results.empty else 0,
            'has_today_run': has_today_run,
            'today_run_info': today_run_info
        }
        
        return render_template('dashboard.html', 
                             latest_results=latest_results,
                             history=history,
                             stats=stats)
                             
    except Exception as e:
        logger.error(f"Błąd w dashboard: {e}")
        return render_template('error.html', error=str(e))

@app.route('/results')
def results():
    """Wyświetla wyniki analizy"""
    try:
        date_filter = request.args.get('date', '')
        ticker_filter = request.args.get('ticker', '')
        
        if date_filter:
            # Filtrowanie po dacie
            companies = db_manager.get_companies_by_date(date_filter)
        elif ticker_filter:
            # Filtrowanie po tickerze
            companies = db_manager.get_companies_by_ticker(ticker_filter)
        else:
            # Najnowsze wyniki
            companies = db_manager.get_latest_results()
        
        if companies.empty:
            logger.warning(f"Brak danych do wyświetlenia w tabeli wyników (companies DataFrame empty)")
            return render_template('results.html', companies=[], message="Brak danych do wyświetlenia")
        
        # Konwertuj DataFrame na listę słowników dla template
        companies_list = []
        for _, row in companies.iterrows():
            company_data = {
                'ticker': row['ticker'],
                'notes_count': row.get('notes_count', 0),
                'selection_data_parsed': row.get('selection_data_parsed', {}),
                'informational_data_parsed': row.get('informational_data_parsed', {}),
                'yield': row.get('yield'),
                'yield_netto': row.get('yield_netto'),
                'current_price': row.get('current_price'),
                'price_for_5_percent_yield': row.get('price_for_5_percent_yield'),
                'stochastic_1m': row.get('stochastic_1m'),
                'stochastic_1w': row.get('stochastic_1w'),
                'stage2_passed': row.get('stage2_passed')
            }
            companies_list.append(company_data)
        logger.info(f"Przekazuję do szablonu {len(companies_list)} spółek")
        return render_template('results.html', results=companies_list)
        
    except Exception as e:
        logger.error(f"Błąd w results: {e}")
        return render_template('results.html', companies=[], error=str(e))

@app.route('/history/<ticker>')
def company_history(ticker):
    """
    Historia konkretnej spółki
    """
    try:
        # Pobierz historię spółki
        history = db_manager.get_company_history_with_versions(ticker, limit=20)
        
        return render_template('company_history.html', 
                             ticker=ticker,
                             history=history)
                             
    except Exception as e:
        logger.error(f"Błąd w company_history: {e}")
        return render_template('error.html', error=str(e))

@app.route('/config')
def config():
    """
    Strona konfiguracji reguł
    """
    try:
        # Załaduj aktualne pliki konfiguracyjne
        selection_rules, data_columns = load_config_files()
        
        # Pobierz wersje (z obsługą błędów)
        try:
            selection_versions = db_manager.get_all_versions('selection')
            if selection_versions.empty:
                selection_versions = None
        except Exception as e:
            logger.warning(f"Błąd podczas pobierania wersji selekcji: {e}")
            selection_versions = None
            
        try:
            info_versions = db_manager.get_all_versions('informational')
            if info_versions.empty:
                info_versions = None
        except Exception as e:
            logger.warning(f"Błąd podczas pobierania wersji informacyjnych: {e}")
            info_versions = None
        
        return render_template('config.html',
                             selection_versions=selection_versions,
                             info_versions=info_versions,
                             selection_rules=selection_rules,
                             data_columns=data_columns)
                             
    except Exception as e:
        logger.error(f"Błąd w config: {e}")
        return render_template('error.html', error=str(e))

@app.route('/config/edit_selection_rules', methods=['GET', 'POST'])
def edit_selection_rules():
    """
    Edycja reguł selekcji
    """
    try:
        if request.method == 'POST':
            # Pobierz dane z formularza
            data = request.get_json()
            
            # Załaduj aktualną konfigurację
            selection_rules, data_columns = load_config_files()
            
            if selection_rules and data:
                # Aktualizuj reguły
                for rule_name, rule_data in data.items():
                    if rule_name in selection_rules['selection_rules']:
                        selection_rules['selection_rules'][rule_name].update(rule_data)
                
                # Zapisz zmiany
                if save_config_files(selection_rules, data_columns):
                    return jsonify({'success': True, 'message': 'Reguły zostały zaktualizowane'})
                else:
                    return jsonify({'success': False, 'message': 'Błąd podczas zapisywania'})
            
            return jsonify({'success': False, 'message': 'Nieprawidłowe dane'})
        
        else:
            # GET - wyświetl formularz edycji
            selection_rules, data_columns = load_config_files()
            return render_template('edit_selection_rules.html', 
                                 selection_rules=selection_rules)
                                 
    except Exception as e:
        logger.error(f"Błąd w edit_selection_rules: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/config/edit_info_columns', methods=['GET', 'POST'])
def edit_info_columns():
    """
    Edycja kolumn informacyjnych
    """
    try:
        if request.method == 'POST':
            # Pobierz dane z formularza
            data = request.get_json()
            
            # Załaduj aktualną konfigurację
            selection_rules, data_columns = load_config_files()
            
            if data_columns and data:
                # Aktualizuj kolumny informacyjne
                if 'informational_columns' in data:
                    data_columns['informational_columns'] = data['informational_columns']
                
                # Zapisz zmiany
                if save_config_files(selection_rules, data_columns):
                    return jsonify({'success': True, 'message': 'Kolumny zostały zaktualizowane'})
                else:
                    return jsonify({'success': False, 'message': 'Błąd podczas zapisywania'})
            
            return jsonify({'success': False, 'message': 'Nieprawidłowe dane'})
        
        else:
            # GET - wyświetl formularz edycji
            selection_rules, data_columns = load_config_files()
            return render_template('edit_info_columns.html', 
                                 data_columns=data_columns)
                                 
    except Exception as e:
        logger.error(f"Błąd w edit_info_columns: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/config/add_selection_rule', methods=['POST'])
def add_selection_rule():
    """
    Dodawanie nowej reguły selekcji
    """
    try:
        data = request.get_json()
        
        if not data or 'rule_name' not in data or 'rule_data' not in data:
            return jsonify({'success': False, 'message': 'Nieprawidłowe dane'})
        
        # Załaduj aktualną konfigurację
        selection_rules, data_columns = load_config_files()
        
        if selection_rules:
            # Dodaj nową regułę
            rule_name = data['rule_name']
            rule_data = data['rule_data']
            
            if rule_name not in selection_rules['selection_rules']:
                selection_rules['selection_rules'][rule_name] = rule_data
                
                # Zapisz zmiany
                if save_config_files(selection_rules, data_columns):
                    return jsonify({'success': True, 'message': f'Reguła {rule_name} została dodana'})
                else:
                    return jsonify({'success': False, 'message': 'Błąd podczas zapisywania'})
            else:
                return jsonify({'success': False, 'message': f'Reguła {rule_name} już istnieje'})
        
        return jsonify({'success': False, 'message': 'Błąd podczas ładowania konfiguracji'})
        
    except Exception as e:
        logger.error(f"Błąd w add_selection_rule: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/config/delete_selection_rule', methods=['POST'])
def delete_selection_rule():
    """
    Usuwanie reguły selekcji
    """
    try:
        data = request.get_json()
        
        if not data or 'rule_name' not in data:
            return jsonify({'success': False, 'message': 'Nieprawidłowe dane'})
        
        # Załaduj aktualną konfigurację
        selection_rules, data_columns = load_config_files()
        
        if selection_rules:
            rule_name = data['rule_name']
            
            if rule_name in selection_rules['selection_rules']:
                del selection_rules['selection_rules'][rule_name]
                
                # Zapisz zmiany
                if save_config_files(selection_rules, data_columns):
                    return jsonify({'success': True, 'message': f'Reguła {rule_name} została usunięta'})
                else:
                    return jsonify({'success': False, 'message': 'Błąd podczas zapisywania'})
            else:
                return jsonify({'success': False, 'message': f'Reguła {rule_name} nie istnieje'})
        
        return jsonify({'success': False, 'message': 'Błąd podczas ładowania konfiguracji'})
        
    except Exception as e:
        logger.error(f"Błąd w delete_selection_rule: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/config/add_info_column', methods=['POST'])
def add_info_column():
    """
    Dodawanie nowej kolumny informacyjnej
    """
    try:
        data = request.get_json()
        
        if not data or 'column_key' not in data or 'column_name' not in data:
            return jsonify({'success': False, 'message': 'Nieprawidłowe dane'})
        
        # Załaduj aktualną konfigurację
        selection_rules, data_columns = load_config_files()
        
        if data_columns:
            column_key = data['column_key']
            column_name = data['column_name']
            
            if column_key not in data_columns['informational_columns']:
                data_columns['informational_columns'][column_key] = column_name
                
                # Zapisz zmiany
                if save_config_files(selection_rules, data_columns):
                    return jsonify({'success': True, 'message': f'Kolumna {column_name} została dodana'})
                else:
                    return jsonify({'success': False, 'message': 'Błąd podczas zapisywania'})
            else:
                return jsonify({'success': False, 'message': f'Kolumna {column_key} już istnieje'})
        
        return jsonify({'success': False, 'message': 'Błąd podczas ładowania konfiguracji'})
        
    except Exception as e:
        logger.error(f"Błąd w add_info_column: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/config/delete_info_column', methods=['POST'])
def delete_info_column():
    """
    Usuwanie kolumny informacyjnej
    """
    try:
        data = request.get_json()
        
        if not data or 'column_key' not in data:
            return jsonify({'success': False, 'message': 'Nieprawidłowe dane'})
        
        # Załaduj aktualną konfigurację
        selection_rules, data_columns = load_config_files()
        
        if data_columns:
            column_key = data['column_key']
            
            if column_key in data_columns['informational_columns']:
                column_name = data_columns['informational_columns'][column_key]
                del data_columns['informational_columns'][column_key]
                
                # Zapisz zmiany
                if save_config_files(selection_rules, data_columns):
                    return jsonify({'success': True, 'message': f'Kolumna {column_name} została usunięta'})
                else:
                    return jsonify({'success': False, 'message': 'Błąd podczas zapisywania'})
            else:
                return jsonify({'success': False, 'message': f'Kolumna {column_key} nie istnieje'})
        
        return jsonify({'success': False, 'message': 'Błąd podczas ładowania konfiguracji'})
        
    except Exception as e:
        logger.error(f"Błąd w delete_info_column: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/run_analysis', methods=['POST'])
def run_analysis_route():
    """
    Uruchomienie analizy
    """
    try:
        # Uruchom analizę
        run_analysis()
        
        return jsonify({
            'success': True,
            'message': 'Analiza została uruchomiona pomyślnie'
        })
        
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania analizy: {e}")
        return jsonify({
            'success': False,
            'message': f'Błąd: {str(e)}'
        }), 500

@app.route('/api/companies')
def api_companies():
    """
    API endpoint dla spółek
    """
    try:
        latest_results = db_manager.get_latest_results()
        companies = latest_results.get('companies', []) if latest_results else []
        
        return jsonify({
            'success': True,
            'companies': companies
        })
        
    except Exception as e:
        logger.error(f"Błąd w API companies: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API dla notatek spółek
@app.route('/api/notes/<ticker>', methods=['GET'])
def get_company_notes(ticker):
    """Pobiera wszystkie notatki dla spółki"""
    try:
        notes = db_manager.get_company_notes(ticker)
        return jsonify({
            'success': True,
            'notes': notes.to_dict('records') if not notes.empty else []
        })
    except Exception as e:
        logger.error(f"Błąd podczas pobierania notatek dla {ticker}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/<ticker>/<int:note_number>', methods=['GET'])
def get_company_note(ticker, note_number):
    """Pobiera konkretną notatkę"""
    try:
        note = db_manager.get_company_note(ticker, note_number)
        if note:
            return jsonify({'success': True, 'note': note})
        else:
            return jsonify({'success': False, 'error': 'Notatka nie znaleziona'}), 404
    except Exception as e:
        logger.error(f"Błąd podczas pobierania notatki {note_number} dla {ticker}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/<ticker>', methods=['POST'])
def add_company_note(ticker):
    """Dodaje nową notatkę"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'error': 'Treść notatki jest wymagana'}), 400
        
        success = db_manager.add_company_note(ticker, title, content)
        if success:
            return jsonify({'success': True, 'message': 'Notatka dodana pomyślnie'})
        else:
            return jsonify({'success': False, 'error': 'Błąd podczas dodawania notatki'}), 500
    except Exception as e:
        logger.error(f"Błąd podczas dodawania notatki dla {ticker}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/<ticker>/<int:note_number>', methods=['PUT'])
def update_company_note(ticker, note_number):
    """Aktualizuje notatkę"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'error': 'Treść notatki jest wymagana'}), 400
        
        success = db_manager.update_company_note(ticker, note_number, title, content)
        if success:
            return jsonify({'success': True, 'message': 'Notatka zaktualizowana pomyślnie'})
        else:
            return jsonify({'success': False, 'error': 'Notatka nie znaleziona'}), 404
    except Exception as e:
        logger.error(f"Błąd podczas aktualizacji notatki {note_number} dla {ticker}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/<ticker>/<int:note_number>', methods=['DELETE'])
def delete_company_note(ticker, note_number):
    """Usuwa notatkę"""
    try:
        success = db_manager.delete_company_note(ticker, note_number)
        if success:
            return jsonify({'success': True, 'message': 'Notatka usunięta pomyślnie'})
        else:
            return jsonify({'success': False, 'error': 'Notatka nie znaleziona'}), 404
    except Exception as e:
        logger.error(f"Błąd podczas usuwania notatki {note_number} dla {ticker}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/<ticker>/count', methods=['GET'])
def get_company_notes_count(ticker):
    """Pobiera liczbę notatek dla spółki"""
    try:
        count = db_manager.get_company_notes_count(ticker)
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        logger.error(f"Błąd podczas pobierania liczby notatek dla {ticker}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Błąd serwera'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 