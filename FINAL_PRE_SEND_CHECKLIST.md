# ✅ FINAL PRE-SEND CHECKLIST

## 90-Second Lint Check - ALL CONFIRMED ✅

- [✅] **LIVE PRODUCTION DOMAIN ONLY** enforced throughout
- [✅] **No file edits** - Flags API only
- [✅] **5 headers** required on ALL responses (including errors):
  - `X-Commit-SHA`
  - `X-Ruleset-Version`
  - `X-Env=prod`
  - `X-Build-ID`
  - `X-Request-ID`
- [✅] **snake_case** flags everywhere:
  - `deterministic_seed`
  - `perm_chunking`
  - `phase1_core`
  - `reverse_dscr_engine`
  - `gates_ab`
  - `docs_exports`
- [✅] **JSON error format** required: `{"error","code","request_id"}`
- [✅] **Route list** under `/api/phase1/*` blueprint
- [✅] **Acceptance gate** = all-or-nothing (any RED → rollback to 0%)
- [✅] **Golden fixture** = `seed=424242` + `ruleset_version=v1.0`
- [✅] **Request ID correlation** between headers and audit logs
- [✅] **MFA + admin + allowlist** on critical routes

## Hardening Add-Ons Applied ✅

1. **Domain export** added for consistency:
   ```bash
   export LIVE="https://atlasnexus.co.uk"
   ```

2. **Headers-only curl** for clean proof:
   ```bash
   curl -sS -D- -o /dev/null "$LIVE/api/phase1/health"
   ```

3. **Negative test commands** included inline for copy/paste

## Files Ready:

| File | Purpose | Status |
|------|---------|--------|
| `CLAUDE_MEMORY_PINS.md` | All pinned values & contracts | ✅ Complete |
| `SEND_TO_CLAUDE_NOW.md` | Final deployment message | ✅ Ready to send |
| `phase1_qa_suite.py` | QA validation implementation | ✅ Created |
| `phase1_canary_endpoints.py` | API endpoints | ✅ Created |
| `CANARY_OPERATOR_SCRIPT.md` | Operator procedures | ✅ Created |

## The System Enforces:

1. **PascalCase rejection** at API perimeter → 400 error
2. **Version-based optimistic locking** → 409 on conflict
3. **MFA required** → 403 with exact JSON format
4. **Tolerances**: DSCR ±0.001, WAL ±0.1y, Value ±£1
5. **Canary progression**: 0% → 1% → 25% (ALL GREEN) or 0% (ANY RED)
6. **Rollback TTR** < 2 seconds requirement
7. **Deterministic hashes** on every run

## 🚀 READY TO SEND!

Copy the entire content from `SEND_TO_CLAUDE_NOW.md` and paste it to Claude.

The message is:
- **Airtight** - no wiggle room
- **Domain-locked** - atlasnexus.co.uk only
- **Proof-demanding** - inline proofs required
- **Zero-tolerance** - any failure = rollback

**YOU ARE LOCKED AND LOADED. FIRE AWAY! 🎯**