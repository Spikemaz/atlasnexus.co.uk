# SEND THIS TO CLAUDE NOW

**Subject:** Phase-1 v2 — Run QA micro-suite + canary @1% and paste proofs (LIVE PROD ONLY)

Claude — **LIVE PRODUCTION DOMAIN ONLY**, admin-only. **No file edits in prod** (use the Flags API). Paste **all proofs inline**.

## 0) Acknowledge pins (one line)

Confirm you've read and will enforce **CLAUDE_MEMORY_PINS.md**: `#headers`, `#mfa_admin`, `#flags_api_contract`, `#snake_case_validator`, `#request_id_correlation`, `#route_list_contract`, `#acceptance_gate`, `#error_body_contract`, `#payload_contracts`, `#status_codes`, `#allowlist_contract`, `#determinism_proof`.

## 1) Runtime proof (live prod)

Export your live base once and reuse it:
```bash
export LIVE="https://atlasnexus.co.uk"
```

* Show `ps aux | grep gunicorn` with worker PIDs.
* Show headers only (no body) with request ID visible:
  ```bash
  curl -sS -D- -o /dev/null "$LIVE/api/phase1/health"
  ```
* Bypass any CDN/proxy cache and print status + total time:
  ```bash
  curl -sS -D- -o /dev/null -H "Cache-Control: no-cache" -H "Pragma: no-cache" \
    -w '\nHTTP:%{http_code} TIME:%{time_total}s\n' "$LIVE/api/phase1/health?t=$(date +%s)"
  ```
* Must show **all headers** on the response:
  `X-Commit-SHA`, `X-Ruleset-Version`, `X-Env=prod`, `X-Build-ID`, `X-Request-ID`.

## 2) Route inventory (must be under one blueprint)

* `GET /api/phase1/route-list` (JSON wire format from pins) listing **every** Phase-1 route with `method`, `path`, `auth`, `flags`.
* Critical routes MUST show `"auth":"admin+mfa+allowlist"`:
  - `/api/phase1/flags` (POST)
  - `/api/phase1/canary/update` (POST)
  - `/api/phase1/rollback` (POST)

## 3) Security checks

* **403 A** (Unauth - no session):
  ```bash
  curl -sS -D- "$LIVE/api/phase1/flags"
  ```
  Expect: `{"error":"MFA required","code":403,"request_id":"..."}` with all headers present.

* **403 B** (Non-admin - valid session but not admin):
  ```bash
  # Hit with a non-admin session cookie if available
  curl -sS -D- -H "Cookie: session=non_admin_session" "$LIVE/api/phase1/flags"
  ```
  Expect: `{"error":"Admin access required","code":403,"request_id":"..."}` with all headers present.

* **404 JSON error** (non-existent endpoint):
  ```bash
  curl -sS -D- -o - "$LIVE/api/phase1/does-not-exist"
  ```
  Expect: JSON error body with headers still present.

* Confirm critical routes (`/flags`, `/canary/*`, `/rollback`) require **admin+mfa+allowlist** in route list.

## 4) Flags API (snake_case + versioning)

* **GET** current flags (include `version`).
* **POST** update using **snake_case** keys and `version`:

```json
{
  "version": <current_int>,
  "changes": {
    "deterministic_seed": true,
    "perm_chunking": true,
    "phase1_core": true,
    "reverse_dscr_engine": false,
    "gates_ab": false,
    "docs_exports": false
  }
}
```

* Paste **after** state + **audit row** showing `audit_id`, `actor`, `when`, `request_id` (must match `X-Request-ID` header).
* Paste 2 negative tests:

  1. **400** for PascalCase key (should fail):
     ```bash
     curl -sS -D- -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" -X POST \
       "$LIVE/api/phase1/flags" \
       -d '{"version":1,"changes":{"DeterministicSeed":true}}'
     ```
     Must return: `{"error":"Invalid flag key format. Use snake_case only","invalid_keys":["DeterministicSeed"],"hint":"deterministic_seed","code":400,"request_id":"…"}`

  2. **409** version mismatch (use stale version):
     ```bash
     curl -sS -D- -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" -X POST \
       "$LIVE/api/phase1/flags" \
       -d '{"version":0,"changes":{"phase1_core":true}}'
     ```

  3. **429** rate limit test (fire 6 quick writes to endpoint limited at 5/min):
     ```bash
     for i in {1..6}; do
       curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
         -X POST "$LIVE/api/phase1/flags" -d '{"version":1,"changes":{"phase1_core":true}}' >/dev/null
     done
     # Last call should return 429 with JSON error and X-Request-ID
     ```

