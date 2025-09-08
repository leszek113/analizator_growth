#!/usr/bin/env python3
"""
Moduł do zarządzania danymi historycznymi spółek
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import yfinance as yf

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDataManager:
    """
    Klasa do zarządzania danymi historycznymi spółek
    """
    
    def __init__(self, db_path: str = 'data/analizator_growth.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicjalizuje tabelę stock_prices"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Utwórz tabelę stock_prices
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stock_prices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        date DATE NOT NULL,
                        timeframe TEXT NOT NULL,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(ticker, date, timeframe)
                    )
                """)
                
                # Utwórz indeksy
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker_date 
                    ON stock_prices(ticker, date, timeframe)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_stock_prices_date 
                    ON stock_prices(date)
                """)
                
                conn.commit()
                logger.info("Tabela stock_prices zainicjalizowana pomyślnie")
                
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji tabeli stock_prices: {e}")
            raise
    
    def get_last_date(self, ticker: str, timeframe: str) -> Optional[datetime]:
        """
        Pobiera ostatnią datę dla danego tickera i timeframe
        
        Args:
            ticker: Symbol spółki
            timeframe: '1D' lub '1W'
            
        Returns:
            Ostatnia data lub None jeśli brak danych
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MAX(date) FROM stock_prices 
                    WHERE ticker = ? AND timeframe = ?
                """, (ticker, timeframe))
                
                result = cursor.fetchone()
                if result and result[0]:
                    return datetime.strptime(result[0], '%Y-%m-%d').date()
                return None
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania ostatniej daty dla {ticker}: {e}")
            return None
    
    def fetch_daily_data(self, ticker: str, start_date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
        """
        Pobiera dane dzienne z Yahoo Finance (5 lat historii)
        
        Args:
            ticker: Symbol spółki
            start_date: Data rozpoczęcia (opcjonalna)
            
        Returns:
            DataFrame z danymi dziennymi lub None jeśli błąd
        """
        try:
            logger.info(f"Pobieram dane dzienne dla {ticker}")
            
            stock = yf.Ticker(ticker)
            
            # Pobierz 5 lat danych dziennych
            data = stock.history(period='5y')
            
            if data.empty:
                logger.warning(f"Brak danych dziennych dla {ticker}")
                return None
            
            # Filtruj dane od start_date jeśli podano
            if start_date:
                data = data[data.index.date >= start_date]
            
            # Dodaj kolumny
            data['timeframe'] = '1D'
            data['ticker'] = ticker
            
            return data
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania danych dziennych dla {ticker}: {e}")
            return None
    
    def save_data(self, ticker: str, data: pd.DataFrame, timeframe: str):
        """
        Zapisuje dane do bazy danych
        
        Args:
            ticker: Symbol spółki
            data: DataFrame z danymi
            timeframe: '1D' lub '1W'
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for date, row in data.iterrows():
                    cursor.execute("""
                        INSERT OR REPLACE INTO stock_prices 
                        (ticker, date, timeframe, open, high, low, close, volume, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ticker,
                        date.strftime('%Y-%m-%d'),
                        timeframe,
                        row['Open'],
                        row['High'],
                        row['Low'],
                        row['Close'],
                        int(row['Volume']) if not pd.isna(row['Volume']) else None,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                
                conn.commit()
                logger.info(f"Zapisano {len(data)} rekordów dla {ticker} ({timeframe})")
                
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania danych dla {ticker}: {e}")
            raise
    
    def cleanup_old_data(self, keep_days: int = 1825):
        """
        Usuwa stare dane, zachowując tylko ostatnie keep_days (5 lat = 1825 dni)
        
        Args:
            keep_days: Liczba dni do zachowania (domyślnie 5 lat)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Oblicz datę graniczną
                cutoff_date = datetime.now().date() - timedelta(days=keep_days)
                
                cursor.execute("""
                    DELETE FROM stock_prices 
                    WHERE date < ?
                """, (cutoff_date.strftime('%Y-%m-%d'),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Usunięto {deleted_count} starych rekordów (starszych niż {keep_days} dni)")
                
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia starych danych: {e}")
    
    def get_weekly_data(self, ticker: str, limit: int = 260) -> pd.DataFrame:
        """
        Pobiera dane tygodniowe (agregowane z dziennych)
        
        Args:
            ticker: Symbol spółki
            limit: Maksymalna liczba rekordów
            
        Returns:
            DataFrame z danymi tygodniowymi
        """
        try:
            # Pobierz dane dzienne
            daily_data = self.get_stock_data(ticker, '1D', limit=limit*7)  # 7x więcej dziennych
            
            if daily_data.empty:
                return pd.DataFrame()
            
            # Agreguj do tygodniowych (niedziela jako koniec tygodnia)
            weekly_data = daily_data.resample('W-SUN').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            return weekly_data
            
        except Exception as e:
            logger.error(f"Błąd podczas agregacji danych tygodniowych dla {ticker}: {e}")
            return pd.DataFrame()
    
    def get_monthly_data(self, ticker: str, limit: int = 60) -> pd.DataFrame:
        """
        Pobiera dane miesięczne (agregowane z dziennych)
        
        Args:
            ticker: Symbol spółki
            limit: Maksymalna liczba rekordów
            
        Returns:
            DataFrame z danymi miesięcznymi
        """
        try:
            # Pobierz dane dzienne
            daily_data = self.get_stock_data(ticker, '1D', limit=limit*30)  # 30x więcej dziennych
            
            if daily_data.empty:
                return pd.DataFrame()
            
            # Agreguj do miesięcznych (ostatni dzień miesiąca)
            monthly_data = daily_data.resample('ME').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            return monthly_data
            
        except Exception as e:
            logger.error(f"Błąd podczas agregacji danych miesięcznych dla {ticker}: {e}")
            return pd.DataFrame()
    
    def get_stock_data(self, ticker: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """
        Pobiera dane historyczne z bazy danych
        
        Args:
            ticker: Symbol spółki
            timeframe: '1D' lub '1W'
            limit: Maksymalna liczba rekordów
            
        Returns:
            DataFrame z danymi
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT date, open, high, low, close, volume
                    FROM stock_prices 
                    WHERE ticker = ? AND timeframe = ?
                    ORDER BY date DESC
                    LIMIT ?
                """
                
                df = pd.read_sql(query, conn, params=[ticker, timeframe, limit])
                
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    df.sort_index(inplace=True)  # Sortuj chronologicznie
                
                return df
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania danych dla {ticker}: {e}")
            return pd.DataFrame()
    
    def update_stock_data(self, ticker: str):
        """
        Inteligentnie aktualizuje dane dzienne dla danego tickera
        
        Args:
            ticker: Symbol spółki
        """
        try:
            # Sprawdź ostatnią datę w bazie
            last_date = self.get_last_date(ticker, '1D')
            
            # Pobierz nowe dane
            if last_date:
                start_date = last_date + timedelta(days=1)
                logger.info(f"Aktualizuję dane dzienne dla {ticker} od {start_date}")
            else:
                start_date = None
                logger.info(f"Pobieram pełną historię dzienną dla {ticker}")
            
            data = self.fetch_daily_data(ticker, start_date)
            
            if data is not None and not data.empty:
                # Zapisz nowe dane
                self.save_data(ticker, data, '1D')
                
                logger.info(f"Dane dzienne dla {ticker} zaktualizowane pomyślnie")
            else:
                logger.warning(f"Brak nowych danych dziennych dla {ticker}")
                
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji danych dla {ticker}: {e}")
    
    def update_all_stock_data(self, selected_tickers: List[str]):
        """
        Inteligentnie aktualizuje dane dla wszystkich wybranych spółek
        
        Args:
            selected_tickers: Lista tickerów spółek które przeszły selekcję
        """
        try:
            logger.info(f"Rozpoczynam inteligentną aktualizację danych dla {len(selected_tickers)} spółek")
            
            for ticker in selected_tickers:
                try:
                    self.update_stock_data(ticker)
                except Exception as e:
                    logger.error(f"Błąd podczas aktualizacji {ticker}: {e}")
                    continue
            
            # Wyczyść stare dane (starsze niż 5 lat)
            self.cleanup_old_data()
            
            logger.info("Inteligentna aktualizacja danych zakończona")
            
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji wszystkich danych: {e}")
    
    def calculate_stochastic_oscillator(self, data: pd.DataFrame, 
                                      k_period: int = 36, 
                                      d_period: int = 12, 
                                      smoothing: int = 12) -> Tuple[pd.Series, pd.Series]:
        """
        Oblicza Stochastic Oscillator
        
        Args:
            data: DataFrame z danymi (Open, High, Low, Close)
            k_period: Okres dla %K (domyślnie 36)
            d_period: Okres dla %D (domyślnie 12)
            smoothing: Okres wygładzania (domyślnie 12)
            
        Returns:
            Tuple (%K, %D) jako Series
        """
        try:
            # Sprawdź czy mamy wymagane kolumny
            required_columns = ['high', 'low', 'close']
            if not all(col in data.columns for col in required_columns):
                raise ValueError(f"Brak wymaganych kolumn: {required_columns}")
            
            # Sprawdź czy mamy wystarczająco danych
            if len(data) < k_period + smoothing + d_period:
                logger.warning(f"Za mało danych dla obliczenia Stochastic: {len(data)} < {k_period + smoothing + d_period}")
                return pd.Series(), pd.Series()
            
            # Oblicz %K
            lowest_low = data['low'].rolling(window=k_period).min()
            highest_high = data['high'].rolling(window=k_period).max()
            
            # Unikaj dzielenia przez zero
            denominator = highest_high - lowest_low
            denominator = denominator.replace(0, np.nan)
            
            k_raw = 100 * ((data['close'] - lowest_low) / denominator)
            
            # Wygładź %K
            k_smoothed = k_raw.rolling(window=smoothing).mean()
            
            # Oblicz %D (SMA z %K)
            d_smoothed = k_smoothed.rolling(window=d_period).mean()
            
            return k_smoothed, d_smoothed
            
        except Exception as e:
            logger.error(f"Błąd podczas obliczania Stochastic Oscillator: {e}")
            return pd.Series(), pd.Series()
    
    def get_stochastic_values(self, ticker: str) -> Dict[str, float]:
        """
        Pobiera wartości Stochastic Oscillator dla 1M i 1W
        
        Args:
            ticker: Symbol spółki
            
        Returns:
            Dict z wartościami {'1M': float, '1W': float} lub None jeśli błąd
        """
        try:
            result = {}
            
            # Pobierz dane miesięczne dla 1M
            data_1m = self.get_monthly_data(ticker, limit=60)
            if not data_1m.empty and len(data_1m) >= 60:
                k_1m, d_1m = self.calculate_stochastic_oscillator(data_1m, k_period=36, d_period=12, smoothing=12)
                if not d_1m.empty and not pd.isna(d_1m.iloc[-1]):
                    result['1M'] = float(d_1m.iloc[-1])
            
            # Pobierz dane tygodniowe dla 1W
            data_1w = self.get_weekly_data(ticker, limit=260)
            if not data_1w.empty and len(data_1w) >= 60:  # 60 tygodni = ~15 miesięcy
                k_1w, d_1w = self.calculate_stochastic_oscillator(data_1w, k_period=36, d_period=12, smoothing=12)
                if not d_1w.empty and not pd.isna(d_1w.iloc[-1]):
                    result['1W'] = float(d_1w.iloc[-1])
            
            return result if result else None
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania Stochastic dla {ticker}: {e}")
            return None
