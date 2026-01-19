# Management Fee Bidirectional Calculation

## 🎯 Overview

The Management Fee field now supports **bidirectional calculation** - users can edit either the percentage OR the euro amount, and the other value will automatically reverse-calculate.

---

## 📊 How It Works

### Two Input Fields:

1. **Management Fee %** (`sponsor-feesManagementPercent`)
   - Editable number input
   - Default: 3%
   - Range: 0-10%
   - Step: 0.1%
   - When changed → Calculates euro amount

2. **Management Fee Amount** (`sponsor-feesManagement`)
   - Editable text input (currency formatted)
   - When changed → Reverse-calculates percentage
   - Can also be auto-filled from % calculation

---

## 🔄 Calculation Logic

### Direction 1: Percentage → Amount (% → €)

**Function:** `calculateManagementFromPercent()` (lines 9001-9022)

**Trigger:** User edits Management Fee %

**Formula:**
```javascript
Management Fee Base = Internal CapEx + Land Purchase + Grid Connection
Management Fee Amount = Management Fee Base × (Percentage / 100)
```

**Example:**
```
Internal CapEx: €100,000,000
Land Purchase: €80,000,000
Grid Connection: €20,000,000
Management Fee Base: €200,000,000

User enters: 3%
Calculated Amount: €200M × 3% = €6,000,000
```

**Steps:**
1. User changes percentage field (e.g., from 3% to 4%)
2. Function calculates: Base × (4 / 100) = Amount
3. Updates Management Fee Amount field with formatted currency
4. Calls `calculateSponsorTotals()` to update all totals

---

### Direction 2: Amount → Percentage (€ → %)

**Function:** `calculateManagementPercent()` (lines 9024-9049)

**Trigger:** User edits Management Fee Amount

**Formula:**
```javascript
Management Fee Base = Internal CapEx + Land Purchase + Grid Connection
Management Fee Percentage = (Management Fee Amount / Management Fee Base) × 100
```

**Example:**
```
Internal CapEx: €100,000,000
Land Purchase: €80,000,000
Grid Connection: €20,000,000
Management Fee Base: €200,000,000

User enters: €10,000,000
Calculated %: (€10M / €200M) × 100 = 5%
```

**Steps:**
1. User changes amount field (e.g., types "10000000")
2. Function parses currency value
3. Calculates: (Amount / Base) × 100 = Percentage
4. Updates Management Fee % field (formatted to 2 decimals)
5. Calls `calculateSponsorTotals()` to update all totals

---

## 🧮 Integration with calculateSponsorTotals()

**Location:** Lines 8900-8923

**Priority Logic:**
1. Check if user has manually entered an amount
2. If manual amount exists → Use it (override % calculation)
3. If no manual amount → Calculate from percentage
4. Update the amount field display

**Code:**
```javascript
const managementFeeManual = parseCurrencyValue(managementFeeInput?.value);

if (managementFeeManual && managementFeeManual > 0) {
    // User has entered a manual amount - use it
    managementFee = managementFeeManual;
} else {
    // Calculate from percentage
    const managementPercent = parseFloat(document.getElementById('sponsor-feesManagementPercent')?.value) || 3;
    managementFee = managementFeeBase * (managementPercent / 100);
    // Update amount field
}
```

---

## 📍 HTML Structure

**Location:** Lines 2820-2830

```html
<!-- Management Fee % -->
<div>
    <label>Management Fee %</label>
    <input type="number"
           id="sponsor-feesManagementPercent"
           min="0" max="10" step="0.1" value="3"
           onchange="calculateManagementFromPercent()"
           placeholder="0-10%">
    <small>Default: 3% (editable)</small>
</div>

<!-- Management Fee Amount -->
<div>
    <label>Management Fee Amount</label>
    <input type="text"
           id="sponsor-feesManagement"
           onchange="calculateManagementPercent()"
           placeholder="Enter amount or auto-calculate from %">
    <small>Editable (overrides % calculation)</small>
</div>
```

---

## 🎬 User Experience Flow

### Scenario 1: User Changes Percentage
1. User sees default 3% in percentage field
2. User changes to 4%
3. **Instant:** Amount field updates to show calculated €8,000,000 (for example)
4. **Instant:** All totals recalculate

### Scenario 2: User Overrides with Custom Amount
1. User sees 3% = €6,000,000 (calculated)
2. User clicks on Amount field and types "7500000"
3. **Instant:** Percentage field updates to show 3.75%
4. **Instant:** All totals recalculate
5. **Next calculation:** If user changes any other field (CapEx, Land, Grid), the system will use the manual amount (€7.5M) instead of recalculating from %

