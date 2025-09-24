"""
WSGI entry point for production deployment
Use with gunicorn: gunicorn "wsgi:app" --workers 4 --threads 8 --timeout 120
"""

import os
import sys
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('SECRET_KEY', os.urandom(32).hex())

from app import app
from production_config import ProductionConfig
from middleware import add_production_headers

# Apply production configuration
app.config.from_object(ProductionConfig)

# Add production middleware
@app.before_request
def before_request():
    """Pre-request security checks"""
    # Enforce HTTPS in production
    if not app.debug and not request.is_secure:
        return 'HTTPS required', 403

@app.after_request
def after_request(response):
    """Add security and tracking headers"""
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Tracking headers
    response.headers['X-Commit-SHA'] = app.config.get('PHASE1_COMMIT_SHA', 'unknown')
    response.headers['X-Ruleset-Version'] = app.config.get('PHASE1_RULESET_VERSION', 'v1.0')
    response.headers['X-Env'] = 'prod'
    response.headers['X-Build-ID'] = app.config.get('PHASE1_BUILD_ID', 'unknown')

    return response

if __name__ == '__main__':
    # Should not run directly in production
    print("Use gunicorn to run in production: gunicorn 'wsgi:app' --workers 4")
    sys.exit(1)