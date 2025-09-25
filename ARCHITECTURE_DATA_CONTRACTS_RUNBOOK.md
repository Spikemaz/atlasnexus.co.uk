# ARCHITECTURE, DATA CONTRACTS & SYSTEM RUNBOOK
## Atlas Nexus Permutation & Securitisation Platform

---

## PART 1: SYSTEM ARCHITECTURE

### 1.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  React/Next.js Frontend - Responsive SPA with Real-time Updates │
└────────────────────────┬───────────────────────────────────────┘
                         │ HTTPS/WSS
┌────────────────────────▼───────────────────────────────────────┐
│                      API GATEWAY (Kong/Nginx)                   │
│         Rate Limiting | Auth | Load Balancing | Caching         │
└────────────────────────┬───────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                    APPLICATION SERVICES LAYER                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Project Service│  │Permutation   │  │Securitisation│         │
│  │  - CRUD      │  │  Service     │  │   Service    │         │
│  │  - Validation│  │  - Engine    │  │  - Waterfall │         │
│  │  - Derived   │  │  - Gates     │  │  - Stress    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Rating Service│  │Document      │  │Derivative    │         │
│  │  - Rules     │  │  Service     │  │  Service     │         │
│  │  - Repo Elig │  │  - Generate  │  │  - ZCIS      │         │
│  │  - Compliance│  │  - Export    │  │  - TRS       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                     WORKER PROCESSES LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Gate A Workers│  │Gate B Workers│  │Calc Workers  │         │
│  │  (6 threads) │  │  (4 threads) │  │ (8 threads)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                      DATA PERSISTENCE LAYER                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   MongoDB    │  │    Redis     │  │  Blob Store  │         │
│  │  - Projects  │  │  - Cache     │  │  - Documents │         │
│  │  - Results   │  │  - Sessions  │  │  - Reports   │         │
│  │  - GridFS    │  │  - Queues    │  │  - Exports   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Interactions

#### Request Flow Sequence
1. Client → API Gateway (authentication/validation)
2. Gateway → Application Service (business logic)
3. Service → Worker Process (heavy computation)
4. Worker → Data Layer (persistence)
5. Response propagation back through layers

#### Async Processing Pattern
```
User Request → Queue (Redis) → Worker Pool → Result Store → Notification
```

---

## PART 2: DATA CONTRACTS

### 2.1 Project Data Contract

**Object Name**: Project
**Source**: User input via web form or API
**Storage**: MongoDB projects collection

| Field | Type | Constraints | Provenance | Serialization |
|-------|------|-------------|------------|---------------|
| id | UUID | Required, Unique | System-generated | String |
| title | String | Max 255 chars | User input | UTF-8 |
| country | Enum | UK/EU/US | User selection | String |
| currency | Enum | GBP/EUR/USD/JPY | User selection | ISO 4217 |
| grossITLoad_MW | Float | 5-500 MW | User input | Number |
| PUE | Float | 0.95-1.50 | User input | Number |
| rent_per_kWh_month | Float | ≥0 | User input | Number |
| opex_pct | Float | 0-100 | User input | Percentage |
| capex_cost_per_MW | Float | >0 | User input | Number |
| capex_market_per_MW | Float | >0 | User input | Number |
| land_fees_total | Float | ≥0 | User input | Number |
| construction_start | Date | Future date | User input | ISO 8601 |
| construction_duration | Integer | 1-60 months | User input | Number |
| tenant_credit_rating | String | AAA-CCC/NR | User/derived | String |
| lease_term | Integer | 5-30 years | User input | Number |
| indexation_terms | Object | CPI linkage | User config | JSON |
| insurance_wrap | Boolean | - | User selection | Boolean |
| insurance_premium_bps | Integer | 0-500 | User/market | Number |

### 2.2 DerivedInputs Data Contract

**Object Name**: DerivedInputs
**Source**: Calculated from Project
**Storage**: Computed in memory, cached in Redis

