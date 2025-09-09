# Timezone Best Practices - Analizator Growth

## ** ZŁOTA ZASADA**
**"Store in UTC, Display in Local"** - Zawsze zapisuj w UTC, wyświetlaj w lokalnym czasie użytkownika.

## ** DLACZEGO UTC W BAZIE DANYCH?**

### **✅ Korzyści:**
1. **Uniwersalność** - działa na całym świecie
2. **Konsystencja** - jeden standard dla wszystkich danych
3. **Migracje** - łatwe przenoszenie między strefami czasowymi
4. **Porównania** - można porównywać dane z różnych stref
5. **Długoterminowość** - nie ma problemów z DST (zmiana czasu)

### **❌ Problemy z lokalnym czasem:**
1. **Nieprzewidywalność** - zależy od strefy czasowej serwera
2. **Migracje** - trudne przenoszenie między strefami
3. **Porównania** - niemożliwe porównanie danych z różnych stref
4. **DST** - problemy z przejściem na czas letni/zimowy

## ** IMPLEMENTACJA W SYSTEMIE**

### **1. Utility Functions (`src/timezone_utils.py`)**

```python
# ✅ DOBRZE - zapis do bazy (UTC)
utc_now = get_utc_now()
cursor.execute("INSERT INTO table (created_at) VALUES (?)", (utc_now,))

# ✅ DOBRZE - wyświetlanie użytkownikowi (CET)
local_time = format_datetime_for_display(utc_now)
print(f"Czas: {local_time}")  # 2025-09-09 10:24:59

# ✅ DOBRZE - konwersja UTC -> CET
local_dt = utc_to_local(utc_dt)

# ✅ DOBRZE - konwersja CET -> UTC
utc_dt = local_to_utc(local_dt)
```

### **2. Baza Danych**

```sql
-- ✅ DOBRZE - wszystkie timestampy bez DEFAULT CURRENT_TIMESTAMP
CREATE TABLE analysis_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TIMESTAMP NOT NULL,  -- UTC
    created_at TIMESTAMP NOT NULL -- UTC
);

-- ❌ BŁĘDNE - CURRENT_TIMESTAMP to UTC w SQLite
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### **3. Scheduler**

```python
# ✅ DOBRZE - scheduler w lokalnej strefie czasowej
scheduler.add_job(
    func=my_job,
    trigger=CronTrigger(hour=10, minute=0, timezone='Europe/Warsaw')
)

# ✅ DOBRZE - run_id w lokalnym czasie
now_local = get_local_now()
run_id = f"auto_{now_local.strftime('%Y%m%d_%H%M%S')}"
```

## ** ZMIANY W SYSTEMIE**

### **✅ Co zostało naprawione:**

1. **Usunięto CURRENT_TIMESTAMP** - wszystkie timestampy są teraz explicit UTC
2. **Dodano timezone_utils.py** - centralne funkcje do zarządzania czasami
3. **Zamieniono datetime.now()** - na get_utc_now() lub get_local_now()
4. **Ujednolicono podejście** - jeden standard w całym systemie

### **📊 Przed vs Po:**

#### **❌ PRZED:**
```python
# Mieszane podejście
datetime.now()  # lokalny czas systemu
datetime.now(warsaw_tz)  # CET
CURRENT_TIMESTAMP  # UTC w SQLite

# Nieprzewidywalne czasy
# Trudne debugowanie
# Brak spójności
```

#### **✅ PO:**
```python
# Spójne podejście
get_utc_now()  # zawsze UTC
get_local_now()  # zawsze CET
format_datetime_for_display(utc_dt)  # konwersja na wyświetlanie

# Przewidywalne czasy
# Łatwe debugowanie
# Pełna spójność
```

## ** UŻYCIE W PRAKTYCE**

### **1. Zapis do bazy danych:**
```python
# ✅ DOBRZE
utc_time = get_utc_now()
cursor.execute("INSERT INTO table (created_at) VALUES (?)", (utc_time,))
```

### **2. Wyświetlanie użytkownikowi:**
```python
# ✅ DOBRZE
display_time = format_datetime_for_display(utc_time)
print(f"Czas: {display_time}")  # 2025-09-09 10:24:59
```

### **3. Porównania dat:**
```python
# ✅ DOBRZE
today = get_local_now().date()
cursor.execute("SELECT * FROM table WHERE DATE(created_at) = ?", (today,))
```

### **4. Logi:**
```python
# ✅ DOBRZE
logger.info(f"Event at {get_utc_now().isoformat()}")
```

## ** TESTING**

### **Sprawdzenie działania:**
```bash
python3 -c "
from src.timezone_utils import get_utc_now, get_local_now, format_datetime_for_display
print(f'UTC: {get_utc_now()}')
print(f'Local: {get_local_now()}')
print(f'Formatted: {format_datetime_for_display(get_utc_now())}')
"
```

## ** KORZYŚCI**

1. **✅ Spójność** - jeden standard w całym systemie
2. **✅ Przewidywalność** - zawsze wiadomo jaki czas
3. **✅ Debugowanie** - łatwe śledzenie problemów z czasem
4. **✅ Migracje** - łatwe przenoszenie między strefami
5. **✅ Skalowalność** - działa na całym świecie
6. **✅ Długoterminowość** - nie ma problemów z DST

## ** PODSUMOWANIE**

System został zoptymalizowany zgodnie z najlepszymi praktykami:

- **Baza danych**: Wszystkie czasy w UTC
- **Wyświetlanie**: Automatyczna konwersja na CET
- **Scheduler**: Lokalna strefa czasowa (Europe/Warsaw)
- **Logi**: UTC dla konsystencji
- **API**: UTC z konwersją na wyświetlanie

**System jest teraz zgodny z międzynarodowymi standardami i gotowy do skalowania!** 🎉
