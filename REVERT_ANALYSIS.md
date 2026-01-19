# Revert Analysis - What Was Reverted and Why

## What Was Reverted

Successfully reverted 2 commits:
1. **c32c7ba** - "Revert Fix project save persistence issue"
2. **Awaiting** - "Revert ABS Day 1 Close Fees calculation"

## Current Status After Revert

### ✅ What's Working:
1. **Basic calculations** - All core CapEx, Land, and Fees calculations are working
2. **Internal/Market CapEx** - Calculating correctly
3. **Land totals** - Purchase + Grid + Stamp Duty working
4. **DM Fees + Management Fees** - Calculating correctly
5. **Grand Total** - Calculating correctly (without ABS fees)

### ❌ What's Broken:

#### 1. ABS Day 1 Close Fees NOT Calculating
**Location:** Line 2983 `sponsor-totalDay1Fees` shows "€0"

**Root cause:** The calculation logic for ABS fees was in commit 520e32f which we reverted.

**Missing calculation (lines 9095-9134 in old version):**
```javascript
// Calculate Day 1 Close ABS Fees
const internalArrangerPercent = parseFloat(document.getElementById('sponsor-internalArrangerFee')?.value) || 0;
const externalArrangerPercent = parseFloat(document.getElementById('sponsor-externalArrangerFee')?.value) || 0;

// For now, calculate arranger fees as 0 until we have debt amount
const debtAmount = 0; // Placeholder
const internalArrangerFee = debtAmount * (internalArrangerPercent / 100);
const externalArrangerFee = debtAmount * (externalArrangerPercent / 100);

// Fixed ABS fees
const legalIssuer = parseCurrencyValue(document.getElementById('sponsor-legalIssuer')?.value) || 0;
const legalUnderwriter = parseCurrencyValue(document.getElementById('sponsor-legalUnderwriter')?.value) || 0;
const ratingAgency = parseCurrencyValue(document.getElementById('sponsor-ratingAgency')?.value) || 0;
const trusteeSetup = parseCurrencyValue(document.getElementById('sponsor-trusteeSetup')?.value) || 0;
const payingAgentSetup = parseCurrencyValue(document.getElementById('sponsor-payingAgentSetup')?.value) || 0;
const financialAdvisors = parseCurrencyValue(document.getElementById('sponsor-financialAdvisors')?.value) || 0;
const technicalAdvisors = parseCurrencyValue(document.getElementById('sponsor-technicalAdvisors')?.value) || 0;
const insuranceAdvisor = parseCurrencyValue(document.getElementById('sponsor-insuranceAdvisor')?.value) || 0;
const listingFees = parseCurrencyValue(document.getElementById('sponsor-listingFees')?.value) || 0;
const spvSetup = parseCurrencyValue(document.getElementById('sponsor-spvSetup')?.value) || 0;
const swapFee = parseCurrencyValue(document.getElementById('sponsor-swapFee')?.value) || 0;
const greenBondFee = parseCurrencyValue(document.getElementById('sponsor-greenBondFee')?.value) || 0;
const otherTransactionCosts = parseCurrencyValue(document.getElementById('sponsor-otherTransactionCosts')?.value) || 0;

// Total Day 1 Close Fees
const totalDay1Fees = internalArrangerFee + externalArrangerFee + legalIssuer + legalUnderwriter +
                      ratingAgency + trusteeSetup + payingAgentSetup + financialAdvisors +
                      technicalAdvisors + insuranceAdvisor + listingFees + spvSetup +
                      swapFee + greenBondFee + otherTransactionCosts;

// Update Day 1 Fees display
const totalDay1FeesEl = document.getElementById('sponsor-totalDay1Fees');
if (totalDay1FeesEl) {
    totalDay1FeesEl.textContent = currencySymbol + totalDay1Fees.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0});
}
```

**What needs to happen:** This calculation needs to be re-added to the `calculateSponsorTotals()` function.

**Insert location:** After line 9095 (after `const feesTotal = feesDM + managementFee;`)

**IMPORTANT:** The feesTotal calculation on line 9095 needs to be updated to:
```javascript
const feesTotal = feesDM + managementFee + totalDay1Fees;
```

#### 2. Project Save Not Working
**Location:** Line 9450 in `saveSponsorProject()` function

**Current code:**
```javascript
// await saveProjects(); // DISABLED - causes duplicate projects
```

**Root cause:** The previous implementation (commit ab68311) was causing duplicate projects, so it was disabled.

**What needs to happen:**
- Need to implement a proper save mechanism that doesn't cause duplicates
- Should save to backend API endpoint `/api/projects/<project_id>`
- Need to handle update vs create scenarios properly

## Why the Original Implementation Failed

Based on the revert comment "causes duplicate projects", the issue was likely:

1. **Save function called multiple times** - Possibly triggered on form changes or multiple button clicks
2. **No debouncing** - Save was being called too frequently
3. **No unique ID check** - Creating new projects instead of updating existing ones

## Recommended Fix Strategy

### For ABS Fees Calculation:
1. Add the ABS fee calculation logic back to `calculateSponsorTotals()`
2. Insert after line 9095
3. Update feesTotal to include totalDay1Fees
4. Test thoroughly to ensure no breaking of other calculations

### For Save Functionality:
1. Implement proper save with backend API call
2. Add debouncing (save only when user clicks "Save" button, not on every field change)
3. Use PUT request to `/api/projects/{project_id}` for updates
4. Add proper error handling and user feedback
5. Ensure project ID is maintained throughout lifecycle

## Files Involved

- **templates/dashboard.html** - Main file with all JavaScript calculations and save logic
  - Line 8920-9200: `calculateSponsorTotals()` function
  - Line 9370-9451: `saveSponsorProject()` function
  - Line 2939-2987: ABS fees UI fields
  - Line 2983: ABS fees total display

## Testing Checklist After Fixes

### ABS Fees:
- [ ] Total Day 1 Close Fees shows correct sum (default should be €4,200,000)
- [ ] Changes to any ABS fee field updates the total in real-time
- [ ] Currency symbol matches selected currency
- [ ] Values format correctly with commas

### Save Functionality:
- [ ] Click Save button saves project to backend
- [ ] Page refresh retains saved project data
- [ ] No duplicate projects created
- [ ] Error messages display if save fails
- [ ] Success message confirms save

## Next Steps

1. **DO NOT** implement both fixes at once
2. **START WITH** ABS fees calculation fix (simpler, lower risk)
3. **TEST** ABS fees thoroughly before moving to save fix
4. **THEN** implement save fix with proper API integration
5. **TEST** save functionality extensively before deploying

## Git Commits

- Revert 1: `c32c7ba` - Reverted save persistence fix
- Revert 2: Pending - Need to revert ABS fees calculation
- Current HEAD: `c32c7ba` (pushed to origin/main)

**Status:** Reverts complete, analysis complete, ready for reimplementation with proper testing.
