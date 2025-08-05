#!/usr/bin/env python3
"""
Moduł do zarządzania automatycznym uruchamianiem analizy
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import yaml

# Dodaj ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from database_manager import DatabaseManager
from stage2_analysis import main as run_analysis

# Konfiguracja logowania
def setup_logging():
    """Konfiguruje dual logging - czytelne i JSON"""
    
    # Katalog na logi
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Logger dla czytelnych logów
    readable_logger = logging.getLogger('auto_schedule_readable')
    readable_logger.setLevel(logging.INFO)
    
    readable_handler = logging.FileHandler(f'{log_dir}/auto_schedule.log')
    readable_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    readable_handler.setFormatter(readable_formatter)
    readable_logger.addHandler(readable_handler)
    
    # Logger dla JSON logów (monitoring)
    json_logger = logging.getLogger('auto_schedule_monitoring')
    json_logger.setLevel(logging.INFO)
    
    json_handler = logging.FileHandler(f'{log_dir}/auto_schedule_monitoring.json')
    json_formatter = logging.Formatter('%(message)s')  # Tylko wiadomość JSON
    json_handler.setFormatter(json_formatter)
    json_logger.addHandler(json_handler)
    
    return readable_logger, json_logger

class AutoScheduler:
    """Klasa do zarządzania automatycznym uruchamianiem analizy"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db_manager = DatabaseManager()
        self.readable_logger, self.json_logger = setup_logging()
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Ładuje konfigurację automatycznego uruchamiania"""
        try:
            config_path = 'config/auto_schedule.yaml'
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
            else:
                # Domyślna konfiguracja
                default_config = {
                    'auto_schedule': {
                        'enabled': False,
                        'time': '09:00',
                        'timezone': 'Europe/Warsaw',
                        'interval_hours': 24
                    }
                }
                # Zapisz domyślną konfigurację
                with open(config_path, 'w', encoding='utf-8') as file:
                    yaml.dump(default_config, file, default_flow_style=False)
                return default_config
        except Exception as e:
            self.readable_logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
            return {'auto_schedule': {'enabled': False}}
    
    def _save_config(self):
        """Zapisuje konfigurację do pliku"""
        try:
            config_path = 'config/auto_schedule.yaml'
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False)
        except Exception as e:
            self.readable_logger.error(f"Błąd podczas zapisywania konfiguracji: {e}")
    
    def _log_event(self, event: str, **kwargs):
        """Loguje event w obu formatach"""
        timestamp = datetime.now().isoformat()
        
        # Czytelny log
        message = f"Event: {event}"
        if kwargs:
            message += f" - {kwargs}"
        self.readable_logger.info(message)
        
        # JSON log dla monitoringu
        json_event = {
            "timestamp": timestamp,
            "event": event,
            **kwargs
        }
        self.json_logger.info(json.dumps(json_event))
    
    def _run_analysis_job(self):
        """Funkcja uruchamiana przez scheduler"""
        run_id = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        # Log rozpoczęcia
        self._log_event("auto_analysis_started", 
                       run_id=run_id, 
                       scheduled_time=self.config['auto_schedule']['time'])
        
        # Zapisz rozpoczęcie do bazy
        self._save_run_start(run_id, start_time)
        
        try:
            # Uruchom analizę
            run_analysis()
            
            # Oblicz czas wykonania
            end_time = datetime.now()
            execution_time = int((end_time - start_time).total_seconds())
            
            # Pobierz liczbę spółek z ostatniego uruchomienia
            latest_run = self.db_manager.get_latest_run()
            companies_count = len(latest_run['stage1_companies']) if latest_run and 'stage1_companies' in latest_run else 0
            
            # Log sukcesu
            self._log_event("auto_analysis_completed",
                           run_id=run_id,
                           status="success",
                           execution_time_seconds=execution_time,
                           companies_count=companies_count)
            
            # Zapisz sukces do bazy
            self._save_run_completion(run_id, end_time, "success", None, companies_count, execution_time)
            
        except Exception as e:
            # Oblicz czas wykonania
            end_time = datetime.now()
            execution_time = int((end_time - start_time).total_seconds())
            
            error_details = {
                "type": type(e).__name__,
                "message": str(e),
                "recoverable": True
            }
            
            # Log błędu
            self._log_event("auto_analysis_error",
                           run_id=run_id,
                           status="error",
                           error_details=error_details,
                           execution_time_seconds=execution_time)
            
            # Zapisz błąd do bazy
            self._save_run_completion(run_id, end_time, "error", json.dumps(error_details), 0, execution_time)
    
    def _run_flag_snapshot_job(self, run_id: str = None):
        """Wykonuje codzienny snapshot flag - zapisuje aktualny stan wszystkich flag"""
        try:
            self._log_event('flag_snapshot_started', time=datetime.now().isoformat())
            self.readable_logger.info("Rozpoczęto codzienny snapshot flag")
            
            # Pobierz wszystkie aktualne flagi
            flags_df = self.db_manager.get_all_flags()
            
            if flags_df.empty:
                self.readable_logger.info("Brak flag do zapisania w historii")
                return
            
            # Zapisz snapshot do historii
            snapshot_count = 0
            for _, row in flags_df.iterrows():
                ticker = row['ticker']
                flag_color = row['flag_color']
                flag_notes = row.get('flag_notes', '')
                
                # Sprawdź czy już jest wpis z dzisiaj dla tego tickera
                today = datetime.now().date()
                
                # Zapisz do historii z powodem 'daily_snapshot'
                success = self._save_flag_to_history(
                    ticker, flag_color, flag_notes, 'daily_snapshot', run_id
                )
                
                if success:
                    snapshot_count += 1
            
            self._log_event('flag_snapshot_completed', 
                           snapshot_count=snapshot_count,
                           time=datetime.now().isoformat())
            
            self.readable_logger.info(f"Codzienny snapshot flag zakończony - zapisano {snapshot_count} flag")
            
        except Exception as e:
            error_details = str(e)
            self._log_event('flag_snapshot_failed', 
                           error=error_details,
                           time=datetime.now().isoformat())
            self.readable_logger.error(f"Błąd podczas codziennego snapshotu flag: {error_details}")
    
    def _save_flag_to_history(self, ticker: str, flag_color: str, flag_notes: str, 
                             change_reason: str, run_id: str = None) -> bool:
        """Zapisuje flagę do historii"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Sprawdź czy już jest wpis z dzisiaj dla tego tickera
                today = datetime.now().date()
                cursor.execute("""
                    SELECT id FROM flag_history 
                    WHERE ticker = ? AND DATE(changed_at) = ? AND change_reason = 'daily_snapshot'
                """, (ticker, today))
                
                if cursor.fetchone():
                    # Aktualizuj istniejący wpis
                    cursor.execute("""
                        UPDATE flag_history 
                        SET flag_color = ?, flag_notes = ?, changed_at = CURRENT_TIMESTAMP
                        WHERE ticker = ? AND DATE(changed_at) = ? AND change_reason = 'daily_snapshot'
                    """, (flag_color, flag_notes, ticker, today))
                else:
                    # Dodaj nowy wpis
                    cursor.execute("""
                        INSERT INTO flag_history (ticker, flag_color, flag_notes, change_reason, run_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (ticker, flag_color, flag_notes, change_reason, run_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.readable_logger.error(f"Błąd podczas zapisywania flagi do historii: {e}")
            return False
    
    def _save_run_start(self, run_id: str, start_time: datetime):
        """Zapisuje rozpoczęcie uruchomienia do bazy"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO auto_schedule_runs 
                    (run_id, scheduled_time, started_at, status)
                    VALUES (?, ?, ?, ?)
                """, (run_id, start_time, start_time, 'running'))
                conn.commit()
        except Exception as e:
            self.readable_logger.error(f"Błąd podczas zapisywania rozpoczęcia uruchomienia: {e}")
    
    def _save_run_completion(self, run_id: str, completed_at: datetime, status: str, 
                           error_details: Optional[str], companies_count: int, execution_time: int):
        """Zapisuje zakończenie uruchomienia do bazy"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE auto_schedule_runs 
                    SET completed_at = ?, status = ?, error_details = ?, 
                        companies_count = ?, execution_time_seconds = ?
                    WHERE run_id = ?
                """, (completed_at, status, error_details, companies_count, execution_time, run_id))
                conn.commit()
        except Exception as e:
            self.readable_logger.error(f"Błąd podczas zapisywania zakończenia uruchomienia: {e}")
    
    def start(self):
        """Uruchamia scheduler"""
        jobs_added = False
        
        # Dodaj zadanie analizy jeśli włączone
        if self.config['auto_schedule']['enabled']:
            try:
                time_str = self.config['auto_schedule']['time']
                hour, minute = map(int, time_str.split(':'))
                timezone = self.config['auto_schedule']['timezone']
                
                self.scheduler.add_job(
                    func=self._run_analysis_job,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
                    id='daily_analysis',
                    name='Codzienna analiza',
                    replace_existing=True
                )
                jobs_added = True
                self.readable_logger.info(f"Dodano zadanie analizy - codziennie o {time_str} ({timezone})")
            except Exception as e:
                self.readable_logger.error(f"Błąd podczas dodawania zadania analizy: {e}")
        
        # Dodaj zadanie flag snapshot jeśli włączone
        if self.config.get('flag_snapshot', {}).get('enabled', False):
            try:
                time_str = self.config['flag_snapshot']['time']
                hour, minute = map(int, time_str.split(':'))
                timezone = self.config['flag_snapshot']['timezone']
                
                self.scheduler.add_job(
                    func=self._run_flag_snapshot_job,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
                    id='flag_snapshot',
                    name='Zapis flag tickerów',
                    replace_existing=True
                )
                jobs_added = True
                self.readable_logger.info(f"Dodano zadanie flag snapshot - codziennie o {time_str} ({timezone})")
            except Exception as e:
                self.readable_logger.error(f"Błąd podczas dodawania zadania flag snapshot: {e}")
        
        if not jobs_added:
            self.readable_logger.info("Brak włączonych zadań")
            return
        
        try:
            # Uruchom scheduler
            self.scheduler.start()
            
            self._log_event("scheduler_started")
            self.readable_logger.info("Scheduler uruchomiony")
            
        except Exception as e:
            self.readable_logger.error(f"Błąd podczas uruchamiania schedulera: {e}")
    
    def stop(self):
        """Zatrzymuje scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self._log_event("scheduler_stopped")
            self.readable_logger.info("Scheduler zatrzymany")
    
    def update_config(self, enabled: bool, time: str, timezone: str = 'Europe/Warsaw'):
        """Aktualizuje konfigurację"""
        self.config['auto_schedule']['enabled'] = enabled
        self.config['auto_schedule']['time'] = time
        self.config['auto_schedule']['timezone'] = timezone
        
        self._save_config()
        
        # Restart scheduler jeśli był uruchomiony
        if self.scheduler.running:
            self.stop()
        
        if enabled:
            self.start()
        
        self._log_event("config_updated", enabled=enabled, time=time, timezone=timezone)
    
    def update_flag_snapshot_config(self, enabled: bool, time: str, timezone: str = 'Europe/Warsaw'):
        """Aktualizuje konfigurację flag snapshot"""
        if 'flag_snapshot' not in self.config:
            self.config['flag_snapshot'] = {}
        
        self.config['flag_snapshot']['enabled'] = enabled
        self.config['flag_snapshot']['time'] = time
        self.config['flag_snapshot']['timezone'] = timezone
        
        self._save_config()
        
        # Restart scheduler jeśli był uruchomiony
        if self.scheduler.running:
            self.stop()
        
        if enabled:
            self.start()
        
        self._log_event("flag_snapshot_config_updated", enabled=enabled, time=time, timezone=timezone)
    
    def get_status(self) -> Dict:
        """Zwraca aktualny status schedulera"""
        status = {
            'enabled': self.config['auto_schedule']['enabled'],
            'time': self.config['auto_schedule']['time'],
            'timezone': self.config['auto_schedule']['timezone'],
            'scheduler_running': self.scheduler.running,
            'next_run': None
        }
        
        if self.scheduler.running:
            job = self.scheduler.get_job('daily_analysis')
            if job:
                status['next_run'] = job.next_run_time.isoformat()
        
        return status
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Zwraca historię automatycznych uruchomień"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT run_id, scheduled_time, started_at, completed_at, 
                           status, error_details, companies_count, execution_time_seconds
                    FROM auto_schedule_runs
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                history = []
                
                for row in rows:
                    history.append({
                        'run_id': row[0],
                        'scheduled_time': row[1],
                        'started_at': row[2],
                        'completed_at': row[3],
                        'status': row[4],
                        'error_details': json.loads(row[5]) if row[5] else None,
                        'companies_count': row[6],
                        'execution_time_seconds': row[7]
                    })
                
                return history
                
        except Exception as e:
            self.readable_logger.error(f"Błąd podczas pobierania historii: {e}")
            return []
    
    def run_now(self) -> Dict:
        """Uruchamia analizę natychmiast"""
        try:
            self._run_analysis_job()
            return {"success": True, "message": "Analiza uruchomiona pomyślnie"}
        except Exception as e:
            return {"success": False, "message": f"Błąd: {str(e)}"}

# Globalna instancja
auto_scheduler = None

def init_auto_scheduler():
    """Inicjalizuje globalną instancję auto_scheduler"""
    global auto_scheduler
    auto_scheduler = AutoScheduler()
    auto_scheduler.start()
    return auto_scheduler

def get_auto_scheduler() -> AutoScheduler:
    """Zwraca globalną instancję auto_scheduler"""
    global auto_scheduler
    if auto_scheduler is None:
        auto_scheduler = AutoScheduler()
    return auto_scheduler 