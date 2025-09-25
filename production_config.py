"""
Production configuration for Phase-1 deployment
Set these environment variables before starting the application
"""

import os

# Core environment settings
os.environ['APP_ENV'] = 'prod'
os.environ['RULESET_VERSION'] = 'v1.0'
os.environ['PHASE1_MAX_CARD'] = '250000'

# Redis for session persistence
os.environ['REDIS_URL'] = 'redis://localhost:6379/2'
os.environ['SESSION_COOKIE_DOMAIN'] = '.atlasnexus.co.uk'

# Build metadata
os.environ['COMMIT_SHA'] = '1489855'  # Latest commit SHA
os.environ['BUILD_ID'] = 'phase1_20250124_2230'

# Admin token (for ops endpoints only in prod)
os.environ['PHASE1_ADMIN_TOKEN'] = 'phase1-admin-secure-token'

# Feature flags
os.environ['PHASE1_CORE_ENABLED'] = 'true'

print("[CONFIG] Production environment variables set:")
for key in ['APP_ENV', 'RULESET_VERSION', 'COMMIT_SHA', 'BUILD_ID']:
    print(f"  {key}={os.environ.get(key)}")