# Phase-1 Production Canary Go/No-Go Checklist

**Date:** ___________  **Time:** ___________  **Operator:** ___________

## ✅ PREFLIGHT (Complete before deploy)

### Environment & Secrets
- [ ] `SECRET_KEY` rotated today (64+ chars)
- [ ] `FLASK_ENV=production`
- [ ] `APP_ENV=prod`
- [ ] `REDIS_URL` with TLS enabled
- [ ] `MONGODB_URI` with least-privilege user
- [ ] `RULESET_VERSION=v1.0`
- [ ] `ADMIN_ALLOWLIST` configured
- [ ] `MFA_REQUIRED=true`

### Security Configuration
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `SESSION_COOKIE_SAMESITE=Lax`
- [ ] Session timeout = 15 minutes
- [ ] CSRF protection on all POST/PUT/DELETE
- [ ] Admin auth = server-side roles + MFA

### Runtime
- [ ] Gunicorn/uWSGI configured (NOT Werkzeug)
- [ ] Workers: ___ Threads: ___ (based on CPU)
- [ ] TLS enforced end-to-end
- [ ] Security headers configured (HSTS, X-Frame-Options)

---

## 🔍 LIVE DOMAIN VALIDATION (Post-deploy)

### 1. Production Headers ✅ = GO | ❌ = NO-GO

```bash
curl -i https://atlasnexus.co.uk/__healthz
```
- [ ] Returns 200 OK
- [ ] `{"status": "ok", "env": "prod"}`
- [ ] Header: `X-Commit-SHA: ___________`
- [ ] Header: `X-Ruleset-Version: v1.0`
- [ ] Header: `X-Env: prod`
- [ ] Header: `X-Build-ID: ___________`

```bash
curl -i https://atlasnexus.co.uk/__version
```
- [ ] Commit matches deployment: ___________
- [ ] Build ID matches: ___________
- [ ] Ruleset version: v1.0

### 2. Runtime Verification ✅ = GO | ❌ = NO-GO

Process check:
- [ ] Server type: _____________ (must NOT be Werkzeug)
- [ ] Workers: _____ Threads: _____
- [ ] Uptime: ___________
- [ ] Memory baseline: _____ MB

Environment:
- [ ] `FLASK_ENV=production` confirmed
- [ ] `SECRET_KEY` set (do NOT print value)
- [ ] Session cookies marked Secure/HttpOnly

### 3. Feature Flags API ✅ = GO | ❌ = NO-GO

```bash
GET /api/admin/flags
```
- [ ] Returns current version: ___________
- [ ] All Phase-1 flags visible
- [ ] Audit log accessible

Enable flags (admin-only):
- [ ] `deterministic_seed`: OFF → ON
- [ ] `perm_chunking`: OFF → ON
- [ ] `phase1_core`: OFF → ON
- [ ] Version incremented to: ___________
- [ ] Audit log shows: who/when/changes

Keep OFF:
- [ ] `reverse_dscr_engine`: OFF
- [ ] `gates_ab`: OFF
- [ ] `docs_exports`: OFF

### 4. Phase-1 Endpoints ✅ = GO | ❌ = NO-GO

```bash
POST /api/phase1/projects/validate
```
- [ ] Returns 200 with A-rated 15y project
- [ ] Validation passes
- [ ] Derived fields calculated

```bash
GET /api/phase1/permutations/presets
```
- [ ] AAA/AA bundle present
- [ ] A-rated bundle present
- [ ] BBB bundle present

```bash
POST /api/phase1/permutations/cardinality
```
- [ ] Expected count: ___________
- [ ] After tenor clipping: ___________
- [ ] After AF pre-prune: ___________
- [ ] Warning if >250k: [ ] Yes [ ] No

---

## 🚀 1% CANARY EXECUTION (Admin-only)

**Start Time:** ___________

### Golden Fixtures Run

**Configuration:**
- Seed: 424242
- Ruleset: v1.0
- Chunk size: 800

#### Small Fixture ✅ = GO | ❌ = NO-GO
- [ ] Diamond count: _____ (expect 2-3)
- [ ] Gold count: _____ (expect 2-3)
- [ ] Gate A pruned: _____% (expect ~32%)
- [ ] Gate B pruned: _____% (expect ~21%)
- [ ] Throughput: _____ perms/sec (target >250)
- [ ] P95: _____ ms (target <10ms)
- [ ] Memory peak: _____ MB (target <250MB)

