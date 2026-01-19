# Auto-Calculated Fields Reference Guide

## 📊 QUICK REFERENCE: All Formulas in Projects Form

---

## ✅ IMPLEMENTED & WORKING

### 1. IT Load (MW)

**Formula:**
```
IT Load = Gross Facility Power / PUE
```

**Example:**
```
Gross Facility Power: 100 MW
PUE: 1.25
IT Load: 100 / 1.25 = 80 MW
```

**Why Division (Not Multiplication):**
- PUE = Total Facility Power / IT Equipment Power
- Rearranging: IT Equipment Power = Total Facility Power / PUE
- Lower PUE = More efficient (less overhead)

**Field IDs:**
- Input: `sponsor-grossFacilityPower`
- Input: `sponsor-pue`
- Output: `sponsor-itLoad` (calculated, disabled)

**Function:** `updateSponsorPowerCalculations()` (line 8386)

**Triggers:**
- On change: Gross Facility Power
- On change: PUE

---

### 2. Overhead Power (MW)

**Formula:**
```
Overhead Power = Gross Facility Power - IT Load
```

**Example:**
```
Gross Facility Power: 100 MW
IT Load: 80 MW
Overhead Power: 100 - 80 = 20 MW
```

**What It Represents:**
- Cooling systems (HVAC)
- UPS losses
- Lighting and building systems
- Electrical distribution losses

**Field IDs:**
- Input: `sponsor-grossFacilityPower`
- Calculated: `sponsor-itLoad`
- Output: `sponsor-overheadPower` (calculated, disabled)

**Function:** `updateSponsorPowerCalculations()` (line 8386)

**Triggers:**
- On change: Gross Facility Power
- On change: PUE (affects IT Load, which affects Overhead)

---

### 3. Land Purchase Cost

**Formula:**
```
Land Purchase = Gross Facility Power × Acres per MW × Cost per Acre
```

**Presets:**

| Quality   | Cost/Acre | Acres/MW | Example (100 MW)      |
|-----------|-----------|----------|-----------------------|
| Rural     | €100,000  | 1.5      | 100 × 1.5 × €100k = €15M |
| Suburban  | €300,000  | 1.5      | 100 × 1.5 × €300k = €45M |
| Urban     | €800,000  | 1.0      | 100 × 1.0 × €800k = €80M |
| Custom    | User      | User     | User enters manually    |

**Example (Urban):**
```
Gross Facility Power: 100 MW
Acres per MW: 1.0 (urban is more compact)
Cost per Acre: €800,000
Land Purchase: 100 × 1.0 × €800,000 = €80,000,000
```

**Field IDs:**
- Input: `sponsor-grossFacilityPower`
- Input: `sponsor-landLocationQuality` (dropdown)
- Output: `sponsor-landPurchase`
- Display: `sponsor-landPurchaseDetails` (shows breakdown)

**Function:** `updateLandPurchaseFromQuality()` (line 8438)

**Triggers:**
- On change: Land Location Quality
- On change: Gross Facility Power

**Note:** Selecting "Custom" allows manual entry without auto-calculation.

---

### 4. Grid Connection Costs

**Formula:**
```
Grid Connection = Gross Facility Power × Cost per MW
```

**Presets:**

| Quality | Cost/MW   | Example (100 MW)      |
|---------|-----------|-----------------------|
| Good    | €200,000  | 100 × €200k = €20M    |
| Medium  | €400,000  | 100 × €400k = €40M    |
| Poor    | €600,000  | 100 × €600k = €60M    |
| Custom  | User      | User enters manually   |

**Example (Good Quality):**
```
Gross Facility Power: 100 MW
Cost per MW: €200,000
Grid Connection: 100 × €200,000 = €20,000,000
```

**What Quality Means:**
- **Good:** Existing substation nearby, minimal upgrades needed
- **Medium:** Substation upgrades required, some new infrastructure
- **Poor:** New substation required, extensive new infrastructure

