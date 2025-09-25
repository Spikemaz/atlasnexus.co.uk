# RULE KEYS, PERMUTATION GATES & PERFORMANCE SPECIFICATIONS
## Atlas Nexus Financial Engineering Platform

---

## PART 1: COMPREHENSIVE RULE KEYS

### 1.1 DSCR Rule Keys

#### RK-DSCR-001: Minimum DSCR by Rating
```
Rule Key: DSCR_MIN_{RATING}_{JURISDICTION}
Priority: 1 (CRITICAL)
Override: Not Permitted

Thresholds:
┌─────────┬────────┬────────┬────────┬─────────┐
│ Rating  │   UK   │   EU   │   US   │ Global  │
├─────────┼────────┼────────┼────────┼─────────┤
│   AAA   │  1.45x │  1.50x │  1.40x │  1.50x  │
│   AA    │  1.35x │  1.40x │  1.30x │  1.40x  │
│   A     │  1.25x │  1.30x │  1.20x │  1.30x  │
│   BBB   │  1.15x │  1.20x │  1.10x │  1.20x  │
│   BB    │  1.10x │  1.15x │  1.05x │  1.15x  │
└─────────┴────────┴────────┴────────┴─────────┘

Pass Criteria: DSCR ≥ Threshold for all periods
Fail Action: Reject structure
```

#### RK-DSCR-002: Stress Test DSCR
```
Rule Key: DSCR_STRESS_{SCENARIO}
Priority: 2 (HIGH)

Stress Scenarios:
- Base Case: As calculated
- CPI 0%: Remove all indexation
- CPI 2.5%: Apply 2.5% annual increase
- Rate +200bp: Increase funding cost
- Combined: CPI 0% + Rate +200bp

Minimum Thresholds:
- AAA: Never below 1.20x
- AA: Never below 1.15x
- A: Never below 1.10x
- BBB: Never below 1.05x

Pass Criteria: Stress DSCR ≥ Minimum
Fail Action: Downgrade rating or reject
```

### 1.2 Tenor & Amortization Rule Keys

#### RK-TENOR-001: Maximum Tenor Limits
```
Rule Key: TENOR_MAX_{RATING}_{ASSET_TYPE}
Priority: 1 (CRITICAL)

Maximum Allowed Tenor (Years):
┌─────────┬──────────┬───────────┬──────────┐
│ Rating  │ Data Ctr │ Renewable │ Infra    │
├─────────┼──────────┼───────────┼──────────┤
│   AAA   │    25    │     30    │    30    │
│   AA    │    22    │     27    │    27    │
│   A     │    20    │     25    │    25    │
│   BBB   │    18    │     22    │    20    │
└─────────┴──────────┴───────────┴──────────┘

Additional Constraint: Tenor ≤ Lease Term - 2 years
```

#### RK-AMORT-001: Amortization Profile Requirements
```
Rule Key: AMORT_PROFILE_{RATING}
Priority: 2 (HIGH)

Minimum Annual Amortization:
- AAA: 3.0% of original principal
- AA: 2.5% of original principal
- A: 2.0% of original principal
- BBB: 1.5% of original principal

Prohibited Structures:
- AAA/AA: No bullet payments >10%
- A: No bullet payments >15%
- BBB: No bullet payments >20%
```

### 1.3 Repo Eligibility Rule Keys

#### RK-REPO-001: Central Bank Eligibility
```
Rule Key: REPO_ELIGIBLE_{CENTRAL_BANK}
Priority: 1 (CRITICAL)

ECB Requirements:
- Rating ≥ A-
- Tenor ≤ 30 years
- AF ≤ 70%
- EUR denominated
- True sale structure

Bank of England Requirements:
- Rating ≥ BBB
- Tenor ≤ 25 years
- AF ≤ 75%
- GBP denominated
- UK law governed

Federal Reserve Requirements:
- Rating ≥ AA-
- Tenor ≤ 30 years
- AF ≤ 80%
- USD denominated
- Rule 144A eligible
```

