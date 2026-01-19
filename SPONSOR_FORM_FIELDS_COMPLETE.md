# Sponsor Form Fields - Complete Reference

**File:** templates/dashboard.html
**Section:** Projects → Create Project → Manual Entry Tab
**Total Fields:** 87+ editable fields + 30+ display-only calculated fields

---

## 1. Project Metadata (9 fields)

| Field ID | Label | Type | Default Value | Unit/Options | Required | Notes |
|----------|-------|------|---------------|--------------|----------|-------|
| `sponsor-projectTitle` | Project Title | text | - | - | ✓ | Project name/identifier |
| `sponsor-locationCountry` | Location Country | select | "United Kingdom" | 45 European countries with tier ratings | ✓ | Includes tier (FLAP, Tier 1-3) |
| `sponsor-status` | Status | select | - | 11 status options | - | 0. Archived → 8. Live |
| `sponsor-capex-currency` | CapEx Currency | select | - | EUR, USD, GBP, JPY, AED | ✓ | Main project currency |
| `sponsor-kwh-currency` | Cost per kWh Currency | select | - | EUR, USD, GBP, JPY, AED | ✓ | Revenue/OPEX currency |
| `sponsor-grossFacilityPower` | Gross Facility Power (MW) | number | - | MW | ✓ | Total grid connection capacity |
| `sponsor-pue` | PUE | number | 1.25 | 0.95 - 1.5 | ✓ | Power Usage Effectiveness |
| `sponsor-itLoad` | IT Load (Calculated) | number | - | MW | - | Readonly: Gross Power / PUE |
| `sponsor-overheadPower` | Overhead Power (Calculated) | number | - | MW | - | Readonly: Gross - IT |

---

## 2. Revenue & Occupancy (8 fields)

| Field ID | Label | Type | Default Value | Unit/Options | Required | Notes |
|----------|-------|------|---------------|--------------|----------|-------|
| `sponsor-grossMonthlyRent` | Gross Monthly Rent (per kWh) | text | - | 0.00 - 300.00 | ✓ | Revenue per kWh per month |
| `sponsor-opexPercent` | OPEX % | text | - | 0% - 100% | ✓ | Operating expense percentage |
| `sponsor-leaseType` | Lease Type | select | "TripleNet" | TripleNet, Gross | ✓ | Triple Net or Gross lease |
| `sponsor-electricityRate` | Electricity Rate (per MWh) | number | 100 | per MWh | - | Gross lease only, hidden for Triple Net |
| `sponsor-occupancy` | Occupancy at Stabilization % | range | 100 | 0 - 100 | ✓ | Slider control with live display |
| `sponsor-preCloseMonths` | Pre-Close Preparation (Months) | number | 1 | 1 - 18 | ✓ | Deal structuring to Day 1 Close |
| `sponsor-constructionStart` | Construction Start Date (Day 1 Close) | date | - | - | ✓ | Financial close date |
| `sponsor-constructionDurationMonths` | Construction Duration (Months) | number | 24 | 1 - 48 | ✓ | Build period |

---

## 3. Timeline (Display-Only, 4 fields)

| Field ID | Label | Type | Notes |
|----------|-------|------|-------|
| `sponsor-completionDate` | Expected Completion Date | date | Readonly: Start + Duration |
| `sponsor-leaseCommenceDate` | Lease Commencement Date | date | Defaults to completion date |
| `sponsor-timeline-today` | Today | display | Current date (Jan 2026) |
| `sponsor-timeline-day1` | Day 1 Close | display | Construction Start - Pre-Close Months |
| `sponsor-timeline-complete` | Complete | display | Construction Start + Duration |
| `sponsor-timeline-revenue` | Revenue Begins | display | Same as Complete |
| `sponsor-timeline-maturity` | Maturity | display | Complete + 15 years |

---

## 4. CapEx Internal (Build) - 17 fields

**Per MW Mode:**
| Field ID | Label | Type | Range | Notes |
|----------|-------|------|-------|-------|
| `sponsor-capexInternalPerMW` | Cost per Gross MW | text | 0 - 25,000,000 | Simplified per-MW costing |