**Field IDs:**
- Input: `sponsor-grossFacilityPower`
- Input: `sponsor-gridConnectionQuality` (dropdown)
- Output: `sponsor-gridConnectionCosts`
- Display: `sponsor-gridConnectionRate` (shows "€200,000 per MW")

**Function:** `updateGridConnectionFromQuality()` (line 8481)

**Triggers:**
- On change: Grid Connection Quality
- On change: Gross Facility Power

---

### 5. Stamp Duty (SDLT)

**Formula:**
```
Stamp Duty = Land Purchase × (Rate % / 100)
```

**OR (if Fixed Amount entered):**
```
Stamp Duty = Fixed Amount (overrides percentage)
```

**Presets:**

| Structure                 | Rate | Notes                                |
|---------------------------|------|--------------------------------------|
| Individual/Personal       | 5%   | Standard UK SDLT                     |
| Company/Corporate         | 5%   | Standard UK SDLT                     |
| Company + 3% Surcharge    | 8%   | Additional properties (3% extra)     |
| REIT/Institutional        | 0-5% | Often exempt or reduced              |
| Custom                    | User | Manual entry                         |

**Example (Company/Corporate):**
```
Land Purchase: €80,000,000
Stamp Duty Rate: 5%
Stamp Duty: €80M × 5% = €4,000,000
```

**Field IDs:**
- Input: `sponsor-landPurchase`
- Input: `sponsor-stampDutyStructure` (dropdown)
- Output: `sponsor-stampDutyPercent`
- Override: `sponsor-stampDutyFixed` (if entered, overrides %)

**Function:** `updateStampDutyFromStructure()` (line 8519)

**Triggers:**
- On change: Stamp Duty Structure
- On change: Land Purchase (recalculates duty)

**Override Behavior:**
- If Fixed Amount has value → Use Fixed Amount
- If Fixed Amount is empty → Use Land Purchase × Rate %

---

### 6. Construction Phase Fee

**Formula:**
```
Construction Fee = CapEx Subtotal × (User Percentage / 100)
```

**Default:**
```
User Percentage: 1.5%
Range: 0% - 5%
Step: 0.1%
```

**Example:**
```
CapEx Subtotal (sum of 16 line items): €100,000,000
Construction Fee Percent: 1.5%
Construction Fee: €100M × 1.5% = €1,500,000
```

**Field IDs:**
- Input: `sponsor-buildConstructionFeePercent` (editable!)
- Calculated from: Sum of 16 CapEx line items
- Output: Included in Total CapEx

**Function:** `calculateSponsorTotals()` (various lines)

**Triggers:**
- On change: Any CapEx line item
- On change: Construction Fee Percent

**Note:** This field was changed from readonly (auto-calculated at 1.5%) to editable per user request. Allows customization for different deal structures.

---

## ❓ NOT YET IMPLEMENTED

### 7. Developer Profit

**Formula (Recommended):**
```
Developer Profit (€) = Market CapEx Total - Internal CapEx Total
Developer Margin (%) = (Developer Profit / Internal CapEx) × 100
```

**Example:**
```
Internal CapEx (actual costs): €100,000,000
Market CapEx (bank valuation): €120,000,000
Developer Profit: €120M - €100M = €20,000,000
Developer Margin: (€20M / €100M) × 100 = 20%
```

**Why This Matters:**
- Shows developer/sponsor returns
- Banks use Market CapEx for loan-to-value (LTV) calculations
- Developer earns profit from the spread between cost and value
- Critical metric for equity investors

**Alternative Formula (with Developer Margin %):**
```
Developer Profit = (Market CapEx - Internal CapEx) × (Developer Margin % / 100)
```

**Example with 15% margin:**
```
Spread: €20,000,000
Developer Margin: 15%
Developer Profit: €20M × 15% = €3,000,000
Remaining €17M: Goes to structuring fees, other stakeholders
```

**Proposed Field IDs:**
- Calculated: `sponsor-developerProfit` (disabled display)
- Calculated: `sponsor-developerMarginPercent` (disabled display)

