"""
Utility functions for timezone handling
Zgodnie z dobrymi praktykami: Store in UTC, Display in Local
"""

import pytz
from datetime import datetime
from typing import Optional

# Strefa czasowa aplikacji
APP_TIMEZONE = 'Europe/Warsaw'
UTC = pytz.UTC

def get_utc_now() -> datetime:
    """
    Zwraca aktualny czas w UTC
    Używaj do zapisywania do bazy danych
    """
    return datetime.utcnow()

def get_local_now() -> datetime:
    """
    Zwraca aktualny czas w strefie czasowej aplikacji (CET)
    Używaj do wyświetlania użytkownikowi
    """
    warsaw_tz = pytz.timezone(APP_TIMEZONE)
    return datetime.now(warsaw_tz)

def utc_to_local(utc_dt: datetime) -> datetime:
    """
    Konwertuje UTC datetime na lokalny czas (CET)
    Używaj do wyświetlania danych z bazy
    """
    if utc_dt.tzinfo is None:
        # Jeśli datetime nie ma timezone info, zakładamy że to UTC
        utc_dt = UTC.localize(utc_dt)
    elif utc_dt.tzinfo != UTC:
        # Jeśli to nie UTC, konwertuj na UTC
        utc_dt = utc_dt.astimezone(UTC)
    
    warsaw_tz = pytz.timezone(APP_TIMEZONE)
    return utc_dt.astimezone(warsaw_tz)

def local_to_utc(local_dt: datetime) -> datetime:
    """
    Konwertuje lokalny czas (CET) na UTC
    Używaj przed zapisem do bazy danych
    """
    if local_dt.tzinfo is None:
        # Jeśli datetime nie ma timezone info, zakładamy że to lokalny czas
        warsaw_tz = pytz.timezone(APP_TIMEZONE)
        local_dt = warsaw_tz.localize(local_dt)
    
    return local_dt.astimezone(UTC)

def format_datetime_for_display(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Formatuje datetime do wyświetlania użytkownikowi
    Automatycznie konwertuje UTC na lokalny czas
    """
    if dt.tzinfo is None:
        # Jeśli datetime nie ma timezone info, zakładamy że to UTC
        dt = UTC.localize(dt)
    elif dt.tzinfo != UTC:
        # Jeśli to nie UTC, konwertuj na UTC a potem na lokalny
        dt = dt.astimezone(UTC)
    
    local_dt = utc_to_local(dt)
    return local_dt.strftime(format_str)

def get_local_date() -> datetime:
    """
    Zwraca aktualną datę w strefie czasowej aplikacji
    Używaj do porównań dat
    """
    return get_local_now().date()

def get_utc_date() -> datetime:
    """
    Zwraca aktualną datę w UTC
    Używaj do zapisywania do bazy danych
    """
    return get_utc_now().date()

def ensure_utc(dt: datetime) -> datetime:
    """
    Zapewnia że datetime jest w UTC
    Używaj przed zapisem do bazy danych
    """
    if dt.tzinfo is None:
        # Jeśli datetime nie ma timezone info, zakładamy że to UTC
        return UTC.localize(dt)
    elif dt.tzinfo == UTC:
        return dt
    else:
        # Konwertuj na UTC
        return dt.astimezone(UTC)

def ensure_local(dt: datetime) -> datetime:
    """
    Zapewnia że datetime jest w lokalnej strefie czasowej
    Używaj do wyświetlania
    """
    if dt.tzinfo is None:
        # Jeśli datetime nie ma timezone info, zakładamy że to UTC
        return utc_to_local(UTC.localize(dt))
    elif dt.tzinfo == pytz.timezone(APP_TIMEZONE):
        return dt
    else:
        # Konwertuj na lokalny czas
        return utc_to_local(dt)