#### RK-REPO-002: Haircut Schedule
```
Rule Key: REPO_HAIRCUT_{RATING}_{TENOR}
Priority: 3 (MEDIUM)

Haircut Matrix (%):
┌─────────┬────────┬────────┬────────┐
│ Rating  │ 0-10Y  │ 10-20Y │ 20-30Y │
├─────────┼────────┼────────┼────────┤
│   AAA   │   2%   │   5%   │   8%   │
│   AA    │   5%   │   8%   │   12%  │
│   A     │   8%   │   12%  │   18%  │
│   BBB   │   12%  │   18%  │   N/A  │
└─────────┴────────┴────────┴────────┘
```

### 1.4 Insurance Wrap Rule Keys

#### RK-WRAP-001: Insurance Enhancement Rules
```
Rule Key: WRAP_ENHANCEMENT_{INSURER_RATING}
Priority: 2 (HIGH)

Enhancement Matrix:
┌──────────────┬─────────────┬──────────────┐
│ Bond Target  │ Min Insurer │ DSCR Relief  │
├──────────────┼─────────────┼──────────────┤
│     AAA      │    AA+      │    -0.20x    │
│     AA       │    AA       │    -0.15x    │
│     A        │    A+       │    -0.10x    │
│     BBB      │    A        │    -0.05x    │
└──────────────┴─────────────┴──────────────┘

Cost (basis points annually):
- AAA wrap: 15-25 bps
- AA wrap: 10-20 bps
- A wrap: 8-15 bps
```

### 1.5 Concentration Rule Keys

#### RK-CONC-001: Single Tenant Concentration
```
Rule Key: TENANT_CONC_MAX_{RATING}
Priority: 2 (HIGH)

Maximum Single Tenant Exposure:
- AAA: 40% (if tenant ≥ AA)
- AA: 35% (if tenant ≥ A)
- A: 30% (if tenant ≥ BBB)
- BBB: 25% (any tenant)

Breach Action: Rating cap or credit enhancement
```

#### RK-CONC-002: Geographic Concentration
```
Rule Key: GEO_CONC_MAX_{REGION}
Priority: 3 (MEDIUM)

Maximum Regional Exposure:
- Single Country: 80%
- Single City: 50%
- Single Site: 30%

Exception: 100% allowed if sovereign ≥ AA
```

---

## PART 2: PERMUTATION GATE SPECIFICATIONS

### 2.1 Gate A: Feasibility Screening

#### Gate A Processing Logic
```
GATE_A_FEASIBILITY_CHECK {

  Input: Raw Permutation
  Output: PASS/FAIL with reason code
  Processing Time: 0.1-0.2 seconds
  Expected Pass Rate: 25-40%

  Checks Performed:

  1. CAPEX_COVERAGE_CHECK:
     - Total Funding = Senior + Mezz + Equity
     - Required = CAPEX + Land + Fees
     - PASS if Funding ≥ Required × 0.85
     - FAIL if Funding < Required × 0.85
     - Reason: "INSUFFICIENT_CAPITAL"

  2. TENOR_VALIDITY_CHECK:
     - Max Tenor = Min(Lease Term - 2, Rating Max)
     - PASS if Chosen Tenor ≤ Max Tenor
     - FAIL if Chosen Tenor > Max Tenor
     - Reason: "TENOR_EXCEEDS_LIMIT"

  3. AF_BOUNDS_CHECK:
     - Max AF = Rating_AF × Jurisdiction_Modifier
     - PASS if Calculated AF ≤ Max AF
     - FAIL if Calculated AF > Max AF
     - Reason: "ADVANCE_FACTOR_BREACH"

  4. COUPON_BOUNDS_CHECK:
     - Min Coupon = Risk_Free + Credit_Spread_Floor
     - Max Coupon = Risk_Free + Credit_Spread_Cap
     - PASS if Min ≤ Coupon ≤ Max
     - FAIL otherwise
     - Reason: "COUPON_OUT_OF_MARKET"

  5. BASIC_MATH_CHECK:
     - Verify Senior ≤ Total Project Cost
     - Verify Mezz ≤ (Total - Senior) × 0.5
     - Verify sum of tranches = 100%
     - FAIL if mathematical inconsistency
     - Reason: "MATH_ERROR"
}
```

