# DOCUMENT FIELD INVENTORIES & EXPORT SPECIFICATIONS
## Atlas Nexus Execution Pack Generation System

---

## OVERVIEW

This document provides complete field inventories for all seven document types in the execution pack, with exact field mappings, data sources, formatting requirements, and conditional logic for mail-merge generation.

---

## 1. TERM SHEETS (PER TRANCHE)

### 1.1 Senior Tranche Term Sheet

#### Header Section
| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TS_DealName` | `project.title + "_Senior"` | String(100) | Required | - |
| `TS_CUSIP` | Generated | XXXXXXXXX | 9 chars | If US deal |
| `TS_ISIN` | Generated | XX0000000000 | 12 chars | If EU/UK deal |
| `TS_IssueDate` | `permutation.settlement_date` | DD-MMM-YYYY | Future date | - |
| `TS_MaturityDate` | `issue_date + tenor_years` | DD-MMM-YYYY | Required | - |

#### Financial Terms
| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TS_Principal` | `permutation.senior_notional` | $###,###,### | >0 | Format per currency |
| `TS_Coupon` | `permutation.senior_coupon` | #.##% | 3.0-7.0% | - |
| `TS_CouponType` | `"Fixed" or "Floating"` | String | Required | Based on structure |
| `TS_PaymentFreq` | `"Monthly"/"Quarterly"/"Semi-Annual"` | Enum | Required | - |
| `TS_DayCount` | `"30/360" or "Act/365"` | Enum | Required | By jurisdiction |
| `TS_AmortType` | `permutation.senior_amort_type` | Enum | Required | Annuity/Bullet/Level |
| `TS_WAL` | `calculated.senior_wal` | #.# years | >0 | - |

#### Credit Features
| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TS_Rating` | `permutation.senior_rating` | AAA/AA/A/BBB | Required | From rating check |
| `TS_DSCR_Min` | `waterfall.min_dscr` | #.##x | ≥1.0 | - |
| `TS_DSCR_Avg` | `waterfall.avg_dscr` | #.##x | ≥1.0 | - |
| `TS_LTV` | `senior_notional/asset_value` | ##.#% | ≤75% | - |
| `TS_RepoEligible` | `rules.repo_eligible` | Yes/No | Boolean | Based on rules |

#### Call Features
| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TS_CallProtection` | `permutation.call_protection_years` | # years | 0-5 | - |
| `TS_CallPrice` | `"Par" or premium schedule` | Text/Table | Required | If callable |
| `TS_MakeWhole` | `"T+## bps"` | Formula | If applicable | US deals |
| `TS_OptionalRedemption` | List of dates | Date array | If applicable | - |

#### Insurance/Enhancement
| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TS_InsuranceWrap` | `permutation.insurance_wrap` | Yes/No | Boolean | - |
| `TS_WrapProvider` | `insurance.provider_name` | String | If wrapped | From approved list |
| `TS_WrapRating` | `insurance.provider_rating` | AA+/AA/AA- | If wrapped | ≥AA |
| `TS_WrapPremium` | `insurance.annual_bps` | ## bps | If wrapped | 10-30 bps |

#### Covenants & Reserves
| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TS_CashTrapDSCR` | `rules.cash_trap_level` | #.##x | Required | By rating |
| `TS_DSRAMonths` | `rules.dsra_requirement` | # months | 3-12 | By rating |
| `TS_LiquidityReserve` | `calculated.liquidity_amount` | $###,### | ≥0 | % of debt service |

### 1.2 Mezzanine Tranche Term Sheet

*Additional fields beyond Senior:*

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TS_Mezz_Subordination` | `mezz_notional/total_debt` | ##.#% | Required | - |
| `TS_Mezz_PIK_Toggle` | `permutation.mezz_pik` | Yes/No | Boolean | If distressed |
| `TS_Mezz_StepUp` | Step-up schedule | Table | If applicable | After year 3 |
| `TS_Mezz_Intercreditor` | `"Second lien"` | Text | Required | Legal structure |

### 1.3 Equity/Residual Certificate

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TS_Equity_Class` | `"Class E Certificates"` | String | Required | - |
| `TS_Equity_Amount` | `total_cost - debt` | $###,### | >0 | Residual |
| `TS_Target_IRR` | `permutation.equity_irr` | ##.#% | 12-25% | - |
| `TS_Distribution_Priority` | `"After all senior obligations"` | Text | Required | - |

