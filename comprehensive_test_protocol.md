# Atlas Forge - Comprehensive Test Protocol & Performance Benchmarks

## Executive Summary

This document defines acceptance tests and performance benchmarks for the Atlas Forge permutation engine, a financial modeling system for data center securitization. The protocol ensures reliability, performance, and reproducibility across 150,000+ permutation scenarios.

## 1. Golden Fixtures Design

### 1.1 Small Project Fixture (5MW Data Center)
**Profile:** Simple single-tenant structure, baseline case
```json
{
  "fixture_id": "SMALL_5MW_BASELINE",
  "project_params": {
    "GrossITLoad_02": 5.0,
    "PUE_03": 1.25,
    "CapexCostPrice_04": 6500000,
    "CapexMarketRate_05": 8000000,
    "LandPurchaseFees_06": 5000000,
    "GrossMonthlyRent_07": 125000,
    "OPEX_08": 20.0,
    "LeaseTermYears_22": 15,
    "Currency_01": "GBP"
  },
  "expected_outputs": {
    "TotalProjectMarketCosts_15": 45000000,
    "TotalProjectInternalCosts_16": 37500000,
    "GrossIncome_10": 1500000,
    "NetIncome_11": 1200000,
    "max_senior_notional_range": [15000000, 25000000],
    "target_dscr_achievable": true,
    "rating_aaa_feasible": true,
    "permutation_count_expected": [500, 1500]
  },
  "validation_thresholds": {
    "dscr_min_floor": 1.25,
    "senior_coverage_ratio": 0.65,
    "equity_irr_min": 12.0
  }
}
```

### 1.2 Medium Project Fixture (50MW Multi-Tranche)
**Profile:** Multi-tenant complex with mezzanine layer
```json
{
  "fixture_id": "MEDIUM_50MW_MULTITRANCHE",
  "project_params": {
    "GrossITLoad_02": 50.0,
    "PUE_03": 1.30,
    "CapexCostPrice_04": 7000000,
    "CapexMarketRate_05": 8500000,
    "LandPurchaseFees_06": 25000000,
    "GrossMonthlyRent_07": 1250000,
    "OPEX_08": 25.0,
    "LeaseTermYears_22": 25,
    "Currency_01": "GBP"
  },
  "structure": {
    "senior_tranche": true,
    "mezzanine_tranche": true,
    "equity_component": true,
    "derivatives_sidecar": true
  },
  "expected_outputs": {
    "TotalProjectMarketCosts_15": 450000000,
    "TotalProjectInternalCosts_16": 375000000,
    "GrossIncome_10": 15000000,
    "NetIncome_11": 11250000,
    "max_senior_notional_range": [150000000, 280000000],
    "mezz_layer_range": [30000000, 80000000],
    "permutation_count_expected": [5000, 15000]
  },
  "validation_thresholds": {
    "dscr_min_floor": 1.30,
    "senior_coverage_ratio": 0.70,
    "mezz_dscr_floor": 1.15,
    "equity_irr_min": 15.0,
    "blended_wacc_max": 6.5
  }
}
```

### 1.3 Large Project Fixture (200MW Complex Derivatives)
**Profile:** Institutional-grade with full derivative hedging
```json
{
  "fixture_id": "LARGE_200MW_DERIVATIVES",
  "project_params": {
    "GrossITLoad_02": 200.0,
    "PUE_03": 1.35,
    "CapexCostPrice_04": 7500000,
    "CapexMarketRate_05": 9000000,
    "LandPurchaseFees_06": 100000000,
    "GrossMonthlyRent_07": 5000000,
    "OPEX_08": 30.0,
    "LeaseTermYears_22": 25,
    "Currency_01": "GBP"
  },
  "complex_features": {
    "insurance_wrap": true,
    "zero_coupon_inflation_swaps": true,
    "currency_hedging": true,
    "power_derivatives": true,
    "credit_enhancement": "MonolineWrap"
  },
  "expected_outputs": {
    "TotalProjectMarketCosts_15": 1900000000,
    "TotalProjectInternalCosts_16": 1600000000,
    "GrossIncome_10": 60000000,
    "NetIncome_11": 42000000,
    "max_senior_notional_range": [800000000, 1400000000],
    "derivatives_value_range": [10000000, 50000000],
    "permutation_count_expected": [25000, 75000]
  },
  "validation_thresholds": {
    "dscr_min_floor": 1.30,
    "senior_coverage_ratio": 0.75,
    "wrap_enhancement_value": 25000000,
    "derivative_hedge_effectiveness": 0.95,
    "repo_eligibility": true
  }
}
```

## 2. Scenario Test Matrix