### Scenario 3: Switching Back to Percentage-Based
1. User has entered custom amount: €7,500,000 (3.75%)
2. User changes percentage field to 4%
3. **Instant:** Amount recalculates to €8,000,000 (new % applied)
4. Manual override is cleared - system now tracks percentage

---

## 🧪 Testing Scenarios

### Test 1: Default Behavior
- [ ] Page loads with 3% default
- [ ] Amount field auto-calculates on page load
- [ ] Verify: Base × 3% = Displayed Amount

### Test 2: Change Percentage
- [ ] Change % from 3% to 5%
- [ ] Verify: Amount updates immediately
- [ ] Verify: New amount = Base × 5%
- [ ] Verify: Fees Total updates

### Test 3: Enter Custom Amount
- [ ] Type custom amount (e.g., €10,000,000)
- [ ] Verify: Percentage reverse-calculates
- [ ] Verify: New % = (€10M / Base) × 100
- [ ] Verify: Fees Total updates

### Test 4: Change Base Values
- [ ] Change Internal CapEx (e.g., add more build costs)
- [ ] Verify: If using % → Amount recalculates
- [ ] Verify: If using manual amount → Amount stays fixed, % adjusts

### Test 5: Edge Cases
- [ ] Enter 0% → Verify amount = €0
- [ ] Enter 10% (max) → Verify amount = Base × 10%
- [ ] Enter €0 in amount → Verify % = 0%
- [ ] Enter very large amount → Verify % calculates correctly

### Test 6: Currency Formatting
- [ ] Change currency from EUR to USD
- [ ] Verify: Amount field updates with $ symbol
- [ ] Verify: Calculations remain accurate

---

## 📐 Calculation Base

**What is included in the base:**
```
Management Fee Base = Internal CapEx + Land Purchase + Grid Connection
```

**Why this base:**
- Industry standard for infrastructure projects
- Represents the total "hard costs" of project development
- Excludes: Market CapEx (bank valuation), Fees themselves (avoid circular calculation)

**Example:**
```
Internal CapEx: €100,000,000
Land Purchase: €80,000,000
Grid Connection: €20,000,000
─────────────────────────────
Base: €200,000,000

At 3%: €6,000,000
At 4%: €8,000,000
At 5%: €10,000,000
```

---

## 🔧 Technical Details

### Functions:

| Function | Purpose | Trigger | Lines |
|----------|---------|---------|-------|
| `calculateManagementFromPercent()` | % → € | User changes percentage | 9001-9022 |
| `calculateManagementPercent()` | € → % | User changes amount | 9024-9049 |
| `calculateSponsorTotals()` | Uses value in totals | Any field change | 8900-8923 |

### Helper Functions Used:
- `parseCurrencyValue()` - Extracts numeric value from formatted currency string
- `formatCurrencyInput()` - Formats number as currency (€1,234,567)

### Event Handlers:
- `onchange="calculateManagementFromPercent()"` on percentage input
- `onchange="calculateManagementPercent()"` on amount input

---

## 🎯 Benefits

1. **Flexibility:** Users can work in their preferred unit (% or €)
2. **Transparency:** Both values always visible and in sync
3. **Override Capability:** Users can enter exact amounts for specific deals
4. **Real-time Updates:** Instant feedback as values change
5. **Intelligent Defaults:** Starts with industry-standard 3%

---

## 🔄 Similar to Per MW Costing

This bidirectional approach is similar to the Per MW CapEx fields:

| CapEx Per MW | Management Fee |
|--------------|----------------|
| User enters €/MW → Total calculates | User enters % → Amount calculates |
| User enters Total → €/MW calculates | User enters Amount → % calculates |
| Base = Gross MW | Base = Internal CapEx + Land + Grid |

Both provide flexibility for different workflow preferences!

---

## 📊 Status

- ✅ HTML fields created (% and Amount)
- ✅ `calculateManagementFromPercent()` function implemented
- ✅ `calculateManagementPercent()` function implemented
- ✅ Integration with `calculateSponsorTotals()` completed
- ✅ Currency formatting applied
- ⚠️ Ready for testing
- ⚠️ Ready for deployment

---

## 🚀 Next Steps

1. Test all scenarios listed above
2. Verify currency formatting across EUR/USD/GBP/JPY/AED
3. Test with real project data
4. Consider adding visual indicator (like "Custom" badge) when user has manually overridden
5. Deploy to Vercel

---

**See Also:**
- [AUTO_CALCULATED_FIELDS_REFERENCE.md](AUTO_CALCULATED_FIELDS_REFERENCE.md) - Other calculated fields
- [DEVELOPER_ECONOMICS_IMPLEMENTATION.md](DEVELOPER_ECONOMICS_IMPLEMENTATION.md) - Developer Profit calculation
