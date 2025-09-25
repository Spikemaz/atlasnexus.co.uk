# Phase-1: First 24 Hours Post-Canary Playbook

**Start Time:** ___________ **Operator:** ___________

## 📋 PREREQUISITES
- [ ] Initial 1% canary successful (30 min, no issues)
- [ ] GO decision documented
- [ ] Rollback procedure validated
- [ ] On-call rotation confirmed

---

## ⏰ HOUR 0-2: WIDEN TO 25% ALLOWLIST

### T+0:00 - Expand Allowlist
```bash
# Add beta users to allowlist (25% of admin accounts)
curl -X POST https://atlasnexus.co.uk/api/admin/allowlist/update \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SESSION" \
  -d '{
    "allowlist": ["beta1@example.com", "beta2@example.com", ...],
    "percentage": 25,
    "ips": ["10.0.1.0/24", "CI_EGRESS_IP"]
  }'
```

### T+0:15 - Enable ReverseDSCR
```bash
curl -X POST https://atlasnexus.co.uk/api/admin/flags/update \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SESSION" \
  -H "If-Match: CURRENT_VERSION" \
  -d '{"updates": {"reverse_dscr_engine": true}}'
```

### T+0:30 - Validation Run
```bash
# Run Medium fixture with ReverseDSCR
curl -X POST https://atlasnexus.co.uk/api/phase1/run \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SESSION" \
  -d '{
    "fixture": "medium",
    "seed": 424242,
    "ruleset_version": "v1.0",
    "features": ["reverse_dscr_engine"]
  }'
```

**Success Criteria:**
- [ ] Throughput >300 perms/sec
- [ ] P95 <10ms
- [ ] DSCR calculations match expected ranges
- [ ] No errors in ReverseDSCR module

### T+1:00 - Synthetic Transaction Setup
```bash
# Start synthetic monitor (runs every 5 min)
curl -X POST https://atlasnexus.co.uk/api/admin/synthetic/start \
  -H "Cookie: session=SESSION" \
  -d '{
    "interval": 300,
    "actions": ["validate", "derived", "cardinality"],
    "alert_threshold": {"error_rate": 0.01, "p95_ms": 2000}
  }'
```

### T+2:00 - Health Check
- [ ] Dashboard check: Error <0.5%, P95 <1.5s
- [ ] Memory stable (±50MB from baseline)
- [ ] Synthetic transactions passing
- [ ] No alerts triggered

---

## ⏰ HOUR 2-6: ENABLE GATES A/B

### T+2:00 - Enable GatesAB
```bash
curl -X POST https://atlasnexus.co.uk/api/admin/flags/update \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SESSION" \
  -H "If-Match: CURRENT_VERSION" \
  -d '{"updates": {"gates_ab": true}}'
```

### T+2:30 - Golden Fixtures with Gates
```bash
# Run all fixtures with Gates enabled
for fixture in small medium large; do
  curl -X POST https://atlasnexus.co.uk/api/phase1/run \
    -H "Content-Type: application/json" \
    -H "Cookie: session=SESSION" \
    -d "{
      \"fixture\": \"$fixture\",
      \"seed\": 424242,
      \"features\": [\"gates_ab\", \"reverse_dscr_engine\"]
    }"
done
```

**Expected Prune Rates:**
| Fixture | Gate A | Gate B |
|---------|--------|--------|
| Small   | 32-35% | 20-23% |
| Medium  | 36-39% | 24-27% |
| Large   | 35-38% | 23-26% |

### T+4:00 - Top Binding Constraints Check
```bash
curl -X GET https://atlasnexus.co.uk/api/phase1/constraints \
  -H "Cookie: session=SESSION"
```

**Expected Top 5:**
1. MIN_DSCR_SENIOR (35-40%)
2. MAX_LTV (25-30%)
3. MIN_COVERAGE (15-20%)
4. CONCENTRATION_LIMIT (10-12%)
5. REPO_ELIGIBILITY (5-8%)

### T+6:00 - Checkpoint
- [ ] Gates pruning within expected ranges
- [ ] Near-miss capture working (fix hints logged)
- [ ] No performance degradation
- [ ] Memory usage <+100MB from baseline

---

## ⏰ HOUR 6-12: FULL FEATURE ACTIVATION

### T+6:00 - Enable DocsExports
```bash
curl -X POST https://atlasnexus.co.uk/api/admin/flags/update \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SESSION" \
  -H "If-Match: CURRENT_VERSION" \
  -d '{"updates": {"docs_exports": true}}'
```

### T+6:30 - Test Document Generation
```bash
# Export top structure
curl -X GET https://atlasnexus.co.uk/api/phase1/securitisation/export/1 \
  -H "Cookie: session=SESSION" \
  -o structure_1_export.json

# Generate term sheet
curl -X POST https://atlasnexus.co.uk/api/phase1/documents/term-sheet \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SESSION" \
  -d '{"structure_rank": 1}'
```

### T+8:00 - Stress Test (25% traffic)
```bash
# Run parallel fixtures to simulate load
for i in {1..5}; do
  curl -X POST https://atlasnexus.co.uk/api/phase1/run \
    -H "Cookie: session=SESSION" \
    -d '{"fixture": "medium", "async": true}' &
done
```

