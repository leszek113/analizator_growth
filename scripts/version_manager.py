#!/usr/bin/env python3
"""
Centralny mechanizm zarządzania wersjami dla Analizator Growth
Automatycznie synchronizuje wersje we wszystkich plikach projektu
"""

import os
import re
import yaml
import json
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VersionManager:
    """
    Klasa do centralnego zarządzania wersjami projektu
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.version_file = os.path.join(project_root, "VERSION")
        self.version_info = self._load_version_info()
    
    def _load_version_info(self) -> Dict:
        """Ładuje informacje o wersji z pliku VERSION"""
        version_file = os.path.join(self.project_root, "VERSION")
        
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                content = f.read().strip()
                return self._parse_version_string(content)
        else:
            # Domyślna wersja
            return {
                'major': 1,
                'minor': 2,
                'patch': 3,
                'build': 0,
                'release_date': '2025-01-15'
            }
    
    def _parse_version_string(self, version_str: str) -> Dict:
        """Parsuje string wersji (np. '1.2.3') na słownik"""
        # Usuń 'v' z początku jeśli istnieje
        version_str = version_str.lstrip('v')
        
        # Podziel na części
        parts = version_str.split('.')
        
        return {
            'major': int(parts[0]) if len(parts) > 0 else 1,
            'minor': int(parts[1]) if len(parts) > 1 else 0,
            'patch': int(parts[2]) if len(parts) > 2 else 0,
            'build': int(parts[3]) if len(parts) > 3 else 0,
            'release_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def get_version_string(self) -> str:
        """Zwraca string wersji (np. '1.2.3')"""
        return f"{self.version_info['major']}.{self.version_info['minor']}.{self.version_info['patch']}"
    
    def get_full_version_string(self) -> str:
        """Zwraca pełny string wersji (np. 'v1.2.3 build 0')"""
        return f"v{self.get_version_string()} build {self.version_info['build']}"
    
    def get_docker_version(self) -> str:
        """Zwraca wersję dla Docker (np. 'v1.2.3')"""
        return f"v{self.get_version_string()}"
    
    def increment_patch(self):
        """Zwiększa patch version"""
        self.version_info['patch'] += 1
        self.version_info['build'] = 0
        self.version_info['release_date'] = datetime.now().strftime('%Y-%m-%d')
        self._save_version()
    
    def increment_minor(self):
        """Zwiększa minor version"""
        self.version_info['minor'] += 1
        self.version_info['patch'] = 0
        self.version_info['build'] = 0
        self.version_info['release_date'] = datetime.now().strftime('%Y-%m-%d')
        self._save_version()
    
    def increment_major(self):
        """Zwiększa major version"""
        self.version_info['major'] += 1
        self.version_info['minor'] = 0
        self.version_info['patch'] = 0
        self.version_info['build'] = 0
        self.version_info['release_date'] = datetime.now().strftime('%Y-%m-%d')
        self._save_version()
    
    def increment_build(self):
        """Zwiększa build number"""
        self.version_info['build'] += 1
        self._save_version()
    
    def _save_version(self):
        """Zapisuje wersję do pliku VERSION"""
        version_file = os.path.join(self.project_root, "VERSION")
        with open(version_file, 'w') as f:
            f.write(self.get_version_string())
        logger.info(f"Zapisano wersję: {self.get_version_string()}")
    
    def sync_all_files(self):
        """Synchronizuje wersję we wszystkich plikach projektu"""
        logger.info("Synchronizacja wersji we wszystkich plikach...")
        
        # Lista plików do aktualizacji z wzorcami
        files_to_update = [
            {
                'path': 'config/version.yaml',
                'patterns': [
                    (r'major: \d+', f"major: {self.version_info['major']}"),
                    (r'minor: \d+', f"minor: {self.version_info['minor']}"),
                    (r'patch: \d+', f"patch: {self.version_info['patch']}"),
                    (r'build: \d+', f"build: {self.version_info['build']}"),
                    (r'release_date: "[\d-]+"', f'release_date: "{self.version_info["release_date"]}"'),
                    (r'full_name: "Analizator Growth v[\d.]+"', f'full_name: "Analizator Growth v{self.get_version_string()}"')
                ]
            },
            {
                'path': 'README.md',
                'patterns': [
                    (r'# Analizator Growth - v[\d.]+', f'# Analizator Growth - v{self.get_version_string()}'),
                    (r'## \[[\d.]+\] - \d{4}-\d{2}-\d{2}', f'## [{self.get_version_string()}] - {self.version_info["release_date"]}')
                ]
            },
            {
                'path': 'Dockerfile',
                'patterns': [
                    (r'ENV APP_VERSION="v[\d.]+"', f'ENV APP_VERSION="{self.get_docker_version()}"'),
                    (r'ENV APP_BUILD="\d+"', f'ENV APP_BUILD="{self.version_info["build"]}"'),
                    (r'ENV APP_RELEASE_DATE="[\d-]+"', f'ENV APP_RELEASE_DATE="{self.version_info["release_date"]}"')
                ]
            },
            {
                'path': 'docker-compose.yml',
                'patterns': [
                    (r'container_name: analizator-growth-v[\d.]+', f'container_name: analizator-growth-{self.get_version_string()}'),
                    (r'image: leszek113/analizator-growth:v[\d.]+', f'image: leszek113/analizator-growth:{self.get_docker_version()}'),
                    (r'APP_VERSION=v[\d.]+', f'APP_VERSION={self.get_docker_version()}'),
                    (r'APP_BUILD=\d+', f'APP_BUILD={self.version_info["build"]}'),
                    (r'APP_RELEASE_DATE=[\d-]+', f'APP_RELEASE_DATE={self.version_info["release_date"]}')
                ]
            },
            {
                'path': 'docker-compose-ubuntu.yml',
                'patterns': [
                    (r'container_name: analizator-growth-v[\d.]+', f'container_name: analizator-growth-{self.get_version_string()}'),
                    (r'image: leszek113/analizator-growth:v[\d.]+', f'image: leszek113/analizator-growth:{self.get_docker_version()}'),
                    (r'APP_VERSION=v[\d.]+', f'APP_VERSION={self.get_docker_version()}'),
                    (r'APP_BUILD=\d+', f'APP_BUILD={self.version_info["build"]}'),
                    (r'APP_RELEASE_DATE=[\d-]+', f'APP_RELEASE_DATE={self.version_info["release_date"]}')
                ]
            },
            {
                'path': 'docker-entrypoint.sh',
                'patterns': [
                    (r'# Analizator Growth v[\d.]+', f'# Analizator Growth {self.get_docker_version()}'),
                    (r'echo "🚀 Uruchamianie Analizatora Growth v[\d.]+..."', f'echo "🚀 Uruchamianie Analizatora Growth {self.get_docker_version()}..."')
                ]
            }
        ]
        
        # Aktualizuj każdy plik
        for file_info in files_to_update:
            file_path = os.path.join(self.project_root, file_info['path'])
            if os.path.exists(file_path):
                self._update_file(file_path, file_info['patterns'])
            else:
                logger.warning(f"Plik nie istnieje: {file_path}")
        
        logger.info("Synchronizacja wersji zakończona!")
    
    def _update_file(self, file_path: str, patterns: List[Tuple[str, str]]):
        """Aktualizuje plik z podanymi wzorcami"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Zastosuj wszystkie wzorce
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # Zapisz tylko jeśli były zmiany
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Zaktualizowano: {file_path}")
            else:
                logger.debug(f"Brak zmian w: {file_path}")
                
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji {file_path}: {e}")
    
    def validate_versions(self) -> bool:
        """Sprawdza czy wszystkie pliki mają spójne wersje"""
        logger.info("Walidacja wersji we wszystkich plikach...")
        
        current_version = self.get_version_string()
        issues = []
        
        # Sprawdź kluczowe pliki
        files_to_check = [
            'config/version.yaml',
            'README.md',
            'Dockerfile',
            'docker-compose.yml'
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Sprawdź czy zawiera aktualną wersję
                if current_version not in content:
                    issues.append(f"{file_path} nie zawiera wersji {current_version}")
        
        if issues:
            logger.error("Znaleziono problemy z wersjami:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        else:
            logger.info("✅ Wszystkie wersje są spójne!")
            return True

def main():
    """Główna funkcja do uruchomienia z linii komend"""
    import sys
    
    if len(sys.argv) < 2:
        print("Użycie: python version_manager.py [sync|validate|increment-patch|increment-minor|increment-major|increment-build]")
        sys.exit(1)
    
    command = sys.argv[1]
    vm = VersionManager()
    
    if command == 'sync':
        vm.sync_all_files()
    elif command == 'validate':
        if vm.validate_versions():
            print("✅ Wszystkie wersje są spójne!")
            sys.exit(0)
        else:
            print("❌ Znaleziono problemy z wersjami!")
            sys.exit(1)
    elif command == 'increment-patch':
        vm.increment_patch()
        vm.sync_all_files()
    elif command == 'increment-minor':
        vm.increment_minor()
        vm.sync_all_files()
    elif command == 'increment-major':
        vm.increment_major()
        vm.sync_all_files()
    elif command == 'increment-build':
        vm.increment_build()
        vm.sync_all_files()
    else:
        print(f"Nieznana komenda: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
