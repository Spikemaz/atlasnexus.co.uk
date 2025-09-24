"""
AtlasNexus Security Hardening Module
===================================
Enhanced security features for production deployment
"""

import time
import json
import os
import hashlib
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional, List
from flask import request, jsonify, g
import ipaddress

class RateLimiter:
    """
    Advanced rate limiting with:
    - Per-IP rate limiting
    - Per-endpoint rate limiting
    - Sliding window algorithm
    - DDoS protection
    """

    def __init__(self, default_limit: int = 100, window_seconds: int = 60):
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(lambda: deque())
        self.blocked_ips = {}
        self.lock = threading.RLock()

        # Enhanced limits for different endpoints
        self.endpoint_limits = {
            '/api/': 50,          # API endpoints
            '/login': 5,          # Login attempts
            '/register': 3,       # Registration attempts
            '/api/permutation/': 20,  # Permutation engine
            '/upload': 10,        # File uploads
        }

        # Load blocked IPs from storage
        self.load_blocked_ips()

    def load_blocked_ips(self):
        """Load blocked IPs from persistent storage"""
        try:
            blocked_file = '/tmp/blocked_ips.json' if os.environ.get('VERCEL') else 'blocked_ips.json'
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    data = json.load(f)
                    self.blocked_ips = {ip: datetime.fromisoformat(timestamp) for ip, timestamp in data.items()}
        except Exception as e:
            print(f"[SECURITY] Error loading blocked IPs: {e}")

    def save_blocked_ips(self):
        """Save blocked IPs to persistent storage"""
        try:
            blocked_file = '/tmp/blocked_ips.json' if os.environ.get('VERCEL') else 'blocked_ips.json'
            data = {ip: timestamp.isoformat() for ip, timestamp in self.blocked_ips.items()}
            with open(blocked_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[SECURITY] Error saving blocked IPs: {e}")

    def is_blocked(self, ip: str) -> bool:
        """Check if an IP is currently blocked"""
        with self.lock:
            if ip in self.blocked_ips:
                # Check if block has expired (24 hour blocks)
                if datetime.utcnow() - self.blocked_ips[ip] > timedelta(hours=24):
                    del self.blocked_ips[ip]
                    self.save_blocked_ips()
                    return False
                return True
            return False

    def block_ip(self, ip: str, duration_hours: int = 24):
        """Block an IP address"""
        with self.lock:
            self.blocked_ips[ip] = datetime.utcnow()
            self.save_blocked_ips()
            print(f"[SECURITY] Blocked IP {ip} for {duration_hours} hours due to rate limiting")

    def check_rate_limit(self, ip: str, endpoint: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request should be rate limited

        Returns:
            Tuple[bool, dict]: (is_allowed, rate_limit_info)
        """
        with self.lock:
            current_time = time.time()
            key = f"{ip}:{endpoint}"

            # Check if IP is blocked
            if self.is_blocked(ip):
                return False, {
                    'error': 'IP_BLOCKED',
                    'message': 'Your IP has been temporarily blocked due to excessive requests',
                    'retry_after': 3600  # 1 hour
                }

            # Determine rate limit for endpoint
            limit = self.default_limit
            for pattern, pattern_limit in self.endpoint_limits.items():
                if pattern in endpoint:
                    limit = pattern_limit
                    break

            # Clean old requests outside the window
            request_times = self.requests[key]
            while request_times and current_time - request_times[0] > self.window_seconds:
                request_times.popleft()

            # Check if we're over the limit
            if len(request_times) >= limit:
                # Potential DDoS - block IP if excessive requests
                if len(request_times) > limit * 3:
                    self.block_ip(ip)
                    return False, {
                        'error': 'IP_BLOCKED',
                        'message': 'IP blocked due to excessive requests',
                        'retry_after': 3600
                    }

                return False, {
                    'error': 'RATE_LIMITED',
                    'message': f'Rate limit exceeded. Max {limit} requests per {self.window_seconds} seconds.',
                    'retry_after': self.window_seconds,
                    'remaining': 0
                }

            # Record this request
            request_times.append(current_time)

            return True, {
                'remaining': limit - len(request_times),
                'reset_time': current_time + self.window_seconds
            }

class InputValidator:
    """
    Enhanced input validation and sanitization
    """

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format with additional security checks"""
        if not email or len(email) > 254:
            return False

        import re
        # RFC 5322 compliant regex (simplified)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False

        # Additional security checks
        suspicious_patterns = [
            r'[<>"\';]',  # Script injection attempts
            r'javascript:',  # JavaScript injection
            r'vbscript:',   # VBScript injection
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not input_str:
            return ""

        # Truncate to max length
        sanitized = str(input_str)[:max_length]

        # Remove or escape dangerous characters
        import html
        sanitized = html.escape(sanitized, quote=True)

        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')

        return sanitized.strip()

    @staticmethod
    def validate_project_data(data: dict) -> Tuple[bool, List[str]]:
        """Validate project data structure"""
        errors = []
        required_fields = ['project_name', 'user_email']

        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not data[field] or not str(data[field]).strip():
                errors.append(f"Empty required field: {field}")

        # Validate specific field formats
        if 'user_email' in data and data['user_email']:
            if not InputValidator.validate_email(data['user_email']):
                errors.append("Invalid email format")

        # Check for suspicious content
        suspicious_keywords = ['<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=']
        for key, value in data.items():
            if isinstance(value, str):
                for keyword in suspicious_keywords:
                    if keyword.lower() in value.lower():
                        errors.append(f"Suspicious content detected in field: {key}")

        return len(errors) == 0, errors

class CORSSecurityManager:
    """
    Enhanced CORS security configuration
    """

    def __init__(self):
        self.allowed_origins = [
            'https://atlasnexus.co.uk',
            'https://www.atlasnexus.co.uk'
        ]

        # Development origins (only in non-production)
        if not os.environ.get('VERCEL_ENV') == 'production':
            self.allowed_origins.extend([
                'http://localhost:5000',
                'http://127.0.0.1:5000'
            ])

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed for CORS requests"""
        if not origin:
            return False

        return origin in self.allowed_origins

    def get_cors_headers(self, origin: str = None) -> Dict[str, str]:
        """Get appropriate CORS headers"""
        headers = {
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Max-Age': '3600'
        }

        if origin and self.is_origin_allowed(origin):
            headers['Access-Control-Allow-Origin'] = origin
            headers['Access-Control-Allow-Credentials'] = 'true'
        else:
            headers['Access-Control-Allow-Origin'] = 'null'

        return headers

class SecurityLogger:
    """
    Enhanced security event logging
    """

    def __init__(self):
        self.log_file = '/tmp/security.log' if os.environ.get('VERCEL') else 'security.log'

    def log_security_event(self, event_type: str, ip: str, details: dict = None):
        """Log security events"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'ip': ip,
            'user_agent': request.headers.get('User-Agent', ''),
            'details': details or {}
        }

        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            print(f"[SECURITY] Error logging event: {e}")

        # Also log to console in development
        if not os.environ.get('VERCEL_ENV') == 'production':
            print(f"[SECURITY] {event_type}: {ip} - {details}")

# Global instances
rate_limiter = RateLimiter()
input_validator = InputValidator()
cors_manager = CORSSecurityManager()
security_logger = SecurityLogger()

def apply_rate_limiting(endpoint: str = None):
    """Decorator to apply rate limiting to routes"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            endpoint_path = endpoint or request.endpoint or request.path

            allowed, rate_info = rate_limiter.check_rate_limit(ip, endpoint_path)

            if not allowed:
                security_logger.log_security_event('RATE_LIMITED', ip, rate_info)
                return jsonify(rate_info), 429

            # Add rate limit headers
            response = f(*args, **kwargs)
            if hasattr(response, 'headers') and 'remaining' in rate_info:
                response.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(int(rate_info.get('reset_time', 0)))

            return response
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator