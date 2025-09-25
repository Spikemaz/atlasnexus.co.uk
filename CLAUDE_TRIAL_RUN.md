# Trial Run (End-to-End) — Copy to Claude

**Run on live prod (admin-only). Use snake_case keys.**

```bash
export LIVE="https://atlasnexus.co.uk"
export ADMIN_TOKEN="<redacted>"

# 1) Validate & cache a project (Projects page)
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/projects/validate" -d '{
  "title":"London DC Alpha",
  "country":"UK",
  "currency":"GBP",
  "ruleset_version":"v1.0",
  "gross_it_load_mw":60,
  "pue":1.30,
  "lease_years":15,
  "tenant_rating":"A",
  "indexation_basis":"CPI_capped",
  "gross_monthly_rent":2500000,
  "opex_pct":0.25,
  "capex_cost_per_mw":6000000,
  "land_fees_total":5000000,
  "base_cpi":0.02
}'

# 2) Pull derived preview (funding_need, tenor_cap, NOI, etc.)
curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/projects/derived"

# 3) Get & apply a preset (Permutations page)
curl -sS "$LIVE/api/phase1/permutations/presets"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/permutations/apply-preset" -d '{"preset":"A"}'

# (Optional) If you'd rather pass ranges directly, use this minimal set:
RANGES='{
  "senior_dscr_floor": {"min":1.25,"max":1.35,"step":0.05},
  "senior_coupon":     {"min":0.04,"max":0.06,"step":0.0025},
  "senior_tenor":      [10,12,15],
  "senior_amort":      ["Level","Annuity"],
  "wrap":              [true,false],
  "equity_trs_pct":    {"min":0.10,"max":0.15,"step":0.05},
  "indexation_basis":  ["CPI_capped"],
  "cpi_floor":         0.01,
  "cpi_cap":           0.04,
  "zcis":              true,
  "zcis_tenor":        5,
  "dsra_months":       3,
  "arranger_fee_pct":  0.0125,
  "legal_fee_pct":     0.0025,
  "rating_fee_pct":    0.0015,
  "admin_bps":         0.0015,
  "liq_reserve_pct":   0.25
}'

# 4) Cardinality preview (how many permutations will run)
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/permutations/cardinality" -d "{\"ranges\": $RANGES }"

# 5) Run the permutation engine (seeded for determinism)
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/run" -d "{
  \"seed\":424242,
  \"ruleset_version\":\"v1.0\",
  \"ranges\": $RANGES
}"

# 6) Review viable outcomes (Top-20) (Securitisation page)
curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/securitisation/top20"

# (Optional) Export the top structure's docs
curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/securitisation/export/1"
```

## What a Good Trial Looks Like:

✅ **Project validation** returns cached project with derived values
✅ **Derived preview** shows funding_need, tenor_cap, NOI calculations
✅ **Preset application** confirms ranges loaded
✅ **Cardinality** shows total permutations to be generated
✅ **Engine run** completes with deterministic seed 424242
✅ **Top-20** lists: rank, tier, day_one_value_core, day_one_value_sidecar, total, min_dscr_senior, wal_years, repo_eligible
✅ **All responses** carry headers: X-Commit-SHA, X-Ruleset-Version, X-Env=prod, X-Build-ID, X-Request-ID

## Expected Output Format:

```json
// Top-20 structure example:
{
  "rank": 1,
  "tier": "AAA",
  "day_one_value_core": 45000000,
  "day_one_value_sidecar": 800000,
  "total": 45800000,
  "min_dscr_senior": 1.25,
  "wal_years": 12.5,
  "repo_eligible": true,
  "near_miss": false
}
```

**If any step returns 403**: Use admin/MFA path as pinned in CLAUDE_MEMORY_PINS.md

---

**This is the exact "input → save → run → see viable stacks" loop for Phase-1 v2!**