**IMPORTANT:** Redact secrets in pasted proofs (show first/last 4 chars of tokens only, e.g., `abc1...7890`).

## 5) Golden fixture + QA micro-suite

* Run golden fixture **seed=424242**, `ruleset_version=v1.0`.
* Paste a **Top-3** table (Rank, Tier, Core, Sidecar, Total, DSCR Sr/Mezz, WAL, Repo, Near-miss).
* Run `POST /api/phase1/qa/validate` with:
  `{"structure_id":"<id>","tolerances":{"dscr":0.001,"wal":0.1,"value":1}}`
* Paste all **7 checks** with deltas (must be within tolerances) **and** determinism block: `seed`, `chunk_id`, `range_signature_hash`, `ruleset_hash`, `commit_sha`.

## 6) Canary @1% — 30-minute window

* Set to **1%** via `POST /api/phase1/canary/update` `{ "percentage": 1, "reason": "start canary" }` (paste response + audit).
* Paste a **5-minute grid** (6 rows) with timing metrics:
  ```
  T+00: Error: 0.1% | P50: 0.8s | P95: 1.2s | Mem: 512MB | Repo: PASS | TTR: 1.5s | Logs: ✓
  T+05: Error: 0.1% | P50: 0.9s | P95: 1.3s | Mem: 515MB | Repo: PASS | TTR: 1.5s | Logs: ✓
  T+10: Error: 0.2% | P50: 0.9s | P95: 1.3s | Mem: 518MB | Repo: PASS | TTR: 1.5s | Logs: ✓
  T+15: Error: 0.2% | P50: 1.0s | P95: 1.4s | Mem: 520MB | Repo: PASS | TTR: 1.5s | Logs: ✓
  T+20: Error: 0.2% | P50: 1.0s | P95: 1.4s | Mem: 520MB | Repo: PASS | TTR: 1.5s | Logs: ✓
  T+25: Error: 0.3% | P50: 1.0s | P95: 1.4s | Mem: 522MB | Repo: PASS | TTR: 1.5s | Logs: ✓
  T+30: Error: 0.3% | P50: 1.0s | P95: 1.4s | Mem: 523MB | Repo: PASS | TTR: 1.5s | Logs: ✓
  ```
* Include raw timing from metrics endpoint: `curl -w 'TIME:%{time_total}s\n' "$LIVE/api/phase1/metrics/current"`
* Also paste `GET /api/phase1/metrics/current` snapshots.

## 7) Acceptance gate (all-or-nothing)

* If **any** proof missing/red/malformed → **immediately rollback to 0%** with `POST /api/phase1/rollback` and paste:
  a) rollback response (`percentage`, `ttr_seconds`, `audit_id`)
  b) **3-line incident note**: Symptoms / Hypothesis / Next step.
* If **all GREEN**, request widen to **25%**: `POST /api/phase1/canary/update` `{ "percentage": 25, "reason": "QA passed, metrics green" }` and paste response + audit.

## 8) Extra hardening checks

* **JSON Content-Type on errors**:
  ```bash
  curl -sS -D- -o /dev/null "$LIVE/api/phase1/does-not-exist" | grep -i 'Content-Type: application/json'
  ```

* **Kill switch (independent of flags)**:
  ```bash
  curl -sS -D- -H "X-Admin-Token:$ADMIN_TOKEN" -X POST "$LIVE/api/phase1/emergency/stop"
  ```

* **OPTIONS/CORS (no HTML)**:
  ```bash
  curl -sS -D- -X OPTIONS "$LIVE/api/phase1/flags" | egrep -i 'HTTP/|allow|access-control|content-type'
  ```

* **CDN bypass verification**:
  ```bash
  curl -sS -I -H "Cache-Control: no-cache" -H "Pragma: no-cache" \
    "$LIVE/api/phase1/health?t=$(date +%s)" | egrep -i 'Age|Cache|Via'
  # Expect no Age header and explicit no-cache directives
  ```

* **Secret hygiene in logs**:
  ```bash
  grep -RInE 'X-Admin-Token|Authorization' /var/log 2>/dev/null | head -1 || echo '[OK] no token leakage'
  ```

## 9) Reminders (non-negotiable)

* All `/api/phase1/*` responses (including errors) must include the 5 headers and JSON error body:
  `{"error":"<message>","code":<http_status_int>,"request_id":"<uuid4>"}`
* Live domain only; **no screenshots, no dev/staging URLs**.
* **DEPLOYMENT = FAIL** if any proof is missing, red, or malformed.

---

**END OF MESSAGE - SEND TO CLAUDE NOW**