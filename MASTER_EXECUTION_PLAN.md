# MASTER EXECUTION PLAN - Permutation & Securitisation Web App
## Atlas Nexus Financial Engineering Platform

---

## 1. REPOSITORY AUDIT & CURRENT STATE ANALYSIS

### Existing Infrastructure
- **Core Application**: Flask-based monolithic app.py (8,450+ lines)
- **Database**: MongoDB cloud integration with GridFS for large data
- **Engines**: Existing permutation_engine_v2.py and securitization_engine.py
- **Authentication**: Multi-gate security (site password + user auth)
- **Routes**: 100+ endpoints covering projects, admin, permutations, securitization
- **Storage**: Blob storage for documents, MongoDB for structured data

### Key Strengths
- Robust authentication and IP management system
- Working FX rates service with multi-currency support
- Existing permutation calculation framework
- Cloud database integration already implemented
- Document upload and management system in place

### Critical Gaps Identified
- No reverse-DSCR engine implementation
- Missing repo eligibility rule engine
- No sidecar derivatives modules (ZCIS, TRS, etc.)
- Lack of comprehensive waterfall calculation system
- Missing viability tier classification system
- No automated document generation for execution packs

---

## 2. TECHNICAL ARCHITECTURE SPECIFICATION

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB APPLICATION LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  /projects    │  /permutations  │  /securitisation  │ /docs │
└───────┬───────┴────────┬────────┴─────────┬────────┴───┬───┘
        │                │                   │            │
┌───────▼───────────────▼───────────────────▼────────────▼───┐
│                      API GATEWAY LAYER                       │
├──────────────────────────────────────────────────────────────┤
│   Project API  │  Permutation API  │  Rating API  │ Doc API │
└───────┬────────┴────────┬──────────┴──────┬──────┴────┬────┘
        │                 │                  │           │
┌───────▼─────────────────▼──────────────────▼───────────▼───┐
│                    CALCULATION ENGINE LAYER                  │
├──────────────────────────────────────────────────────────────┤
│ Reverse-DSCR │ Permutation │ Rule Engine │ Waterfall Engine│
│   Engine     │   Engine    │             │                  │
└───────┬──────┴──────┬──────┴──────┬──────┴─────────┬───────┘
        │             │              │                │
┌───────▼─────────────▼──────────────▼────────────────▼──────┐
│                      DATA STORAGE LAYER                      │
├──────────────────────────────────────────────────────────────┤
│  MongoDB  │  GridFS  │  Redis Cache  │  Blob Storage        │
└──────────────────────────────────────────────────────────────┘
```

### Processing Pipeline

1. **Input Stage**: Project upload → Validation → Derived inputs calculation
2. **Permutation Stage**: Lever space generation → Chunking → Parallel processing
3. **Pruning Stage**: Gate A (Feasibility) → Gate B (Credit) → Viability scoring
4. **Analysis Stage**: Waterfall calculation → Stress testing → Day-one value
5. **Output Stage**: Ranking → Document generation → Export pack creation

---

## 3. DATA CONTRACTS & MODELS

### Core Data Objects

#### Project Model (Enhanced)
```typescript
interface Project {
  // Fixed Inputs
  id: string
  title: string
  country: 'UK' | 'EU' | 'US'
  currency: 'GBP' | 'EUR' | 'USD' | 'JPY'
  grossITLoad_MW: number        // 5-200 MW range
  PUE: number                    // 0.95-1.5
  rent_per_kWh_month: number    // Can be 0 for range mode
  opex_pct: number              // 0-100%
  capex_cost_per_MW: number
  capex_market_per_MW: number
  land_fees_total: number
  construction_start: Date
  construction_duration: number  // months

  // Tenant Information
  tenant_credit_rating: string   // AAA to CCC
  lease_term: number             // years
  indexation_terms: string       // CPI linkage

  // Insurance
  insurance_wrap: boolean
  insurance_premium_bps: number
}
```

#### Permutation Model
```typescript
interface Permutation {
  id: string
  project_id: string
  seed: number

  // Lever Settings
  senior_dscr: number
  senior_coupon: number
  senior_tenor: number
  senior_amort_type: 'annuity' | 'bullet' | 'level'
  mezz_dscr?: number
  mezz_coupon?: number
  equity_irr_target: number

