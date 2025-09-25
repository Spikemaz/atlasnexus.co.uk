# Message to Claude for Phase-1 v2 Deployment

**Subject:** Phase-1 v2 — Run securitisation QA micro-suite + canary proofs

**Claude — on the live prod domain (admin-only), follow our operator script, then paste these proofs:**

1. **Headers & runtime** from Sections 1–2 of `CANARY_OPERATOR_SCRIPT.md` (gunicorn, `X-Commit-SHA`, `X-Ruleset-Version`, `X-Env=prod`, `X-Build-ID`).

2. **Flags API** before/after (turn ON: `DeterministicSeed`, `PermChunking`, `Phase1Core`; keep OFF: `ReverseDSCR`, `GatesAB`, `DocsExports`) with audit line and `version` increments.

3. **Golden fixtures (seed 424242, ruleset v1.0):** Top-20 tables, prune stats, stress DSCR (CPI 0/1.8/2.5), throughput, P50/P95, memory, chunks, plus `range_signature_hash` & `ruleset_hash`.

4. **Securitisation QA micro-suite (on rank #1):**
   - Reverse-DSCR reco (±0.001)
   - WAL senior (±0.1y)
   - Tenor guardrail check
   - Repo rule key + PASS/FAIL reason
   - Indexation split (if flatten_core=Y)
   - Sidecar reconciliation (±£1)
   - Near-miss hints (≥3)

5. **Go/No-Go Gate Decision:**
   - Error rate < 1%
   - P95 < 2s
   - Memory stable
   - All QA checks PASS
   - Rollback TTR < 2s

6. **Action Taken:**
   - If ALL GREEN: "Widened canary from 1% to 25%"
   - If ANY RED: "Rolled back to 0%, incident: [specific failure]"

**Expected Response Format:**
```
DEPLOYMENT PROOF - Phase-1 v2
=============================

1. RUNTIME HEADERS:
   X-Commit-SHA: abc1234
   X-Ruleset-Version: v1.0
   X-Env: prod
   X-Build-ID: build-789
   X-Gunicorn-Workers: 4

2. FLAGS (v1→v2):
   DeterministicSeed: false→true
   PermChunking: false→true
   Phase1Core: false→true
   [Audit: admin@2025-09-24T17:00:00Z]

3. GOLDEN FIXTURE (seed 424242):
   Top Structure: ID-001, DSCR 1.25, WAL 12.5y
   Prune: 100k→15k→8k→5k
   P95: 1200ms, Memory: 512MB
   Hashes: range=a7c3f9e2, ruleset=9f3a2b7e

4. QA SUITE RESULTS:
   ✓ Reverse-DSCR: 1.250 vs 1.251 (Δ=0.001)
   ✓ WAL: 12.5y vs 12.4y (Δ=0.1y)
   ✓ Tenor: 15y ≤ 23y (lease-2)
   ✓ Repo: PASS (UK/SPV/GBP/LMA/T+2)
   ✓ Indexation: Core flat, excess in sidecar
   ✓ Sidecar: £800k net (£1M × 0.8)
   ✓ Near-misses: 4 hints found

5. GO/NO-GO: **GO**
   - Error rate: 0.2% ✓
   - P95: 1.2s ✓
   - Memory: stable ✓
   - QA: PASS ✓
   - Rollback: 1.5s ✓

6. ACTION: Widened canary 1% → 25%
   Timestamp: 2025-09-24T17:15:00Z
   Operator: admin
```

---

**Important Notes:**
- Use admin token from environment: `PHASE1_ADMIN_TOKEN`
- All endpoints require `X-Admin-Token` header
- Monitor `/api/phase1/canary/metrics` after widening
- If rollback needed, use `/api/phase1/rollback` immediately
- Check `/api/phase1/logs/errors?last=10` for any failures

**Files to Reference:**
- `CANARY_OPERATOR_SCRIPT.md` - Full operator procedures
- `phase1_qa_suite.py` - QA validation logic
- `phase1_canary_endpoints.py` - API endpoints
- `feature_flags.json` - Current flag configuration

---

END OF MESSAGE TEMPLATE