| Field | Type | Constraints | Provenance | Serialization |
|-------|------|-------------|------------|---------------|
| netITLoad_MW | Float | >0 | grossIT/PUE | Number |
| grossIncome_annual | Float | >0 | rent × capacity × 12 | Number |
| netIncome_NOI | Float | >0 | gross × (1-OPEX%) | Number |
| totalProjectCosts | Float | >0 | capex + land + fees | Number |
| maxAF | Float | 0-1 | By rating/jurisdiction | Percentage |
| minDSCR | Float | >1 | By rating requirement | Number |
| maxTenor | Integer | Years | Min(lease, rating max) | Number |
| repoEligible | Boolean | - | Rule evaluation | Boolean |

### 2.3 LeverSet Data Contract

**Object Name**: LeverSet
**Source**: Permutation space definition
**Storage**: Generated in memory during processing

| Field | Type | Constraints | Provenance | Serialization |
|-------|------|-------------|------------|---------------|
| senior_dscr_range | Array | [1.15-1.50] | Config/rules | Float array |
| senior_coupon_range | Array | [3.0-7.0%] | Market data | Float array |
| senior_tenor_options | Array | [5,10,15,20,25] | Standard set | Int array |
| senior_amort_types | Array | Enum set | Config | String array |
| mezz_dscr_range | Array | [1.10-1.30] | Config/rules | Float array |
| mezz_coupon_range | Array | [6.0-12.0%] | Market data | Float array |
| equity_irr_targets | Array | [12-25%] | Market req | Float array |
| zcis_tenors | Array | [5Y, 10Y] | Fixed options | String array |
| trs_notional_range | Array | [5-25%] | Risk limits | Float array |

### 2.4 Permutation Data Contract

**Object Name**: Permutation
**Source**: Generated by permutation engine
**Storage**: MongoDB permutations collection + GridFS

| Field | Type | Constraints | Provenance | Serialization |
|-------|------|-------------|------------|---------------|
| id | UUID | Unique | SHA256(inputs) | String |
| project_id | UUID | FK to Project | Parent ref | String |
| seed | Integer | Deterministic | Generated | Number |
| timestamp | DateTime | - | System time | ISO 8601 |
| levers | Object | Valid ranges | Lever values | JSON |
| gate_a_result | Enum | PASS/FAIL | Gate A eval | String |
| gate_b_result | Enum | PASS/FAIL | Gate B eval | String |
| viability_tier | Enum | 5 levels | Scoring algo | String |
| day_one_value | Float | ≥0 | Calculation | Number |
| dscr_path | Array | Annual values | Waterfall calc | Float array |
| constraints_hit | Array | Rule keys | Validation | String array |
| metrics | Object | KPIs | Calculations | JSON |

### 2.5 WaterfallRun Data Contract

**Object Name**: WaterfallRun
**Source**: Waterfall calculation engine
**Storage**: Embedded in permutation results

| Field | Type | Constraints | Provenance | Serialization |
|-------|------|-------------|------------|---------------|
| period | Integer | 1-300 months | Time index | Number |
| gross_income | Float | ≥0 | Project income | Number |
| opex | Float | ≥0 | Operating cost | Number |
| senior_interest | Float | ≥0 | Debt service | Number |
| senior_principal | Float | ≥0 | Amortization | Number |
| mezz_interest | Float | ≥0 | Mezz service | Number |
| mezz_principal | Float | ≥0 | Mezz amort | Number |
| reserve_funding | Float | ≥0 | Reserve req | Number |
| cash_trap | Float | ≥0 | Trapped cash | Number |
| equity_distribution | Float | ≥0 | Residual | Number |
| ending_balance | Object | Balances | All tranches | JSON |
| dscr | Float | >0 | Coverage calc | Number |
| triggers | Array | Active flags | Covenant check | String array |

### 2.6 StressResult Data Contract

**Object Name**: StressResult
**Source**: Stress testing module
**Storage**: Embedded in permutation results

| Field | Type | Constraints | Provenance | Serialization |
|-------|------|-------------|------------|---------------|
| scenario_id | String | Unique key | Generated | String |
| scenario_type | Enum | CPI/Rate/Credit | Category | String |
| parameters | Object | Stress params | Input values | JSON |
| base_dscr | Float | >0 | Base case | Number |
| stressed_dscr | Float | >0 | Stress case | Number |
| dscr_degradation | Float | Percentage | Calculated | Percentage |
| breach_period | Integer | Months | When <1.0 | Number |
| recovery_period | Integer | Months | Back >1.0 | Number |
| rating_impact | String | Notches | Rating change | String |

