#!/usr/bin/env python3
"""
Moduł do zarządzania cache
"""

import time
import json
import hashlib
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Prosty cache manager używający pamięci
    """
    
    def __init__(self, default_ttl=300):  # 5 minut domyślnie
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key):
        """
        Pobiera wartość z cache
        """
        if key in self.cache:
            value, timestamp, ttl = self.cache[key]
            if time.time() - timestamp < ttl:
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                # Usuń wygasły wpis
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key, value, ttl=None):
        """
        Ustawia wartość w cache
        """
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = (value, time.time(), ttl)
        logger.debug(f"Cache set for key: {key}, ttl: {ttl}")
    
    def delete(self, key):
        """
        Usuwa wartość z cache
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self):
        """
        Czyści cały cache
        """
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self):
        """
        Usuwa wygasłe wpisy z cache
        """
        now = time.time()
        expired_keys = []
        
        for key, (value, timestamp, ttl) in self.cache.items():
            if now - timestamp >= ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self):
        """
        Zwraca statystyki cache
        """
        now = time.time()
        active_entries = 0
        expired_entries = 0
        
        for key, (value, timestamp, ttl) in self.cache.items():
            if now - timestamp < ttl:
                active_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self.cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'memory_usage': len(str(self.cache))
        }

# Globalna instancja cache managera
cache_manager = CacheManager()

def cached(ttl=300, key_prefix=''):
    """
    Decorator do cache'owania funkcji
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generuj klucz cache na podstawie argumentów
            cache_key = f"{key_prefix}:{f.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Sprawdź cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Wykonaj funkcję i zapisz wynik
            result = f(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern):
    """
    Usuwa wpisy z cache pasujące do wzorca
    """
    keys_to_delete = []
    for key in cache_manager.cache.keys():
        if pattern in key:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache_manager.delete(key)
    
    logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")

def get_cache_info():
    """
    Zwraca informacje o cache
    """
    return cache_manager.get_stats()