---

## 2. RATING/RULE COMPLIANCE SHEET

### 2.1 Compliance Summary Table

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `RC_TestDate` | `datetime.now()` | DD-MMM-YYYY HH:MM | Required | - |
| `RC_OverallResult` | `PASS/FAIL/CONDITIONAL` | Enum | Required | - |
| `RC_RatingAchieved` | `final_rating` | AAA to B | Required | - |
| `RC_ConstraintCount` | Count of breaches | Integer | ≥0 | - |

### 2.2 Individual Rule Results

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `RC_Rule_ID` | `rule.key` | String(20) | Required | RK-XXX-### |
| `RC_Rule_Description` | `rule.description` | String(200) | Required | - |
| `RC_Rule_Category` | `rule.category` | Enum | Required | DSCR/Tenor/AF/etc |
| `RC_Required_Value` | `rule.threshold` | Numeric/String | Required | - |
| `RC_Actual_Value` | `calculated.value` | Numeric/String | Required | - |
| `RC_Pass_Fail` | `PASS/FAIL` | Enum | Required | Compare actual vs required |
| `RC_Impact_If_Fail` | `rule.consequence` | String(100) | If failed | Rating cap/rejection |
| `RC_Remediation` | `rule.fix_suggestion` | String(200) | If failed | How to fix |

### 2.3 Binding Constraints Section

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `RC_Binding_Constraint` | Constraint identifier | String | If any | Most restrictive rule |
| `RC_Constraint_Value` | Limiting value | Numeric | If binding | - |
| `RC_Headroom` | Distance to breach | Numeric/% | If close | Within 10% |
| `RC_Sensitivity` | Impact of 1% change | Numeric | Calculated | - |

---

## 3. STRESS TEST GRID

### 3.1 Scenario Definitions

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `ST_Scenario_ID` | Generated | ST-### | Unique | Sequential |
| `ST_Scenario_Name` | `scenario.name` | String(50) | Required | Descriptive |
| `ST_Scenario_Type` | `CPI/Rate/Credit/Combined` | Enum | Required | - |
| `ST_CPI_Assumption` | `0%/1.8%/2.5%/3.5%` | Percentage | Required | - |
| `ST_Rate_Shock` | `0/+100/+200/-100 bps` | Integer | Required | Basis points |
| `ST_Default_Rate` | `0%/5%/10%` | Percentage | For credit stress | - |

### 3.2 Results Matrix

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `ST_Base_DSCR` | `base_case.min_dscr` | #.##x | >0 | No stress |
| `ST_Stressed_DSCR` | `stress_case.min_dscr` | #.##x | >0 | With stress |
| `ST_DSCR_Degradation` | `(base-stress)/base` | ##.#% | Calculated | Percentage drop |
| `ST_Years_Below_1x` | Count of breach periods | Integer | ≥0 | Where DSCR<1.0 |
| `ST_Recovery_Period` | Months to recover | Integer | If breached | Back above 1.0 |
| `ST_Rating_Migration` | Notches downgrade | Integer | 0-5 | Impact on rating |
| `ST_Pass_Fail` | `PASS/FAIL` | Enum | Required | Based on floors |

### 3.3 Visualization Requirements

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `ST_DSCR_Chart_Data` | Annual DSCR array | JSON array | Required | For line chart |
| `ST_Heatmap_Data` | Scenario vs metric matrix | 2D array | Required | For heatmap |
| `ST_Sensitivity_Table` | Parameter impact table | Table | Required | Tornado diagram |

---

## 4. WATERFALL SUMMARY

### 4.1 Annual Cash Flow Projection

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `WF_Year` | Period counter | Integer | 1-30 | Annual periods |
| `WF_Gross_Revenue` | `income.gross_annual` | $###,### | ≥0 | Before expenses |
| `WF_Operating_Exp` | `income * opex_pct` | $###,### | ≥0 | OPEX |
| `WF_NOI` | `gross - opex` | $###,### | Can be negative | Net operating |
| `WF_Senior_Interest` | `senior_balance * coupon` | $###,### | ≥0 | Interest payment |
| `WF_Senior_Principal` | Amortization schedule | $###,### | ≥0 | Principal payment |
| `WF_Senior_Balance` | Running balance | $###,### | ≥0 | Outstanding |
| `WF_Mezz_Interest` | If applicable | $###,### | ≥0 | After senior |
| `WF_Mezz_Principal` | If applicable | $###,### | ≥0 | After senior |
| `WF_Reserve_Funding` | DSRA topup | $###,### | ≥0 | If required |
| `WF_Cash_Available` | For distribution | $###,### | ≥0 | After obligations |
| `WF_Cash_Trapped` | If triggered | $###,### | ≥0 | Held in reserve |
| `WF_Equity_Dist` | Residual cashflow | $###,### | ≥0 | To equity |

