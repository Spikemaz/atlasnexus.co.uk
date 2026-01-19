# Comprehensive Calculated Totals Implementation

## 🎯 Overview

The Calculated Totals section has been completely rebuilt to match the comprehensive dashboard from [atlas_abs_calculator_v2.0_complete_FIXED.html](atlas_abs_calculator_v2.0_complete_FIXED.html), featuring an Investment Timeline, detailed project cost breakdowns, and a Revenue & NOI Waterfall.

---

## 📊 New Sections Added

### 1. Investment Timeline Visualization

**Location:** Lines 2995-3054

**Visual Elements:**
- **Today** (Orange dot) - Current date
- **Day 1 Close** (Blue dot) - Financial close date
- **Complete** (Green dot) - Construction complete/COD
- **Revenue Begins** (Gold dot) - Revenue start date
- **Maturity** (Purple dot) - End of debt tenor

**Connectors:**
- Preparation period (Today → Day 1)
- Construction duration (Day 1 → Complete)
- Operating period (Revenue → Maturity)

**Dynamic Updates:**
- All dates and durations update based on:
  - Construction Start Date
  - Construction Duration
  - Debt Tenor
  - Current date

**Field IDs:**
| Element | ID | Updates From |
|---------|-----|--------------|
| Today | `sponsor-timeline-today` | Current date |
| Day 1 Close | `sponsor-timeline-day1` | Construction Start |
| Complete | `sponsor-timeline-complete` | Start + Duration |
| Revenue Begins | `sponsor-timeline-revenue` | Same as Complete |
| Maturity | `sponsor-timeline-maturity` | Complete + Tenor |
| Construction Duration | `sponsor-timeline-duration` | Construction Duration field |
| Operating Period | `sponsor-timeline-operating` | Debt Tenor field |

---

### 2. Project Costs Breakdown

**Location:** Lines 3056-3123

#### A. Internal CapEx (DARK Cost)

**Color:** Cyan (`#00d4ff`)

**Components:**
- **Base** - Sum of all build line items (before contingency)
- **Contingency** - Calculated from Contingency %
- **Total** - Base + Contingency

**Field IDs:**
- `sponsor-capexInternalBase` - Base amount
- `sponsor-contingencyInternal` - Contingency amount
- `sponsor-capexInternalTotal` - Total (already existed)

**Example:**
```
Base: €100,000,000
Contingency (10%): €10,000,000
──────────────────────────────
Total: €110,000,000
```

#### B. Market CapEx (Debt Raised)

**Color:** Gold (`#ffd700`)

**Components:**
- **Base** - Sum of all market build line items (before contingency)
- **Contingency** - Calculated from Contingency %
- **Total** - Base + Contingency

**Field IDs:**
- `sponsor-capexMarketBase` - Base amount
- `sponsor-contingencyMarket` - Contingency amount
- `sponsor-capexMarketTotal` - Total (already existed)

**Why Different from Internal:**
- Market values represent bank appraisal value
- Used for loan-to-value (LTV) calculations
- Typically higher than internal costs
- The spread creates developer profit

#### C. Site Acquisition

**Color:** Orange (`#ffa726`)

**Components:**
- **Land Purchase** - Total land acquisition cost
- **Grid Connection** - Infrastructure connection cost
- **Stamp Duty** - Transfer tax
- **Site Purchase Amount** - Total of all three

**Field IDs:**
- `sponsor-landBreakdownPurchase` - Land cost
- `sponsor-landBreakdownGrid` - Grid cost
- `sponsor-landBreakdownStamp` - Stamp duty
- `sponsor-landTotal` - Total (already existed)

**Example:**
```
Land Purchase: €80,000,000
Grid Connection: €20,000,000
Stamp Duty: €4,000,000
──────────────────────────────
Site Purchase Amount: €104,000,000
```

#### D. Day 1 Close Fees

**Color:** Green (`#4caf50`)

**Components:**
- **Upfront Fees** - DM + Management fees

**Field IDs:**
- `sponsor-feesTotal` - Total fees (already existed)

**What's Included:**
- Development Management (DM) fees
- Management fees (now bidirectional % ↔ €)
- Paid at financial close
- Capitalized into debt

---

### 3. Grand Totals (Three Versions)

**Location:** Lines 3125-3156

#### A. Internal Grand Total

**Color:** Cyan (`#00d4ff`)

**Formula:**
```
Internal Grand Total = Internal CapEx + Land Total + Upfront Fees
```

**What It Represents:**
- DARK's actual cost to build
- Real cash outlay
- Cost basis for developer returns

**Field ID:** `sponsor-grandTotal`