**Proposed Function:**
```javascript
function calculateDeveloperProfit() {
    const internalTotal = parseFloat(document.getElementById('sponsor-capex-internal-total')?.textContent?.replace(/[^0-9.-]/g, '')) || 0;
    const marketTotal = parseFloat(document.getElementById('sponsor-capex-market-total')?.textContent?.replace(/[^0-9.-]/g, '')) || 0;

    const developerProfit = marketTotal - internalTotal;
    const developerMarginPercent = internalTotal > 0 ? (developerProfit / internalTotal) * 100 : 0;

    // Update display fields (formatted with currency)
    // ...
}
```

**Triggers:**
- On change: Any Internal CapEx field
- On change: Any Market CapEx field
- On page load

**Placement:** Below Market CapEx section, before Fees section (after line 2650)

**Status:** ❓ Awaiting user decision to implement

---

## 📊 SUMMARY TABLE

| Field                | Formula                           | Status      | Function                           | Line  |
|----------------------|-----------------------------------|-------------|------------------------------------|-------|
| IT Load              | Gross Power / PUE                 | ✅ WORKING  | `updateSponsorPowerCalculations()` | 8386  |
| Overhead Power       | Gross Power - IT Load             | ✅ WORKING  | `updateSponsorPowerCalculations()` | 8386  |
| Land Purchase        | MW × Acres/MW × $/Acre            | ✅ WORKING  | `updateLandPurchaseFromQuality()`  | 8438  |
| Grid Connection      | MW × Cost/MW                      | ✅ WORKING  | `updateGridConnectionFromQuality()`| 8481  |
| Stamp Duty           | Land × Rate% OR Fixed             | ✅ WORKING  | `updateStampDutyFromStructure()`   | 8519  |
| Construction Fee     | Subtotal × User% (editable)       | ✅ EDITABLE | User input + `calculateSponsorTotals()` | 2530 |
| **Developer Profit** | **Market - Internal**             | ❓ PENDING  | **Needs implementation**           | -     |

---

## 🔧 CALCULATION FLOW

### On Page Load:
1. Load saved project data (if editing existing project)
2. Populate all input fields
3. Calculate IT Load and Overhead Power
4. Calculate Land Purchase (if quality selected)
5. Calculate Grid Connection (if quality selected)
6. Calculate Stamp Duty (if structure selected)
7. Calculate all CapEx totals
8. (Future) Calculate Developer Profit

### On Gross Facility Power Change:
1. Recalculate IT Load (Gross / PUE)
2. Recalculate Overhead Power (Gross - IT)
3. Recalculate Land Purchase (MW × preset values)
4. Recalculate Grid Connection (MW × preset cost)
5. Update MW displays in CapEx sections
6. Recalculate Per MW totals (if Per MW tab active)
7. (Future) Update Developer Profit

### On PUE Change:
1. Recalculate IT Load (Gross / PUE)
2. Recalculate Overhead Power (Gross - IT)

### On Land Location Quality Change:
1. Set Cost per Acre (based on preset)
2. Set Acres per MW (based on preset)
3. Calculate Land Purchase (MW × Acres/MW × Cost/Acre)
4. Recalculate Stamp Duty (if structure selected)
5. Recalculate Total CapEx

### On Grid Connection Quality Change:
1. Set Cost per MW (based on preset)
2. Calculate Grid Connection (MW × Cost/MW)
3. Recalculate Total CapEx

### On Stamp Duty Structure Change:
1. Set Rate % (based on preset)
2. Calculate Stamp Duty (Land × Rate%)
3. Recalculate Total CapEx

### On Any CapEx Field Change:
1. Recalculate subtotal (sum of all line items)
2. Calculate Construction Fee (subtotal × user %)
3. Calculate Total Internal CapEx
4. Calculate Total Market CapEx
5. (Future) Calculate Developer Profit

---

## 🎯 BEST PRACTICES

### When to Auto-Calculate:
✅ **DO auto-calculate when:**
- Formula is deterministic (one correct answer)
- User benefits from automation (saves time)
- Value depends on other fields (derived data)
- Industry has standard presets (land costs, grid costs, etc.)

