#!/usr/bin/env bash
# PRODUCTION TRIAL SCRIPT — End-to-end deal-stack flow
set -Eeuo pipefail

LIVE="${LIVE:-https://atlasnexus.co.uk}"
need() { [[ -n "${!1:-}" ]] || { echo "❌ Missing env: $1"; exit 1; }; }
need ADMIN_TOKEN

say(){ printf "\n%s\n" "▶ $*"; }

say "🚀 Starting Phase-1 v2 Production Trial against $LIVE"

# 0) Ping health (headers only, no body)
say "Health headers"
curl -sS -D- -o /dev/null "$LIVE/api/phase1/health?t=$(date +%s)" \
  -H "Cache-Control: no-cache" -H "Pragma: no-cache"

# 1) Validate & cache a project (Projects)
say "Projects → validate"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/projects/validate" -d '{
  "title":"London DC Alpha",
  "country":"UK","currency":"GBP","ruleset_version":"v1.0",
  "gross_it_load_mw":60,"pue":1.30,"lease_years":15,"tenant_rating":"A",
  "indexation_basis":"CPI_capped","gross_monthly_rent":2500000,
  "opex_pct":0.25,"capex_cost_per_mw":6000000,"land_fees_total":5000000,
  "arranger_fee_pct":0.0125,"legal_fee_pct":0.0025,"rating_fee_pct":0.0015,"admin_bps":15,
  "base_cpi":0.02
}'

# 2) Derived preview
say "Projects → derived"
curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/projects/derived"

# 3) Apply preset (A = Balanced)
say "Permutations → apply preset A"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/permutations/apply-preset" -d '{"preset":"A"}'

# 4) Cardinality preview
say "Permutations → cardinality"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/permutations/cardinality" -d '{"ranges":{}}'

# 5) Run permutations (deterministic)
say "Engine → run (seed 424242)"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/run" -d '{"seed":424242,"ruleset_version":"v1.0"}'

# 6) Review Top-20 & export #1
say "Securitisation → top20"
curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/securitisation/top20"

say "Securitisation → export #1 (if enabled)"
curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/securitisation/export/1" || true

echo -e "\n✅ Trial complete — you should see viable stacks with tiers, values, DSCR, WAL, repo flag."