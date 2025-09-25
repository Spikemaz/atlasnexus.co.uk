#!/usr/bin/env bash
set -euo pipefail

LIVE="${LIVE:-http://127.0.0.1:5000}"
ADMIN_TOKEN="${ADMIN_TOKEN:-phase1-admin-secure-token}"
COOKIE_JAR="$(mktemp)"

say(){ printf "\n▶ %s\n" "$*"; }

say "Ping health"
curl -sS -D- -o /dev/null "$LIVE/api/phase1/health" | sed -n '1,10p'

# Seed session via dev bridge (APP_ENV!=prod)
say "Seed admin+MFA session via X-Admin-Token (dev only)"
curl -sS -c "$COOKIE_JAR" -b "$COOKIE_JAR" -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/health" >/dev/null

HDRS=(-H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" -b "$COOKIE_JAR" -c "$COOKIE_JAR")

say "1) Validate & cache PROJECT: London DC Alpha"
cat > /tmp/project.json <<'JSON'
{
  "title": "London DC Alpha",
  "country": "UK",
  "currency": "GBP",
  "ruleset_version": "v1.0",

  "gross_it_load_mw": 50.0,
  "pue": 1.25,
  "lease_years": 15,
  "tenant_rating": "A",
  "indexation_basis": "CPI_capped",

  "gross_monthly_rent": 2500000,
  "rent_per_kwh_month": null,

  "opex_pct": 0.28,
  "capex_cost_per_mw": 7000000,
  "land_fees_total": 15000000,
  "capex_market_per_mw": 7500000,

  "arranger_fee_pct": 0.0125,
  "legal_fee_pct": 0.0025,
  "rating_fee_pct": 0.0015,
  "admin_bps": 15,

  "wrap": false,
  "wrap_premium_bps": 0,
  "repo_target": true,

  "construction_start": "2025-10-01",
  "construction_months": 12,
  "base_cpi": 0.02
}
JSON

curl -sS "${HDRS[@]}" -X POST "$LIVE/api/phase1/projects/validate" -d @/tmp/project.json | python -m json.tool

say "2) Derived preview"
curl -sS "${HDRS[@]}" "$LIVE/api/phase1/projects/derived" | python -m json.tool

say "3) Load presets; apply 'A (Balanced)'"
curl -sS "${HDRS[@]}" "$LIVE/api/phase1/permutations/presets" | python -m json.tool | sed -n '1,80p'

# Try common preset labels; fall back if needed
apply_preset() {
  curl -sS "${HDRS[@]}" -X POST "$LIVE/api/phase1/permutations/apply-preset" \
    -d "{\"preset\":\"$1\"}" | python -m json.tool
}

# Try a few known keys
for P in "A (Balanced)" "A" "balanced" "Balanced"; do
  if apply_preset "$P" >/tmp/preset.out 2>/dev/null; then
    echo "Applied preset: $P"
    cat /tmp/preset.out | sed -n '1,120p'
    break
  fi
done

say "4) (Optional) Nudge ranges for a bigger sweep (still sane)"
cat > /tmp/ranges.json <<'JSON'
{
  "senior": {
    "dscr_floor": {"min":1.25,"max":1.40,"step":0.05},
    "coupon_fixed_pct": {"min":4.0,"max":6.5,"step":0.25},
    "tenor_years": [10,12,15,20],
    "amort": ["Level","Annuity"],
    "wrap": [false]
  },
  "mezz": {
    "on": [false]
  },
  "equity": {
    "trs_pct": {"min":0.10,"max":0.15,"step":0.05}
  },
  "indexation": {
    "mode": "CPI_capped",
    "cpi_floor_pct": {"min":0.010,"max":0.020,"step":0.005},
    "cpi_cap_pct": {"min":0.035,"max":0.045,"step":0.005},
    "flatten_core": [true]
  },
  "sidecar": {
    "zcis": [true],
    "zcis_tenor": [5],
    "rate_floor_sale": [true],
    "residual_strip": [false],
    "haircut_pct": {"min":0.05,"max":0.25,"step":0.05}
  },
  "fees_reserves": {
    "arranger_fee_pct": 0.0125,
    "legal_fee_pct": 0.0025,
    "rating_fee_pct": 0.0015,
    "admin_bps": 15,
    "liq_reserve_pct": 0.25,
    "dsra_months": 3
  }
}
JSON

curl -sS "${HDRS[@]}" -X POST "$LIVE/api/phase1/permutations/cardinality" -d @/tmp/ranges.json | python -m json.tool

say "5) RUN engine (exhaustive), seed=424242"
cat > /tmp/run.json <<'JSON'
{
  "seed": 424242,
  "ruleset_version": "v1.0",
  "exhaustive": true,
  "max_results": 20000
}
JSON

curl -sS "${HDRS[@]}" -X POST "$LIVE/api/phase1/run" -d @/tmp/run.json | python -m json.tool | sed -n '1,120p'

say "6) TOP-20"
curl -sS "${HDRS[@]}" "$LIVE/api/phase1/securitisation/top20" | python -m json.tool | sed -n '1,160p'

say "7) Export #1 (if implemented)"
curl -sS "${HDRS[@]}" "$LIVE/api/phase1/securitisation/export/1" | python -m json.tool || true

echo
echo "✅ DONE — full local deal sweep complete."