**Detailed Breakdown (16 fields):**
| Field ID | Label | Type | Notes |
|----------|-------|------|-------|
| `sponsor-buildArchitectural` | Architectural | number | Architectural design & engineering |
| `sponsor-buildCivilStructural` | Civil & Structural | number | Foundations, structure, shell |
| `sponsor-buildSubstations` | Substations | number | Electrical substations |
| `sponsor-buildUndergroundUtilities` | Underground Utilities | number | Conduits, cabling, infrastructure |
| `sponsor-buildCrusaderModules` | Crusader Modules | number | Modular data hall units |
| `sponsor-buildBess` | BESS | number | Battery Energy Storage System |
| `sponsor-buildMainContractorInstallation` | Main Contractor Installation | number | Labor, installation, commissioning |
| `sponsor-buildPhotovoltaicSystem` | Photovoltaic System | number | Solar panels, inverters |
| `sponsor-buildLandscaping` | Landscaping | number | Site landscaping, access roads |
| `sponsor-buildPreliminariesGeneral` | Preliminaries General | number | Site setup, temporary facilities |
| `sponsor-buildMainContractorMargin` | Main Contractor Margin | number | Contractor profit/overhead |
| `sponsor-buildConnection` | Connection | number | Grid connection equipment |
| `sponsor-buildLand` | Land | number | Land acquisition (internal cost) |
| `sponsor-buildOperationsTeam` | Operations Team | number | Pre-operational team costs |
| `sponsor-buildOSE` | OS&E | number | Owner-supplied equipment |
| `sponsor-buildMarketing` | Marketing | number | Marketing & sales expenses |
| `sponsor-buildConstructionFeePercent` | Construction Phase Fee (%) | number | Default: 1.5% (editable) |

---

## 5. CapEx Market - 17 fields

**Per MW Mode:**
| Field ID | Label | Type | Range | Notes |
|----------|-------|------|-------|-------|
| `sponsor-capexMarketPerMW` | Cost per Gross MW | text | 0 - 25,000,000 | Simplified per-MW costing |

**Detailed Breakdown (16 fields):**
| Field ID | Label | Type | Notes |
|----------|-------|------|-------|
| `sponsor-marketArchitectural` | Architectural | number | Market/appraisal value |
| `sponsor-marketCivilStructural` | Civil & Structural | number | Market/appraisal value |
| `sponsor-marketSubstations` | Substations | number | Market/appraisal value |
| `sponsor-marketUndergroundUtilities` | Underground Utilities | number | Market/appraisal value |
| `sponsor-marketCrusaderModules` | Crusader Modules | number | Market/appraisal value |
| `sponsor-marketBess` | BESS | number | Market/appraisal value |
| `sponsor-marketMainContractorInstallation` | Main Contractor Installation | number | Market/appraisal value |
| `sponsor-marketPhotovoltaicSystem` | Photovoltaic System | number | Market/appraisal value |
| `sponsor-marketLandscaping` | Landscaping | number | Market/appraisal value |
| `sponsor-marketPreliminariesGeneral` | Preliminaries General | number | Market/appraisal value |
| `sponsor-marketMainContractorMargin` | Main Contractor Margin | number | Market/appraisal value |
| `sponsor-marketConnection` | Connection | number | Market/appraisal value |
| `sponsor-marketLand` | Land | number | Market/appraisal value |
| `sponsor-marketOperationsTeam` | Operations Team | number | Market/appraisal value |
| `sponsor-marketOSE` | OS&E | number | Market/appraisal value |
| `sponsor-marketMarketing` | Marketing | number | Market/appraisal value |
| `sponsor-marketConstructionPhaseFee` | Construction Phase Fee (max 1.5%) | number | Readonly: 1.5% of subtotal |

---

## 6. Contingency - 1 field

| Field ID | Label | Type | Default | Range | Notes |
|----------|-------|------|---------|-------|-------|
| `sponsor-contingencyPercent` | Contingency Percent | text | - | 0% - 100% | Applied to each CapEx separately |

---

## 7. Land & Infrastructure - 8 fields

| Field ID | Label | Type | Default | Range/Options | Required | Notes |
|----------|-------|------|---------|---------------|----------|-------|
| `sponsor-locationQuality` | Location Quality | select | "good" | excellent/good/fair/poor/custom | - | Auto-fills land purchase cost |
| `sponsor-landPurchase` | Land Purchase | text | - | 0 - 1,000,000,000 | ✓ | Total land acquisition cost |
| `sponsor-gridConnectionQuality` | Grid Connection Quality | select | "good" | good/medium/poor/custom | - | Affects grid cost per MW |
| `sponsor-gridConnectionCosts` | Grid Connection Costs | text | - | - | ✓ | Total grid connection costs |
| `sponsor-stampDutyStructure` | Stamp Duty Land Tax (SDLT) Structure | select | "company" | individual/company/company_additional/reit/custom | - | UK stamp duty structure |
| `sponsor-stampDutyPercent` | Stamp Duty Rate (%) | text | "5%" | 0 - 20% | ✓ | Auto-populated from structure |
| `sponsor-stampDutyFixed` | Stamp Duty Fixed (Overrides %) | text | - | - | - | Optional fixed override |

