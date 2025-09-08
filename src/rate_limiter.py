#!/usr/bin/env python3
"""
Moduł do rate limiting API
"""

import time
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Prosty rate limiter używający sliding window
    """
    
    def __init__(self):
        # Słownik przechowujący historię żądań dla każdego IP
        self.requests = defaultdict(lambda: deque())
        # Konfiguracja limitów
        self.limits = {
            'api_notes': {'requests': 100, 'window': 3600},  # 100 żądań na godzinę
            'api_flags': {'requests': 50, 'window': 3600},   # 50 żądań na godzinę
            'api_general': {'requests': 200, 'window': 3600} # 200 żądań na godzinę
        }
    
    def is_allowed(self, ip, endpoint_type='api_general'):
        """
        Sprawdza czy żądanie jest dozwolone
        """
        now = time.time()
        window = self.limits[endpoint_type]['window']
        max_requests = self.limits[endpoint_type]['requests']
        
        # Usuń stare żądania (poza oknem czasowym)
        requests = self.requests[ip]
        while requests and now - requests[0] > window:
            requests.popleft()
        
        # Sprawdź czy nie przekroczono limitu
        if len(requests) >= max_requests:
            logger.warning(f"Rate limit exceeded for IP {ip} on endpoint {endpoint_type}")
            return False
        
        # Dodaj nowe żądanie
        requests.append(now)
        return True
    
    def get_remaining_requests(self, ip, endpoint_type='api_general'):
        """
        Zwraca liczbę pozostałych żądań
        """
        now = time.time()
        window = self.limits[endpoint_type]['window']
        max_requests = self.limits[endpoint_type]['requests']
        
        # Usuń stare żądania
        requests = self.requests[ip]
        while requests and now - requests[0] > window:
            requests.popleft()
        
        return max(0, max_requests - len(requests))
    
    def get_reset_time(self, ip, endpoint_type='api_general'):
        """
        Zwraca czas do resetu limitu
        """
        requests = self.requests[ip]
        if not requests:
            return 0
        
        window = self.limits[endpoint_type]['window']
        oldest_request = requests[0]
        return int(oldest_request + window - time.time())

# Globalna instancja rate limitera
rate_limiter = RateLimiter()

def rate_limit(endpoint_type='api_general'):
    """
    Decorator do rate limiting
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Pobierz IP klienta
            ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if ip:
                ip = ip.split(',')[0].strip()
            else:
                ip = 'unknown'
            
            # Sprawdź rate limit
            if not rate_limiter.is_allowed(ip, endpoint_type):
                remaining = rate_limiter.get_remaining_requests(ip, endpoint_type)
                reset_time = rate_limiter.get_reset_time(ip, endpoint_type)
                
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'remaining_requests': remaining,
                    'reset_in_seconds': reset_time
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_rate_limit_info(ip, endpoint_type='api_general'):
    """
    Zwraca informacje o rate limicie dla danego IP
    """
    remaining = rate_limiter.get_remaining_requests(ip, endpoint_type)
    reset_time = rate_limiter.get_reset_time(ip, endpoint_type)
    
    return {
        'remaining_requests': remaining,
        'reset_in_seconds': reset_time,
        'limit': rate_limiter.limits[endpoint_type]['requests'],
        'window_seconds': rate_limiter.limits[endpoint_type]['window']
    }