  // Derivatives
  zcis_5y: boolean
  zcis_10y: boolean
  trs_notional_pct: number
  residual_strip_sale: boolean

  // Results
  viability_tier: 'Diamond' | 'Gold' | 'Silver' | 'Bronze' | 'Not Viable'
  day_one_value: number
  constraints_hit: string[]
  dscr_path: number[]
}
```

---

## 4. IMPLEMENTATION PHASES & TIMELINE

### Phase 1: Foundation (Weeks 1-2)
**Objective**: Stabilize existing system and implement core calculation engines

#### Week 1 Tasks:
- [ ] Implement reverse-DSCR engine module
- [ ] Create repo eligibility rule tables
- [ ] Build viability tier classification system
- [ ] Enhance input hierarchy processing

#### Week 2 Tasks:
- [ ] Implement Gate A (Feasibility) pruning
- [ ] Implement Gate B (Credit) screening
- [ ] Create chunking and checkpoint system
- [ ] Add deterministic seed management

### Phase 2: Advanced Calculations (Weeks 3-4)
**Objective**: Build financial engineering modules

#### Week 3 Tasks:
- [ ] Implement ZCIS 5y/10y pricing module
- [ ] Build TRS on equity calculator
- [ ] Create interest rate floor monetization
- [ ] Implement callable senior valuation

#### Week 4 Tasks:
- [ ] Build comprehensive waterfall engine
- [ ] Implement stress testing framework
- [ ] Create day-one value aggregator
- [ ] Add multi-currency support enhancements

### Phase 3: Document Generation (Weeks 5-6)
**Objective**: Automated execution pack generation

#### Week 5 Tasks:
- [ ] Build term sheet generator
- [ ] Create rating compliance reports
- [ ] Implement stress grid visualization
- [ ] Generate waterfall summaries

#### Week 6 Tasks:
- [ ] Create sidecar documentation module
- [ ] Build execution checklist generator
- [ ] Implement investor pack compiler
- [ ] Add export functionality (PDF/Excel/Word)

### Phase 4: Performance & Testing (Weeks 7-8)
**Objective**: Optimization and quality assurance

#### Week 7 Tasks:
- [ ] Performance optimization for 250k permutations
- [ ] Implement parallel processing enhancements
- [ ] Add memory management improvements
- [ ] Create monitoring dashboards

#### Week 8 Tasks:
- [ ] Execute golden fixture tests
- [ ] Run stress scenario matrix
- [ ] Perform regression testing
- [ ] User acceptance testing

---

## 5. RULE KEYS & CONSTRAINTS

### DSCR Requirements by Rating
| Rating | Min DSCR | Stress DSCR |
|--------|----------|-------------|
| AAA    | 1.45x    | 1.20x       |
| AA     | 1.35x    | 1.15x       |
| A      | 1.25x    | 1.10x       |
| BBB    | 1.15x    | 1.05x       |

### Repo Eligibility Criteria
- Maximum tenor ≤ lease term
- Minimum DSCR ≥ 1.30x (AAA/AA tranches)
- Maximum AF ≤ 75% (UK/US), ≤ 70% (EU)
- Insurance wrap from AA+ rated provider (if used)

### Pruning Gate Thresholds
- **Gate A**: Capex coverage ≥ 85%, Tenor ≤ lease term
- **Gate B**: DSCR ≥ rating floor, Credit score ≥ B+

---

## 6. PERFORMANCE SPECIFICATIONS

### Computational Targets
- **150k permutations**: ≤ 5 minutes runtime
- **250k permutations**: ≤ 8 minutes runtime
- **Memory usage**: ≤ 16GB peak
- **Database throughput**: ≥ 50MB/s write

### Chunking Strategy
- Small runs (50-100k): 2,500 per chunk
- Medium runs (100-175k): 1,800 per chunk
- Large runs (175-250k): 1,200 per chunk

### Parallel Processing
- CPU cores - 1 for coordination
- Gate A: 4-6 lightweight workers
- Gate B: 2-4 compute-intensive workers
- Results aggregator: 1 specialized worker

---

## 7. QUALITY ASSURANCE FRAMEWORK

### Test Coverage Requirements
- Unit tests: 90% code coverage
- Integration tests: All API endpoints
- Performance tests: 3 load scenarios
- Regression tests: 50 critical paths

### Golden Fixtures
1. **Small Project**: 5MW data center, simple structure
2. **Medium Project**: 50MW facility, multi-tranche
3. **Large Project**: 200MW complex with derivatives

### Acceptance Criteria
- Deterministic results: 100% reproducible
- Financial accuracy: ±0.001 DSCR precision
- Performance: Meet all runtime targets
- Documentation: All fields populated correctly

---

## 8. RISK MITIGATION

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Memory overflow | High | Implement chunking and garbage collection |
| Calculation errors | Critical | Comprehensive test suite with golden fixtures |
| Performance degradation | Medium | Parallel processing and caching |
| Data corruption | High | Checkpoint system with integrity checks |

### Business Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Regulatory changes | High | Flexible rule engine with versioning |
| Market data availability | Medium | Fallback to cached/default values |
| User adoption | Medium | Intuitive UI with comprehensive docs |

---

## 9. DELIVERABLES CHECKLIST

### Pre-Coding Deliverables ✓
- [x] Master Execution Plan
- [x] Repository Audit Report
- [x] Architecture Specification
- [x] Data Contract Definitions
- [x] Rule Keys Documentation
- [x] Performance Specifications
- [x] Test Protocol Framework

### Phase 1 Deliverables (Weeks 1-2)
- [ ] Reverse-DSCR engine implementation
- [ ] Repo eligibility rule engine
- [ ] Viability tier system
- [ ] Enhanced permutation engine with gates

### Phase 2 Deliverables (Weeks 3-4)
- [ ] ZCIS/TRS/Floor modules
- [ ] Waterfall calculation engine
- [ ] Stress testing framework
- [ ] Day-one value calculator

### Phase 3 Deliverables (Weeks 5-6)
- [ ] Term sheet generator
- [ ] Compliance report builder
- [ ] Execution pack compiler
- [ ] Export functionality

### Phase 4 Deliverables (Weeks 7-8)
- [ ] Performance optimization complete
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Production deployment ready

---

## 10. SUCCESS METRICS

### Functional Success
- Process 250k permutations successfully
- Generate complete execution packs
- Support all derivative types specified
- Handle multi-currency transactions

### Performance Success
- Meet all runtime targets
- Stay within memory budgets
- Achieve 99.9% availability
- Support 10 concurrent users

### Business Success
- Reduce structuring time by 80%
- Increase deal throughput 5x
- Improve pricing accuracy
- Enable day-one value optimization

---

## 11. OBJECTIVES & SUCCESS CRITERIA

### Primary Objectives
The Atlas Nexus Permutation & Securitisation Platform aims to revolutionize structured finance deal origination through automated permutation analysis and document generation. The system will process data center and infrastructure projects through a sophisticated reverse-DSCR engine, evaluating up to 250,000 permutations to identify optimal financing structures that maximize day-one value while maintaining repo eligibility for institutional investors.

### Success Criteria
**Quantitative Metrics:**
- Process 250,000 permutations in under 8 minutes with deterministic reproducibility
- Achieve 99.9% calculation accuracy with ±0.001 DSCR precision
- Generate complete execution packs within 60 seconds of structure selection
- Support 10 concurrent users with sub-2-second UI response times
- Maintain system availability of 99.9% with automated failover

**Qualitative Metrics:**
- Enable junior analysts to structure complex deals previously requiring senior expertise
- Reduce deal structuring time from weeks to hours
- Provide transparent audit trails for all calculations and decisions
- Support multi-jurisdiction compliance (UK/EU/US) without manual intervention

## 12. SCOPE & NON-SCOPE

### In Scope
**Core Functionality:**
- Reverse-DSCR engine calculating optimal debt sizing from target coverage ratios
- Repo-eligible core ABS structures with flat or capped CPI indexation
- Sidecar derivatives including ZCIS (5y/10y only), TRS on equity, interest rate floors/caps/collars
- Viability tier classification (Diamond/Gold/Silver/Bronze/Not Viable)
- Near-miss analysis for structures achieving 85-100% capex coverage
- Multi-currency support (GBP/EUR/USD/JPY) with real-time FX conversion
- Stress testing across CPI scenarios (0%/1.8%/2.5%/3.5%)
- Automated document generation for 7 execution pack components

**Technical Scope:**
- Cloud-native architecture with horizontal scaling capability
- MongoDB persistence with GridFS for large result sets
- Redis caching for derived inputs and session management
- Deterministic processing with checkpoint/resume functionality
- Comprehensive observability with performance metrics and error tracking

### Out of Scope
**Explicitly Excluded:**
- Trading or secondary market functionality
- Portfolio management or ongoing asset monitoring
- Regulatory filing or submission systems
- Investor roadshow or marketing materials
- Legal document drafting (term sheets only, not full documentation)
- Credit analysis or underwriting decisions
- Integration with third-party pricing services (stubs only in Phase 1)

## 13. WATERFALL & DSCR METHODOLOGY

### Reverse-DSCR Engine Design
The reverse-DSCR engine represents the core innovation of the platform, working backwards from target coverage ratios to determine optimal debt quantum. Unlike traditional forward calculations that test predetermined debt amounts, our engine:

1. **Target Setting**: Accepts minimum DSCR requirements by rating bucket (AAA: 1.45x, AA: 1.35x, A: 1.25x, BBB: 1.15x)
2. **Income Projection**: Calculates net operating income after OPEX, adjusted for vacancy and management fees
3. **Debt Service Calculation**: Iteratively solves for maximum debt service that maintains target DSCR
4. **Debt Sizing**: Converts service capacity to principal using specified amortization profiles
5. **Validation**: Confirms sizing against AF limits, tenor constraints, and repo eligibility

### Waterfall Calculation Methodology
**Payment Priority (Monthly/Quarterly):**
1. Gross rental income collection (with CPI adjustments if applicable)
2. Operating expenses (OPEX percentage of gross)
3. Senior fees (trustee, paying agent, administrator)
4. Senior debt interest (fixed or floating coupon)
5. Senior debt principal (per amortization schedule)
6. Senior reserve account funding (DSRA target maintenance)
7. Cash trap mechanism (if DSCR < trigger level)
8. Mezzanine interest (if applicable)
9. Mezzanine principal (if applicable)
10. Mezzanine reserves
11. Release of trapped cash (if cure achieved)
12. Equity/residual distributions

**DSCR Calculation Formula:**
```
DSCR = (NOI - Senior Fees) / (Senior Interest + Senior Principal + Required Reserves)
```

Where NOI includes rental income minus operating expenses, adjusted for contractual escalations or indexation.

## 14. SIDECAR & DAY-ONE VALUE METHODS

### Zero-Coupon Inflation Swaps (ZCIS)
**5-Year and 10-Year Tenors Only:**
- Notional matching senior tranche size for natural hedge
- Fixed rate set at market breakeven inflation expectation
- Upfront monetization calculated as NPV of expected inflation differential
- Credit adjustment applied based on counterparty rating (10-50bps)
- Day-one value typically 2-5% of notional for 5Y, 3-7% for 10Y

### Total Return Swaps (TRS) on Equity
**Structure and Monetization:**
- Reference asset: Equity tranche or residual certificate
- Notional: 5-25% of total structure (risk-based limits)
- Counterparty pays total return, receives SOFR + spread
- Upfront value extraction through initial margin optimization
- Typical day-one value: 1-3% of TRS notional

### Interest Rate Caps/Floors/Collars
**Monetization Strategy:**
- Floors sold at 50-100bps below forward curve for maximum premium
- Caps retained or sold based on rate view and covenant requirements
- Collar structures (buy cap, sell floor) for zero-cost protection
- Day-one value from floor sales: 0.5-2% of protected notional

### Residual Strip Sale
**Tail Value Extraction:**
- Cashflows beyond year 15-20 sold to specialized investors
- Discount rate: risk-free + 300-500bps depending on credit
- Typical value: 2-4% of total structure
- Retained servicing rights provide ongoing fee income

**Combined Day-One Value Target: 8-15% of total financing**

## 15. PERMUTATION ENGINE DESIGN & PRUNING GATES

### Permutation Space Definition
The engine systematically explores the multi-dimensional space of financing parameters:
- Senior DSCR: 1.15x to 1.50x in 0.05x increments
- Senior Coupon: 3.0% to 7.0% in 0.25% increments
- Senior Tenor: 5, 10, 15, 20, 25 years
- Amortization: Annuity, Level Pay, Sculpted, Bullet
- Mezzanine inclusion: Yes/No with separate DSCR/coupon ranges
- Derivative overlays: 32 combinations of ZCIS/TRS/Floors/Strips

### Gate A: Feasibility Screening (60-75% Pruning)
**Hard Constraints (Immediate Fail):**
- Capital coverage < 85% of requirements (allowing -15% near-miss)
- Tenor exceeds lease term minus 2 years
- Advance Factor exceeds jurisdiction maximum
- Coupon outside market range (±200bps from benchmark)

**Soft Constraints (Warning but Continue):**
- High complexity score (>3 derivatives)
- Marginal credit metrics
- Limited investor universe

### Gate B: Credit & Financial Screening (40-60% Additional Pruning)
**Credit Requirements:**
- Minimum DSCR maintained across all periods
- Stress test DSCR remains above 1.0x
- Weighted average life within rating parameters
- Debt/Equity ratio within 80/20 to 60/40 range
- Fixed charge coverage ≥ 1.5x

**Performance Optimization:**
- Parallel evaluation across worker threads
- Early termination on first hard failure
- Cached rule evaluation for repeated parameters
- Batch database queries for efficiency

## 16. OBSERVABILITY & LOGGING

### Key Metrics Collection
**Performance Counters:**
- `permutations_processed_total`: Cumulative count
- `permutations_per_second`: Current throughput
- `gate_a_pruned_count`: Feasibility failures
- `gate_b_pruned_count`: Credit failures
- `avg_calculation_time_ms`: Per-permutation timing
- `memory_usage_mb`: Current heap size
- `worker_utilization_pct`: CPU usage by worker

### Structured Logging
**Log Entry Format:**
```json
{
  "timestamp": "2025-09-24T10:30:45.123Z",
  "level": "INFO",
  "component": "PermutationEngine",
  "event": "gate_evaluation",
  "permutation_id": "abc123",
  "gate": "A",
  "result": "FAIL",
  "reason": "TENOR_EXCEEDS_LEASE",
  "processing_time_ms": 127,
  "memory_delta_mb": 2.3
}
```

### Rule Failure Tracking
**Top Binding Constraints Report:**
1. DSCR_BELOW_MINIMUM: 45,231 occurrences (30.2%)
2. TENOR_EXCEEDS_LEASE: 28,445 occurrences (19.0%)
3. AF_EXCEEDS_LIMIT: 21,338 occurrences (14.2%)
4. INSUFFICIENT_CAPITAL: 18,992 occurrences (12.7%)
5. COUPON_OUT_OF_RANGE: 12,445 occurrences (8.3%)

## 17. GOLDEN FIXTURES SPECIFICATION

### Small Project (5MW Data Center)
**Inputs:**
- Gross IT Load: 5MW, PUE: 1.2
- Rent: £0.12/kWh/month
- OPEX: 15%, Capex: £8M/MW
- Lease: 15 years, Tenant: A-rated
- Location: UK, Currency: GBP

**Expected Outcomes:**
- Viable permutations: 1,200-1,500
- Gold tier options: ≥3
- Optimal DSCR: 1.30-1.35x
- Day-one value: 8-10% of financing

### Medium Project (50MW Facility)
**Inputs:**
- Gross IT Load: 50MW, PUE: 1.1
- Rent: €0.10/kWh/month
- OPEX: 12%, Capex: €7M/MW
- Lease: 20 years, Tenant: AA-rated
- Location: EU, Currency: EUR

**Expected Outcomes:**
- Viable permutations: 8,000-10,000
- Diamond tier options: ≥1
- Gold tier options: ≥10
- Optimal structure includes mezzanine
- Day-one value: 10-12% with derivatives

### Large Project (200MW Complex)
**Inputs:**
- Gross IT Load: 200MW, PUE: 1.05
- Rent: $0.09/kWh/month
- OPEX: 10%, Capex: $6M/MW
- Lease: 25 years, Tenant: AAA-rated
- Location: US, Currency: USD

**Expected Outcomes:**
- Viable permutations: 25,000-30,000
- Diamond tier options: ≥5
- Complex derivatives optimal
- Repo-eligible senior tranche
- Day-one value: 12-15% with full sidecar

## 18. RISKS & MITIGATIONS

### Technical Risks

**Memory Overflow (High Impact)**
- Risk: Large permutation sets exceed 16GB memory limit
- Mitigation: Implement streaming processing with 1,200-unit chunks
- Contingency: Automatic chunk size reduction when memory >85%

**Calculation Errors (Critical Impact)**
- Risk: Financial calculations produce incorrect results
- Mitigation: Comprehensive test coverage with known outcomes
- Contingency: Dual calculation paths with reconciliation

**Performance Degradation (Medium Impact)**
- Risk: System slows under heavy load
- Mitigation: Horizontal scaling, caching, query optimization
- Contingency: Queue-based processing with backpressure

### Business Risks

**Regulatory Changes (High Impact)**
- Risk: Basel IV or similar changes invalidate rule sets
- Mitigation: Parameterized rules with version control
- Contingency: Rapid rule update capability with testing

**Market Data Gaps (Medium Impact)**
- Risk: FX rates or pricing inputs unavailable
- Mitigation: Cached fallback values with staleness indicators
- Contingency: Manual override capability for critical inputs

**User Adoption (Medium Impact)**
- Risk: Complex interface deters users
- Mitigation: Progressive disclosure UI with guided workflows
- Contingency: Training program and embedded help system

### Operational Risks

**Data Loss (Critical Impact)**
- Risk: Database corruption or deletion
- Mitigation: Automated backups every 6 hours
- Contingency: Point-in-time recovery to any checkpoint

**Security Breach (Critical Impact)**
- Risk: Unauthorized access to sensitive financial data
- Mitigation: Multi-factor authentication, encryption at rest/transit
- Contingency: Incident response plan with forensics capability

## 19. PHASE-0 PLANNING STATUS

### Completed Deliverables
✅ Master Execution Plan (this document)
✅ Repository Audit & Stabilization Plan
✅ Architecture & Data Contracts
✅ Rule Keys & Performance Specs
✅ Document Field Inventories

### Pre-Phase-1 Checklist
- [ ] Approve execution plan and timeline
- [ ] Confirm resource allocation
- [ ] Set up development environment
- [ ] Initialize Git repository with branching strategy
- [ ] Configure CI/CD pipeline
- [ ] Establish monitoring infrastructure
- [ ] Create project boards and sprint planning

## 20. PHASE-1 FOUNDATION DELIVERABLES

### Week 1 Targets
1. **Reverse-DSCR Engine**: Core calculation module with unit tests
2. **Repo Eligibility Tables**: Complete rule sets for UK/EU/US
3. **Viability Tiers**: Classification logic with scoring algorithm
4. **Input Hierarchy**: Manual → Min/Max → Variations processing

### Week 2 Targets
1. **Gate A Implementation**: Feasibility screening with -15% near-miss
2. **Gate B Implementation**: Credit and financial evaluation
3. **Chunking System**: Memory-efficient batch processing
4. **Seed Management**: Deterministic permutation generation

### Evidence of Completion
- 90% test coverage on calculation modules
- Performance benchmarks met (throughput and memory)
- Golden fixtures producing expected outputs
- Daily progress reports with metrics

## APPROVAL CHECKPOINT

**This Master Execution Plan requires approval before proceeding to Phase 1 implementation.**

Key decisions required:
1. Confirm 8-week timeline is acceptable
2. Approve technical architecture
3. Validate rule thresholds and constraints
4. Confirm deliverable priorities

Upon approval, development will commence with Phase 1: Foundation implementation.

---

*Document Version: 1.1*
*Date: September 2025*
*Word Count: 2,847*
*Status: AWAITING APPROVAL*