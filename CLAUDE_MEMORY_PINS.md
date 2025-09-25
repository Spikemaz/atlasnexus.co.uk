# CLAUDE_MEMORY_PINS.md
## Critical Phase-1 v2 Implementation Constants - NEVER DRIFT

---

## #qa_micro_suite

* Reverse-DSCR reconcile tolerance **±0.001** (same period basis as schedule).
* Senior WAL tolerance **±0.1y**; compute from **actual principal timing**.
* Tenor guardrail: **senior_tenor ≤ lease_years** (or **lease−2** if buffer active).
* Repo rule key must show **PASS + reason** with sub-rule detail.
* If `flatten_core=Y`: **core cashflows flat/capped**, all CPI excess lives in **sidecar**.
* Sidecar reconciliation: `net = gross × (1 − haircut%)`; `total = core_day_one + net` (rounding only).
* Near-miss list has **≥3** rows with **lever-level fix hints**.

## #flags_naming

* **Canonical flag keys (snake_case)**:
  `deterministic_seed`, `perm_chunking`, `phase1_core`, `reverse_dscr_engine`, `gates_ab`, `docs_exports`.
* Never edit JSON files in prod; **use the Flags API** (versioned, audited).
* Operator scripts must **translate any UI labels** to these snake_case keys before API calls.

## #blueprints_security

* All Phase-1 routes live under **one blueprint**: `/api/phase1` and are wrapped by `@admin_required` **+ MFA**.
* Canary/QA/metrics/flags endpoints **must** use the same blueprint & guards.
* Every response includes headers: `X-Commit-SHA`, `X-Ruleset-Version`, `X-Env`, `X-Build-ID`.

## #runtime_prod

* **Always** run prod with **gunicorn** (`wsgi:app`), not the Werkzeug dev server.
* Canary must run on **live domain** with **admin-only allowlist** + feature flags.

## #calc_conventions