**Example:**
```
Internal CapEx: €110,000,000
Land Total: €104,000,000
Upfront Fees: €6,000,000
──────────────────────────────
Internal Grand Total: €220,000,000
```

#### B. Market Grand Total

**Color:** Gold (`#ffd700`)

**Formula:**
```
Market Grand Total = Market CapEx + Land Total + Upfront Fees
```

**What It Represents:**
- Total debt raised at Day 1 Close
- Bank appraisal value
- Basis for LTV calculations

**Field ID:** `sponsor-grandTotalMarket`

**Example:**
```
Market CapEx: €132,000,000 (20% higher than internal)
Land Total: €104,000,000
Upfront Fees: €6,000,000
──────────────────────────────
Market Grand Total: €242,000,000
```

#### C. DARK Development Profit

**Color:** Green (`#4caf50`)

**Formula:**
```
DARK Development Profit = Market Grand Total - Internal Grand Total
```

**What It Represents:**
- Spread between market value and actual cost
- Developer equity value creation
- Paid on completion (COD)

**Field ID:** `sponsor-darkProfit`

**Example:**
```
Market Grand Total: €242,000,000
Internal Grand Total: €220,000,000
──────────────────────────────
DARK Development Profit: €22,000,000
```

**Developer Margin:**
```
Margin % = (€22M / €220M) × 100 = 10%
```

---

### 4. Revenue & NOI Waterfall (Year 1)

**Location:** Lines 3158-3187

**Color:** Cyan theme (`#00d4ff`)

**Purpose:** Calculate Net Operating Income available for debt service

#### Waterfall Steps:

**1. Gross Annual Revenue**

**Formula:**
```
Gross Annual Revenue = Monthly Rent × 12 × (Occupancy % / 100)
```

**Example:**
```
Monthly Rent: €1,000,000
Occupancy: 95%
Gross Annual Revenue: €1,000,000 × 12 × 0.95 = €11,400,000
```

**Field ID:** `sponsor-noiGrossRevenue`

---

**2. Less: Electricity (if Gross lease)**

**Formula:**
```
Electricity Cost = IT Load (MW) × 8760 hours × Rate per MWh
```

**Conditional:** Only applies if Lease Type = "Gross"

**Example:**
```
IT Load: 80 MW
Hours per year: 8760
Electricity Rate: €100/MWh
Electricity Cost: 80 × 8760 × €100 = €70,080,000
```

**Field ID:** `sponsor-noiElectricity`

**Note:** For Triple Net leases, this displays €0 (tenant pays electricity)

---

**3. Less: Other OpEx**

**Formula:**
```
Other OpEx = Gross Annual Revenue × (OpEx % / 100)
```

**Example:**
```
Gross Revenue: €11,400,000
OpEx %: 5%
Other OpEx: €11,400,000 × 5% = €570,000
```

**Field ID:** `sponsor-noiOtherOpex`

**What's Included:**
- Property management
- Insurance
- Maintenance reserves
- Security, landscaping, utilities (if applicable)

---

**4. = Net Operating Income (NOI)**

**Formula:**
```
NOI (before AMF) = Gross Revenue - Electricity - Other OpEx
```

**Example:**
```
Gross Revenue: €11,400,000
Electricity: €0 (Triple Net)
Other OpEx: €570,000
NOI: €11,400,000 - €0 - €570,000 = €10,830,000
```

**Field ID:** `sponsor-noiBeforeAMF`

---

**5. Less: Asset Management Fee**

**Formula:**
```
Asset Mgmt Fee = NOI (before AMF) × 1%
```

**Example:**
```
NOI: €10,830,000
AMF: €10,830,000 × 1% = €108,300
```

**Field ID:** `sponsor-noiAMF`

**Purpose:** Ongoing fee for managing the asset

---

**6. = NOI for Debt Service**

**Formula:**
```
NOI for Debt Service = NOI (before AMF) - Asset Mgmt Fee
```

**Example:**
```
NOI: €10,830,000
AMF: €108,300
NOI for Debt Service: €10,721,700
```

**Field ID:** `sponsor-noiForDebtService`

**Purpose:** This is the cash available to service debt (pay interest & principal)

**DSCR Calculation:**
```
DSCR = NOI for Debt Service / Annual Debt Service
```

---

## 🔧 JavaScript Implementation

### Main Calculation Function

**Function:** `calculateSponsorTotals()`

**Location:** Lines 8920-9152

**Enhanced With:**

