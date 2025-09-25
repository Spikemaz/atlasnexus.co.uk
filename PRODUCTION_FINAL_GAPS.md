# Phase-1 Production Deployment - Final Gap Closure

## Changes Made (Ready to Deploy)

### 1. ✅ Environment Variables (production_config.py)
- `APP_ENV=prod` - Disables dev bridge
- `RULESET_VERSION=v1.0`
- `COMMIT_SHA=1489855`
- `BUILD_ID=phase1_20250124_2230`
- Redis session config added

### 2. ✅ Route Inventory Endpoint Added
- Added `/api/phase1/route-list` endpoint in `phase1_flask_integration.py`
- Returns JSON array with all routes and auth requirements
- Follows pinned wire format contract

### 3. ✅ Error Handlers Already Present
- JSON error handlers for 404/429/500 confirmed in `app.py`
- Returns proper error format with request_id

### 4. ✅ Dev Bridge Gated
- Line 990: `if os.getenv("APP_ENV", "dev") == "prod": return`
- X-Admin-Token bridge disabled in production

## Deployment Steps

1. **Deploy to Vercel with new env vars:**
   ```bash
   vercel env add APP_ENV production
   vercel env add RULESET_VERSION production
   vercel env add COMMIT_SHA production
   vercel env add BUILD_ID production
   vercel env add PHASE1_ADMIN_TOKEN production
   vercel deploy --prod
   ```

2. **Or use the deploy.sh script created**

## Test Commands After Deployment

### 1. Runtime Headers (expect X-Env=prod)
```bash
curl --ssl-no-revoke -sS -D- -o nul "https://atlasnexus.co.uk/api/phase1/health"
```

### 2. Route List (expect JSON)
```bash
curl --ssl-no-revoke -sS "https://atlasnexus.co.uk/api/phase1/route-list"
```

### 3. Full Engine Test with Session
```bash
set JAR=%TEMP%\p1.jar
curl --ssl-no-revoke -sS -c %JAR% -b %JAR% -H "Content-Type: application/json" -H "X-Admin-Token: phase1-admin-secure-token" -X POST "https://atlasnexus.co.uk/api/phase1/projects/validate" -d "{\"title\":\"Test\",\"country\":\"UK\",\"currency\":\"GBP\",\"gross_it_load_mw\":75,\"pue\":1.25,\"lease_years\":25,\"tenant_rating\":\"AA\",\"gross_monthly_rent\":2500000,\"capex_cost_per_mw\":5400000}"

curl --ssl-no-revoke -sS -c %JAR% -b %JAR% -H "Content-Type: application/json" -H "X-Admin-Token: phase1-admin-secure-token" -X POST "https://atlasnexus.co.uk/api/phase1/run" -d "{\"seed\":424242,\"topn\":20,\"ranges\":{\"senior_tenor\":[10,12,15,20],\"senior_coupon\":{\"min\":0.04,\"max\":0.06,\"step\":0.0025},\"senior_dscr\":{\"min\":1.25,\"max\":1.45,\"step\":0.05}}}"

curl --ssl-no-revoke -sS -c %JAR% -b %JAR% -H "X-Admin-Token: phase1-admin-secure-token" "https://atlasnexus.co.uk/api/phase1/securitisation/top20"

curl --ssl-no-revoke -sS -c %JAR% -b %JAR% -H "X-Admin-Token: phase1-admin-secure-token" "https://atlasnexus.co.uk/api/phase1/securitisation/export/1"
```

### 4. Error Contract Test
```bash
curl --ssl-no-revoke -sS "https://atlasnexus.co.uk/api/phase1/does-not-exist"
```
Expect: `{"error":"Not found","code":404,"request_id":"..."}`

## Expected Outcomes After Deployment

✅ `X-Env: prod` in headers
✅ `/route-list` returns JSON route inventory
✅ `/run` processes full permutation count
✅ `/top20` and `/export` work with session persistence
✅ 404 returns JSON error not HTML

## Canary Rollout After Acceptance

Once all tests pass:
```bash
curl --ssl-no-revoke -sS -H "X-Admin-Token: phase1-admin-secure-token" -H "Content-Type: application/json" -X POST "https://atlasnexus.co.uk/api/phase1/canary/update" -d "{\"percentage\":25,\"reason\":\"Acceptance gate passed\"}"
```

Monitor for 10 mins, then:
```bash
curl --ssl-no-revoke -sS -H "X-Admin-Token: phase1-admin-secure-token" -H "Content-Type: application/json" -X POST "https://atlasnexus.co.uk/api/phase1/canary/update" -d "{\"percentage\":100,\"reason\":\"Full production rollout\"}"
```