#### Gate A Performance Metrics
```
Throughput Targets:
- Single permutation: <200ms
- Batch (1000): <5 seconds
- Full chunk (2500): <12 seconds

Resource Usage:
- CPU: 5-10% per worker
- Memory: 50MB per worker
- I/O: Minimal (memory only)
```

### 2.2 Gate B: Credit & Financial Screening

#### Gate B Processing Logic
```
GATE_B_CREDIT_CHECK {

  Input: Gate A survivors
  Output: PASS/FAIL with scoring
  Processing Time: 0.3-0.5 seconds
  Expected Pass Rate: 40-60% of Gate A

  Checks Performed:

  1. DSCR_CALCULATION:
     - Calculate period-by-period DSCR
     - Find minimum, average, and tail DSCR
     - PASS if Min DSCR ≥ Rating Requirement
     - FAIL if any period < Floor
     - Score: Min DSCR × 100

  2. CREDIT_RATING_CHECK:
     - Calculate weighted average rating
     - Apply tenant credit adjustments
     - PASS if achieves target rating
     - FAIL if >2 notches below target
     - Score: Rating_Numeric × 10

  3. DEBT_METRICS_CHECK:
     - Debt/Equity ratio ≤ 80/20
     - Interest Coverage ≥ 2.0x
     - Fixed Charge Coverage ≥ 1.5x
     - PASS if all metrics satisfied
     - Score: Average_Coverage × 50

  4. STRESS_RESILIENCE_CHECK:
     - Quick stress: CPI 0% scenario
     - Quick stress: Rate +100bp
     - PASS if maintains 1.0x DSCR
     - FAIL if breaches in year 1-3
     - Score: Stress_DSCR × 75

  5. COMPLEXITY_CHECK:
     - Count derivatives used
     - Assess structure complexity
     - PASS if complexity ≤ Medium
     - WARN if High complexity
     - Score: (10 - Complexity) × 5
}
```

#### Gate B Performance Metrics
```
Throughput Targets:
- Single permutation: <500ms
- Batch (1000): <20 seconds
- Full chunk (1000): <30 seconds

Resource Usage:
- CPU: 20-30% per worker
- Memory: 150MB per worker
- I/O: Database reads for rules
```

---

## PART 3: PERFORMANCE SPECIFICATIONS

### 3.1 System Performance Requirements

#### Overall Performance Targets
```
┌─────────────────────┬─────────────┬─────────────┐
│ Permutation Count   │ Target Time │ Max Memory  │
├─────────────────────┼─────────────┼─────────────┤
│ 10,000             │ 30 seconds  │ 2 GB        │
│ 50,000             │ 2 minutes   │ 4 GB        │
│ 100,000            │ 4 minutes   │ 8 GB        │
│ 150,000            │ 5 minutes   │ 12 GB       │
│ 250,000            │ 8 minutes   │ 16 GB       │
└─────────────────────┴─────────────┴─────────────┘

Concurrent Users: 10
Response Time (P95): <2 seconds for UI operations
Availability Target: 99.9% uptime
```

### 3.2 Processing Pipeline Performance

#### Stage-by-Stage Performance
```
1. Input Processing (5% of time)
   - Project validation: <500ms
   - Derived calculation: <1s
   - Lever space setup: <2s

2. Permutation Generation (10% of time)
   - Chunk creation: <1s per 10k
   - Queue setup: <500ms
   - Seed generation: <100ms

3. Gate A Processing (20% of time)
   - Throughput: 5000/second
   - CPU usage: 40% total
   - Memory: 2GB steady

4. Gate B Processing (35% of time)
   - Throughput: 2000/second
   - CPU usage: 60% total
   - Memory: 4GB steady

5. Detailed Calculation (25% of time)
   - Waterfall: 100/second
   - Stress test: 50/second
   - Memory: 6GB peak

6. Results & Output (5% of time)
   - Aggregation: <5s
   - Ranking: <2s
   - Storage: <10s
```