### 4.2 Key Metrics Summary

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `WF_Min_DSCR` | Minimum across periods | #.##x | >0 | Worst case |
| `WF_Avg_DSCR` | Average across periods | #.##x | >0 | Weighted avg |
| `WF_Senior_WAL` | Weighted avg life | #.# years | >0 | Duration |
| `WF_Final_Maturity` | Last payment date | MM/YYYY | Required | Legal final |
| `WF_Total_Interest` | Sum of interest | $###,### | ≥0 | Life total |
| `WF_Equity_Returns` | IRR calculation | ##.#% | Can be negative | After all costs |

---

## 5. SIDECAR DOCUMENTATION PACK

### 5.1 ZCIS Term Sheets

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `ZCIS_Tenor` | `5Y or 10Y` | String | Required | Only 2 options |
| `ZCIS_Notional` | `sidecar.zcis_notional` | $###,### | >0 | Matched to senior |
| `ZCIS_Fixed_Rate` | Market breakeven | #.##% | 1-4% | From pricing |
| `ZCIS_Index` | `CPI-U/HICP/RPI` | Enum | Required | By jurisdiction |
| `ZCIS_Base_Level` | Current index | ###.## | >0 | At inception |
| `ZCIS_Payment` | `"At maturity"` | String | Fixed | Zero coupon |
| `ZCIS_Upfront_Value` | NPV calculation | $###,### | Can be negative | Day-one monetization |

### 5.2 TRS Specifications

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `TRS_Reference` | `"Equity tranche"` | String | Required | Underlying asset |
| `TRS_Notional` | `equity * trs_pct` | $###,### | >0 | 5-25% typical |
| `TRS_Total_Return` | Pass through | Description | Required | All economics |
| `TRS_Funding_Rate` | `SOFR + spread` | Formula | Required | Floating rate |
| `TRS_Reset_Freq` | `"Monthly"/"Quarterly"` | Enum | Required | Rate reset |
| `TRS_Upfront_Cash` | Initial payment | $###,### | ≥0 | Day-one value |

### 5.3 Interest Rate Derivatives

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `IRD_Type` | `Floor/Cap/Collar` | Enum | Required | Derivative type |
| `IRD_Strike` | Strike rate | #.##% | 0-5% | Protection level |
| `IRD_Notional` | Hedged amount | $###,### | >0 | Usually = senior |
| `IRD_Premium` | Upfront cost | $###,### or bps | ≥0 | Market price |
| `IRD_Monetization` | Sale proceeds | $###,### | ≥0 | If sold upfront |

---

## 6. EXECUTION CHECKLIST

### 6.1 Service Providers

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `EX_Arranger` | `deal.arranger_name` | String | Required | Lead bank |
| `EX_Legal_Issuer` | Law firm name | String | Required | Issuer counsel |
| `EX_Legal_Investor` | Law firm name | String | Optional | Investor counsel |
| `EX_Rating_Agency` | S&P/Moody's/Fitch | String | Required | 1-3 agencies |
| `EX_Trustee` | Bank name | String | Required | Corporate trustee |
| `EX_Paying_Agent` | Bank name | String | Required | Payment admin |
| `EX_SPV_Admin` | Service provider | String | Required | SPV management |

### 6.2 Documentation Requirements

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `EX_Doc_Type` | Document name | String | Required | Legal document |
| `EX_Doc_Status` | Draft/Final/Executed | Enum | Required | Current status |
| `EX_Doc_Owner` | Responsible party | String | Required | Who provides |
| `EX_Doc_Deadline` | Due date | DD-MMM-YYYY | Required | Timeline |