### 2.7 SecuritisationPackage Data Contract

**Object Name**: SecuritisationPackage
**Source**: Document generation service
**Storage**: Blob storage with metadata in MongoDB

| Field | Type | Constraints | Provenance | Serialization |
|-------|------|-------------|------------|---------------|
| package_id | UUID | Unique | Generated | String |
| permutation_id | UUID | FK | Parent ref | String |
| generation_date | DateTime | - | System time | ISO 8601 |
| documents | Array | Doc list | Generated | JSON |
| term_sheets | Array | Per tranche | Template fill | PDF/Base64 |
| compliance_report | Object | Rules/checks | Evaluation | PDF/Base64 |
| stress_grid | Object | Scenarios | Calculation | Excel/Base64 |
| waterfall_summary | Object | Cash flows | Model output | PDF/Base64 |
| sidecar_docs | Array | Derivatives | Terms | PDF/Base64 |
| execution_checklist | Object | Tasks/timeline | Generated | PDF/Base64 |
| investor_pack | Object | Summary | Compiled | PPT/Base64 |
| metadata | Object | Package info | System | JSON |

---

## PART 3: SYSTEM RUNBOOK

### 3.1 Project Upload → Derived Inputs

**Process Name**: PROJECT_INGESTION
**Trigger**: User submits project via web form
**Duration**: 2-5 seconds

**Steps**:
1. **Validate Input** (100ms)
   - Check required fields present
   - Validate ranges and constraints
   - Verify currency/country compatibility

2. **Store Project** (200ms)
   - Generate unique project ID
   - Save to MongoDB projects collection
   - Create audit log entry

3. **Calculate Derived Inputs** (500ms)
   - Compute net IT load (gross/PUE)
   - Calculate NOI (income × (1-OPEX%))
   - Determine total project costs
   - Apply jurisdiction rules for AF/tenor

4. **Cache Results** (100ms)
   - Store derived inputs in Redis
   - Set TTL to 24 hours
   - Return project ID to user

**Error Handling**:
- Validation failure → Return specific field errors
- Database error → Retry 3x, then fail gracefully
- Calculation error → Log and return safe defaults

### 3.2 Permutation Generation → Pruning

**Process Name**: PERMUTATION_EXECUTION
**Trigger**: User clicks "Run Permutations"
**Duration**: 2-8 minutes for 250k permutations

**Steps**:
1. **Initialize Permutation Space** (1 second)
   - Load lever ranges from configuration
   - Calculate total permutation count
   - Generate deterministic seed

2. **Create Chunks** (500ms)
   - Divide into optimal batch sizes
   - Assign chunk IDs
   - Queue chunks for processing

3. **Gate A Processing** (30-60 seconds)
   - Parallel evaluation across workers
   - Check capex coverage (≥85%)
   - Validate tenor ≤ lease term
   - Prune ~60-75% of permutations

4. **Gate B Processing** (60-120 seconds)
   - Credit evaluation on survivors
   - Check DSCR ≥ rating floors
   - Validate financial ratios
   - Prune additional 40-60%

5. **Detailed Calculation** (60-180 seconds)
   - Run waterfall for viable permutations
   - Calculate day-one value
   - Perform stress testing
   - Score and tier results

6. **Result Aggregation** (5 seconds)
   - Collect results from workers
   - Deduplicate identical outcomes
   - Rank by day-one value
   - Store top 1000 in database

**Checkpointing**:
- Save progress every 5% completion
- Store checkpoint in Redis
- Enable resume from last checkpoint

### 3.3 Rating Checks → Stress Testing

**Process Name**: RISK_EVALUATION
**Trigger**: Post-permutation calculation
**Duration**: 10-30 seconds per permutation

**Steps**:
1. **Load Rule Engine** (100ms)
   - Fetch jurisdiction rules
   - Load rating requirements
   - Initialize compliance checks

2. **Apply Rating Rules** (500ms)
   - Check DSCR minimums
   - Verify tenor constraints
   - Validate amortization profile
   - Confirm insurance requirements

