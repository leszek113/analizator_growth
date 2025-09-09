#!/usr/bin/env python3
"""
Główna aplikacja Flask dla Analizatora Growth
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os
import pandas as pd
import yaml
import re
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database_manager import DatabaseManager
from src.stage2_analysis import main as run_analysis
from src.auto_scheduler import get_auto_scheduler, init_auto_scheduler
from src.config_loader import get_api_key, is_api_auth_enabled, get_version_string, get_full_version_string, get_app_name, get_app_description
from src.rate_limiter import rate_limit
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'analizator_growth_secret_key_change_in_production')

# Inicjalizuj auto scheduler na start aplikacji
init_auto_scheduler()

# Inicjalizacja menedżera bazy danych
db_manager = DatabaseManager()

# ===== FUNKCJE WALIDACYJNE =====

def validate_ticker(ticker):
    """
    Waliduje format tickera
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Ticker może zawierać tylko litery, cyfry i kropki
    pattern = r'^[A-Za-z0-9.]+$'
    return bool(re.match(pattern, ticker.strip()))

def validate_note_content(content):
    """
    Waliduje treść notatki
    """
    if not content or not isinstance(content, str):
        return False
    
    # Sprawdź długość (max 1000 znaków)
    if len(content.strip()) > 1000:
        return False
    
    # Sprawdź czy nie zawiera niebezpiecznych znaków
    dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
    content_lower = content.lower()
    for pattern in dangerous_patterns:
        if pattern in content_lower:
            return False
    
    return True

def validate_flag_color(color):
    """
    Waliduje kolor flagi
    """
    valid_colors = ['red', 'green', 'yellow', 'blue', 'none']
    return color in valid_colors

def validate_date_format(date_str):
    """
    Waliduje format daty (YYYY-MM-DD)
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_api_request():
    """
    Waliduje żądanie API (sprawdza autoryzację)
    """
    if not is_api_auth_enabled():
        return True, None
    
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return False, "Brak klucza API"
    
    if api_key != get_api_key():
        return False, "Nieprawidłowy klucz API"
    
    return True, None

@app.context_processor
def inject_globals():
    """Wstrzykuje globalne zmienne do wszystkich szablonów"""
    return {
        'current_year': datetime.now().year,
        'app_name': get_app_name(),
        'app_description': get_app_description(),
        'version': get_version_string(),
        'full_version': get_full_version_string()
    }

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
                             latest_results={'stage1_companies': latest_results},
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
        show_all = request.args.get('show_all', 'false').lower() == 'true'
        
        # Określ typ widoku i datę dla nagłówka
        view_type = 'latest'
        view_date = ''
        
        if date_filter:
            # Filtrowanie po dacie
            companies = db_manager.get_companies_by_date(date_filter)
            view_type = 'date'
            view_date = date_filter
        elif ticker_filter:
            # Filtrowanie po tickerze
            companies = db_manager.get_companies_by_ticker(ticker_filter)
            view_type = 'ticker'
            view_date = ticker_filter
        elif show_all:
            # Wszystkie selekcje
            companies = db_manager.get_all_results()
            view_type = 'all'
        else:
            # Najnowsze wyniki
            companies = db_manager.get_latest_results()
            view_type = 'latest'
            view_date = db_manager.get_latest_run_date()
        
        if companies.empty:
            logger.warning(f"Brak danych do wyświetlenia w tabeli wyników (companies DataFrame empty)")
            return render_template('results.html', companies=[], message="Brak danych do wyświetlenia")
        
        # Sortuj po yield_netto malejąco (od największej do najmniejszej)
        companies = companies.sort_values(by='yield_netto', ascending=False, na_position='last')
        
        # Konwertuj DataFrame na listę słowników dla template
        companies_list = []
        for _, row in companies.iterrows():
            company_data = {
                'ticker': row['ticker'],
                'notes_count': row.get('notes_count', 0),
                'flag_color': row.get('flag_color', 'none'),
                'flag_notes': row.get('flag_notes', ''),
                'selection_data_parsed': row.get('selection_data_parsed', {}),
                'informational_data_parsed': row.get('informational_data_parsed', {}),
                'yield': row.get('yield'),
                'yield_netto': row.get('yield_netto'),
                'current_price': row.get('current_price'),
                'price_for_5_percent_yield': row.get('price_for_5_percent_yield'),
                'stochastic_1m': row.get('stochastic_1m') if row.get('stochastic_1m') is not None else 'N/A',
                'stochastic_1w': row.get('stochastic_1w') if row.get('stochastic_1w') is not None else 'N/A',
                'stage2_passed': row.get('stage2_passed')
            }
            companies_list.append(company_data)
        logger.info(f"Przekazuję do szablonu {len(companies_list)} spółek")
        return render_template('results.html', 
                             results=companies_list, 
                             view_type=view_type, 
                             view_date=view_date,
                             date_filter=date_filter,
                             ticker_filter=ticker_filter)
        
    except Exception as e:
        logger.error(f"Błąd w results: {e}")
        return render_template('results.html', companies=[], error=str(e))

@app.route('/notes')
def notes():
    """Wyświetla listę spółek z notatkami"""
    try:
        ticker_filter = request.args.get('ticker', '')
        
        # Pobierz spółki z notatkami
        if ticker_filter:
            # Filtrowanie po tickerze
            companies = db_manager.get_companies_by_ticker(ticker_filter)
        else:
            # Wszystkie spółki z najnowszego uruchomienia
            companies = db_manager.get_latest_results()
        
        if companies.empty:
            logger.warning("Brak spółek do wyświetlenia w notatkach")
            return render_template('notes.html', companies=[], message="Brak spółek do wyświetlenia")
        
        # Filtruj tylko spółki z notatkami
        companies_with_notes = []
        for _, row in companies.iterrows():
            ticker = row['ticker']
            notes_count = db_manager.get_company_notes_count(ticker)
            
            if notes_count > 0:  # Tylko spółki z notatkami
                company_data = {
                    'ticker': ticker,
                    'notes_count': notes_count,
                    'selection_data_parsed': row.get('selection_data_parsed', {}),
                    'informational_data_parsed': row.get('informational_data_parsed', {}),
                    'yield': row.get('yield'),
                    'yield_netto': row.get('yield_netto'),
                    'current_price': row.get('current_price'),
                    'price_for_5_percent_yield': row.get('price_for_5_percent_yield'),
                    'stage2_passed': row.get('stage2_passed')
                }
                
                # Pobierz ostatnią notatkę
                notes = db_manager.get_company_notes(ticker)
                if not notes.empty:
                    latest_note = notes.iloc[-1]  # Ostatnia notatka
                    company_data['latest_note'] = {
                        'title': latest_note.get('title', ''),
                        'content': latest_note.get('content', ''),
                        'created_at': latest_note.get('created_at', ''),
                        'note_number': latest_note.get('note_number', 0)
                    }
                
                companies_with_notes.append(company_data)
        
        logger.info(f"Przekazuję do szablonu {len(companies_with_notes)} spółek z notatkami")
        return render_template('notes.html', 
                             companies=companies_with_notes,
                             ticker_filter=ticker_filter)
        
    except Exception as e:
        logger.error(f"Błąd w notes: {e}")
        return render_template('notes.html', companies=[], error=str(e))

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
@rate_limit('api_notes')
def add_company_note(ticker):
    """Dodaje nową notatkę"""
    try:
        # Waliduj ticker
        if not validate_ticker(ticker):
            return jsonify({'success': False, 'error': 'Nieprawidłowy format tickera'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Brak danych'}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'error': 'Treść notatki jest wymagana'}), 400
        
        # Waliduj treść notatki
        if not validate_note_content(content):
            return jsonify({'success': False, 'error': 'Nieprawidłowa treść notatki'}), 400
        
        # Waliduj tytuł (max 100 znaków)
        if len(title) > 100:
            return jsonify({'success': False, 'error': 'Tytuł zbyt długi (max 100 znaków)'}), 400
        
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

# ===== API ENDPOINTS DLA AUTOMATYCZNEGO URZUCAMIANIA =====

@app.route('/api/auto-schedule/status')
def get_auto_schedule_status():
    """Zwraca status automatycznego uruchamiania (publiczny)"""
    scheduler = get_auto_scheduler()
    status = scheduler.get_status()
    return jsonify(status)

@app.route('/api/auto-schedule/health')
def get_auto_schedule_health():
    """Zwraca health check automatycznego uruchamiania (publiczny)"""
    scheduler = get_auto_scheduler()
    status = scheduler.get_status()
    
    health = {
        "status": "healthy" if status['scheduler_running'] else "unhealthy",
        "enabled": status['enabled'],
        "next_run": status['next_run'],
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(health)

@app.route('/api/auto-schedule/history')
def get_auto_schedule_history():
    """Zwraca historię automatycznych uruchomień (publiczny)"""
    scheduler = get_auto_scheduler()
    limit = request.args.get('limit', 10, type=int)
    history = scheduler.get_history(limit)
    return jsonify({"history": history})

@app.route('/api/auto-schedule/configure', methods=['POST'])
def configure_auto_schedule():
    """Konfiguruje automatyczne uruchamianie (chroniony)"""
    # Sprawdź autoryzację API
    if is_api_auth_enabled():
        api_key = request.headers.get('X-API-Key')
        if api_key != get_api_key():
            return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    enabled = data.get('enabled', False)
    time = data.get('time', '09:00')
    timezone = data.get('timezone', 'Europe/Warsaw')
    
    scheduler = get_auto_scheduler()
    scheduler.update_config(enabled, time, timezone)
    
    return jsonify({
        "success": True,
        "message": "Konfiguracja zaktualizowana",
        "config": {
            "enabled": enabled,
            "time": time,
            "timezone": timezone
        }
    })

@app.route('/api/auto-schedule/run-now', methods=['POST'])
def run_auto_analysis_now():
    """Uruchamia analizę natychmiast (chroniony)"""
    # Sprawdź autoryzację API
    if is_api_auth_enabled():
        api_key = request.headers.get('X-API-Key')
        if api_key != get_api_key():
            return jsonify({"error": "Unauthorized"}), 401
    
    scheduler = get_auto_scheduler()
    result = scheduler.run_now()
    
    return jsonify(result)

# ===== API ENDPOINTY DLA FLAG SNAPSHOT =====

@app.route('/api/flag-snapshot/status')
def get_flag_snapshot_status():
    """Zwraca status zadania flag snapshot"""
    try:
        from src.auto_scheduler import get_auto_scheduler
        scheduler = get_auto_scheduler()
        
        # Pobierz konfigurację
        config = scheduler.config.get('flag_snapshot', {})
        
        return jsonify({
            'enabled': config.get('enabled', False),
            'time': config.get('time', '23:30'),
            'timezone': config.get('timezone', 'Europe/Warsaw'),
            'scheduler_running': scheduler.scheduler.running,
            'next_run': None  # TODO: dodać obliczanie następnego uruchomienia
        })
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statusu flag snapshot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/flag-snapshot/configure', methods=['POST'])
def configure_flag_snapshot():
    """Konfiguruje zadanie flag snapshot (chroniony)"""
    try:
        # Sprawdź API key
        if is_api_auth_enabled():
            api_key = request.headers.get('X-API-Key')
            if api_key != get_api_key():
                return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        enabled = data.get('enabled', False)
        time = data.get('time', '23:30')
        timezone = data.get('timezone', 'Europe/Warsaw')
        
        from src.auto_scheduler import get_auto_scheduler
        scheduler = get_auto_scheduler()
        scheduler.update_flag_snapshot_config(enabled, time, timezone)
        
        return jsonify({
            'success': True,
            'message': 'Konfiguracja flag snapshot zaktualizowana',
            'config': {
                'enabled': enabled,
                'time': time,
                'timezone': timezone
            }
        })
    except Exception as e:
        logger.error(f"Błąd podczas konfiguracji flag snapshot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/flag-snapshot/run-now', methods=['POST'])
def run_flag_snapshot_now():
    """Uruchamia flag snapshot natychmiast (chroniony)"""
    try:
        # Sprawdź API key
        if is_api_auth_enabled():
            api_key = request.headers.get('X-API-Key')
            if api_key != get_api_key():
                return jsonify({'error': 'Unauthorized'}), 401
        
        from src.auto_scheduler import get_auto_scheduler
        scheduler = get_auto_scheduler()
        scheduler._run_flag_snapshot_job()
        
        return jsonify({'success': True, 'message': 'Flag snapshot został uruchomiony'})
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania flag snapshot: {e}")
        return jsonify({'error': str(e)}), 500

# ===== API ENDPOINTY DLA FLAG =====

@app.route('/api/flags/<ticker>', methods=['GET'])
def get_company_flag(ticker):
    """
    Pobiera flagę dla spółki
    """
    try:
        flag = db_manager.get_company_flag(ticker.upper())
        if flag:
            return jsonify({'success': True, 'flag': flag})
        else:
            return jsonify({'success': True, 'flag': {'flag_color': 'none'}})
    except Exception as e:
        logger.error(f"Błąd podczas pobierania flagi dla {ticker}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/flags/<ticker>', methods=['POST'])
@rate_limit('api_flags')
def set_company_flag(ticker):
    """
    Ustawia flagę dla spółki
    """
    try:
        # Waliduj ticker
        if not validate_ticker(ticker):
            return jsonify({'success': False, 'message': 'Nieprawidłowy format tickera'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Brak danych'}), 400
        
        flag_color = data.get('flag_color')
        flag_notes = data.get('flag_notes', '').strip()[:40]  # Max 40 znaków
        
        # Waliduj kolor flagi
        if not validate_flag_color(flag_color):
            return jsonify({'success': False, 'message': 'Nieprawidłowy kolor flagi'}), 400
        
        # Waliduj notatki (sprawdź czy nie zawierają niebezpiecznych znaków)
        if flag_notes and not validate_note_content(flag_notes):
            return jsonify({'success': False, 'message': 'Nieprawidłowa treść notatek'}), 400
        
        success = db_manager.set_company_flag(ticker.upper(), flag_color, flag_notes)
        if success:
            return jsonify({'success': True, 'message': 'Flaga została ustawiona'})
        else:
            return jsonify({'success': False, 'message': 'Błąd podczas ustawiania flagi'}), 500
    except Exception as e:
        logger.error(f"Błąd podczas ustawiania flagi dla {ticker}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/flags/history/<ticker>')
def get_flag_history(ticker):
    """
    Pobiera historię flag dla spółki
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db_manager.get_flag_history(ticker.upper(), limit)
        return jsonify({'success': True, 'history': history.to_dict('records')})
    except Exception as e:
        logger.error(f"Błąd podczas pobierania historii flag dla {ticker}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/flags/report')
def get_flags_report():
    """
    Generuje raport flag
    """
    try:
        report = db_manager.get_flags_report()
        return jsonify({'success': True, 'report': report})
    except Exception as e:
        logger.error(f"Błąd podczas generowania raportu flag: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/flags/snapshot', methods=['POST'])
def run_flag_snapshot():
    """Ręczne uruchomienie snapshotu flag (chroniony)"""
    try:
        # Sprawdź API key
        if is_api_auth_enabled():
            api_key = request.headers.get('X-API-Key')
            if api_key != get_api_key():
                return jsonify({'error': 'Unauthorized'}), 401
        
        # Uruchom snapshot
        from src.auto_scheduler import get_auto_scheduler
        scheduler = get_auto_scheduler()
        scheduler._run_flag_snapshot_job()
        
        return jsonify({'success': True, 'message': 'Snapshot flag został uruchomiony'})
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania snapshotu flag: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/flag-snapshot/history')
def get_flag_snapshot_history():
    """Pobiera historię zapisu flag tickerów"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Pobierz historię z bazy danych
        history = db_manager.get_flag_snapshot_history(limit)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania historii zapisu flag: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Błąd serwera'), 500

if __name__ == '__main__':
    # Inicjalizuj auto scheduler
    init_auto_scheduler()
    app.run(debug=True, host='0.0.0.0', port=5002) 