# Phase-1 Production Deployment Guide

## Critical Issues Fixed

### 1. ✅ Production Server (Not Dev)
- **WSGI Entry Point**: `wsgi.py` configured for gunicorn
- **Command**: `gunicorn "wsgi:app" --workers 4 --threads 8 --timeout 120`
- **No Werkzeug dev server in production**

### 2. ✅ Security Hardening
- **Secret Key**: Moved to environment variable `SECRET_KEY`
- **Session Security**:
  - `SESSION_COOKIE_SECURE=True` (HTTPS only)
  - `SESSION_COOKIE_HTTPONLY=True` (no JS access)
  - `SESSION_COOKIE_SAMESITE=Lax` (CSRF protection)
- **Headers**: X-Content-Type-Options, X-Frame-Options, HSTS

### 3. ✅ Feature Flags API (Not File Edits)
- **Redis Backend**: Atomic operations with versioning
- **API Endpoints**:
  - `GET /api/admin/flags` - Current state + version
  - `POST /api/admin/flags/update` - Atomic updates
  - `POST /api/admin/flags/rollback` - Emergency rollback
  - `GET /api/admin/flags/history` - Change history
  - `GET /api/admin/flags/audit` - Audit log
- **Optimistic Locking**: Version checking prevents conflicts
- **Full Audit Trail**: Who, what, when, old→new

### 4. ✅ Admin Authentication
- **MFA Required**: `admin_with_mfa_required` decorator
- **Session Timeout**: 15 minutes of inactivity
- **Server-Side Roles**: Not just session boolean
- **Audit Logging**: Every admin action logged

### 5. ✅ Production Headers
- **Every Response Includes**:
  - `X-Commit-SHA: f42638c`
  - `X-Ruleset-Version: v1.0`
  - `X-Env: prod`
  - `X-Build-ID: phase1_20250924_154500`

### 6. ✅ Rate Limiting
- **Per-IP and Per-User Bucketing**
- **Limits**:
  - Auth: 5/minute
  - API: 50/minute
  - Permutations: 20/minute
- **Redis-backed with automatic expiry**

## Deployment Steps

### 1. Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export MONGODB_URI=mongodb+srv://...
export REDIS_URL=redis://...
export COMMIT_SHA=f42638c
export BUILD_ID=phase1_20250924_154500
```

### 2. Install Dependencies
```bash
pip install -r requirements_prod.txt
```

### 3. Run with Gunicorn
```bash
gunicorn "wsgi:app" \
  --workers 4 \
  --threads 8 \
  --timeout 120 \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

### 4. Verify Production Headers
```bash
curl -I https://atlasnexus.co.uk/__healthz

# Expected headers:
# X-Commit-SHA: f42638c
# X-Ruleset-Version: v1.0
# X-Env: prod
# X-Build-ID: phase1_20250924_154500
```

### 5. Admin Banner Verification
The admin panel at `https://atlasnexus.co.uk/admin` displays:
```
ATLAS v1 • Phase-1 BUILD • Commit: f42638c • Date: 2025-09-24 UTC • Admin-Only Mode
```

## Feature Flags Management

### Enable Flags (Admin with MFA)
```bash
curl -X POST https://atlasnexus.co.uk/api/admin/flags/update \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "updates": {
      "deterministic_seed": true,
      "perm_chunking": true,
      "phase1_core": true
    }
  }'
```

### Emergency Rollback
```bash
curl -X POST https://atlasnexus.co.uk/api/admin/flags/rollback \
  -H "Cookie: session=..."
```

## Monitoring

### Health Check
```bash
curl https://atlasnexus.co.uk/__healthz
# {"status": "ok", "env": "prod", "time": "..."}

curl https://atlasnexus.co.uk/__version
# {"commit": "f42638c", "build_id": "...", "ruleset_version": "v1.0"}
```

### Phase-1 Dashboard
```bash
curl https://atlasnexus.co.uk/api/phase1/dashboard \
  -H "Cookie: session=..."
```

## Canary Rollout

### 1% Allowlist (Admin-Only)
- Test accounts only
- Monitor for 30 minutes
- Success criteria: Error <1%, P95 <2s

### 25% Allowlist
- Selected beta users
- Monitor for 24 hours
- Auto-rollback on threshold breach

### 100% Admin Rollout
- All admin accounts
- Public remains at 0%
- Full monitoring before public release

## Emergency Procedures

### Auto-Rollback Triggers
- Error rate >1% for 10 minutes
- P95 response time >2 seconds for 10 minutes
- Memory usage >1GB sustained
- Any uncaught exception in Phase-1 code

### Manual Rollback
1. Execute: `POST /api/admin/flags/rollback`
2. Verify all flags disabled
3. Post incident report:
   - Symptoms
   - Cause hypothesis
   - Next steps

## Security Checklist

- [x] No hardcoded secrets
- [x] HTTPS enforced
- [x] MFA for admin accounts
- [x] Session timeout (15 min)
- [x] Rate limiting active
- [x] Audit logging enabled
- [x] PII redacted in logs
- [x] ASCII-only logging
- [x] Security headers set

## Production Verification

Before going live, confirm:

1. **Not localhost**: All tests against `https://atlasnexus.co.uk`
2. **Production server**: Gunicorn, not Werkzeug
3. **Headers present**: X-Commit-SHA, X-Ruleset-Version, X-Env
4. **Flags API working**: Version increments, audit logs
5. **Admin MFA active**: Cannot access without verification
6. **Rate limits enforced**: Test with burst requests
7. **Rollback tested**: TTR <2 seconds

## Support

- Logs: Check CloudWatch/server logs
- Metrics: Phase-1 dashboard
- Alerts: Set up for error rate, P95, memory
- Incident: Follow rollback procedures