3. **Run Stress Scenarios** (5-10 seconds)
   - CPI stress: 0%, 1.8%, 2.5%
   - Rate shock: +100bp, +200bp
   - Tenant default: 5%, 10%
   - Combined scenarios

4. **Calculate Impact** (1 second)
   - Measure DSCR degradation
   - Identify breach periods
   - Calculate recovery time
   - Assess rating migration

5. **Generate Compliance Report** (2 seconds)
   - Document all checks performed
   - List pass/fail results
   - Identify binding constraints
   - Suggest remediation

**Quality Checks**:
- Verify all rules applied
- Cross-check calculations
- Validate against benchmarks

### 3.4 Scoring → Document Generation

**Process Name**: OUTPUT_GENERATION
**Trigger**: Permutation selection
**Duration**: 30-60 seconds

**Steps**:
1. **Calculate Viability Score** (1 second)
   - Weight day-one value (40%)
   - Weight DSCR stability (30%)
   - Weight rating achieved (20%)
   - Weight complexity (10%)

2. **Assign Tier** (100ms)
   - Diamond: Top 1% + all constraints met
   - Gold: Top 5% + key constraints met
   - Silver: Top 15% + minimum viable
   - Bronze: Top 30% + near-miss
   - Not Viable: Failed critical constraints

3. **Generate Term Sheets** (5 seconds)
   - Load templates
   - Populate fields from results
   - Apply conditional formatting
   - Generate PDF output

4. **Create Stress Grid** (3 seconds)
   - Format scenario results
   - Generate charts
   - Create sensitivity tables
   - Export to Excel

5. **Compile Execution Pack** (10 seconds)
   - Aggregate all documents
   - Create table of contents
   - Add executive summary
   - Package as ZIP

**Export Formats**:
- PDF: Term sheets, summaries
- Excel: Financial models, grids
- Word: Legal documents
- PowerPoint: Investor presentations

### 3.5 System Monitoring & Recovery

**Process Name**: SYSTEM_HEALTH
**Trigger**: Continuous monitoring
**Frequency**: Every 30 seconds

**Health Checks**:
1. **Application Health**
   - API endpoint responsiveness
   - Worker process status
   - Queue depth monitoring
   - Memory usage tracking

2. **Database Health**
   - Connection pool status
   - Query performance
   - Replication lag
   - Storage capacity

3. **Cache Health**
   - Redis connectivity
   - Cache hit ratio
   - Memory usage
   - Key expiration

**Recovery Procedures**:
1. **Worker Failure**
   - Detect via heartbeat timeout
   - Reassign work to healthy workers
   - Restart failed worker
   - Log incident

2. **Database Failure**
   - Failover to replica
   - Queue writes to Redis
   - Alert operations team
   - Initiate recovery

3. **Memory Pressure**
   - Reduce chunk sizes
   - Force garbage collection
   - Clear non-essential cache
   - Scale horizontally if needed

**Alerting Thresholds**:
- CPU > 80% for 5 minutes
- Memory > 85% sustained
- Queue depth > 10,000
- Error rate > 1%
- Response time > 2 seconds (P95)

---

## PART 4: OPERATIONAL PROCEDURES

### 4.1 Startup Sequence
```bash
1. Start MongoDB cluster
2. Initialize Redis cache
3. Start API gateway
4. Launch application services
5. Initialize worker pools
6. Verify health checks
7. Enable user traffic
```

### 4.2 Shutdown Sequence
```bash
1. Stop accepting new requests
2. Complete in-flight operations
3. Checkpoint all work
4. Flush cache to disk
5. Graceful worker shutdown
6. Stop application services
7. Stop data services
```

### 4.3 Backup Procedures
- **Frequency**: Every 6 hours
- **Retention**: 30 days
- **Method**: MongoDB dump + GridFS export
- **Verification**: Restore test weekly

### 4.4 Deployment Process
1. Blue-green deployment strategy
2. Database migrations first
3. Deploy to staging
4. Run smoke tests
5. Gradual production rollout
6. Monitor error rates
7. Quick rollback capability

---

*Document Version: 1.0*
*Last Updated: September 2025*
*Next Review: October 2025*