# 🚀 HOW TO USE PHASE-1 FEATURES

## Step 1: Access Admin Panel

1. Go to: **https://atlasnexus.co.uk/admin-panel**
2. Login with your admin credentials
3. Complete MFA verification

## Step 2: Navigate to Phase-1 Features

Once logged in, you'll see the menu on the left side with:

### 📁 Phase-1: Projects
- Click **"Phase-1: Projects"** in the menu
- Fill out the project form with:
  - Project Title: "London DC Alpha"
  - Country: UK
  - Currency: GBP
  - IT Load: 75 MW
  - PUE: 1.25
  - Lease Years: 25
  - Tenant Rating: AA
  - Monthly Rent: 2500000
  - CapEx per MW: 5400000
- Click **"Validate Project"**
- You'll see derived fields like funding need, DSCR floor, etc.

### 🔢 Phase-1: Permutations
- Click **"Phase-1: Permutations"** in the menu
- Choose a preset:
  - **Conservative A**: Narrow ranges, high DSCR
  - **Balanced A**: Medium ranges
  - **Aggressive A**: Wide ranges, lower DSCR
- Or set custom ranges:
  - Senior Tenor: Select years (7, 10, 12, 15, 20)
  - Senior Coupon: Min 4%, Max 6%, Step 0.25%
  - Senior DSCR: Min 1.25, Max 1.45, Step 0.05
- Watch the **Cardinality Preview** update (e.g., "1,920 permutations")

### ⚙️ Phase-1: Run Engine
- Click **"Phase-1: Run Engine"** in the menu
- Enter Seed: 424242 (for reproducible results)
- Click **"Run Engine"**
- Wait for processing (shows progress)
- Results appear with:
  - Total permutations processed
  - Diamond/Gold/Silver counts
  - Top-20 structures

### 📊 Phase-1: Securitisation
- Click **"Phase-1: Securitisation"** in the menu
- View Top-20 results with:
  - Tier badges (Diamond/Gold/Silver)
  - Senior amount, coupon, tenor
  - DSCR values
  - WAL (Weighted Average Life)
  - Day-one values
  - Repo eligibility
- Click **"Export"** on any structure for full term sheet

### 🔧 Phase-1: Ops Monitor
- Click **"Phase-1: Ops Monitor"** in the menu
- View system status:
  - Canary deployment percentage
  - Error rates
  - Memory usage
  - Performance metrics

## Alternative: Direct API Access

If the UI isn't loading properly, you can use the API directly:

### Via Browser Console (when logged in as admin):

```javascript
// Validate project
fetch('/api/phase1/projects/validate', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    title: "London DC Alpha",
    country: "UK",
    currency: "GBP",
    gross_it_load_mw: 75,
    pue: 1.25,
    lease_years: 25,
    tenant_rating: "AA",
    gross_monthly_rent: 2500000,
    capex_cost_per_mw: 5400000
  })
}).then(r => r.json()).then(console.log)

// Run engine
fetch('/api/phase1/run', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    seed: 424242,
    topn: 20,
    ranges: {
      senior_tenor: [10, 12, 15, 20],
      senior_coupon: {min: 0.04, max: 0.06, step: 0.0025},
      min_dscr_senior: {min: 1.25, max: 1.45, step: 0.05}
    }
  })
}).then(r => r.json()).then(console.log)

// Get Top-20
fetch('/api/phase1/securitisation/top20', {
  credentials: 'include'
}).then(r => r.json()).then(console.log)

// Single calculator
fetch('/api/phase1/calc', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    noi_monthly: 1950000,
    funding_need: 415000000,
    senior: {coupon_pct: 0.055, tenor_years: 15, min_dscr: 1.25}
  })
}).then(r => r.json()).then(console.log)
```

## Troubleshooting

### If you see "Admin access required":
- Make sure you're logged in as admin
- Check that MFA verification is complete
- Try refreshing the page

### If Phase-1 menu items don't appear:
- Clear browser cache
- Hard refresh (Ctrl+F5)
- Check browser console for errors

### If API calls fail:
- Verify you're on HTTPS (not HTTP)
- Check that cookies are enabled
- Ensure you're using the production domain

## Features Summary

You have built and deployed:

1. **Project Validation** (/api/phase1/projects/validate)
   - Validates data center projects
   - Calculates derived fields

2. **Permutation Engine** (/api/phase1/run)
   - Processes up to 250k permutations
   - Ranks by day-one value
   - Returns Top-20 structures

3. **Single Calculator** (/api/phase1/calc)
   - Instant stack calculations
   - Reverse-engineers from DSCR
   - No session required

4. **Async Runner** (/api/phase1/run/submit)
   - For 50k-250k sweeps
   - Progress tracking
   - Background processing

5. **Export System** (/api/phase1/securitisation/export/{rank})
   - Full term sheets
   - Waterfall analysis
   - Stress testing grids

All these features are LIVE on https://atlasnexus.co.uk and accessible through the admin panel!