# CANARY OPERATOR SCRIPT v2.0
## Phase-1 Securitization Deployment Protocol

---

## Section 1: Pre-Flight Checks

### 1.1 Environment Headers
```bash
# Verify runtime environment
curl -H "X-Admin-Token: $ADMIN_TOKEN" https://atlasnexus.co.uk/api/phase1/runtime

# Expected headers:
X-Commit-SHA: [git_sha]
X-Ruleset-Version: v1.0
X-Env: prod
X-Build-ID: [build_id]
X-Gunicorn-Workers: 4
```

### 1.2 Flag Configuration
```bash
# Check current flags
curl https://atlasnexus.co.uk/api/phase1/flags

# Enable required flags (admin-only) - using canonical snake_case keys
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/flags \
  -d '{
    "deterministic_seed": true,
    "perm_chunking": true,
    "phase1_core": true,
    "reverse_dscr_engine": false,
    "gates_ab": false,
    "docs_exports": false
  }'

# Verify audit log
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/flags/audit
```

---

## Section 2: Golden Fixtures (seed 424242)

### 2.1 Run Standard Fixture
```bash
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/permutation \
  -d '{
    "seed": 424242,
    "ruleset_version": "v1.0",
    "project_data": {
      "jurisdiction": "UK",
      "asset_value": 50000000,
      "lease_years": 25,
      "indexation": "CPI",
      "tenant_covenant": "AA"
    }
  }'
```

### 2.2 Capture Baseline Metrics
```json
{
  "top_20_structures": [...],
  "prune_stats": {
    "total_generated": 100000,
    "after_dscr_prune": 15000,
    "after_repo_prune": 8000,
    "final_ranked": 5000
  },
  "performance": {
    "p50_ms": 850,
    "p95_ms": 1200,
    "memory_peak_mb": 512
  },
  "hashes": {
    "range_signature": "a7c3f9e2b4d6",
    "ruleset": "9f3a2b7e8c1d"
  }
}
```

### 2.3 Stress Test (CPI variations)
```bash
# CPI = 0%
curl -X POST ... -d '{"cpi": 0, ...}'

# CPI = 1.8%
curl -X POST ... -d '{"cpi": 1.8, ...}'

# CPI = 2.5%
curl -X POST ... -d '{"cpi": 2.5, ...}'
```

---

## Section 3: QA Micro-Suite Execution

### 3.1 Run QA Suite on Top Structure
```bash
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/qa/validate \
  -d '{
    "structure_id": "[winning_structure_id]"
  }'
```

### 3.2 Required Validations
- [ ] Reverse-DSCR reconciliation (±0.001)
- [ ] WAL calculation (±0.1y)
- [ ] Tenor guardrail (senior ≤ lease-2)
- [ ] Repo rule key components present
- [ ] Indexation split confirmed (if flatten_core=Y)
- [ ] Sidecar value reconciliation (±£1)
- [ ] Near-miss hints (≥3 with lever guidance)

---

## Section 4: Go/No-Go Gate

### 4.1 Collect Metrics (30-min window)
```bash
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/metrics/current
```

### 4.2 Decision Criteria
| Metric | Threshold | Current | Status |
|--------|-----------|---------|---------|
| Error Rate | < 1% | ___ | ⬜ |
| P95 Step Time | < 2s | ___ | ⬜ |
| Memory Drift | None | ___ | ⬜ |
| QA Checks | Pass | ___ | ⬜ |
| Repo Rule | Pass | ___ | ⬜ |
| Rollback TTR | < 2s | ___ | ⬜ |
| Log Fields | Complete | ___ | ⬜ |

### 4.3 Decision
- **ALL GREEN**: Proceed to widen canary (1% → 25%)
- **ANY RED**: Execute rollback, stay at 0%

---

## Section 5: Canary Control

### 5.1 Current Status
```bash
curl https://atlasnexus.co.uk/api/phase1/canary/status
```

### 5.2 Widen Canary (if GO)
```bash
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/canary/update \
  -d '{
    "percentage": 25,
    "reason": "QA passed, metrics green"
  }'
```

### 5.3 Emergency Rollback (if NO-GO)
```bash
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/rollback \
  -d '{
    "target_percentage": 0,
    "reason": "[specific_failure]"
  }'
```

---

## Section 6: Proof Collection for Claude

### 6.1 Headers & Runtime
```
[Paste output from Section 1.1]
```

### 6.2 Flags Configuration
```
[Paste before/after flags with audit log]
```

### 6.3 Golden Fixtures
```
[Paste metrics from Section 2.2]
```

### 6.4 QA Suite Results
```
[Paste all 7 check results from Section 3.2]
```

### 6.5 Go/No-Go Decision
```
Decision: [GO/NO-GO]
Action Taken: [widened to 25% / rolled back to 0%]
Timestamp: [ISO timestamp]
Operator: [name]
```

---

## Section 7: Incident Response (if NO-GO)

### 7.1 Three-Line Report
1. **Symptoms**: [What failed - specific metric/check]
2. **Hypothesis**: [Likely cause based on pattern]
3. **Next Step**: [Immediate action to investigate/fix]

### 7.2 Rollback Confirmation
```bash
# Verify rollback complete
curl https://atlasnexus.co.uk/api/phase1/canary/status

# Check error logs
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/logs/errors?last=10
```

---

## Quick Reference Commands

```bash
# Health check
curl https://atlasnexus.co.uk/api/phase1/health

# Full system status
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/status/full

# View canary metrics
curl https://atlasnexus.co.uk/api/phase1/canary/metrics

# Emergency kill switch
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  https://atlasnexus.co.uk/api/phase1/emergency/stop
```

---

**END OF OPERATOR SCRIPT v2.0**