**Location Quality Options:**
- Excellent (FLAP-D): €500,000/MW land cost
- Good (FLAP): €400,000/MW land cost
- Fair (Tier 2/3): €300,000/MW land cost
- Poor (Emerging): €200,000/MW land cost
- Custom: Manual entry

**Grid Connection Quality Options:**
- Good: €200k/MW (existing substation nearby)
- Medium: €400k/MW (upgrades needed)
- Poor: €600k/MW (new substation required)
- Custom: Manual entry

---

## 8. Developer Economics (Display-Only, 2 fields)

| Field ID | Label | Type | Calculation | Notes |
|----------|-------|------|-------------|-------|
| `sponsor-developerProfit` | Developer Profit (Market - Internal) | text | Market CapEx - Internal CapEx | Disabled/readonly |
| `sponsor-developerMarginPercent` | Developer Margin (%) | text | (Developer Profit / Internal CapEx) × 100 | Disabled/readonly |

---

## 9. Fees (Simple) - 3 fields

| Field ID | Label | Type | Default | Range | Notes |
|----------|-------|------|---------|-------|-------|
| `sponsor-feesDM` | DM | text | - | - | Development Management fee |
| `sponsor-feesManagementPercent` | Management Fee % | number | 3 | 0 - 10 | Default 3% (editable) |
| `sponsor-feesManagement` | Management Fee Amount | text | - | - | Editable (overrides % calculation) |

---

## 10. Construction Interest Coverage (Pre-COD) - 6 fields

### Senior Tranche (3 fields)
| Field ID | Label | Type | Default | Options/Range | Notes |
|----------|-------|------|---------|---------------|-------|
| `sponsor-seniorCoverageMethod` | Coverage Method | select | "dsra" | dsra/insurance/sponsor_equity/lc/mixed | How to cover construction interest |
| `sponsor-seniorCoveragePercent` | Coverage % | number | 100 | 0 - 100 | Percentage covered |
| `sponsor-seniorMethodCost` | Method Cost % | number | 0 | 0 - 10 | Cost of coverage method |

**Senior Coverage Methods:**
- DSRA Reserve (Most Common)
- Insurance Wrap (Rating Agency Favorite)
- Sponsor Equity Contribution
- Letter of Credit (LC)
- Mixed Methods

### Mezzanine Tranche (3 fields)
| Field ID | Label | Type | Default | Options/Range | Notes |
|----------|-------|------|---------|---------------|-------|
| `sponsor-mezzCoverageMethod` | Coverage Method | select | "pik" | pik/dsra/sponsor_equity/mixed | How to cover mezz interest |
| `sponsor-mezzCoveragePercent` | Coverage % | number | 100 | 0 - 100 | Percentage covered |
| `sponsor-mezzMethodCost` | Method Cost % | number | 2 | 0 - 10 | Cost of coverage method |

**Mezzanine Coverage Methods:**
- PIK/Capitalization (Most Common for Mezz)
- DSRA Reserve
- Sponsor Equity Contribution
- Mixed Methods

---

## 11. ABS Fees (Day 1 Close) - 15 fields

**Percentage-Based Arranger Fees (2 fields):**
| Field ID | Label | Type | Default | Range | Unit | Notes |
|----------|-------|------|---------|-------|------|-------|
| `sponsor-internalArrangerFee` | Internal Arranger Fee (% of Debt) | number | 3.0 | 0 - 10 | % | Internal lead arranger/underwriter |
| `sponsor-externalArrangerFee` | External Arranger Fee (% of Debt) | number | 2.0 | 0 - 10 | % | External arranger/syndication |

