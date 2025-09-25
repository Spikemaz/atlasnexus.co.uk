# Phase-1 Production Operations Guide

## 🚀 Production Status: LIVE

- **Engine**: Operational at 100% canary
- **Capacity**: 250k permutations max
- **Proven**: 1,920 permutations in single run
- **Export**: Full term sheets available

## 🔐 Authentication Model

### Business Endpoints (Admin + MFA Session Required)
Once `APP_ENV=prod` is set, these require real admin login:
- `POST /api/phase1/projects/validate`
- `POST /api/phase1/run`
- `GET /api/phase1/securitisation/top20`
- `GET /api/phase1/securitisation/export/{rank}`

### Ops Endpoints (X-Admin-Token Header)
These use token authentication:
- `GET /api/phase1/status/full`
- `POST /api/phase1/canary/update`
- `POST /api/phase1/rollback`
- `POST /api/phase1/flags`

## 💼 Running Your First Deal

### Via UI (Recommended)
1. Login with admin credentials + MFA
2. Navigate to Phase-1 → Projects
3. Validate your project inputs
4. Set permutation ranges (or use preset)
5. Run engine with seed 424242
6. View Top-20 results
7. Export term sheets

### Via CLI
```bash
set JAR=%TEMP%\phase1.jar
set LIVE=https://atlasnexus.co.uk

REM Login + MFA
curl -sS -c %JAR% -b %JAR% -X POST %LIVE%/auth/login -d "username=admin&password=***"
curl -sS -c %JAR% -b %JAR% -X POST %LIVE%/auth/mfa -d "code=123456"

REM Run engine
curl -sS -c %JAR% -b %JAR% -H "Content-Type: application/json" ^
  -X POST %LIVE%/api/phase1/run ^
  -d "{\"seed\":424242,\"topn\":20,\"ranges\":{
    \"senior_tenor\":[10,12,15,20],
    \"senior_coupon\":{\"min\":0.04,\"max\":0.06,\"step\":0.0025},
    \"senior_dscr\":{\"min\":1.25,\"max\":1.45,\"step\":0.05}
  }}"

REM Get results
curl -sS -c %JAR% -b %JAR% %LIVE%/api/phase1/securitisation/top20
curl -sS -c %JAR% -b %JAR% %LIVE%/api/phase1/securitisation/export/1
```

## 📊 Scaling Permutations

### Current (1,920 perms)
```json
{
  "senior_tenor": [10, 12, 15, 20],
  "senior_coupon": {"min": 0.04, "max": 0.0625, "step": 0.0025},
  "senior_dscr": {"min": 1.20, "max": 1.45, "step": 0.05},
  "indexation_mode": ["flat", "CPI_capped"],
  "zcis_tenor_years": [3, 5, 7, 10]
}
```

### Phase 2 (~10k perms)
- Add finer coupon steps: `"step": 0.001`
- Add more DSCR points: `"step": 0.02`

### Phase 3 (~50k perms)
- Enable mezz layer: `"mezz_on": [true, false]`
- Add wrap structures: `"wrap": [true, false]`

### Maximum (250k guardrail)
- All dimensions enabled
- Finest granularity steps
- Monitor via `/api/phase1/status/full`

## 🛠️ Operations Commands

### Check Status
```bash
curl -sS -H "X-Admin-Token: phase1-admin-secure-token" ^
  https://atlasnexus.co.uk/api/phase1/status/full
```

### Emergency Rollback
```bash
curl -sS -H "X-Admin-Token: phase1-admin-secure-token" ^
  -H "Content-Type: application/json" ^
  -X POST https://atlasnexus.co.uk/api/phase1/rollback ^
  -d "{\"target_percentage\":0,\"reason\":\"emergency rollback\"}"
```

### Update Feature Flags
```bash
curl -sS -H "X-Admin-Token: phase1-admin-secure-token" ^
  -H "Content-Type: application/json" ^
  -X POST https://atlasnexus.co.uk/api/phase1/flags ^
  -d "{\"reverse_dscr_engine\":true}"
```

## 🔍 Monitoring

### Key Metrics to Watch
- **Error rate**: Should be < 0.1%
- **P95 latency**: Should be < 5s for 1-10k perms
- **Memory drift**: Should be stable
- **Success rate**: Should be > 99.9%

### Health Check
```bash
curl -sS https://atlasnexus.co.uk/api/phase1/health
```

### Route Inventory
```bash
curl -sS https://atlasnexus.co.uk/api/phase1/route-list
```

## ⚠️ Important Notes

1. **Once APP_ENV=prod is set**:
   - Dev token bridge is disabled
   - Business endpoints require real admin session
   - Ops endpoints still use X-Admin-Token

2. **Session Management**:
   - Use cookie jar (-c/-b flags) for multi-request flows
   - Sessions persist via Redis
   - Results available across requests in same session

3. **Deterministic Runs**:
   - Use seed 424242 for reproducible results
   - Same inputs + seed = same outputs

## 📞 Support

For issues or questions:
- Check `/api/phase1/status/full` for system health
- Review logs in Vercel dashboard
- Emergency rollback available via ops endpoint