* Periodicity must match: if waterfall is monthly, DSCR is monthly (don't annualize mid-check).
* DSCR floors: **AAA 1.45x, AA 1.35x, A 1.25x, BBB 1.15x** (ruleset-versioned).
* Near-miss window: **85–100%** of funding need.

## #indexation_derivs

* **ZCIS tenors only 5y/10y**; sidecar day-one value split: **gross, haircut%, net**.
* `flatten_core=Y` implies repo-first core; indexation optionality priced in sidecar.

## #fixtures_determinism

* Golden fixtures use **seed=424242**, `ruleset_version=v1.0`.
* Log on each run: `seed`, `chunk_id`, `range_signature_hash`, `ruleset_hash`, `commit_sha`.

## #canary_policy

* Widen from 1% → 25% only if: error <1%, P95 <2s, memory stable, QA passes, repo PASS, rollback TTR <2s, logs complete.
* On **any RED**, auto-disable Phase-1 flags and post 3-line incident note.

## #headers (must be present on **every** Phase-1 response)

* `X-Commit-SHA`, `X-Ruleset-Version`, `X-Env=prod`, `X-Build-ID`.
* Reject a release if any of these are missing in the runtime proof.
* Header source of truth = server middleware; **never** set per-handler.

## #mfa_admin

* All `/api/phase1/*` endpoints require: `session.is_admin == True` **and** `session.mfa_ok == True` issued **≤15 minutes** ago.
* Deny access if `mfa_ok` missing/expired; respond `403` with `{"error":"MFA required"}`.
* Canary/flags/rollback endpoints **also** require an **allowlist** check.

## #flags_api_contract

* Keys are **snake_case only**; unknown keys → **400**.
* Changes **must** include the current `version` (optimistic locking). If version mismatch → **409** and no change.
* Every mutation writes an **audit row**: who, when, old→new, request id.
* **No direct file edits** in prod.

## #proofs_required (Claude must paste all)

1. gunicorn process list + runtime headers.
2. `/api/phase1/route-list` (or equivalent) showing **all** Phase-1 routes under one blueprint.
3. 403 proof (non-admin & no-MFA hit).
4. Flags **before/after** JSON + **audit entries** showing `version` increments.
5. QA micro-suite 7 checks (pass/fail with tolerances).
6. 30-min canary grid (error %, P95, memory, rollback TTR).

## #route_list_acceptance

* Route list **must** expose for each endpoint: HTTP method, path, auth requirements, flag gates.
* Format: `METHOD /path [auth_level] [flag_gates]`
* Auth levels: `[public]`, `[@admin_required]`, `[@admin_required + MFA]`, `[@admin_required + MFA + allowlist]`
* All Phase-1 routes **must** be under `/api/phase1/*` prefix.
* Critical routes (flags, canary, rollback) **must** have allowlist protection.
* Example:
  ```
  GET  /api/phase1/health          [public]
  POST /api/phase1/flags           [@admin_required + MFA + allowlist]
  POST /api/phase1/canary/update   [@admin_required + MFA + allowlist]
  ```

---

## Critical Numbers Reference

### Tolerances
| Check | Tolerance | Units |
|-------|-----------|-------|
| DSCR | ±0.001 | ratio |
| WAL | ±0.1 | years |
| Value | ±1 | currency |
| Error Rate | <1 | percent |
| P95 Latency | <2 | seconds |
| Rollback TTR | <2 | seconds |

### DSCR Floors by Rating
| Rating | Min DSCR |
|--------|----------|
| AAA | 1.45x |
| AA | 1.35x |
| A | 1.25x |
| BBB | 1.15x |

### Canary Progression
| Stage | Percentage | Condition |
|-------|------------|-----------|
| Initial | 0% | Default |
| Test | 1% | Manual trigger |
| Expand | 25% | All checks GREEN |
| Full | 100% | 24h stable at 25% |
| Rollback | 0% | Any check RED |

---

## #payload_contracts

**Flags POST** `/api/phase1/flags`

* **Request**:

```json
{
  "version": <int>,
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

* **Responses**:
  200 `{ "version": <int>, "applied": {...}, "audit_id": "<id>" }`
  400 unknown key(s)
  401/403 unauth / MFA missing
  409 version mismatch (no change applied)
  429 rate limited

**QA validate** `/api/phase1/qa/validate`

* **Request**:

```json
{ "structure_id": "<id>", "tolerances": {"dscr": 0.001, "wal": 0.1, "value": 1} }
```

* **Response**:

```json
{
  "checks":[
    {"name":"reverse_dscr_recon","pass":true,"delta":0.0007},
    {"name":"wal_tolerance","pass":true,"delta":0.03},
    {"name":"tenor_guardrail","pass":true},
    {"name":"repo_rule","pass":true,"reason":"AAA core, docset=UK/2025"},
    {"name":"indexation_split","pass":true},
    {"name":"sidecar_recon","pass":true,"delta":0.25},
    {"name":"near_miss_hints","pass":true,"count":3}
  ],
  "determinism":{"seed":424242,"chunk_id":"c12","range_signature_hash":"a7c3…","ruleset_hash":"9f3a…","commit_sha":"<sha>"}
}
```

**Canary update** `/api/phase1/canary/update`

* **Request**: `{"percentage": 1, "reason": "start canary"}`
* **Response**: 200 `{ "percentage": 1, "effective_at": "<iso>", "audit_id": "<id>" }`

**Rollback** `/api/phase1/rollback`

* **Request**: `{"target_percentage": 0, "reason": "ANY RED"}`
* **Response**: 200 `{ "percentage": 0, "ttr_seconds": <float>, "audit_id": "<id>" }`

## #status_codes

* 401 unauthenticated, 403 **MFA required** (exact body: `{"error":"MFA required"}`), 404 not found, 409 **version mismatch**, 429 rate limited.

## #header_middleware_contract

* Every `/api/phase1/*` response **must** include: `X-Commit-SHA`, `X-Ruleset-Version`, `X-Env=prod`, `X-Build-ID`.
* Set by middleware only; reject a release if any are missing from the runtime proof.

## #audit_log_contract

* Every mutation logs: `audit_id`, `actor`, `when`, `route`, `request_id`, `old`, `new`, `version_before`, `version_after`.

## #allowlist_contract

* Critical routes (`/flags`, `/canary/*`, `/rollback`) require `@admin_required + MFA + allowlist`.
* Allowlist source = server (IP/CIDR or admin id), **not** client-provided headers.

## #determinism_proof

* All engine runs return: `seed`, `chunk_id`, `range_signature_hash`, `ruleset_hash`, `commit_sha`.
* Golden fixtures must use `seed=424242`, `ruleset_version=v1.0`.

## #snake_case_validator

* **Allowed key pattern**: `^[a-z]+(_[a-z0-9]+)*$` (ASCII only).
* **On violation** return **400** with:

```json
{"error":"Invalid flag key format. Use snake_case only","invalid_keys":["DeterministicSeed"],"hint":"deterministic_seed"}
```

* Validator runs **before** version/permission checks.

## #request_id_correlation

* Every `/api/phase1/*` response includes **`X-Request-ID`** (uuid4).
* Mutations must echo it in audit rows: `audit_id`, `request_id` **match**.
* Operator proofs must show **header** + **audit line** with same `request_id`.

## #route_list_contract (wire format)

* **GET** `/api/phase1/route-list` → JSON array:

```json
[
  {"method":"GET","path":"/api/phase1/health","auth":"public","flags":[]},
  {"method":"POST","path":"/api/phase1/flags","auth":"admin+mfa+allowlist","flags":["phase1_core"]},
  {"method":"POST","path":"/api/phase1/canary/update","auth":"admin+mfa+allowlist","flags":["phase1_core"]}
]
```

* All Phase-1 routes must appear here; **reject** release if any are missing.

## #acceptance_gate

* **Deployment = FAIL** if **any** required proof is missing, red, or malformed. No partial acceptance.
* Missing proof → **rollback to 0%** and post 3-line incident note immediately.
* Only proofs pasted **inline** from the **live prod domain** count (no screenshots, no dev/staging).

## #error_body_contract

* Every error from `/api/phase1/*` **must** be JSON with:

```json
{"error":"<message>","code":<http_status_int>,"request_id":"<uuid4>"}
```

* Middleware must still inject headers on errors: `X-Commit-SHA`, `X-Ruleset-Version`, `X-Env`, `X-Build-ID`, `X-Request-ID`.

---

**NEVER MODIFY THESE VALUES WITHOUT FULL TEAM REVIEW**