**Fixed ABS Fees (13 fields):**
| Field ID | Label | Type | Default Value | Notes |
|----------|-------|------|---------------|-------|
| `sponsor-legalIssuer` | Legal Counsel - Issuer | text | 750,000 | Issuer/sponsor legal fees |
| `sponsor-legalUnderwriter` | Legal Counsel - Underwriter | text | 500,000 | Underwriter/investor legal fees |
| `sponsor-ratingAgency` | Rating Agency - Initial Fees | text | 350,000 | Moody's, S&P, Fitch initial rating |
| `sponsor-trusteeSetup` | Trustee/Security Trustee - Setup | text | 200,000 | Initial setup and documentation |
| `sponsor-payingAgentSetup` | Paying Agent/Account Bank - Setup | text | 150,000 | Initial setup fees |
| `sponsor-financialAdvisors` | Financial/Tax Advisors | text | 400,000 | Structuring and tax advisory |
| `sponsor-technicalAdvisors` | Technical/Engineering Advisors | text | 300,000 | Independent technical due diligence |
| `sponsor-insuranceAdvisor` | Insurance Advisor | text | 100,000 | Insurance structuring and placement |
| `sponsor-listingFees` | Listing/Regulatory Fees | text | 250,000 | Exchange listing and compliance |
| `sponsor-spvSetup` | SPV Setup & Administration | text | 150,000 | Special purpose vehicle incorporation |
| `sponsor-swapFee` | Swap Execution Fee | text | 250,000 | Interest rate swap setup/execution |
| `sponsor-greenBondFee` | Green Bond/ESG Verification Fee | text | 100,000 | ESG consultant for green certification |
| `sponsor-otherTransactionCosts` | Other Transaction Costs | text | 200,000 | Printing, marketing, roadshow, misc. |

**Total Default ABS Fees:** €4,200,000 (fixed fees only, arranger fees = 0 until debt amount calculated)

---

## 12. Calculated Totals (Display-Only, 30+ fields)

### Project Costs Breakdown

**Internal CapEx:**
| Display ID | Label | Calculation |
|------------|-------|-------------|
| `sponsor-capexInternalBase` | Base | Sum of all internal build items |
| `sponsor-contingencyInternal` | Contingency | Base × Contingency % |
| `sponsor-capexInternalTotal` | Total | Base + Contingency |

**Market CapEx:**
| Display ID | Label | Calculation |
|------------|-------|-------------|
| `sponsor-capexMarketBase` | Base | Sum of all market build items |
| `sponsor-contingencyMarket` | Contingency | Base × Contingency % |
| `sponsor-capexMarketTotal` | Total | Base + Contingency |

**Land & Infrastructure:**
| Display ID | Label | Calculation |
|------------|-------|-------------|
| `sponsor-landTotal` | Land Purchase | Direct input |
| `sponsor-gridTotal` | Grid Connection | Direct input |
| `sponsor-stampDutyTotal` | Stamp Duty | Land × Rate % (or fixed) |
| `sponsor-landInfrastructureTotal` | Total | Land + Grid + Stamp Duty |

**Fees:**
| Display ID | Label | Calculation |
|------------|-------|-------------|
| `sponsor-totalDay1Fees` | Total Day 1 Close Fees (Capitalized) | Sum of 15 ABS fees |
| `sponsor-feesTotal` | Fees Total | DM + Management + Day 1 Fees |

**Grand Totals:**
| Display ID | Label | Calculation |
|------------|-------|-------------|
| `sponsor-grandTotal` | Internal Grand Total | Internal CapEx + Land/Infra + Fees |
| `sponsor-grandTotalMarket` | Market Grand Total | Market CapEx + Land/Infra + Fees |
| `sponsor-darkProfit` | DARK Development Profit | Market Grand Total - Internal Grand Total |

---

## 13. Currency Display Elements (Dynamic)

These span elements update to show the selected currency symbol:

| Display ID | Shows | Updates From |
|------------|-------|--------------|
| `capex-internal-currency` | EUR/USD/GBP/JPY/AED | sponsor-capex-currency |
| `capex-market-currency` | EUR/USD/GBP/JPY/AED | sponsor-capex-currency |
| `land-currency-display` | EUR/USD/GBP/JPY/AED | sponsor-capex-currency |
| `grid-currency-display` | EUR/USD/GBP/JPY/AED | sponsor-capex-currency |
| `stamp-currency-display` | EUR/USD/GBP/JPY/AED | sponsor-capex-currency |
| `developer-currency` | EUR/USD/GBP/JPY/AED | sponsor-capex-currency |
| `fees-currency` | EUR/USD/GBP/JPY/AED | sponsor-capex-currency |
| `abs-fees-currency` | EUR/USD/GBP/JPY/AED | sponsor-capex-currency |
| `sponsor-kwh-currency-display` | EUR/USD/GBP/JPY/AED | sponsor-kwh-currency |
| `sponsor-electricity-currency-display` | EUR/USD/GBP/JPY/AED | sponsor-kwh-currency |