### 2.1 Core Variable Combinations
```yaml
test_dimensions:
  cpi_scenarios:
    values: [0.0, 1.8, 2.5, 3.5, 4.0]
    tolerance: ±0.1%

  senior_tenor_variants:
    values: [5, 10, 15, 20, 25]
    units: years
    constraints: ["≤ LeaseTermYears_22"]

  dscr_floor_by_rating:
    AAA: [1.30, 1.35, 1.40]
    AA: [1.25, 1.30, 1.35]
    A: [1.20, 1.25, 1.30]
    BBB: [1.15, 1.20, 1.25]

  insurance_wrap_scenarios:
    none: {WrapPremium_bps_58: 0}
    senior_only: {WrapPremium_bps_58: 60, coverage: "SeniorOnly"}
    whole_stack: {WrapPremium_bps_58: 100, coverage: "WholeStack"}

  jurisdiction_tests:
    uk_repo_eligible: {jurisdiction: "UK", repo_eligible: true}
    eu_pp_only: {jurisdiction: "EU", repo_eligible: false}
    us_144a: {jurisdiction: "US", repo_eligible: false}
```

### 2.2 Combinatorial Test Cases (Total: 3,750 base scenarios)
- CPI scenarios: 5 variants
- Tenor variants: 5 options
- DSCR/Rating combinations: 12 pairs
- Insurance scenarios: 3 options
- Jurisdictions: 3 markets
- **Total combinations:** 5 × 5 × 12 × 3 × 3 = 2,700 core scenarios
- **With fixture variations:** 2,700 × 3 fixtures = 8,100 total test scenarios

## 3. Performance Baselines & Benchmarks

### 3.1 Runtime Performance Targets
```yaml
permutation_performance:
  target_throughput: 150000  # permutations

  timing_benchmarks:
    p50_processing_time: "≤ 180 seconds"
    p95_processing_time: "≤ 300 seconds"
    p99_processing_time: "≤ 450 seconds"

  batch_processing:
    batch_size: 1000
    batches_per_minute_target: 20
    parallel_workers: 8

  memory_constraints:
    peak_memory_limit: "16 GB"
    sustained_memory_limit: "12 GB"
    memory_per_worker: "2 GB"
    garbage_collection_frequency: "every 5000 scenarios"
```

### 3.2 Database Performance Targets
```yaml
database_performance:
  gridfs_storage:
    write_throughput: "≥ 50 MB/s"
    read_throughput: "≥ 100 MB/s"
    compression_ratio: "≥ 3:1"

  query_performance:
    scenario_retrieval: "≤ 100ms for 1000 scenarios"
    aggregation_queries: "≤ 500ms for summary stats"
    full_result_export: "≤ 30s for 150k scenarios"

  concurrent_access:
    max_concurrent_users: 10
    performance_degradation_limit: "≤ 20% with full load"
```

### 3.3 Calculation Accuracy Standards
```yaml
numerical_precision:
  financial_calculations:
    dscr_precision: "±0.001"
    irr_precision: "±0.01%"
    npv_precision: "±£1,000"
    amortization_precision: "±£10"

  convergence_criteria:
    senior_debt_sizing: "±£50,000"
    equity_irr_calculation: "±0.05%"
    derivative_valuation: "±£5,000"

  floating_point_consistency:
    cross_platform_tolerance: "±1e-10"
    rounding_method: "banker's rounding"
```

## 4. Reproducibility Controls

### 4.1 Seed Management Testing
```python
reproducibility_tests = {
    "deterministic_output": {
        "description": "Same inputs produce identical outputs",
        "test": "run_with_seed(12345) == run_with_seed(12345)",
        "tolerance": "exact_match",
        "required_fields": ["all_kpi_values", "scenario_rankings", "summary_stats"]
    },

    "cross_session_consistency": {
        "description": "Results consistent across engine restarts",
        "test": "restart_engine(); compare_outputs()",
        "acceptance_threshold": "100% match on core metrics"
    },

    "parallel_execution_consistency": {
        "description": "Single-thread and multi-thread produce same results",
        "test": "compare_single_vs_parallel_execution()",
        "tolerance": "±1e-12 for floating point calculations"
    }
}
```

### 4.2 Version Control for Rulesets
```yaml
ruleset_versioning:
  config_versioning:
    current_version: "1.0.0"
    backward_compatibility: "maintain for 2 major versions"

  regression_baseline:
    golden_results_store: "test_fixtures/golden_results_v1.0.0/"
    comparison_tolerance: "±0.01% for all KPIs"

  change_impact_testing:
    ruleset_changes: "require full regression suite pass"
    parameter_additions: "require backward compatibility test"
    formula_modifications: "require QA approval + audit trail"
```

## 5. Edge Case Testing

### 5.1 Near-Miss Scenarios (85-100% CapEx Coverage)
```yaml
edge_case_scenarios:
  capex_coverage_stress:
    85_percent:
      senior_debt_limit: "TotalProjectMarketCosts_15 * 0.85"
      expected_outcome: "viable with higher equity"

    95_percent:
      senior_debt_limit: "TotalProjectMarketCosts_15 * 0.95"
      expected_outcome: "optimal leverage zone"

    99_percent:
      senior_debt_limit: "TotalProjectMarketCosts_15 * 0.99"
      expected_outcome: "stress case - minimal equity buffer"

    100_percent:
      senior_debt_limit: "TotalProjectMarketCosts_15 * 1.00"
      expected_outcome: "failure - insufficient equity"
```

