# Copy-paste message for Claude (fix & prove)

**Subject:** Phase-1 v2 — Align flags, register endpoints, run QA & paste proofs

**Claude — actions on live prod (admin-only):**

## 1. **Standardise feature flags:**

* Ensure Flags API keys are **snake_case**: `deterministic_seed`, `perm_chunking`, `phase1_core`, `reverse_dscr_engine`, `gates_ab`, `docs_exports`.
* Update any scripts/docs still using `DeterministicSeed`/`PermChunking` etc.
* Paste **before/after** flag JSON + **audit entries** (version increments).

```bash
# Before
curl https://atlasnexus.co.uk/api/phase1/flags

# Update to snake_case
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/flags \
  -d '{
    "deterministic_seed": true,
    "perm_chunking": true,
    "phase1_core": true,
    "reverse_dscr_engine": false,
    "gates_ab": false,
    "docs_exports": false
  }'

# After (verify version increment)
curl https://atlasnexus.co.uk/api/phase1/flags
```

## 2. **Blueprint & security check:**

* Confirm **all** Phase-1 routes (QA, canary, metrics, flags) are under the **same** `/api/phase1` blueprint and protected by **admin_required + MFA**.
* Paste the **route list** and a **403 proof** when hitting without admin.

```bash
# List all Phase-1 routes
curl https://atlasnexus.co.uk/api/phase1/routes

# Test 403 without admin token
curl https://atlasnexus.co.uk/api/phase1/runtime
# Expected: 403 Forbidden

# Test with admin token
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/runtime
# Expected: 200 OK with headers
```

## 3. **Runtime proof (prod):**

* Show gunicorn process (`ps aux | grep gunicorn`) and curl the runtime endpoint with headers.

```bash
# On server
ps aux | grep gunicorn | grep -v grep

# Runtime check with headers
curl -I -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/runtime
```

## 4. **Golden fixture test (seed 424242):**

```bash
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/permutation \
  -d '{
    "seed": 424242,
    "ruleset_version": "v1.0",
    "project_data": {
      "jurisdiction": "UK",
      "asset_value": 50000000,
      "lease_years": 25,
      "indexation": "CPI",
      "tenant_covenant": "AA"
    }
  }'
```

## 5. **Run QA suite on top structure:**

```bash
# Get winning structure ID from previous response
STRUCTURE_ID="[from_golden_fixture_response]"

# Run QA validation
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/qa/validate \
  -d "{\"structure_id\": \"$STRUCTURE_ID\"}"
```

## 6. **Check metrics & go/no-go:**

```bash
# Current metrics
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/metrics/current

# Full system status with go/no-go evaluation
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/status/full
```

## 7. **Canary control (if GO):**

```bash
# Check current canary status
curl https://atlasnexus.co.uk/api/phase1/canary/status

# If all GREEN, widen to 25%
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/canary/update \
  -d '{
    "percentage": 25,
    "reason": "QA passed, all metrics GREEN"
  }'
```

---

## Expected Proof Format:

```
PHASE-1 v2 DEPLOYMENT PROOF
===========================

1. FLAGS STANDARDIZED:
   Before: {"DeterministicSeed": false, ...} (v1)
   After: {"deterministic_seed": true, ...} (v2)
   Audit: admin@2025-09-24T17:30:00Z

2. BLUEPRINT SECURITY:
   Routes: /api/phase1/[health, runtime, flags, qa/validate, metrics/current, canary/*, rollback]
   All protected: ✓ (@admin_required + MFA)
   403 proof: {"error": "Unauthorized", "message": "Valid admin token required"}

3. RUNTIME:
   Process: gunicorn 20.1.0 --workers 4 --bind 0.0.0.0:8000 wsgi:app
   Headers:
   - X-Commit-SHA: abc1234
   - X-Ruleset-Version: v1.0
   - X-Env: prod
   - X-Build-ID: build-789
   - X-Gunicorn-Workers: 4

4. GOLDEN FIXTURE (424242):
   Top: ID-001, DSCR 1.25, WAL 12.5y, Tenor 15y
   Prune: 100k→15k→8k→5k
   Performance: P50=850ms, P95=1200ms
   Hashes: range=a7c3f9e2b4d6, ruleset=9f3a2b7e8c1d

5. QA SUITE: ALL PASS ✓
   - Reverse-DSCR: 1.250 vs 1.251 (Δ=0.001) ✓
   - WAL: 12.5y vs 12.4y (Δ=0.1y) ✓
   - Tenor: 15y ≤ 23y ✓
   - Repo: PASS (UK/SPV/GBP/LMA/T+2) ✓
   - Indexation: Core flat, excess in sidecar ✓
   - Sidecar: £800k = £1M × 0.8 ✓
   - Near-misses: 4 hints found ✓

6. GO/NO-GO: **GO**
   - Error rate: 0.2% < 1% ✓
   - P95: 1.2s < 2s ✓
   - Memory: stable ✓
   - QA: PASS ✓
   - Rollback TTR: 1.5s < 2s ✓
   - Logs: Complete ✓

7. ACTION: Canary widened 1% → 25%
   Timestamp: 2025-09-24T17:45:00Z
   Operator: admin
```

---

**Critical Reminders:**
- All flag keys must be **snake_case**
- All endpoints under **/api/phase1** blueprint
- Must show **gunicorn** process (not Werkzeug)
- QA tolerances: DSCR ±0.001, WAL ±0.1y, Value ±£1
- Canary progression: 0% → 1% → 25% → 100%
- Any RED = immediate rollback to 0%

---

END OF FIX & PROVE MESSAGE