```javascript
// Update COMPREHENSIVE TOTALS SECTION - New Breakdown Elements

// Internal CapEx Breakdown
const capexInternalBaseEl = document.getElementById('sponsor-capexInternalBase');
const contingencyInternalEl = document.getElementById('sponsor-contingencyInternal');
if (capexInternalBaseEl) capexInternalBaseEl.textContent = currencySymbol + internalCapexBase.toLocaleString(...);
if (contingencyInternalEl) contingencyInternalEl.textContent = currencySymbol + internalCapexContingency.toLocaleString(...);

// Market CapEx Breakdown
const capexMarketBaseEl = document.getElementById('sponsor-capexMarketBase');
const contingencyMarketEl = document.getElementById('sponsor-contingencyMarket');
if (capexMarketBaseEl) capexMarketBaseEl.textContent = currencySymbol + marketCapexBase.toLocaleString(...);
if (contingencyMarketEl) contingencyMarketEl.textContent = currencySymbol + marketCapexContingency.toLocaleString(...);

// Land Breakdown
const landBreakdownPurchaseEl = document.getElementById('sponsor-landBreakdownPurchase');
const landBreakdownGridEl = document.getElementById('sponsor-landBreakdownGrid');
const landBreakdownStampEl = document.getElementById('sponsor-landBreakdownStamp');
if (landBreakdownPurchaseEl) landBreakdownPurchaseEl.textContent = currencySymbol + landPurchase.toLocaleString(...);
if (landBreakdownGridEl) landBreakdownGridEl.textContent = currencySymbol + gridConnection.toLocaleString(...);
if (landBreakdownStampEl) landBreakdownStampEl.textContent = currencySymbol + stampDuty.toLocaleString(...);

// Grand Totals - Market and DARK Profit
const grandTotalMarket = marketCapexTotal + landTotal + feesTotal;
const darkProfit = grandTotalMarket - grandTotal;

if (grandTotalMarketEl) grandTotalMarketEl.textContent = currencySymbol + grandTotalMarket.toLocaleString(...);
if (darkProfitEl) darkProfitEl.textContent = currencySymbol + darkProfit.toLocaleString(...);

// Calculate NOI Waterfall
calculateNOIWaterfall();
```

---

### NOI Waterfall Function

**Function:** `calculateNOIWaterfall()`

**Location:** Lines 9192-9243

**Inputs:**
- `sponsor-grossMonthlyRent` - Monthly rent
- `sponsor-occupancy` - Occupancy %
- `sponsor-leaseType` - Triple Net or Gross
- `sponsor-electricityRate` - Rate per MWh (if Gross)
- `sponsor-itLoad` - IT Load in MW
- `sponsor-opexPercent` - OpEx %

**Calculations:**
```javascript
// Gross Annual Revenue
const grossAnnualRevenue = grossMonthlyRent × 12 × (occupancy / 100);

// Electricity Cost (conditional)
if (leaseType === 'Gross') {
    electricityCost = itLoad × 8760 × electricityRate;
}

// Other OpEx
const otherOpex = grossAnnualRevenue × opexPercent;

// NOI before AMF
const noiBeforeAMF = grossAnnualRevenue - electricityCost - otherOpex;

// Asset Management Fee
const assetMgmtFee = noiBeforeAMF × 0.01;

// NOI for Debt Service
const noiForDebtService = noiBeforeAMF - assetMgmtFee;
```

**Outputs:**
- Updates 6 display fields with calculated values
- Uses revenue currency (GBP/EUR/USD/etc.)
- Formats with proper currency symbols

---

## 🎨 Color Scheme

| Section | Color Code | Hex | Usage |
|---------|-----------|-----|-------|
| Internal CapEx | Cyan | `#00d4ff` | DARK's cost basis |
| Market CapEx | Gold | `#ffd700` | Bank valuation/debt |
| Site Acquisition | Orange | `#ffa726` | Land & infrastructure |
| Day 1 Fees | Green | `#4caf50` | Upfront fees |
| Developer Profit | Green | `#4caf50` | Equity value creation |
| NOI Waterfall | Cyan | `#00d4ff` | Revenue calculations |

