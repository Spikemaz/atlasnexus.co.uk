#!/bin/bash
set -euo pipefail

export LIVE="http://127.0.0.1:5000"
export ADMIN_TOKEN="phase1-admin-secure-token"

echo "=== Phase-1 v2 Full Permutation Test ==="
echo

# 0) Health
echo "▶ Health Check"
curl -sS -I "$LIVE/api/phase1/health" | head -10

# 1) Validate project
echo
echo "▶ Validate Project: London DC Alpha"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/projects/validate" -d '{
  "title":"London DC Alpha","country":"UK","currency":"GBP",
  "gross_it_load_mw":75,"pue":1.25,"lease_years":25,"tenant_rating":"AA",
  "gross_monthly_rent":2500000,"opex_pct":0.22,
  "capex_cost_per_mw":5400000,"land_fees_total":3500000,
  "capex_market_per_mw":5600000,"ruleset_version":"v1.0","indexation_basis":"CPI_capped",
  "arranger_fee_pct":0.0125,"legal_fee_pct":0.0025,"rating_fee_pct":0.0015,"admin_bps":15
}' | python -m json.tool

# 2) Apply preset
echo
echo "▶ Apply Balanced Preset"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/permutations/apply-preset" -d '{"preset":"balanced_a"}' | python -m json.tool

# 3) Run ALL permutations (persist Top-20 in session)
echo
echo "▶ Run Permutation Engine (ALL permutations, seed=424242)"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/run" -d '{"seed":424242,"topn":20}' | python -m json.tool | head -50

# 4) View Top-20 (now populated from session)
echo
echo "▶ Get Top-20 Results"
curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/securitisation/top20" | python -m json.tool | head -100

# 5) Export #1
echo
echo "▶ Export Structure #1"
curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/securitisation/export/1" | python -m json.tool

echo
echo "✅ DONE - Full permutation processing complete!"