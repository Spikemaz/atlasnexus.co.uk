# FINAL MESSAGE TO SEND TO CLAUDE NOW

**Subject:** Phase-1 v2 — run QA micro-suite + canary @1% and paste proofs (live prod)

Claude — **live production domain only**, admin-only, **no file edits** (Flags API only). Paste proofs **inline**.

1. **Acknowledge** you're applying all pins (`#headers`, `#mfa_admin`, `#flags_api_contract`, `#snake_case_validator`, `#request_id_correlation`, `#route_list_contract`, `#acceptance_gate`, `#error_body_contract`).

2. **Runtime**: `ps aux | grep gunicorn` + `curl -i https://<live>/api/phase1/health` showing the 5 headers incl. `X-Request-ID`.

3. **Routes**: `GET /api/phase1/route-list` (JSON wire format from pins).

4. **403 test**: hit a Phase-1 route w/o MFA → `{"error":"MFA required","code":403,"request_id":"…"}`.

5. **Flags** (snake_case only):
   * GET (show `version`) → POST with `{"version":<current>,"changes":{…}}` → GET after + **audit row** with matching `request_id`.
   * Include a deliberate **409** (stale version) and **400** (PascalCase key) example.

6. **Golden fixture** (seed **424242**, ruleset **v1.0**): top-3 table + 7 QA checks (all deltas within tolerances) + determinism fields.

7. **Canary @1% for 30 min**: paste 5-min grid (Error %, P95, memory, repo PASS, rollback TTR <2s, logs complete).

8. **Decision**: GO → request widen to **25%** (paste response). NO-GO → rollback to **0%** + 3-line incident note.

---

## Last-Mile Gotchas:

* Ensure header middleware runs on **all** responses, including 4xx/5xx.
* Confirm clocks are NTP-synced (request/audit timestamps).
* Don't let caches strip custom headers; bypass CDN for `/api/phase1/*` if needed.
* Content-Type for errors must be `application/json` (no HTML error pages).

---

## Quick Curl Reference:

```bash
# Set admin token
export ADMIN_TOKEN="<your-admin-token>"

# 1. Health check with headers
curl -i https://atlasnexus.co.uk/api/phase1/health

# 2. Route list
curl -s -H "X-Admin-Token:$ADMIN_TOKEN" https://atlasnexus.co.uk/api/phase1/route-list | jq .

# 3. 403 MFA test
curl -s https://atlasnexus.co.uk/api/phase1/runtime | jq .

# 4. Get current flags
curl -s -H "X-Admin-Token:$ADMIN_TOKEN" https://atlasnexus.co.uk/api/phase1/flags | jq .

# 5. Test PascalCase rejection (expect 400)
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type:application/json" \
  https://atlasnexus.co.uk/api/phase1/flags \
  -d '{"version":1,"changes":{"DeterministicSeed":true}}' | jq .

# 6. Update flags (snake_case)
curl -i -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type:application/json" \
  https://atlasnexus.co.uk/api/phase1/flags \
  -d '{"version":<current>,"changes":{"deterministic_seed":true,"perm_chunking":true,"phase1_core":true,"reverse_dscr_engine":false,"gates_ab":false,"docs_exports":false}}'

# 7. Run golden fixture
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type:application/json" \
  https://atlasnexus.co.uk/api/phase1/permutation \
  -d '{"seed":424242,"ruleset_version":"v1.0","project_data":{"jurisdiction":"UK","asset_value":50000000,"lease_years":25,"indexation":"CPI","tenant_covenant":"AA"}}' | jq .

# 8. Run QA validation
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type:application/json" \
  https://atlasnexus.co.uk/api/phase1/qa/validate \
  -d '{"structure_id":"<winning_id>","tolerances":{"dscr":0.001,"wal":0.1,"value":1}}' | jq .

# 9. Start canary at 1%
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type:application/json" \
  https://atlasnexus.co.uk/api/phase1/canary/update \
  -d '{"percentage":1,"reason":"Start canary"}' | jq .

# 10. Check metrics
curl -s -H "X-Admin-Token:$ADMIN_TOKEN" https://atlasnexus.co.uk/api/phase1/metrics/current | jq .

# 11a. GO: Widen to 25%
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type:application/json" \
  https://atlasnexus.co.uk/api/phase1/canary/update \
  -d '{"percentage":25,"reason":"All checks GREEN"}' | jq .

# 11b. NO-GO: Rollback to 0%
curl -s -X POST -H "X-Admin-Token:$ADMIN_TOKEN" -H "Content-Type:application/json" \
  https://atlasnexus.co.uk/api/phase1/rollback \
  -d '{"target_percentage":0,"reason":"<specific_failure>"}' | jq .
```

---

**DEPLOYMENT = FAIL if any proof is missing, red, or malformed. No partial acceptance.**

---

END OF FINAL MESSAGE