---

## 14. Validation Rules

### Required Fields (marked with *)
- Project Title
- Location Country
- CapEx Currency
- Cost per kWh Currency
- Gross Facility Power (MW)
- PUE (0.95 - 1.5)
- Gross Monthly Rent (per kWh)
- OPEX %
- Lease Type
- Occupancy at Stabilization %
- Pre-Close Preparation (Months)
- Construction Start Date
- Construction Duration (Months)
- Land Purchase
- Grid Connection Costs
- Stamp Duty Rate (%)

### Range Validations
| Field | Min | Max | Step |
|-------|-----|-----|------|
| Gross Facility Power | 0.1 | - | 0.01 |
| PUE | 0.95 | 1.5 | 0.01 |
| Gross Monthly Rent | 0 | 300 | 0.01 |
| OPEX % | 0 | 100 | 1 |
| Occupancy % | 0 | 100 | 1 |
| Pre-Close Months | 1 | 18 | 1 |
| Construction Duration | 1 | 48 | 1 |
| Contingency % | 0 | 100 | - |
| Management Fee % | 0 | 10 | 0.1 |
| Senior/Mezz Coverage % | 0 | 100 | 1 |
| Senior/Mezz Method Cost % | 0 | 10 | 0.1 |
| Internal/External Arranger Fee | 0 | 10 | 0.1 |
| CapEx Per MW | 0 | 25,000,000 | - |
| Land Purchase | 0 | 1,000,000,000 | - |

---

## 15. Auto-Calculations Triggered

### On Field Change Events

**updateSponsorPowerCalculations()** - Triggered by:
- sponsor-grossFacilityPower
- sponsor-pue
- Calculates: IT Load, Overhead Power

**calculateSponsorTotals()** - Triggered by:
- All CapEx fields (internal/market)
- All Land & Infrastructure fields
- All Fee fields
- All ABS fee fields
- Contingency percent
- Calculates: All totals, grand totals, developer profit

**updateSponsorTimeline()** - Triggered by:
- sponsor-preCloseMonths
- sponsor-constructionStart
- sponsor-constructionDurationMonths
- sponsor-leaseCommenceDate
- Updates: Timeline display (Day 1, Complete, Revenue, Maturity)

**calculateManagementFromPercent()** - Triggered by:
- sponsor-feesManagementPercent
- Calculates: Management Fee Amount

**calculateManagementPercent()** - Triggered by:
- sponsor-feesManagement (manual entry)
- Back-calculates: Management Fee %

**calculateCapexFromPerMW()** - Triggered by:
- sponsor-capexInternalPerMW
- sponsor-capexMarketPerMW
- Calculates: Total CapEx from Per MW rate

**toggleElectricityRate()** - Triggered by:
- sponsor-leaseType
- Shows/hides: Electricity Rate field (Gross lease only)

**updateGridConnectionFromQuality()** - Triggered by:
- sponsor-gridConnectionQuality
- Auto-fills: Grid Connection Costs

**updateStampDutyFromStructure()** - Triggered by:
- sponsor-stampDutyStructure
- Auto-fills: Stamp Duty Rate %

**updateLandFromQuality()** - Triggered by:
- sponsor-locationQuality
- Auto-fills: Land Purchase cost

---

## 16. Field Organization Summary

### By Section:
1. **Project Metadata:** 9 fields (5 required)
2. **Revenue & Occupancy:** 8 fields (5 required)
3. **Timeline:** 4 calculated display fields
4. **CapEx Internal:** 17 fields (1 per MW or 16 detailed)
5. **CapEx Market:** 17 fields (1 per MW or 16 detailed)
6. **Contingency:** 1 field
7. **Land & Infrastructure:** 8 fields (3 required)
8. **Developer Economics:** 2 calculated display fields
9. **Fees (Simple):** 3 fields
10. **Construction Interest Coverage:** 6 fields (3 senior, 3 mezz)
11. **ABS Fees:** 15 fields (13 fixed + 2 percentage-based)
12. **Calculated Totals:** 30+ display fields

### By Type:
- **Text inputs:** ~25 fields
- **Number inputs:** ~50 fields
- **Select dropdowns:** 7 fields
- **Date inputs:** 3 fields
- **Range slider:** 1 field
- **Readonly/Calculated:** 30+ fields

