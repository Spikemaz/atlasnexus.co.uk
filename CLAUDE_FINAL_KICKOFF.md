# Final Copy-Paste Kickoff Message for Claude

**Subject:** Phase-1 v2 — Confirm pins, unify flags, run QA, paste proofs (live prod, admin-only)

**Claude — on the live production domain only. No file edits in prod; use the Flags API. Paste the proofs inline.**

## 1. **Acknowledge pins**

* Confirm you've read `CLAUDE_MEMORY_PINS.md` and will enforce: `#headers`, `#mfa_admin`, `#flags_api_contract`, `#canary_policy`.

## 2. **Runtime proof (gunicorn + headers)**

* Paste `ps aux | grep gunicorn` showing workers.
* `curl -i https://<prod-domain>/api/phase1/health` with headers:
  * `X-Commit-SHA`, `X-Ruleset-Version`, `X-Env=prod`, `X-Build-ID`.

## 3. **Blueprint + security**

* Paste `/api/phase1/route-list` (or equivalent) showing **all** Phase-1 routes under one blueprint.
* Show a **403** from hitting any Phase-1 route without admin+MFA (body must be `{"error":"MFA required"}`).
* Confirm allowlist is active for canary/flags/rollback endpoints.

## 4. **Flags — snake_case only + versioned writes**

* GET **before**: `/api/phase1/flags` (must show only: `deterministic_seed`, `perm_chunking`, `phase1_core`, `reverse_dscr_engine`, `gates_ab`, `docs_exports`, `version`).
* POST update with **version** to set:
  * `deterministic_seed=true`, `perm_chunking=true`, `phase1_core=true`,
  * keep `reverse_dscr_engine=false`, `gates_ab=false`, `docs_exports=false`.
* Paste **after** flags and the **audit entry** (who/when/old→new/version++). Unknown keys must 400; version mismatch must 409 (prove this with one deliberate mismatch).

## 5. **Golden fixture + QA micro-suite (seed 424242, ruleset v1.0)**

* Run the medium fixture and paste **Top-3** structures (Rank/Tier/Core/Sidecar/Total/DSCR Sr/WAL/Repo).
* Run the QA micro-suite on the top structure and paste results for all **7 checks** with tolerances:
  * DSCR reconciliation ±0.001
  * WAL ±0.1y
  * Tenor guardrail (senior ≤ lease or lease−2 buffer)
  * Repo rule PASS + reason
  * Indexation split (flatten_core semantics)
  * Sidecar net = gross × (1 − haircut%) ± 1 unit
  * Near-miss list ≥3 with lever-level hints

## 6. **Canary @1% for 30 minutes (admin allowlist)**

* Start canary to **1%**.
* Every 5 minutes, paste the grid:
  * Error % (target <1%), P95 step time (target <2s), memory, repo PASS, rollback TTR test (<2s), logs completeness.
* If **ALL GREEN** after 30 mins, request GO to widen to 25%.
* If **ANY RED**, execute rollback to 0% and paste the **3-line incident note** (Symptoms / Hypothesis / Next step) plus proof that flags are OFF again and canary=0%.

---

## Expected Proof Format:

```
PHASE-1 v2 DEPLOYMENT PROOFS
=============================

1. PINS ACKNOWLEDGED:
   ✓ #headers enforced
   ✓ #mfa_admin active (15-min window)
   ✓ #flags_api_contract (snake_case, versioned)
   ✓ #canary_policy understood

2. RUNTIME:
   root     1234  0.0  0.2  12345  6789 ?  S  17:00  0:00 gunicorn: master [wsgi:app]
   www-data 1235  0.0  0.3  23456  7890 ?  S  17:00  0:01 gunicorn: worker [wsgi:app]
   www-data 1236  0.0  0.3  23456  7891 ?  S  17:00  0:01 gunicorn: worker [wsgi:app]

   HTTP/1.1 200 OK
   X-Commit-SHA: abc1234
   X-Ruleset-Version: v1.0
   X-Env: prod
   X-Build-ID: build-789
   {"status":"healthy","timestamp":"2025-09-24T18:00:00Z","canary_percentage":0}

3. BLUEPRINT + SECURITY:
   Route List:
   GET  /api/phase1/health          [public]
   GET  /api/phase1/runtime         [@admin_required + MFA]
   GET  /api/phase1/flags           [@admin_required + MFA]
   POST /api/phase1/flags           [@admin_required + MFA + allowlist]
   POST /api/phase1/qa/validate     [@admin_required + MFA]
   GET  /api/phase1/metrics/current [@admin_required + MFA]
   GET  /api/phase1/canary/status   [@admin_required]
   POST /api/phase1/canary/update   [@admin_required + MFA + allowlist]
   POST /api/phase1/rollback        [@admin_required + MFA + allowlist]

   403 without MFA:
   curl https://prod/api/phase1/runtime
   {"error":"MFA required"}

4. FLAGS:
   Before (v1):
   {"deterministic_seed":false,"perm_chunking":false,"phase1_core":false,
    "reverse_dscr_engine":false,"gates_ab":false,"docs_exports":false,"version":1}

   After (v2):
   {"deterministic_seed":true,"perm_chunking":true,"phase1_core":true,
    "reverse_dscr_engine":false,"gates_ab":false,"docs_exports":false,"version":2}

   Audit:
   {"timestamp":"2025-09-24T18:05:00Z","operator":"admin","request_id":"req_xyz",
    "changes":{"deterministic_seed":"false→true","perm_chunking":"false→true",
               "phase1_core":"false→true"},"version":"1→2"}

   409 on version mismatch (tested):
   POST with version:1 → {"error":"Version conflict","expected":2,"provided":1}

5. GOLDEN FIXTURE + QA:
   Top-3 Structures:
   #1: AAA | Core £45M | Sidecar £0.8M | Total £45.8M | DSCR 1.25 | WAL 12.5y | Repo PASS
   #2: AA  | Core £44M | Sidecar £1.2M | Total £45.2M | DSCR 1.20 | WAL 13.0y | Repo PASS
   #3: AA  | Core £43M | Sidecar £1.5M | Total £44.5M | DSCR 1.18 | WAL 13.5y | Repo FAIL

   QA Suite (#1):
   ✓ DSCR recon: 1.250 vs 1.251 (Δ=0.001) PASS
   ✓ WAL: 12.5y vs 12.4y (Δ=0.1y) PASS
   ✓ Tenor: 15y ≤ 23y (lease-2) PASS
   ✓ Repo: PASS (UK/SPV/GBP/LMA/T+2)
   ✓ Indexation: Core flat, excess in sidecar PASS
   ✓ Sidecar: £800k = £1M × 0.8 (Δ=0) PASS
   ✓ Near-misses: 4 hints ["DSCR→1.30", "Tenor→10y", "Senior→£40M", "Mezz→5%"] PASS

6. CANARY GRID @1%:
   T+00: Error 0.0% | P95 0.8s | Mem 512MB | Repo PASS | TTR 1.5s | Logs ✓
   T+05: Error 0.1% | P95 1.0s | Mem 515MB | Repo PASS | TTR 1.5s | Logs ✓
   T+10: Error 0.2% | P95 1.1s | Mem 518MB | Repo PASS | TTR 1.5s | Logs ✓
   T+15: Error 0.2% | P95 1.2s | Mem 520MB | Repo PASS | TTR 1.5s | Logs ✓
   T+20: Error 0.3% | P95 1.2s | Mem 520MB | Repo PASS | TTR 1.5s | Logs ✓
   T+25: Error 0.3% | P95 1.3s | Mem 522MB | Repo PASS | TTR 1.5s | Logs ✓
   T+30: Error 0.3% | P95 1.3s | Mem 523MB | Repo PASS | TTR 1.5s | Logs ✓

   ALL GREEN → Requesting approval to widen to 25%
```

---

## If ANY RED (Incident Template):

```
INCIDENT & ROLLBACK
===================
1. Symptoms: P95 latency 2.3s exceeded 2s threshold at T+15
2. Hypothesis: Permutation chunking memory pressure in constrained environment
3. Next Step: Profile chunk allocation patterns, consider adaptive sizing

Actions taken:
- Canary: 1% → 0% (completed 18:20:15Z)
- Flags: phase1_core → false (v3)
- Verified: Error rate back to 0%, P95 < 1s
```

---

---

## Proof Checklist (Claude must provide ALL):

✅ **Runtime**: gunicorn process list + `curl -i /api/phase1/health` showing the 4 headers.
✅ **Routes**: `/api/phase1/route-list` formatted `METHOD /path [auth_level] [flag_gates]`.
✅ **403 test**: call a Phase-1 route without MFA → body `{"error":"MFA required"}`.
✅ **Flags**: GET before → POST with `version` → GET after + **audit row**; also paste a deliberate 409 example.
✅ **Fixture + QA**: Top-3 table + all 7 QA checks with deltas within tolerances.
✅ **Canary 1% (30 min)**: 5-min grid with Error %, P95, memory, repo PASS, rollback TTR (<2s), logs complete.
✅ **Decision**: GO (request widen to 25%) **or** NO-GO (rollback to 0% + 3-line incident).

## Critical Enforcement:

**REJECT ANY PascalCase flag keys on the API** - The API must enforce snake_case at the perimeter. Any request with PascalCase keys (e.g., "DeterministicSeed") must return 400 with error: `{"error":"Invalid flag key format. Use snake_case only","invalid_keys":["DeterministicSeed"]}`.

**END OF FINAL KICKOFF**