**Visual Hierarchy:**
- Bold section titles with icons
- Light background with colored borders
- Darker text for labels (#94a3b8)
- White text for values
- Bold totals with larger font

---

## 🧪 Testing Scenarios

### Test 1: Internal vs Market CapEx

**Setup:**
```
Internal Build Total: €100,000,000
Market Build Total: €120,000,000
Contingency: 10%
```

**Expected Results:**
```
Internal Base: €100,000,000
Internal Contingency: €10,000,000
Internal Total: €110,000,000

Market Base: €120,000,000
Market Contingency: €12,000,000
Market Total: €132,000,000
```

---

### Test 2: DARK Development Profit

**Setup:**
```
Internal Grand Total: €220,000,000
Market Grand Total: €242,000,000
```

**Expected Results:**
```
DARK Profit: €22,000,000
Margin: 10%
```

---

### Test 3: NOI Waterfall - Triple Net Lease

**Setup:**
```
Monthly Rent: €1,000,000
Occupancy: 95%
Lease Type: Triple Net
OpEx %: 5%
```

**Expected Results:**
```
Gross Annual Revenue: €11,400,000
Electricity: €0
Other OpEx: €570,000
NOI (before AMF): €10,830,000
AMF (1%): €108,300
NOI for Debt Service: €10,721,700
```

---

### Test 4: NOI Waterfall - Gross Lease

**Setup:**
```
Monthly Rent: €1,000,000
Occupancy: 95%
Lease Type: Gross
OpEx %: 5%
IT Load: 80 MW
Electricity Rate: €100/MWh
```

**Expected Results:**
```
Gross Annual Revenue: €11,400,000
Electricity: 80 × 8760 × €100 = €70,080,000
Other OpEx: €570,000
NOI (before AMF): -€59,250,000 (negative!)
AMF (1%): -€592,500
NOI for Debt Service: -€58,657,500
```

**Note:** Gross lease with high electricity cost can result in negative NOI - this is realistic and expected!

---

### Test 5: Currency Changes

**Setup:**
```
Change CapEx Currency: EUR → USD
```

**Expected Results:**
- All CapEx breakdown values update with $ symbol
- Land breakdown updates with $ symbol
- All grand totals update with $ symbol
- NOI Waterfall maintains revenue currency (GBP/EUR/etc.)

---

### Test 6: Timeline Updates

**Setup:**
```
Construction Start: Feb 2026
Construction Duration: 18 months
Debt Tenor: 20 years
```

**Expected Results:**
```
Today: Jan 2026
Day 1 Close: Feb 2026
Construction Duration: 18 months
Complete: Aug 2027
Revenue Begins: Aug 2027
Operating Period: 20 years
Maturity: Aug 2047
```

---

## 📈 Key Formulas Reference

### CapEx Calculations:
```
Internal CapEx Base = Sum of all internal build fields
Internal CapEx Contingency = Base × (Contingency % / 100)
Internal CapEx Total = Base + Contingency

Market CapEx Base = Sum of all market build fields
Market CapEx Contingency = Base × (Contingency % / 100)
Market CapEx Total = Base + Contingency
```

### Grand Totals:
```
Internal Grand Total = Internal CapEx Total + Land Total + Fees Total
Market Grand Total = Market CapEx Total + Land Total + Fees Total
DARK Profit = Market Grand Total - Internal Grand Total
Developer Margin % = (DARK Profit / Internal Grand Total) × 100
```

### NOI Waterfall:
```
Gross Annual Revenue = Monthly Rent × 12 × (Occupancy % / 100)
Electricity Cost = IT Load (MW) × 8760 × Rate per MWh  (if Gross lease)
Other OpEx = Gross Revenue × (OpEx % / 100)
NOI (before AMF) = Gross Revenue - Electricity - Other OpEx
Asset Mgmt Fee = NOI × 1%
NOI for Debt Service = NOI - AMF
```

---

## 🚀 Status

- ✅ Investment Timeline visualization
- ✅ Project Costs Breakdown (4 sections)
- ✅ Three Grand Totals (Internal, Market, Profit)
- ✅ Revenue & NOI Waterfall (Year 1)
- ✅ calculateNOIWaterfall() function
- ✅ Enhanced calculateSponsorTotals()
- ✅ Currency formatting across all sections
- ✅ Real-time updates
- ⚠️ Ready for testing
- ⚠️ Deployed to Vercel

---

## 🔗 Related Documentation

- [AUTO_CALCULATED_FIELDS_REFERENCE.md](AUTO_CALCULATED_FIELDS_REFERENCE.md) - All calculated field formulas
- [DEVELOPER_ECONOMICS_IMPLEMENTATION.md](DEVELOPER_ECONOMICS_IMPLEMENTATION.md) - Developer Profit calculations
- [MANAGEMENT_FEE_BIDIRECTIONAL.md](MANAGEMENT_FEE_BIDIRECTIONAL.md) - Management Fee % ↔ € logic
- [REVENUE_SECTION_IMPLEMENTATION.md](REVENUE_SECTION_IMPLEMENTATION.md) - Revenue parameters and conditional fields

---

**Total Implementation:** ~300 lines of HTML + ~150 lines of JavaScript

**Visual Inspiration:** atlas_abs_calculator_v2.0_complete_FIXED.html

**Styling:** Adapted to match Projects form dark theme with cyan/gold/orange/green color scheme