### By Required Status:
- **Required (*):** 16 fields
- **Optional:** 71+ fields

---

## 17. Save Data Structure

When saved via `saveSponsorProject()`, the project is sent to:
- **Endpoint:** `POST /api/projects/{project_id}`
- **Location:** app.py lines 6388-6482

**Project Data Structure:**
```javascript
{
  meta: {
    projectTitle: string,
    locationCountry: string,
    status: string,
    capexCurrency: string,
    kwhCurrency: string,
    grossFacilityPower: number,
    pue: number,
    itLoad: number,
    overheadPower: number,
    grossMonthlyRent: number,
    opexPercent: number,
    leaseType: string,
    electricityRate: number,
    occupancy: number,
    preCloseMonths: number,
    constructionStart: date,
    constructionDurationMonths: number,
    completionDate: date,
    leaseCommenceDate: date
  },
  capex: {
    internal: {
      perMW: number,
      detailed: { /* 16 breakdown items */ }
    },
    market: {
      perMW: number,
      detailed: { /* 16 breakdown items */ }
    },
    contingencyPercent: number
  },
  land: {
    locationQuality: string,
    landPurchase: number,
    gridConnectionQuality: string,
    gridConnectionCosts: number,
    stampDutyStructure: string,
    stampDutyPercent: number,
    stampDutyFixed: number
  },
  fees: {
    feesDM: number,
    managementPercent: number,
    managementAmount: number
  },
  constructionInterest: {
    senior: {
      method: string,
      coveragePercent: number,
      methodCost: number
    },
    mezz: {
      method: string,
      coveragePercent: number,
      methodCost: number
    }
  },
  absFees: {
    internalArrangerPercent: number,
    externalArrangerPercent: number,
    legalIssuer: number,
    legalUnderwriter: number,
    ratingAgency: number,
    trusteeSetup: number,
    payingAgentSetup: number,
    financialAdvisors: number,
    technicalAdvisors: number,
    insuranceAdvisor: number,
    listingFees: number,
    spvSetup: number,
    swapFee: number,
    greenBondFee: number,
    otherTransactionCosts: number
  },
  rollups: {
    capexInternalTotal: number,
    capexMarketTotal: number,
    landInfrastructureTotal: number,
    feesTotal: number,
    totalDay1Fees: number,
    grandTotalInternal: number,
    grandTotalMarket: number,
    developerProfit: number,
    developerMarginPercent: number
  }
}
```

---

## 18. Key Helper Functions

### Currency Formatting
- `parseCurrencyValue(value)` - Removes currency symbols and commas, returns number
- `formatCurrencyInput(value)` - Formats number with commas and currency symbol

### Calculation Functions
- `calculateSponsorTotals()` - Master calculation function (lines 8920-9200)
- `calculateCapexFromPerMW(type)` - Per MW → Total CapEx conversion
- `updateSponsorPowerCalculations()` - IT Load and Overhead calculations
- `updateSponsorTimeline()` - Timeline date calculations

### Auto-Fill Functions
- `updateLandFromQuality()` - Location Quality → Land Purchase
- `updateGridConnectionFromQuality()` - Grid Quality → Grid Costs
- `updateStampDutyFromStructure()` - SDLT Structure → Rate %

### UI Functions
- `switchCapexTab(type, mode)` - Toggle Per MW ↔ Detailed Breakdown
- `toggleElectricityRate()` - Show/hide electricity rate for Gross leases
- `switchSponsorTab(tab)` - Toggle Upload ↔ Manual Entry

---

## 19. Location Reference

**File:** templates/dashboard.html

**Key Line Ranges:**
- Project Metadata: Lines 2254-2433
- CapEx Internal: Lines 2435-2536
- CapEx Market: Lines 2538-2639
- Contingency: Lines 2641-2650
- Land & Infrastructure: Lines 2652-2765
- Developer Economics: Lines 2767-2808
- Fees (Simple): Lines 2810-2831
- Construction Interest Coverage: Lines 2833-2892
- ABS Fees: Lines 2894-2987
- Calculated Totals: Lines 2989-3200+
- Calculation Functions: Lines 8920-9200
- Save Function: Lines 9370-9521

---

**Last Updated:** 2026-01-19
**Total Editable Fields:** 87+
**Total Display Fields:** 30+
**Total Form Elements:** 117+
**Required Fields:** 16
**Auto-Calculated Fields:** 30+
