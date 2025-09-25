# Quick Kickoff Message for Claude (copy/paste)

**Subject:** Phase-1 v2 — Confirm pins, unify flags, run QA, paste proofs

**Claude — live prod, admin-only:**

1. **Acknowledge** you've read `CLAUDE_MEMORY_PINS.md` and are applying `#headers`, `#mfa_admin`, and `#flags_api_contract`.

2. **Runtime proof:** show gunicorn (`ps aux | grep gunicorn`) and curl a Phase-1 endpoint with headers `X-Commit-SHA / X-Ruleset-Version / X-Env=prod / X-Build-ID`.

3. **Blueprint & security:** paste route list showing all Phase-1 routes under `/api/phase1` and a **403** example when hitting without admin/MFA.

4. **Flags:** ensure **snake_case** keys only (`deterministic_seed`, `perm_chunking`, `phase1_core`, `reverse_dscr_engine`, `gates_ab`, `docs_exports`). POST changes with `version` and paste **before/after + audit**.

5. **Golden fixture** (seed `424242`, ruleset `v1.0`) then run the **QA micro-suite** and paste the 7 check results within tolerances (DSCR ±0.001, WAL ±0.1y, sidecar ±1 unit, etc.).

6. **Canary @1%** for 30 minutes, paste the grid (error <1%, P95 <2s, memory stable, repo PASS, rollback TTR <2s). If ALL GREEN, request approval to widen to 25%; if any RED, execute rollback and post the 3-line incident note.

*No file edits in prod; use the Flags API only. Paste proofs inline.*

---

## Expected Response Format:

```
PHASE-1 v2 DEPLOYMENT CONFIRMATION
===================================

1. MEMORY PINS ACKNOWLEDGED:
   ✓ #headers applied to all responses
   ✓ #mfa_admin enforced (15-min window)
   ✓ #flags_api_contract (snake_case, versioned)

2. RUNTIME PROOF:
   Process: root 1234 gunicorn 20.1.0 --workers 4 --bind 0.0.0.0:8000 wsgi:app
   Headers:
   - X-Commit-SHA: abc1234
   - X-Ruleset-Version: v1.0
   - X-Env: prod
   - X-Build-ID: build-789

3. BLUEPRINT & SECURITY:
   Routes: /api/phase1/[health, runtime, flags, qa/validate, metrics/current, canary/*, rollback]
   403 without admin: {"error": "Unauthorized", "message": "Valid admin token required"}
   403 without MFA: {"error": "MFA required"}

4. FLAGS UNIFIED:
   Before (v1): {"DeterministicSeed": false, "PermChunking": false, ...}
   After (v2): {"deterministic_seed": true, "perm_chunking": true, ...}
   Audit: admin@2025-09-24T18:00:00Z, request_id: req_abc123

5. GOLDEN FIXTURE + QA:
   Seed 424242 result: ID-001, DSCR 1.25, WAL 12.5y
   QA Checks:
   ✓ Reverse-DSCR: Δ=0.001
   ✓ WAL: Δ=0.1y
   ✓ Tenor: 15y ≤ 23y
   ✓ Repo: PASS (UK/SPV/GBP/LMA/T+2)
   ✓ Indexation: Core flat, excess sidecar
   ✓ Sidecar: £800k (£1M × 0.8)
   ✓ Near-misses: 4 hints

6. CANARY GRID (30-min @1%):
   | Metric | Value | Threshold | Status |
   |--------|-------|-----------|--------|
   | Error Rate | 0.2% | <1% | ✓ |
   | P95 | 1.2s | <2s | ✓ |
   | Memory | Stable | No drift | ✓ |
   | Repo | PASS | Required | ✓ |
   | Rollback TTR | 1.5s | <2s | ✓ |

   DECISION: ALL GREEN - Requesting approval to widen to 25%
```

---

## If ANY RED (Rollback Template):

```
ROLLBACK EXECUTED
=================
1. Symptoms: [Specific metric that failed, e.g., "P95 latency 2.3s exceeded 2s threshold"]
2. Hypothesis: [Likely cause, e.g., "Permutation chunking overhead in tight memory environment"]
3. Next Step: [Immediate action, e.g., "Profile memory allocation in chunking algorithm"]

Canary: 1% → 0%
Flags: phase1_core → false
Timestamp: 2025-09-24T18:30:00Z
```

---

**END OF KICKOFF MESSAGE**