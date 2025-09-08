import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFinanceAnalyzer:
    """
    Klasa do analizy danych z Yahoo Finance i obliczania wskaźników technicznych
    """
    
    def __init__(self):
        self.cache = {}  # Prosty cache dla pobranych danych
    
    def get_stock_data(self, ticker: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """
        Pobiera dane historyczne dla danej spółki z walidacją
        
        Args:
            ticker: Symbol spółki (np. 'AAPL')
            period: Okres danych ('1mo', '1wk', '1d', etc.)
            
        Returns:
            DataFrame z danymi lub None jeśli błąd
        """
        try:
            # Waliduj ticker
            if not self._validate_ticker(ticker):
                logger.error(f"Nieprawidłowy ticker: {ticker}")
                return None
            
            if ticker in self.cache and period in self.cache[ticker]:
                logger.info(f"Używam cache dla {ticker} ({period})")
                return self.cache[ticker][period]
            
            logger.info(f"Pobieram dane dla {ticker} ({period})")
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                logger.warning(f"Brak danych dla {ticker}")
                return None
            
            # Waliduj dane
            if not self._validate_stock_data(data):
                logger.warning(f"Dane dla {ticker} nie przeszły walidacji")
                return None
            
            # Inicjalizuj cache
            if ticker not in self.cache:
                self.cache[ticker] = {}
            self.cache[ticker][period] = data
            
            return data
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania danych dla {ticker}: {e}")
            return None
    
    def _validate_ticker(self, ticker: str) -> bool:
        """
        Waliduje format tickera
        """
        import re
        if not ticker or not isinstance(ticker, str):
            return False
        
        # Ticker powinien zawierać tylko litery, cyfry i kropki
        pattern = r'^[A-Za-z0-9.]+$'
        return bool(re.match(pattern, ticker.strip()))
    
    def _validate_stock_data(self, data: pd.DataFrame) -> bool:
        """
        Waliduje dane giełdowe
        """
        try:
            # Sprawdź czy DataFrame nie jest pusty
            if data.empty:
                return False
            
            # Sprawdź wymagane kolumny
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_columns):
                logger.warning(f"Brak wymaganych kolumn: {required_columns}")
                return False
            
            # Sprawdź czy ceny są dodatnie
            price_columns = ['Open', 'High', 'Low', 'Close']
            for col in price_columns:
                if (data[col] <= 0).any():
                    logger.warning(f"Znaleziono nieprawidłowe ceny w kolumnie {col}")
                    return False
            
            # Sprawdź czy High >= Low
            if (data['High'] < data['Low']).any():
                logger.warning("Znaleziono wiersze gdzie High < Low")
                return False
            
            # Sprawdź czy High >= Open i High >= Close
            if (data['High'] < data['Open']).any() or (data['High'] < data['Close']).any():
                logger.warning("Znaleziono wiersze gdzie High < Open lub High < Close")
                return False
            
            # Sprawdź czy Low <= Open i Low <= Close
            if (data['Low'] > data['Open']).any() or (data['Low'] > data['Close']).any():
                logger.warning("Znaleziono wiersze gdzie Low > Open lub Low > Close")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Błąd podczas walidacji danych: {e}")
            return False
    
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
            required_columns = ['High', 'Low', 'Close']
            if not all(col in data.columns for col in required_columns):
                raise ValueError(f"Brak wymaganych kolumn: {required_columns}")
            
            # Oblicz %K
            lowest_low = data['Low'].rolling(window=k_period).min()
            highest_high = data['High'].rolling(window=k_period).max()
            
            # Unikaj dzielenia przez zero
            denominator = highest_high - lowest_low
            denominator = denominator.replace(0, np.nan)
            
            k_raw = 100 * ((data['Close'] - lowest_low) / denominator)
            
            # Wygładź %K
            k_smoothed = k_raw.rolling(window=smoothing).mean()
            
            # Oblicz %D (SMA z %K)
            d_smoothed = k_smoothed.rolling(window=d_period).mean()
            
            return k_smoothed, d_smoothed
            
        except Exception as e:
            logger.error(f"Błąd podczas obliczania Stochastic Oscillator: {e}")
            return pd.Series(), pd.Series()
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Pobiera aktualną cenę spółki
        
        Args:
            ticker: Symbol spółki (np. 'AAPL')
            
        Returns:
            Aktualna cena lub None jeśli błąd
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Spróbuj różne klucze dla ceny
            current_price = None
            price_keys = ['currentPrice', 'regularMarketPrice', 'price']
            
            for key in price_keys:
                if key in info and info[key] is not None:
                    current_price = float(info[key])
                    break
            
            if current_price is None:
                logger.warning(f"Nie można pobrać ceny dla {ticker}")
                return None
            
            logger.info(f"Aktualna cena {ticker}: ${current_price:.2f}")
            return current_price
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania ceny dla {ticker}: {e}")
            return None
    
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
            
            # Pobierz dane dla 5 lat (więcej danych dla obliczeń)
            data_5y = self.get_stock_data(ticker, "5y")
            if data_5y is not None and not data_5y.empty:
                # Użyj standardowych parametrów 36,12,12 dla miesięcznych
                k_1m, d_1m = self.calculate_stochastic_oscillator(data_5y, k_period=36, d_period=12, smoothing=12)
                if not d_1m.empty:
                    result['1M'] = d_1m.iloc[-1]  # Ostatnia wartość %D
            
            # Pobierz dane dla 2 lat (dla tygodniowych obliczeń)
            data_2y = self.get_stock_data(ticker, "2y")
            if data_2y is not None and not data_2y.empty:
                # Użyj standardowych parametrów 36,12,12 dla tygodniowych
                k_1w, d_1w = self.calculate_stochastic_oscillator(data_2y, k_period=36, d_period=12, smoothing=12)
                if not d_1w.empty:
                    result['1W'] = d_1w.iloc[-1]  # Ostatnia wartość %D
            
            return result if result else None
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania Stochastic dla {ticker}: {e}")
            return None
    
    def check_stage2_conditions(self, ticker: str, threshold: float = 30.0) -> Dict[str, any]:
        """
        Sprawdza warunki Etapu 2 dla danej spółki
        
        Args:
            ticker: Symbol spółki
            threshold: Próg dla Stochastic (domyślnie 30%)
            
        Returns:
            Dict z wynikami analizy
        """
        try:
            stochastic_values = self.get_stochastic_values(ticker)
            
            if stochastic_values is None:
                return {
                    'ticker': ticker,
                    'stochastic_1m': None,
                    'stochastic_1w': None,
                    'stage2_passed': False,
                    'error': 'Nie udało się pobrać danych'
                }
            
            stochastic_1m = stochastic_values.get('1M')
            stochastic_1w = stochastic_values.get('1W')
            
            # Sprawdź warunki: przynajmniej jeden < threshold
            condition_1m = stochastic_1m is not None and stochastic_1m < threshold
            condition_1w = stochastic_1w is not None and stochastic_1w < threshold
            
            stage2_passed = condition_1m or condition_1w
            
            return {
                'ticker': ticker,
                'stochastic_1m': stochastic_1m,
                'stochastic_1w': stochastic_1w,
                'stage2_passed': stage2_passed,
                'condition_1m': condition_1m,
                'condition_1w': condition_1w,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania warunków Etapu 2 dla {ticker}: {e}")
            return {
                'ticker': ticker,
                'stochastic_1m': None,
                'stochastic_1w': None,
                'stage2_passed': False,
                'error': str(e)
            }
    
    def analyze_stage2_stocks(self, tickers: List[str]) -> pd.DataFrame:
        """
        Analizuje listę spółek pod kątem warunków Etapu 2
        
        Args:
            tickers: Lista symboli spółek
            
        Returns:
            DataFrame z wynikami analizy
        """
        results = []
        
        for ticker in tickers:
            logger.info(f"Analizuję {ticker}...")
            result = self.check_stage2_conditions(ticker)
            results.append(result)
        
        df = pd.DataFrame(results)
        return df 