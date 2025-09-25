# Ultra-Short Kickoff for Claude (Live Prod Only)

**Subject:** Phase-1 v2 — run QA micro-suite + canary @1% and paste proofs (live prod)

Claude — on the **live production domain**, admin-only. **No file edits in prod; use Flags API.**

## Actions Required:

1. **Acknowledge** you're applying `CLAUDE_MEMORY_PINS.md`, incl. `#headers`, `#mfa_admin`, `#flags_api_contract`, `#snake_case_validator`, `#request_id_correlation`.

2. **Runtime proof**:
   * `ps aux | grep gunicorn` (show workers)
   * `curl -i https://<live>/api/phase1/health` showing **X-Commit-SHA / X-Ruleset-Version / X-Env=prod / X-Build-ID / X-Request-ID**.

3. **Routes**: `GET /api/phase1/route-list` (JSON format per contract).

4. **403 test**: call any Phase-1 route without MFA → body exactly `{"error":"MFA required"}`.

5. **Flags (snake_case only)**:
   * GET before (with `version`)
   * POST `/api/phase1/flags` body:
   ```json
   {"version": <current>, "changes": {
     "deterministic_seed": true, "perm_chunking": true, "phase1_core": true,
     "reverse_dscr_engine": false, "gates_ab": false, "docs_exports": false
   }}
   ```
   * Paste **409** example using stale `version`.
   * Paste **400** example using `"DeterministicSeed"` (PascalCase) with `invalid_keys` array.
   * Paste **audit row** showing **matching `X-Request-ID`**.

6. **Golden fixture (seed 424242)**: top-3 table + 7 QA checks with deltas within tolerances. Include determinism fields (`seed`, `chunk_id`, `range_signature_hash`, `ruleset_hash`, `commit_sha`).

7. **Canary @1% for 30 min**: 5-minute grid → Error %, P95, memory, repo PASS, rollback TTR (<2s), logs complete.

8. **Decision**: GO → request widen to **25%** (paste response). NO-GO → rollback to **0%** + 3-line incident note.

---

## Curl Command Pack:

```bash
# Health (headers + request id)
curl -i https://<live>/api/phase1/health

# 403 test - PascalCase rejection (expect 400)
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type: application/json" \
  https://<live>/api/phase1/flags \
  -d '{"version":1,"changes":{"DeterministicSeed":true}}' | jq .

# Flags versioned update (happy path)
curl -i -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type: application/json" \
  https://<live>/api/phase1/flags \
  -d '{"version":<paste-current>,"changes":{"deterministic_seed":true,"perm_chunking":true,"phase1_core":true}}'

# QA validate
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type: application/json" \
  https://<live>/api/phase1/qa/validate \
  -d '{"structure_id":"<winning_id>","tolerances":{"dscr":0.001,"wal":0.1,"value":1}}' | jq .

# Canary 1%
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type: application/json" \
  https://<live>/api/phase1/canary/update -d '{"percentage":1,"reason":"Start canary"}' | jq .

# Check canary status
curl -s -H "X-Admin-Token:$ADMIN_TOKEN" https://<live>/api/phase1/canary/status | jq .

# Get metrics
curl -s -H "X-Admin-Token:$ADMIN_TOKEN" https://<live>/api/phase1/metrics/current | jq .

# Canary 1% → 25% (GO)
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type: application/json" \
  https://<live>/api/phase1/canary/update -d '{"percentage":25,"reason":"QA passed, metrics GREEN"}' | jq .

# Emergency rollback (NO-GO)
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type: application/json" \
  https://<live>/api/phase1/rollback -d '{"target_percentage":0,"reason":"P95 exceeded threshold"}' | jq .
```

---

## Expected Proof Template:

```
PHASE-1 v2 PROOFS
=================

1. PINS ACK: ✓ All sections applied

2. RUNTIME:
   root 1234 gunicorn: master
   www 1235 gunicorn: worker
   Headers: SHA=abc123, Ruleset=v1.0, Env=prod, Build=789, ReqID=uuid-xyz

3. ROUTES: [{"method":"GET","path":"/api/phase1/health","auth":"public","flags":[]}...]

4. 403: {"error":"MFA required"}

5. FLAGS:
   Before: v1, all false
   After: v2, seed/perm/core true
   409: {"error":"Version conflict","expected":2,"provided":1}
   400: {"error":"Invalid flag key format","invalid_keys":["DeterministicSeed"],"hint":"deterministic_seed"}
   Audit: reqID=uuid-xyz matches header

6. FIXTURE: #1 AAA £45.8M DSCR=1.25 WAL=12.5y
   QA: All 7 ✓ (DSCR Δ=0.0007, WAL Δ=0.03y, etc)
   Determinism: seed=424242, chunk=c12, range=a7c3..., ruleset=9f3a...

7. CANARY:
   T+00: 0.0% | 0.8s | 512MB | PASS | 1.5s ✓
   T+30: 0.3% | 1.3s | 523MB | PASS | 1.5s ✓

8. DECISION: GO → 25%
```

---

**END OF ULTRA-SHORT KICKOFF**