### When to Allow Manual Override:
✅ **DO allow override when:**
- User may have specific deal terms (custom stamp duty)
- Negotiated rates differ from presets (special grid connection deal)
- Project has unique characteristics (irregular land shape)
- User wants to model "what-if" scenarios

### Display Format:
- Calculated fields: **Disabled input** with colored background
  - IT Load: Cyan background (`rgba(0, 212, 255, 0.1)`)
  - Overhead Power: Orange background (`rgba(255, 167, 38, 0.1)`)
  - Developer Profit (future): Cyan background
- Helper text: Show breakdown below field
  - "100 acres @ €800,000/acre"
  - "€200,000 per MW"
  - "Applied to land purchase price"

### Validation:
- Prevent negative values (min="0")
- Validate ranges (PUE typically 0.95-1.5)
- Show warnings for unusual values (PUE > 2.0 is inefficient)
- Recalculate on blur, not on every keystroke (performance)

---

## 🧪 TESTING CHECKLIST

### IT Load & Overhead Power:
- [ ] Enter Gross Facility Power = 100 MW, PUE = 1.25
- [ ] Verify IT Load = 80 MW (100 / 1.25)
- [ ] Verify Overhead = 20 MW (100 - 80)
- [ ] Change PUE to 1.0, verify IT Load = 100 MW, Overhead = 0 MW
- [ ] Change Gross to 50 MW, verify IT Load = 50 MW, Overhead = 0 MW

### Land Purchase:
- [ ] Select Rural, verify calculation: MW × 1.5 × €100k
- [ ] Select Suburban, verify: MW × 1.5 × €300k
- [ ] Select Urban, verify: MW × 1.0 × €800k
- [ ] Select Custom, verify manual entry allowed
- [ ] Change Gross MW, verify Land Purchase updates

### Grid Connection:
- [ ] Select Good, verify: MW × €200k
- [ ] Select Medium, verify: MW × €400k
- [ ] Select Poor, verify: MW × €600k
- [ ] Select Custom, verify manual entry allowed
- [ ] Change Gross MW, verify Grid Connection updates

### Stamp Duty:
- [ ] Select Individual (5%), verify: Land × 5%
- [ ] Select Company (5%), verify: Land × 5%
- [ ] Select Company+Surcharge (8%), verify: Land × 8%
- [ ] Enter Fixed Amount, verify percentage is overridden
- [ ] Clear Fixed Amount, verify percentage is used again

### Construction Fee:
- [ ] Verify default = 1.5%
- [ ] Change to 2.0%, verify total updates
- [ ] Set to 0%, verify fee = €0
- [ ] Set to 5% (max), verify capped at 5%
- [ ] Try to enter 10%, verify prevented or capped

---

## 📖 USER DOCUMENTATION

### For End Users:

**"Why are some fields grayed out?"**
> Grayed (disabled) fields are calculated automatically based on other inputs. For example, IT Load is calculated from Gross Facility Power and PUE. You cannot edit these directly.

**"Can I override the calculated values?"**
> Some fields like Land Purchase and Grid Connection can be overridden by selecting "Custom" from the dropdown. Construction Phase Fee is fully editable (0-5%).

**"What if my project has negotiated rates?"**
> Select "Custom" for Land Location Quality or Grid Connection Quality to enter your specific negotiated rates. For Stamp Duty, you can enter a Fixed Amount to override the percentage.

**"What is Developer Profit?"**
> Developer Profit is the difference between Market CapEx (what banks value the project at) and Internal CapEx (what you actually spend to build it). This spread represents potential developer returns.

---

**Status: ✅ 6/7 CALCULATIONS IMPLEMENTED**

**Next: Developer Profit calculation (30 minutes to implement)**

**See Also:**
- [CAPEX_TABS_IMPLEMENTATION.md](CAPEX_TABS_IMPLEMENTATION.md) - CapEx structure
- [REVENUE_SECTION_IMPLEMENTATION.md](REVENUE_SECTION_IMPLEMENTATION.md) - Conditional fields
- [ABS_CALCULATOR_MIGRATION_STATUS.md](ABS_CALCULATOR_MIGRATION_STATUS.md) - Overall progress
