#!/usr/bin/env python3
"""
Moduł do ładowania konfiguracji z plików YAML i zmiennych środowiskowych
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigLoader:
    """Klasa do ładowania i zarządzania konfiguracją"""
    
    def __init__(self):
        self.config = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """Ładuje wszystkie pliki konfiguracyjne"""
        try:
            # Załaduj konfigurację API
            self.config['api'] = self.load_yaml_config('config/api.yaml')
            
            # Załaduj konfigurację selekcji
            self.config['selection'] = self.load_yaml_config('config/selection_rules.yaml')
            
            # Załaduj konfigurację kolumn
            self.config['columns'] = self.load_yaml_config('config/data_columns.yaml')
            
            # Załaduj konfigurację auto schedule
            self.config['auto_schedule'] = self.load_yaml_config('config/auto_schedule.yaml')
            
            # Załaduj konfigurację wersji
            self.config['version'] = self.load_yaml_config('config/version.yaml')
            
            logger.info("Wszystkie konfiguracje załadowane pomyślnie")
            
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
            raise
    
    def load_yaml_config(self, file_path: str) -> Dict[str, Any]:
        """Ładuje konfigurację z pliku YAML"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Plik konfiguracyjny nie istnieje: {file_path}")
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            # Przetwórz zmienne środowiskowe
            config = self.process_env_variables(config)
            
            return config
            
        except Exception as e:
            logger.error(f"Błąd podczas ładowania {file_path}: {e}")
            return {}
    
    def process_env_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Przetwarza zmienne środowiskowe w konfiguracji"""
        if isinstance(config, dict):
            processed = {}
            for key, value in config.items():
                processed[key] = self.process_env_variables(value)
            return processed
        elif isinstance(config, list):
            return [self.process_env_variables(item) for item in config]
        elif isinstance(config, str) and config.startswith('{{ env.') and config.endswith('}}'):
            # Wyciągnij nazwę zmiennej środowiskowej
            env_var = config[7:-2]  # Usuń '{{ env.' i '}}'
            return os.getenv(env_var, config)  # Zwróć zmienną lub oryginalny tekst
        else:
            return config
    
    def get_api_key(self) -> str:
        """Pobiera API key z konfiguracji"""
        try:
            # Sprawdź zmienną środowiskową
            env_key = os.getenv('API_KEY')
            if env_key:
                return env_key
            
            # Sprawdź konfigurację
            api_config = self.config.get('api', {})
            api_key = api_config.get('key', 'default_key_change_me')
            
            # Jeśli to nadal template, użyj domyślnego
            if api_key.startswith('{{ env.'):
                api_key = 'default_key_change_me'
            
            return api_key
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania API key: {e}")
            return 'default_key_change_me'
    
    def get_config(self, section: str) -> Dict[str, Any]:
        """Pobiera konfigurację dla danej sekcji"""
        return self.config.get(section, {})
    
    def is_api_auth_enabled(self) -> bool:
        """Sprawdza czy autoryzacja API jest włączona"""
        api_config = self.config.get('api', {})
        security_config = api_config.get('security', {})
        return security_config.get('enable_api_auth', True)
    
    def get_timeout(self) -> int:
        """Pobiera timeout dla API"""
        api_config = self.config.get('api', {})
        return api_config.get('timeout', 30)
    
    def get_max_retries(self) -> int:
        """Pobiera maksymalną liczbę prób"""
        api_config = self.config.get('api', {})
        return api_config.get('max_retries', 3)
    
    def get_version_info(self) -> Dict[str, Any]:
        """Pobiera informacje o wersji z pliku lub zmiennych środowiskowych"""
        # Sprawdź zmienne środowiskowe Docker
        docker_version = os.getenv('APP_VERSION')
        docker_build = os.getenv('APP_BUILD')
        docker_release_date = os.getenv('APP_RELEASE_DATE')
        
        if docker_version:
            # Użyj wersji z Docker
            return {
                'version': {
                    'major': int(docker_version.split('.')[0].replace('v', '')),
                    'minor': int(docker_version.split('.')[1]),
                    'patch': int(docker_version.split('.')[2]),
                    'build': int(docker_build) if docker_build else 0
                },
                'info': {
                    'name': 'Analizator Growth',
                    'full_name': f'Analizator Growth {docker_version}',
                    'description': 'System analizy spółek giełdowych z selekcją i oceną',
                    'release_date': docker_release_date or '2025-09-07'
                }
            }
        else:
            # Użyj wersji z pliku
            return self.config.get('version', {})
    
    def get_version_string(self) -> str:
        """Pobiera string wersji (np. '1.0.0')"""
        version = self.get_version_info()
        major = version.get('version', {}).get('major', 1)
        minor = version.get('version', {}).get('minor', 0)
        patch = version.get('version', {}).get('patch', 0)
        return f"{major}.{minor}.{patch}"
    
    def get_full_version_string(self) -> str:
        """Pobiera pełny string wersji (np. 'v1.0.0 build 1')"""
        version = self.get_version_info()
        major = version.get('version', {}).get('major', 1)
        minor = version.get('version', {}).get('minor', 0)
        patch = version.get('version', {}).get('patch', 0)
        build = version.get('version', {}).get('build', 1)
        return f"v{major}.{minor}.{patch} build {build}"
    
    def get_app_name(self) -> str:
        """Pobiera nazwę aplikacji"""
        version = self.get_version_info()
        return version.get('info', {}).get('name', 'Analizator Growth')
    
    def get_app_description(self) -> str:
        """Pobiera opis aplikacji"""
        version = self.get_version_info()
        return version.get('info', {}).get('description', 'System analizy spółek giełdowych')

# Globalna instancja
config_loader = ConfigLoader()

def get_api_key() -> str:
    """Funkcja pomocnicza do pobierania API key"""
    return config_loader.get_api_key()

def get_config(section: str) -> Dict[str, Any]:
    """Funkcja pomocnicza do pobierania konfiguracji"""
    return config_loader.get_config(section)

def is_api_auth_enabled() -> bool:
    """Funkcja pomocnicza do sprawdzania autoryzacji API"""
    return config_loader.is_api_auth_enabled()

def get_version_info() -> Dict[str, Any]:
    """Funkcja pomocnicza do pobierania informacji o wersji"""
    return config_loader.get_version_info()

def get_version_string() -> str:
    """Funkcja pomocnicza do pobierania string wersji"""
    return config_loader.get_version_string()

def get_full_version_string() -> str:
    """Funkcja pomocnicza do pobierania pełnego string wersji"""
    return config_loader.get_full_version_string()

def get_app_name() -> str:
    """Funkcja pomocnicza do pobierania nazwy aplikacji"""
    return config_loader.get_app_name()

def get_app_description() -> str:
    """Funkcja pomocnicza do pobierania opisu aplikacji"""
    return config_loader.get_app_description()
