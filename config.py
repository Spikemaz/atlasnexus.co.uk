"""
AtlasNexus Configuration Module
================================
Centralized configuration for all application settings
"""

import os
from datetime import timedelta

# ====================
# Environment Settings
# ====================
ENV = os.environ.get('VERCEL_ENV', 'LOCAL')
IS_PRODUCTION = ENV == 'production'
IS_LOCAL = ENV == 'LOCAL'
DEBUG = not IS_PRODUCTION

# ====================
# Security Configuration
# ====================
# IMPORTANT: Change these in production!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-fixed-secret-key-keep-this-secure-in-production-2024')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'spikemaz8@aol.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'SpikeMaz')

# Gate1 Passwords
GATE1_PASSWORDS = ['SpikeMaz', 'RedAMC']

# Session Configuration
SESSION_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

# ====================
# Lockout Configuration
# ====================
MAX_SITE_AUTH_ATTEMPTS = 5
SITE_AUTH_LOCKOUT_MINUTES = 30
MAX_USER_AUTH_ATTEMPTS = 3
USER_AUTH_LOCKOUT_HOURS = 24

# Lockout durations
LOCKOUT_DURATIONS = {
    'timeout': 0.5,  # 30 minutes
    '30min': 0.5,
    '24h': 24,
    '7d': 168,
    '30d': 720,
    'permanent': 87600  # 10 years
}

# ====================
# Rate Limiting
# ====================
REGISTRATION_RATE_LIMIT_HOURS = 24
VERIFICATION_EMAIL_COOLDOWN_MINUTES = 10
VERIFICATION_TOKEN_EXPIRY_HOURS = 1

# ====================
# Password Configuration  
# ====================
PASSWORD_EXPIRY_DAYS = 30
PASSWORD_MIN_LENGTH = 8

# ====================
# File Storage
# ====================
DATA_DIR = 'data'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ====================
# Email Configuration (loaded from email_config.py if available)
# ====================
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'atlasnexushelp@gmail.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '')

# ====================
# Application URLs
# ====================
def get_base_url():
    """Get the base URL for the application"""
    if IS_PRODUCTION:
        return 'https://atlasnexus.co.uk/'
    elif 'VERCEL_URL' in os.environ:
        return f"https://{os.environ['VERCEL_URL']}/"
    else:
        return 'http://localhost:5000/'

BASE_URL = get_base_url()

# ====================
# Database Files
# ====================
DB_FILES = {
    'users': os.path.join(DATA_DIR, 'users.json'),
    'registrations': os.path.join(DATA_DIR, 'registrations.json'),
    'lockouts': os.path.join(DATA_DIR, 'ip_lockouts.json'),
    'attempts': os.path.join(DATA_DIR, 'ip_attempts_log.json'),
    'login_attempts': os.path.join(DATA_DIR, 'login_attempts.json'),
    'admin_actions': os.path.join(DATA_DIR, 'admin_actions.json'),
    'ip_tracking': os.path.join(DATA_DIR, 'ip_tracking.json'),
    'projects': os.path.join(DATA_DIR, 'projects.json')
}

# ====================
# Allowed Files
# ====================
ALLOWED_ROOT_FILES = {
    'app.py',
    'config.py',
    'email_config.py',
    'requirements.txt',
    'vercel.json',
    'runtime.txt',
    'Procfile',
    'README.md',
    '.gitignore',
    'securitization_engine.py',
    'market_news_service.py',
    'real_news_service.py'
}

ALLOWED_TEMPLATES = {
    'Gate1.html',
    'Gate2.html',
    'dashboard.html',
    '404.html',
    'terms.html',
    'privacy.html',
    'compliance.html',
    'data-protection.html',
    'security.html',
    'contact.html',
    'market_news.html',
    'market_news_content.html',
    'awaiting_verification.html',
    'registration-submitted.html',
    'admin_panel.html',
    'admin_approve_config.html',
    'securitisation_engine.html',
    'permutation_engine.html',
    'project_specifications_enhanced.html'
}

ALLOWED_STATIC_FILES = {
    'style.css',
    'script.js',
    'logo.png',
    'favicon.ico',
    'background.jpg',
    'atlas-nexus-logo.png',
    'smooth-scroll.js'
}

# ====================
# Market Data Configuration
# ====================
FRED_API_KEY = 'c1b8ad8c1fb7b3c30f7c9d96c2e17390'
FRED_BASE_URL = 'https://api.stlouisfed.org/fred/series/observations'

# ====================
# Feature Flags
# ====================
FEATURES = {
    'securitization': True,
    'market_news': True,
    'real_news': True,
    'companies_house': True,
    'email_verification': True,
    'two_factor_auth': False,  # Future feature
    'ip_whitelisting': False,   # Future feature
}

# ====================
# Logging Configuration
# ====================
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
LOG_FILE = 'app.log' if IS_LOCAL else None

# ====================
# API Keys and External Services
# ====================
COMPANIES_HOUSE_API_KEY = os.environ.get('COMPANIES_HOUSE_API_KEY', '')
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY', '')

# ====================
# Admin Dashboard Settings
# ====================
ADMIN_PANEL_FEATURES = {
    'user_management': True,
    'ip_management': True,
    'system_stats': True,
    'audit_logs': True,
    'data_export': True,
    'quick_actions': True
}

# ====================
# Registration Settings
# ====================
REGISTRATION_FIELDS_REQUIRED = [
    'email',
    'full_name',
    'phone',
    'country_code',
    'company_name',
    'company_number',
    'job_title',
    'business_address'
]

# ====================
# Security Headers
# ====================
SECURITY_HEADERS = {
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains' if IS_PRODUCTION else None
}