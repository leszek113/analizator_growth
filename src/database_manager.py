import sqlite3
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Klasa do zarządzania bazą danych SQLite dla analizatora rynku
    """
    
    def __init__(self, db_path: str = "market_analyzer.db"):
        """
        Inicjalizuje menedżer bazy danych
        
        Args:
            db_path: Ścieżka do pliku bazy danych
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """
        Inicjalizuje bazę danych z wszystkimi tabelami
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela uruchomień analizy
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_runs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        selected_count INTEGER DEFAULT 0,
                        notes TEXT,
                        selection_rules_version TEXT,
                        informational_columns_version TEXT
                    )
                """)
                
                # Tabela wersji reguł selekcji
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS selection_rules_versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version TEXT UNIQUE NOT NULL,
                        rules_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    )
                """)
                
                # Tabela wersji kolumn informacyjnych
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS informational_columns_versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version TEXT UNIQUE NOT NULL,
                        columns_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    )
                """)
                
                # Tabela spółek z Etapu 1 (z JSON dla elastyczności)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stage1_companies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        run_id INTEGER NOT NULL,
                        ticker TEXT NOT NULL,
                        selection_data TEXT,  -- JSON z danymi selekcji
                        informational_data TEXT,  -- JSON z danymi informacyjnymi
                        yield REAL,
                        yield_netto REAL,
                        current_price REAL,
                        price_for_5_percent_yield REAL,
                        stochastic_1m REAL,
                        stochastic_1w REAL,
                        stage2_passed BOOLEAN,
                        FOREIGN KEY (run_id) REFERENCES analysis_runs (id)
                    )
                """)
                
                # Tabela notatek dla spółek
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS company_notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        note_number INTEGER NOT NULL,
                        title TEXT,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(ticker, note_number)
                    )
                """)
                
                # Dodaj kolumny jeśli nie istnieją (migracja)
                try:
                    cursor.execute("ALTER TABLE stage1_companies ADD COLUMN current_price REAL")
                except sqlite3.OperationalError:
                    pass  # Kolumna już istnieje
                
                try:
                    cursor.execute("ALTER TABLE stage1_companies ADD COLUMN price_for_5_percent_yield REAL")
                except sqlite3.OperationalError:
                    pass  # Kolumna już istnieje
                
                # Dodaj indeksy dla lepszej wydajności
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_stage1_run_id ON stage1_companies(run_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_stage1_ticker ON stage1_companies(ticker)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_ticker ON company_notes(ticker)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_ticker_number ON company_notes(ticker, note_number)")
                
                conn.commit()
                logger.info("Baza danych zainicjalizowana pomyślnie")
                
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji bazy danych: {e}")
            raise
    
    def create_analysis_run(self, selected_count: int, notes: str = None, 
                           current_selection_version: str = 'v1.0', 
                           current_info_version: str = 'v1.0') -> int:
        """
        Tworzy nowe uruchomienie analizy
        
        Args:
            selected_count: Liczba wybranych spółek
            notes: Notatki do uruchomienia
            current_selection_version: Aktualna wersja reguł selekcji
            current_info_version: Aktualna wersja kolumn informacyjnych
            
        Returns:
            ID utworzonego uruchomienia
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Usuń poprzednie uruchomienia z dzisiaj (jedno uruchomienie dziennie)
                today = datetime.now().date()
                cursor.execute("""
                    SELECT run_id FROM analysis_runs 
                    WHERE DATE(run_date) = ?
                    ORDER BY run_date DESC
                """, (today,))
                
                existing_runs = cursor.fetchall()
                if existing_runs:
                    for run in existing_runs:
                        run_id = run[0]
                        # Usuń powiązane spółki
                        cursor.execute("DELETE FROM stage1_companies WHERE run_id = ?", (run_id,))
                        
                        # Usuń uruchomienie
                        cursor.execute("DELETE FROM analysis_runs WHERE run_id = ?", (run_id,))
                    
                    logger.info(f"Usunięto {len(existing_runs)} poprzednich uruchomień z dzisiaj")
                
                # Utwórz nowe uruchomienie
                cursor.execute("""
                    INSERT INTO analysis_runs (run_date, selected_count, notes, 
                                              selection_rules_version, informational_columns_version)
                    VALUES (?, ?, ?, ?, ?)
                """, (datetime.now(), selected_count, notes, 
                      current_selection_version, current_info_version))
                
                run_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Utworzono uruchomienie analizy ID: {run_id} (selekcja: {current_selection_version}, info: {current_info_version})")
                return run_id
                
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia uruchomienia analizy: {e}")
            raise
    
    def save_stage1_companies(self, run_id: int, stage1_df: pd.DataFrame, stage2_df: pd.DataFrame):
        """
        Zapisuje spółki Etapu 1 z danymi selekcji i informacjami o Etapie 2
        
        Args:
            run_id: ID uruchomienia analizy
            stage1_df: DataFrame z wynikami Etapu 1
            stage2_df: DataFrame z wynikami Etapu 2
        """
        try:
            # Importuj Yahoo Finance Analyzer dla pobierania cen
            from src.yahoo_finance_analyzer import YahooFinanceAnalyzer
            yahoo_analyzer = YahooFinanceAnalyzer()
            with sqlite3.connect(self.db_path) as conn:
                # Przygotuj dane do zapisu
                records = []
                for _, row in stage1_df.iterrows():
                    ticker = row.get('Ticker', row.get('Ticker_3', ''))
                    
                    # Znajdź dane z Etapu 2 dla tego tickera
                    stage2_data = stage2_df[stage2_df['ticker'] == ticker]
                    
                    # Załaduj konfigurację kolumn
                    config = self._load_data_columns_config()
                    
                    # Przygotuj dane selekcji w JSON
                    selection_data = {}
                    yield_value = None
                    yield_netto_value = None
                    
                    for key, column_name in config['selection_columns'].items():
                        value = row.get(column_name, '')
                        selection_data[key] = value
                        
                        # Zapisz Yield brutto jeśli to pole yield
                        if key == 'yield' and value:
                            try:
                                yield_value = float(str(value).replace('%', ''))
                            except (ValueError, TypeError):
                                yield_value = None
                    
                    # Oblicz Yield Netto jeśli mamy Yield brutto
                    if yield_value is not None:
                        yield_netto_value = yield_value * 0.81
                    
                    # Pobierz aktualną cenę i oblicz cenę dla Yield 5%
                    current_price = None
                    price_for_5_percent_yield = None
                    
                    try:
                        current_price = yahoo_analyzer.get_current_price(ticker)
                        if current_price and yield_value:
                            price_for_5_percent_yield = self.calculate_price_for_5_percent_yield(
                                ticker, yield_value, current_price
                            )
                    except Exception as e:
                        logger.warning(f"Nie można pobrać ceny dla {ticker}: {e}")
                    
                    # Przygotuj dane informacyjne w JSON
                    informational_data = {}
                    for key, column_name in config['informational_columns'].items():
                        informational_data[key] = row.get(column_name, '')
                    
                    record = {
                        'run_id': run_id,
                        'ticker': ticker,
                        # Dane w JSON
                        'selection_data': json.dumps(selection_data, ensure_ascii=False),
                        'informational_data': json.dumps(informational_data, ensure_ascii=False),
                        # Pola Yield
                        'yield': yield_value,
                        'yield_netto': yield_netto_value,
                        # Pola cenowe - używamy nowych nazw kolumn
                        'current_price_new': current_price,
                        'price_for_5_percent_yield_new': price_for_5_percent_yield,
                        # Informacje o Etapie 2
                        'stochastic_1m': stage2_data['stochastic_1m'].iloc[0] if not stage2_data.empty else None,
                        'stochastic_1w': stage2_data['stochastic_1w'].iloc[0] if not stage2_data.empty else None,
                        'stage2_passed': stage2_data['stage2_passed'].iloc[0] if not stage2_data.empty else False
                    }
                    records.append(record)
                
                # Zapisz do bazy
                df_to_save = pd.DataFrame(records)
                df_to_save.to_sql('stage1_companies', conn, if_exists='append', index=False)
                
                logger.info(f"Zapisano {len(records)} spółek Etapu 1 z danymi Etapu 2 dla uruchomienia {run_id}")
                
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania spółek Etapu 1: {e}")
            raise
    
    def _load_data_columns_config(self):
        """
        Ładuje konfigurację kolumn danych
        """
        try:
            import yaml
            with open('config/data_columns.yaml', 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji kolumn: {e}")
            raise
    
    def _get_current_selection_version(self) -> str:
        """
        Pobiera obecną wersję reguł selekcji
        """
        try:
            import yaml
            with open('config/selection_rules.yaml', 'r', encoding='utf-8') as file:
                selection_rules = yaml.safe_load(file)
            
            # Sprawdź czy istnieje wersja w bazie
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM selection_rules_versions ORDER BY created_at DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    return result[0]
                else:
                    # Utwórz nową wersję
                    return self._create_new_selection_version(selection_rules)
                    
        except Exception as e:
            logger.error(f"Błąd podczas pobierania wersji selekcji: {e}")
            return "v1.0"
    
    def _get_current_info_version(self) -> str:
        """
        Pobiera obecną wersję kolumn informacyjnych
        """
        try:
            config = self._load_data_columns_config()
            
            # Sprawdź czy istnieje wersja w bazie
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM informational_columns_versions ORDER BY created_at DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    return result[0]
                else:
                    # Utwórz nową wersję
                    return self._create_new_info_version(config['informational_columns'])
                    
        except Exception as e:
            logger.error(f"Błąd podczas pobierania wersji informacyjnej: {e}")
            return "v1.0"
    
    def _create_new_selection_version(self, selection_rules: dict) -> str:
        """
        Tworzy nową wersję reguł selekcji
        """
        try:
            import json
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Pobierz najnowszą wersję
                cursor.execute("SELECT version FROM selection_rules_versions ORDER BY created_at DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    # Zwiększ numer wersji
                    current_version = result[0]
                    version_parts = current_version.split('.')
                    new_minor = int(version_parts[1]) + 1
                    new_version = f"{version_parts[0]}.{new_minor}"
                else:
                    new_version = "v1.0"
                
                # Zapisz nową wersję
                rules_json = json.dumps(selection_rules, ensure_ascii=False)
                cursor.execute("""
                    INSERT INTO selection_rules_versions (version, rules_json, description)
                    VALUES (?, ?, ?)
                """, (new_version, rules_json, f"Automatycznie utworzona wersja {new_version}"))
                
                conn.commit()
                logger.info(f"Utworzono nową wersję reguł selekcji: {new_version}")
                return new_version
                
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia nowej wersji selekcji: {e}")
            return "v1.0"
    
    def _create_new_info_version(self, informational_columns: dict) -> str:
        """
        Tworzy nową wersję kolumn informacyjnych
        """
        try:
            import json
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Pobierz najnowszą wersję
                cursor.execute("SELECT version FROM informational_columns_versions ORDER BY created_at DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    # Zwiększ numer wersji
                    current_version = result[0]
                    version_parts = current_version.split('.')
                    new_minor = int(version_parts[1]) + 1
                    new_version = f"{version_parts[0]}.{new_minor}"
                else:
                    new_version = "v1.0"
                
                # Zapisz nową wersję
                columns_json = json.dumps(informational_columns, ensure_ascii=False)
                cursor.execute("""
                    INSERT INTO informational_columns_versions (version, columns_json, description)
                    VALUES (?, ?, ?)
                """, (new_version, columns_json, f"Automatycznie utworzona wersja {new_version}"))
                
                conn.commit()
                logger.info(f"Utworzono nową wersję kolumn informacyjnych: {new_version}")
                return new_version
                
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia nowej wersji informacyjnej: {e}")
            return "v1.0"
    
    def get_company_history(self, ticker: str, limit: int = 10) -> pd.DataFrame:
        """
        Pobiera historię konkretnej spółki
        
        Args:
            ticker: Symbol spółki
            limit: Maksymalna liczba wpisów do pobrania
            
        Returns:
            DataFrame z historią spółki
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                history = pd.read_sql("""
                    SELECT 
                        ar.run_date,
                        sc.ticker,
                        sc.company_name,
                        sc.quality_rating,
                        sc.yield_value,
                        sc.dividend_growth_streak,
                        sc.sp_credit_rating,
                        sc.dk_rating,
                        sc.stochastic_1m,
                        sc.stochastic_1w,
                        sc.stage2_error,
                        sc.final_selection,
                        ar.run_id
                    FROM stage1_companies sc
                    JOIN analysis_runs ar ON sc.run_id = ar.run_id
                    WHERE sc.ticker = ?
                    ORDER BY ar.run_date DESC
                    LIMIT ?
                """, conn, params=[ticker, limit])
                
                return history
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania historii spółki {ticker}: {e}")
            return pd.DataFrame()
    
    def get_companies_by_date(self, date_str: str) -> pd.DataFrame:
        """
        Pobiera wyniki analizy z konkretnej daty
        
        Args:
            date_str: Data w formacie YYYY-MM-DD
            
        Returns:
            DataFrame z wynikami
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT s.ticker, s.selection_data, s.informational_data,
                           s.yield, s.yield_netto, s.current_price_new as current_price,
                           s.price_for_5_percent_yield_new as price_for_5_percent_yield,
                           s.stochastic_1m, s.stochastic_1w, s.stage2_passed,
                           a.run_date
                    FROM stage1_companies s
                    JOIN analysis_runs a ON s.run_id = a.run_id
                    WHERE DATE(a.run_date) = ?
                    ORDER BY s.ticker
                """
                df = pd.read_sql(query, conn, params=(date_str,))
                
                if df.empty:
                    logger.warning(f"Brak danych dla daty {date_str}")
                    return df
                
                # Parsuj JSON dane
                df['selection_data_parsed'] = df['selection_data'].apply(
                    lambda x: json.loads(x) if x else {}
                )
                df['informational_data_parsed'] = df['informational_data'].apply(
                    lambda x: json.loads(x) if x else {}
                )
                
                # Dodaj liczbę notatek dla każdej spółki
                df['notes_count'] = df['ticker'].apply(self.get_company_notes_count)
                
                logger.info(f"Pobrano {len(df)} spółek z daty {date_str}")
                return df
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania danych z daty {date_str}: {e}")
            return pd.DataFrame()
    
    def get_latest_run_date(self) -> str:
        """
        Pobiera datę najnowszego uruchomienia
        
        Returns:
            Data w formacie 'YYYY-MM-DD'
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = pd.read_sql("""
                    SELECT DATE(run_date) as run_date
                    FROM analysis_runs 
                    ORDER BY run_date DESC 
                    LIMIT 1
                """, conn)
                
                if not result.empty:
                    return result.iloc[0]['run_date']
                return ""
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania najnowszej daty: {e}")
            return ""
    
    def has_today_run(self) -> bool:
        """
        Sprawdza czy już była selekcja dzisiaj
        
        Returns:
            True jeśli już była selekcja dzisiaj, False w przeciwnym razie
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                today = datetime.now().date()
                cursor.execute("""
                    SELECT COUNT(*) FROM analysis_runs 
                    WHERE DATE(run_date) = ?
                """, (today,))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania dzisiejszej selekcji: {e}")
            return False
    
    def get_today_run_info(self) -> dict:
        """
        Pobiera informacje o dzisiejszym uruchomieniu analizy
        
        Returns:
            Dict z informacjami lub pusty dict
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                today = datetime.now().date()
                cursor.execute("""
                    SELECT run_id, run_date, selected_count, notes,
                           selection_rules_version, informational_columns_version
                    FROM analysis_runs 
                    WHERE DATE(run_date) = ?
                    ORDER BY run_date DESC
                    LIMIT 1
                """, (today,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'run_id': result[0],
                        'run_date': result[1],
                        'selected_count': result[2],
                        'notes': result[3],
                        'selection_rules_version': result[4],
                        'informational_columns_version': result[5]
                    }
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"Błąd podczas pobierania informacji o dzisiejszej selekcji: {e}")
            return {}
    
    def get_latest_results(self) -> pd.DataFrame:
        """
        Pobiera najnowsze wyniki analizy z danymi selekcji i informacjami o Etapie 2
        
        Returns:
            DataFrame z wynikami
        """
        try:
            # Pobierz najnowsze uruchomienie
            latest_run = self.get_latest_run()
            if latest_run.empty:
                logger.warning("Brak uruchomień analizy")
                return pd.DataFrame()
            
            run_id = int(latest_run.iloc[0]['run_id'])
            
            # Spółki Etapu 1 z danymi selekcji i informacjami o Etapie 2
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT ticker, selection_data, informational_data, 
                           yield, yield_netto, current_price_new as current_price, 
                           price_for_5_percent_yield_new as price_for_5_percent_yield,
                           stochastic_1m, stochastic_1w, stage2_passed
                    FROM stage1_companies 
                    WHERE run_id = ?
                    ORDER BY ticker
                """
                df = pd.read_sql(query, conn, params=(run_id,))
                
                if df.empty:
                    logger.warning(f"Brak danych dla uruchomienia {run_id}")
                    return df
                
                # Parsuj JSON dane
                df['selection_data_parsed'] = df['selection_data'].apply(
                    lambda x: json.loads(x) if x else {}
                )
                df['informational_data_parsed'] = df['informational_data'].apply(
                    lambda x: json.loads(x) if x else {}
                )
                
                # Dodaj liczbę notatek dla każdej spółki
                df['notes_count'] = df['ticker'].apply(self.get_company_notes_count)
                
                logger.info(f"Pobrano {len(df)} spółek z uruchomienia {run_id}")
                return df
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania najnowszych wyników: {e}")
            return pd.DataFrame()
    
    def get_analysis_history(self, limit: int = 10) -> pd.DataFrame:
        """
        Pobiera historię uruchomień analizy
        
        Args:
            limit: Maksymalna liczba rekordów
            
        Returns:
            DataFrame z historią uruchomień
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT run_id, run_date, selected_count, notes, 
                           selection_rules_version, informational_columns_version
                    FROM analysis_runs 
                    ORDER BY run_date DESC 
                    LIMIT ?
                """
                df = pd.read_sql(query, conn, params=(limit,))
                return df
        except Exception as e:
            logger.error(f"Błąd podczas pobierania historii: {e}")
            return pd.DataFrame()
    
    def get_company_history_with_versions(self, ticker: str, limit: int = 10) -> pd.DataFrame:
        """
        Pobiera historię konkretnej spółki z wersjonowaniem
        
        Args:
            ticker: Ticker spółki
            limit: Maksymalna liczba wyników
            
        Returns:
            DataFrame z historią spółki i wersjami reguł
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT sc.run_id, ar.run_date, sc.ticker, sc.final_selection,
                           sc.stochastic_1m, sc.stochastic_1w, sc.stage2_passed,
                           ar.selection_rules_version, ar.informational_columns_version,
                           sc.selection_data, sc.informational_data
                    FROM stage1_companies sc
                    JOIN analysis_runs ar ON sc.run_id = ar.run_id
                    WHERE sc.ticker = ?
                    ORDER BY ar.run_date DESC
                    LIMIT ?
                """
                df = pd.read_sql(query, conn, params=(ticker, limit))
                
                # Parsuj JSON dane
                if not df.empty:
                    df['selection_data_parsed'] = df['selection_data'].apply(
                        lambda x: json.loads(x) if x else {}
                    )
                    df['informational_data_parsed'] = df['informational_data'].apply(
                        lambda x: json.loads(x) if x else {}
                    )
                
                return df
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania historii spółki z wersjonowaniem: {e}")
            return pd.DataFrame()
    
    def get_version_details(self, version_type: str, version: str) -> dict:
        """
        Pobiera szczegóły konkretnej wersji reguł
        
        Args:
            version_type: 'selection' lub 'informational'
            version: Numer wersji (np. 'v1.0')
            
        Returns:
            Słownik z szczegółami wersji
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if version_type == 'selection':
                    query = """
                        SELECT version, rules_json, created_at, description
                        FROM selection_rules_versions
                        WHERE version = ?
                    """
                else:
                    query = """
                        SELECT version, columns_json, created_at, description
                        FROM informational_columns_versions
                        WHERE version = ?
                    """
                
                cursor = conn.cursor()
                cursor.execute(query, (version,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'version': result[0],
                        'data': json.loads(result[1]),
                        'created_at': result[2],
                        'description': result[3]
                    }
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"Błąd podczas pobierania szczegółów wersji: {e}")
            return {}
    
    def get_all_versions(self, version_type: str) -> pd.DataFrame:
        """
        Pobiera wszystkie wersje reguł
        
        Args:
            version_type: 'selection' lub 'informational'
            
        Returns:
            DataFrame z wszystkimi wersjami
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if version_type == 'selection':
                    query = """
                        SELECT version, created_at, description
                        FROM selection_rules_versions
                        ORDER BY created_at DESC
                    """
                else:
                    query = """
                        SELECT version, created_at, description
                        FROM informational_columns_versions
                        ORDER BY created_at DESC
                    """
                
                df = pd.read_sql(query, conn)
                return df
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania wersji: {e}")
            return pd.DataFrame()
    
    def calculate_price_for_5_percent_yield(self, ticker: str, yield_percent: float, current_price: float) -> Optional[float]:
        """
        Oblicza cenę, przy której Yield Netto wynosiłby 5%
        
        Args:
            ticker: Symbol spółki
            yield_percent: Yield brutto w procentach (z Google Sheets)
            current_price: Aktualna cena spółki
            
        Returns:
            Cena dla Yield Netto 5% lub None jeśli błąd
        """
        try:
            if not yield_percent or not current_price:
                return None
            
            # Dywidenda roczna brutto = Yield% × Aktualna cena
            annual_dividend_brutto = (yield_percent / 100) * current_price
            
            # Dywidenda roczna netto = Dywidenda brutto × 0.81
            annual_dividend_netto = annual_dividend_brutto * 0.81
            
            # Cena dla Yield Netto 5% = Dywidenda netto / 0.05
            # 0.05 = 5% docelowy Yield Netto
            target_price = annual_dividend_netto / 0.05
            
            return target_price
            
        except Exception as e:
            logger.error(f"Błąd podczas obliczania ceny dla Yield 5% dla {ticker}: {e}")
            return None
    
    def detect_config_changes(self) -> dict:
        """
        Wykrywa zmiany w konfiguracji i tworzy nowe wersje jeśli potrzeba
        
        Returns:
            Słownik z informacjami o zmianach
        """
        try:
            import yaml
            
            # Załaduj obecną konfigurację
            with open('config/selection_rules.yaml', 'r', encoding='utf-8') as file:
                current_selection_rules = yaml.safe_load(file)
            
            config = self._load_data_columns_config()
            current_info_columns = config['informational_columns']
            
            # Pobierz najnowsze wersje z bazy
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Sprawdź reguły selekcji
                cursor.execute("""
                    SELECT rules_json FROM selection_rules_versions 
                    ORDER BY created_at DESC LIMIT 1
                """)
                result = cursor.fetchone()
                db_selection_rules = json.loads(result[0]) if result else {}
                
                # Sprawdź kolumny informacyjne
                cursor.execute("""
                    SELECT columns_json FROM informational_columns_versions 
                    ORDER BY created_at DESC LIMIT 1
                """)
                result = cursor.fetchone()
                db_info_columns = json.loads(result[0]) if result else {}
            
            changes = {
                'selection_changed': current_selection_rules != db_selection_rules,
                'info_changed': current_info_columns != db_info_columns,
                'new_selection_version': None,
                'new_info_version': None
            }
            
            # Utwórz nowe wersje jeśli są zmiany
            if changes['selection_changed']:
                changes['new_selection_version'] = self._create_new_selection_version(current_selection_rules)
            
            if changes['info_changed']:
                changes['new_info_version'] = self._create_new_info_version(current_info_columns)
            
            return changes
            
        except Exception as e:
            logger.error(f"Błąd podczas wykrywania zmian: {e}")
            return {'selection_changed': False, 'info_changed': False} 
    
    def get_company_notes_count(self, ticker: str) -> int:
        """
        Pobiera liczbę notatek dla spółki
        
        Args:
            ticker: Symbol spółki
            
        Returns:
            Liczba notatek
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM company_notes WHERE ticker = ?", (ticker,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Błąd podczas pobierania liczby notatek dla {ticker}: {e}")
            return 0
    
    def get_company_notes(self, ticker: str) -> pd.DataFrame:
        """
        Pobiera wszystkie notatki dla spółki
        
        Args:
            ticker: Symbol spółki
            
        Returns:
            DataFrame z notatkami
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT id, note_number, title, content, created_at, updated_at
                    FROM company_notes 
                    WHERE ticker = ?
                    ORDER BY note_number DESC, created_at DESC
                """
                df = pd.read_sql(query, conn, params=(ticker,))
                return df
        except Exception as e:
            logger.error(f"Błąd podczas pobierania notatek dla {ticker}: {e}")
            return pd.DataFrame()
    
    def get_company_note(self, ticker: str, note_number: int) -> dict:
        """
        Pobiera konkretną notatkę
        
        Args:
            ticker: Symbol spółki
            note_number: Numer notatki
            
        Returns:
            Słownik z danymi notatki lub None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, content, created_at, updated_at
                    FROM company_notes 
                    WHERE ticker = ? AND note_number = ?
                """, (ticker, note_number))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'title': result[1],
                        'content': result[2],
                        'created_at': result[3],
                        'updated_at': result[4]
                    }
                return None
        except Exception as e:
            logger.error(f"Błąd podczas pobierania notatki {note_number} dla {ticker}: {e}")
            return None
    
    def add_company_note(self, ticker: str, title: str, content: str) -> bool:
        """
        Dodaje nową notatkę dla spółki
        
        Args:
            ticker: Symbol spółki
            title: Tytuł notatki
            content: Treść notatki
            
        Returns:
            True jeśli sukces, False w przeciwnym razie
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Znajdź następny numer notatki
                cursor.execute("""
                    SELECT MAX(note_number) FROM company_notes WHERE ticker = ?
                """, (ticker,))
                result = cursor.fetchone()
                next_number = (result[0] or 0) + 1
                
                # Dodaj notatkę
                cursor.execute("""
                    INSERT INTO company_notes (ticker, note_number, title, content)
                    VALUES (?, ?, ?, ?)
                """, (ticker, next_number, title, content))
                
                conn.commit()
                logger.info(f"Dodano notatkę #{next_number} dla {ticker}")
                return True
                
        except Exception as e:
            logger.error(f"Błąd podczas dodawania notatki dla {ticker}: {e}")
            return False
    
    def update_company_note(self, ticker: str, note_number: int, title: str, content: str) -> bool:
        """
        Aktualizuje notatkę
        
        Args:
            ticker: Symbol spółki
            note_number: Numer notatki
            title: Nowy tytuł
            content: Nowa treść
            
        Returns:
            True jeśli sukces, False w przeciwnym razie
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE company_notes 
                    SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE ticker = ? AND note_number = ?
                """, (title, content, ticker, note_number))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Zaktualizowano notatkę #{note_number} dla {ticker}")
                    return True
                else:
                    logger.warning(f"Nie znaleziono notatki #{note_number} dla {ticker}")
                    return False
                    
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji notatki {note_number} dla {ticker}: {e}")
            return False
    
    def delete_company_note(self, ticker: str, note_number: int) -> bool:
        """
        Usuwa notatkę
        
        Args:
            ticker: Symbol spółki
            note_number: Numer notatki
            
        Returns:
            True jeśli sukces, False w przeciwnym razie
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM company_notes 
                    WHERE ticker = ? AND note_number = ?
                """, (ticker, note_number))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Usunięto notatkę #{note_number} dla {ticker}")
                    return True
                else:
                    logger.warning(f"Nie znaleziono notatki #{note_number} dla {ticker}")
                    return False
                    
        except Exception as e:
            logger.error(f"Błąd podczas usuwania notatki {note_number} dla {ticker}: {e}")
            return False 
    
    def get_companies_by_ticker(self, ticker: str) -> pd.DataFrame:
        """
        Pobiera wszystkie wyniki dla konkretnej spółki
        
        Args:
            ticker: Symbol spółki
            
        Returns:
            DataFrame z wynikami
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT s.ticker, s.selection_data, s.informational_data,
                           s.yield, s.yield_netto, s.current_price_new as current_price, 
                           s.price_for_5_percent_yield_new as price_for_5_percent_yield,
                           s.stochastic_1m, s.stochastic_1w, s.stage2_passed,
                           a.run_date
                    FROM stage1_companies s
                    JOIN analysis_runs a ON s.run_id = a.run_id
                    WHERE s.ticker = ?
                    ORDER BY a.run_date DESC
                """
                df = pd.read_sql(query, conn, params=(ticker.upper(),))
                
                if df.empty:
                    logger.warning(f"Brak danych dla spółki {ticker}")
                    return df
                
                # Parsuj JSON dane
                df['selection_data_parsed'] = df['selection_data'].apply(
                    lambda x: json.loads(x) if x else {}
                )
                df['informational_data_parsed'] = df['informational_data'].apply(
                    lambda x: json.loads(x) if x else {}
                )
                
                # Dodaj liczbę notatek
                df['notes_count'] = df['ticker'].apply(self.get_company_notes_count)
                
                logger.info(f"Pobrano {len(df)} wyników dla spółki {ticker}")
                return df
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania danych dla spółki {ticker}: {e}")
            return pd.DataFrame() 
    
    def get_latest_run(self) -> pd.DataFrame:
        """
        Pobiera najnowsze uruchomienie analizy
        
        Returns:
            DataFrame z najnowszym uruchomieniem lub pusty DataFrame
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT run_id, run_date, selected_count, notes,
                           selection_rules_version, informational_columns_version
                    FROM analysis_runs 
                    ORDER BY run_date DESC 
                    LIMIT 1
                """
                df = pd.read_sql(query, conn)
                return df
        except Exception as e:
            logger.error(f"Błąd podczas pobierania najnowszego uruchomienia: {e}")
            return pd.DataFrame() 