### 6.3 Timeline & Milestones

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `EX_Milestone` | Task description | String | Required | Key event |
| `EX_Start_Date` | Begin date | DD-MMM-YYYY | Required | - |
| `EX_End_Date` | Complete date | DD-MMM-YYYY | Required | After start |
| `EX_Duration` | Business days | Integer | >0 | Calculated |
| `EX_Dependencies` | Predecessor tasks | Array | Optional | Critical path |
| `EX_Status` | Not Started/In Progress/Complete | Enum | Required | Tracking |

---

## 7. INVESTOR SUMMARY PACK

### 7.1 Executive Summary

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `IS_Deal_Name` | `project.title` | String | Required | Marketing name |
| `IS_Asset_Class` | `"Data Center ABS"` | String | Required | Sector |
| `IS_Total_Size` | Sum all tranches | $###M | >0 | Headline number |
| `IS_Sponsor` | Sponsor name | String | Required | Originator |
| `IS_Highlights` | Bullet points | Array | 3-5 items | Key features |

### 7.2 Investment Metrics Dashboard

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `IS_Senior_Yield` | All-in yield | #.##% | Required | Total return |
| `IS_Senior_Spread` | Over benchmark | +### bps | Required | Credit spread |
| `IS_WAL_Senior` | Weighted life | #.# years | Required | Duration |
| `IS_Rating_Senior` | Credit rating | AAA/AA/A | Required | - |
| `IS_Enhancement` | Subordination | ##.#% | Required | Credit support |
| `IS_Repo_Status` | Eligibility | Yes/No | Required | Central bank |

### 7.3 Risk Factors

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `IS_Risk_Category` | Risk type | Enum | Required | Credit/Market/Op |
| `IS_Risk_Description` | Risk detail | String(500) | Required | Explanation |
| `IS_Risk_Mitigation` | Mitigants | String(500) | Required | How addressed |
| `IS_Risk_Rating` | Low/Medium/High | Enum | Required | Assessment |

### 7.4 Comparable Transactions

| Field Name | Data Source | Format | Validation | Conditional Logic |
|------------|------------|--------|------------|-------------------|
| `IS_Comp_Name` | Deal name | String | Required | Recent comp |
| `IS_Comp_Date` | Issue date | MMM-YYYY | Required | Within 12 months |
| `IS_Comp_Size` | Deal size | $###M | Required | Similar size |
| `IS_Comp_Rating` | Rating | AAA/AA/A | Required | Similar rating |
| `IS_Comp_Pricing` | Spread | +### bps | Required | Pricing benchmark |
| `IS_Comp_Performance` | Trading level | +/- ## bps | Optional | Secondary market |

---

## FORMATTING SPECIFICATIONS

### Currency Formatting
```
USD: $#,###,###.##
EUR: €#.###.###,##
GBP: £#,###,###.##
JPY: ¥#,###,###
```

### Date Formatting
```
Term Sheets: DD-MMM-YYYY (15-Sep-2025)
Legal Docs: DD/MM/YYYY (15/09/2025)
US Docs: MM/DD/YYYY (09/15/2025)
```

### Percentage Formatting
```
Rates: #.##% (4.25%)
Ratios: #.##x (1.35x)
LTV: ##.#% (67.5%)
```

### Conditional Logic Examples
```python
if jurisdiction == "UK":
    date_format = "DD/MM/YYYY"
    currency_symbol = "£"
elif jurisdiction == "EU":
    date_format = "DD.MM.YYYY"
    currency_symbol = "€"
else:  # US
    date_format = "MM/DD/YYYY"
    currency_symbol = "$"

if rating >= "AA":
    repo_eligible = "Yes"
else:
    repo_eligible = "No"

if insurance_wrap:
    dscr_requirement *= 0.85
    rating_uplift = 1
```

---

## DATA SOURCE MAPPING

### Primary Sources
1. **Permutation Engine Output**: All calculation results
2. **Rule Engine Results**: Compliance and eligibility
3. **Waterfall Calculations**: Cash flow projections
4. **Stress Test Module**: Scenario analysis
5. **Market Data Service**: Pricing and comparables
6. **Document Templates**: Base formats

### Field Population Priority
1. User input (override if manual)
2. Calculated values (from engines)
3. Market data (from services)
4. Default values (from config)

### Validation Hierarchy
1. Hard constraints (must pass)
2. Soft constraints (warning if fail)
3. Best practices (recommendation)

---

*Document Version: 1.0*
*Last Updated: September 2025*
*Template Library: /templates/execution_pack/*