#### Medium Fixture ✅ = GO | ❌ = NO-GO
- [ ] Diamond count: _____ (expect 3-5)
- [ ] Gold count: _____ (expect 5-7)
- [ ] Gate A pruned: _____% (expect ~37%)
- [ ] Gate B pruned: _____% (expect ~26%)
- [ ] Throughput: _____ perms/sec (target >300)
- [ ] P95: _____ ms (target <8ms)
- [ ] Memory peak: _____ MB (target <350MB)

#### Large Fixture ✅ = GO | ❌ = NO-GO
- [ ] Diamond count: _____ (expect 5-8)
- [ ] Gold count: _____ (expect 8-12)
- [ ] Gate A pruned: _____% (expect ~36%)
- [ ] Gate B pruned: _____% (expect ~25%)
- [ ] Throughput: _____ perms/sec (target >280)
- [ ] P95: _____ ms (target <10ms)
- [ ] Memory peak: _____ MB (target <500MB)

### Stress Testing ✅ = GO | ❌ = NO-GO

CPI Scenarios (Senior DSCR):
- [ ] 0% CPI: _____ (must be ≥1.00)
- [ ] 1.8% CPI: _____ (expect ~1.20)
- [ ] 2.5% CPI: _____ (expect ~1.25)

### 30-Minute Monitoring ✅ = GO | ❌ = NO-GO

**Check every 5 minutes:**

| Time | Error Rate | P95 (ms) | Memory (MB) | Status |
|------|------------|----------|-------------|--------|
| +5m  | _______%   | ______   | _______     | [ ] GO |
| +10m | _______%   | ______   | _______     | [ ] GO |
| +15m | _______%   | ______   | _______     | [ ] GO |
| +20m | _______%   | ______   | _______     | [ ] GO |
| +25m | _______%   | ______   | _______     | [ ] GO |
| +30m | _______%   | ______   | _______     | [ ] GO |

**Success Criteria:**
- [ ] Error rate <1% sustained
- [ ] P95 <2000ms (2s) sustained
- [ ] Memory stable (no leak)
- [ ] No repo conflicts
- [ ] No uncaught exceptions

---

## 🔄 ROLLBACK DRILL ✅ = GO | ❌ = NO-GO

Execute rollback:
```bash
POST /api/admin/flags/rollback
```

Verify:
- [ ] All Phase-1 flags → OFF
- [ ] TTR: _________ seconds (target <2s)
- [ ] Audit log shows EMERGENCY_ROLLBACK
- [ ] Version incremented
- [ ] No errors during rollback

Final flag states:
- [ ] `deterministic_seed`: OFF
- [ ] `perm_chunking`: OFF
- [ ] `phase1_core`: OFF
- [ ] `reverse_dscr_engine`: OFF
- [ ] `gates_ab`: OFF
- [ ] `docs_exports`: OFF

---

## 📊 FINAL DECISION

### Go/No-Go Summary

| Section | Result | Notes |
|---------|--------|-------|
| Preflight | [ ] GO [ ] NO-GO | |
| Live Domain Validation | [ ] GO [ ] NO-GO | |
| Feature Flags API | [ ] GO [ ] NO-GO | |
| Phase-1 Endpoints | [ ] GO [ ] NO-GO | |
| Golden Fixtures | [ ] GO [ ] NO-GO | |
| 30-Min Monitoring | [ ] GO [ ] NO-GO | |
| Rollback Drill | [ ] GO [ ] NO-GO | |

### **FINAL DECISION: [ ] GO TO 25% [ ] NO-GO (ROLLBACK)**

**Decision Time:** ___________

**Decision Maker:** ___________

**Notes/Issues:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## 📞 ESCALATION

If NO-GO:
1. Execute rollback immediately
2. Document symptoms: ___________
3. Hypothesis: ___________
4. Next steps: ___________
5. Notify: Team Lead, DevOps, Product Owner

If GO:
1. Document success metrics
2. Prepare 25% canary plan
3. Schedule monitoring window
4. Update stakeholders

---

**Sign-off:**

Technical Lead: _______________ Date: ___________

Product Owner: _______________ Date: ___________

DevOps Lead: _______________ Date: ___________