### 3.3 Database Performance

#### MongoDB Performance Requirements
```
Write Performance:
- Bulk inserts: 10,000 docs/second
- Single document: <50ms
- GridFS large file: 50MB/second

Read Performance:
- Simple query: <20ms
- Aggregation: <500ms
- Full scan: <5 seconds

Index Requirements:
- project_id + timestamp (compound)
- viability_tier + day_one_value (compound)
- seed (unique)
```

#### Redis Cache Performance
```
Cache Operations:
- GET: <1ms
- SET: <2ms
- Bulk operations: <10ms

Memory Allocation:
- Derived inputs: 500MB
- Session data: 200MB
- Queue data: 300MB
- Results cache: 1GB
```

### 3.4 Optimization Strategies

#### Memory Optimization
```
Techniques Applied:
1. Lazy Loading:
   - Load rules on demand
   - Stream large results
   - Paginate outputs

2. Garbage Collection:
   - Force GC every 50 chunks
   - Clear unused references
   - Compact memory pools

3. Data Compression:
   - Compress checkpoint files (LZ4)
   - Compress GridFS documents
   - Use binary protocols

Memory Savings: 30-40% reduction
```

#### CPU Optimization
```
Techniques Applied:
1. Vectorization:
   - Batch DSCR calculations
   - Array operations via NumPy
   - SIMD instructions

2. Parallelization:
   - Multi-process workers
   - Async I/O operations
   - Work stealing queues

3. Algorithm Optimization:
   - Early termination
   - Memoization of results
   - Branch prediction hints

Performance Gain: 2-3x throughput
```

#### I/O Optimization
```
Techniques Applied:
1. Batching:
   - Bulk database writes
   - Aggregate reads
   - Pooled connections

2. Caching:
   - Redis for hot data
   - Local memory cache
   - CDN for documents

3. Async Operations:
   - Non-blocking I/O
   - Event-driven updates
   - Background processing

Latency Reduction: 50-60%
```

### 3.5 Scalability Plan

#### Horizontal Scaling
```
Current: Single Server (8 cores, 32GB RAM)
- Capacity: 250k permutations
- Users: 10 concurrent
- Throughput: 100 requests/second

Phase 1: Load Balanced (2 servers)
- Capacity: 500k permutations
- Users: 25 concurrent
- Throughput: 200 requests/second

Phase 2: Distributed (4 servers + queue)
- Capacity: 1M permutations
- Users: 50 concurrent
- Throughput: 500 requests/second

Phase 3: Cloud Native (Auto-scaling)
- Capacity: Unlimited
- Users: 100+ concurrent
- Throughput: 1000+ requests/second
```

### 3.6 Monitoring & Alerting

#### Key Performance Indicators
```
Application Metrics:
- Permutations/second processed
- Gate A/B pass rates
- Average calculation time
- Queue depth
- Error rate

System Metrics:
- CPU utilization by service
- Memory usage and GC frequency
- Disk I/O and latency
- Network throughput
- Database connection pool

Business Metrics:
- Projects processed/day
- Average permutation count
- Success rate
- User session duration
- Feature usage patterns

Alert Thresholds:
- CPU > 80% for 5 minutes
- Memory > 85% sustained
- Queue depth > 10,000
- Error rate > 1%
- Response time > 2s (P95)
```

---

## PART 4: IMPLEMENTATION PRIORITIES

### Phase 1: Core Performance (Week 1)
1. Implement chunking system
2. Set up worker pools
3. Create Gate A/B logic
4. Add basic monitoring

### Phase 2: Optimization (Week 2)
1. Add caching layer
2. Implement compression
3. Optimize algorithms
4. Add checkpointing

### Phase 3: Scaling (Week 3)
1. Add load balancing
2. Implement queuing
3. Add horizontal scaling
4. Complete monitoring

---

*Document Version: 1.0*
*Performance Baseline: September 2025*
*Next Review: October 2025*