### 5.2 Boundary Condition Handling
```yaml
boundary_tests:
  parameter_limits:
    dscr_minimum:
      test_value: 1.001
      expected: "warning but proceeding"

    dscr_floor_breach:
      test_value: 0.999
      expected: "scenario rejection"

    tenor_maximum:
      test_value: 40.001
      expected: "validation error"

  numerical_extremes:
    very_large_project:
      gross_it_load: 2999  # Near maximum
      expected: "graceful handling, no overflow"

    very_small_rent:
      monthly_rent: 100001  # Just above minimum
      expected: "valid calculation, appropriate warnings"
```

### 5.3 Rule Conflict Scenarios
```yaml
conflict_resolution:
  competing_constraints:
    high_dscr_short_tenor:
      TargetDSCRSenior_37: 1.50
      SeniorTenorY_39: 5
      expected_resolution: "sizing algorithm convergence or graceful failure"

    wrap_vs_rating_requirements:
      MonolineWrapFlag_57: "None"
      MinSeniorRatingTarget_75: "AAA"
      stress_scenario: "high"
      expected: "clear pass/fail decision with reasoning"
```

## 6. Regression Test Suite

### 6.1 Critical Path Coverage
```yaml
critical_path_tests:
  scenario_generation:
    coverage_target: "100%"
    key_functions:
      - "permutation_variable_expansion"
      - "constraint_application"
      - "scenario_state_calculation"

  financial_calculations:
    coverage_target: "100%"
    key_functions:
      - "senior_debt_sizing"
      - "dscr_calculation"
      - "waterfall_computation"
      - "derivative_valuation"

  ranking_and_filtering:
    coverage_target: "100%"
    key_functions:
      - "composite_scoring"
      - "hard_filter_application"
      - "result_ranking"
```

### 6.2 Output Format Validation
```yaml
output_validation:
  json_schema_compliance:
    scenario_output: "validate against schema v1.0.0"
    summary_statistics: "validate aggregation correctness"

  csv_export_integrity:
    column_headers: "match specification exactly"
    data_types: "numeric fields as numbers, not strings"
    null_handling: "consistent null representation"

  pdf_report_generation:
    waterfall_charts: "visual accuracy check against calculations"
    summary_tables: "cross-reference with raw data"
    formatting: "professional presentation standards"
```

### 6.3 Integration Point Testing
```yaml
integration_tests:
  database_operations:
    connection_resilience: "handle connection drops gracefully"
    transaction_integrity: "all-or-nothing for batch operations"
    concurrent_access: "proper locking and consistency"

  api_endpoints:
    input_validation: "reject malformed requests with clear errors"
    error_handling: "meaningful HTTP status codes and messages"
    rate_limiting: "respect system capacity limits"

  external_services:
    market_data_feeds: "graceful degradation if unavailable"
    email_notifications: "proper error handling for failed sends"
    blob_storage: "retry logic for temporary failures"
```

## 7. Numerical Thresholds & Pass/Fail Criteria

### 7.1 Acceptance Criteria by Test Category

#### Financial Accuracy
- **DSCR calculations:** ±0.001 absolute tolerance
- **IRR computations:** ±0.01% relative tolerance
- **NPV calculations:** ±£1,000 or ±0.1%, whichever is larger
- **Debt service amounts:** ±£10 absolute tolerance

#### Performance Benchmarks
- **150k permutations runtime:** ≤300 seconds (P95)
- **Memory usage:** ≤16GB peak, ≤12GB sustained
- **Database query response:** ≤500ms for aggregations
- **Concurrent user support:** ≥10 users with <20% degradation

#### Reliability Standards
- **Scenario success rate:** ≥95% of valid input combinations
- **Reproducibility:** 100% identical results with same seed
- **Error handling:** Graceful failure with meaningful messages
- **Data integrity:** 0 tolerance for data corruption

### 7.2 Test Execution Framework

```yaml
test_execution:
  automated_suite:
    frequency: "every commit to main branch"
    full_regression: "nightly"
    performance_benchmarks: "weekly"

  manual_verification:
    golden_fixture_review: "monthly"
    edge_case_validation: "quarterly"
    business_logic_audit: "semi-annually"

  reporting:
    pass_fail_dashboard: "real-time"
    performance_trends: "weekly reports"
    regression_analysis: "on failures"
```

## 8. Implementation Roadmap

### Phase 1: Core Infrastructure (Weeks 1-2)
- Set up automated test harness
- Implement golden fixtures
- Create performance monitoring

### Phase 2: Scenario Coverage (Weeks 3-4)
- Deploy comprehensive test matrix
- Implement edge case testing
- Add reproducibility controls

### Phase 3: Integration & Optimization (Weeks 5-6)
- Complete regression suite
- Performance tuning based on benchmarks
- Documentation and training

This comprehensive test protocol ensures the Atlas Forge permutation engine meets enterprise-grade reliability, performance, and accuracy standards required for institutional financial modeling.