**Monitor:**
- [ ] Concurrent execution handling
- [ ] Queue depth <100
- [ ] P95 <15ms under load
- [ ] No timeout errors

### T+10:00 - Data Validation
```bash
# Compare results across runs
curl -X POST https://atlasnexus.co.uk/api/phase1/validate/consistency \
  -H "Cookie: session=SESSION" \
  -d '{
    "seed": 424242,
    "runs": 3,
    "compare": ["top_20", "prune_stats", "stress_dscr"]
  }'
```

**Expected:** 100% consistency across identical seed runs

### T+12:00 - Major Checkpoint
- [ ] All Phase-1 features enabled
- [ ] 25% traffic stable for 10+ hours
- [ ] No memory leaks detected
- [ ] Error rate <0.1%
- [ ] P95 consistently <2s

---

## ⏰ HOUR 12-24: MONITORING & OPTIMIZATION

### T+12:00 - Rotate SECRET_KEY
```bash
# Generate new key
NEW_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Update via deployment pipeline
echo "SECRET_KEY=$NEW_KEY" >> .env.new

# Graceful restart
kill -HUP $(cat gunicorn.pid)
```

**Verify:** Sessions invalidated, users must re-authenticate

### T+14:00 - Backup Validation
```bash
# Trigger Redis snapshot
redis-cli BGSAVE

# Verify backup
aws s3 ls s3://backups/redis/latest/

# Test restore to staging
./scripts/restore_redis_staging.sh
```

### T+16:00 - Performance Tuning
```bash
# Analyze slow queries
curl -X GET https://atlasnexus.co.uk/api/admin/metrics/slow-queries \
  -H "Cookie: session=SESSION"

# Check cache hit rates
curl -X GET https://atlasnexus.co.uk/api/admin/metrics/cache \
  -H "Cookie: session=SESSION"
```

**Optimize if:**
- Cache hit rate <80%
- Any query >100ms P95
- Memory usage growing >10MB/hour

### T+18:00 - Prepare for 100% Rollout
```bash
# Generate rollout plan
curl -X POST https://atlasnexus.co.uk/api/admin/rollout/plan \
  -H "Cookie: session=SESSION" \
  -d '{
    "target": 100,
    "admin_only": true,
    "eta": "T+24:00"
  }'
```

### T+20:00 - Final Validation Suite
```bash
# Run full test suite
./scripts/run_production_tests.sh

# Verify all rules
curl -X POST https://atlasnexus.co.uk/api/phase1/rules/validate \
  -H "Cookie: session=SESSION" \
  -d '{
    "ruleset": "v1.0",
    "checks": ["dscr_floors", "tenor_limits", "wal_bounds", "af_bands"]
  }'
```

### T+22:00 - Pre-100% Checklist
- [ ] 24 hours at 25% with no major issues
- [ ] All features tested and stable
- [ ] Rollback procedure re-validated
- [ ] On-call team briefed
- [ ] Stakeholders notified

### T+24:00 - GO/NO-GO for 100% Admin
```bash
# Check final metrics
curl -X GET https://atlasnexus.co.uk/api/phase1/metrics/summary \
  -H "Cookie: session=SESSION"
```

**Decision Criteria:**
- Error rate <0.1% over 24h
- P95 <2s consistently
- No unresolved issues
- All validations passing

**If GO:**
```bash
curl -X POST https://atlasnexus.co.uk/api/admin/rollout/execute \
  -H "Cookie: session=SESSION" \
  -d '{"target": 100, "admin_only": true}'
```

**If NO-GO:**
- Document issues
- Keep at 25% for another 24h
- Schedule engineering review

---

## 📊 KEY METRICS TO TRACK

### Every Hour
- Error rate (target <0.1%)
- P95 response time (target <2s)
- Memory usage (stable ±100MB)
- Active sessions count
- Feature flag versions

### Every 4 Hours
- Gate A/B prune rates
- Top binding constraints
- Near-miss counts
- Cache hit rates
- Queue depths

### Every 8 Hours
- Consistency validation
- Backup success
- Synthetic transaction summary
- Audit log review

---

## 🚨 ROLLBACK TRIGGERS

**Immediate Rollback If:**
- Error rate >1% for 10 minutes
- P95 >5s for 10 minutes
- Memory leak >100MB/hour
- Data inconsistency detected
- Security incident

**Command:**
```bash
curl -X POST https://atlasnexus.co.uk/api/admin/flags/rollback \
  -H "Cookie: session=SESSION"
```

---

## 📞 ESCALATION MATRIX

| Hour | Primary | Backup | Escalation |
|------|---------|--------|------------|
| 0-6  | DevOps Lead | SRE On-call | CTO |
| 6-12 | Tech Lead | DevOps Lead | Product Owner |
| 12-18 | SRE On-call | Tech Lead | CTO |
| 18-24 | DevOps Lead | SRE On-call | Product Owner |

---

## ✅ T+24:00 SUCCESS CRITERIA

- [ ] 100% admin rollout complete
- [ ] All Phase-1 features operational
- [ ] No rollbacks required
- [ ] Metrics within SLO
- [ ] Ready for public beta planning

**Sign-off:**
- Technical Lead: ___________ Time: ___________
- Product Owner: ___________ Time: ___________
- DevOps Lead: ___________ Time: ___________

---

**Next:** Schedule public beta (0% → 1% → 10% → 50% → 100%) over 7 days