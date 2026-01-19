# 13 Primary Output KPIs - Detailed Explanation

## Overview

For each permutation scenario, the engine calculates **13 Primary Key Performance Indicators (KPIs)**. These metrics evaluate the financial viability, risk profile, and investment attractiveness of each capital structure configuration.

---

## 1. **SeniorNotional** 💰

### What It Is
The maximum principal amount of senior debt that can be raised while maintaining the target Debt Service Coverage Ratio (DSCR).

### Why It Matters
- **Lender Perspective:** Largest amount they can safely lend
- **Sponsor Perspective:** More debt = less equity required = higher leverage = higher returns
- **Goal:** Maximize this value while staying investment-grade

### How It's Calculated
Using a **binary search algorithm** that finds the optimal debt amount where:
```
DSCR = NetIncome / DebtService ≥ TargetDSCR
```

### Example
```
NetIncome: £22.5M/year
TargetDSCR: 1.35
SeniorCoupon: 5.5%
SeniorTenor: 25 years

Result: SeniorNotional = £390,000,000
```

**Interpretation:** The project can support £390M of senior debt while maintaining a 1.35x safety cushion on debt service payments.

### Typical Range
- Data Centers: £200M - £800M
- Small Projects: £50M - £200M
- Large Infrastructure: £1B+

---

## 2. **DSCR_Min** 📉

### What It Is
The **minimum** Debt Service Coverage Ratio across all periods of the loan term. This is the "worst case" coverage ratio.

### Why It Matters
- **Most Critical Risk Metric** for lenders
- Even one period with DSCR < 1.0 means potential default
- Rating agencies focus heavily on this metric
- Lower DSCR_Min = higher risk = lower rating = higher cost of capital

### Formula
```
DSCR_Min = Minimum of (NetIncome[t] / DebtService[t]) for all periods t
```

### Example
```
Year 1: NetIncome £22.5M / DebtService £16.67M = 1.35x
Year 5: NetIncome £23.2M / DebtService £16.67M = 1.39x
Year 10: NetIncome £24.8M / DebtService £16.67M = 1.49x
Year 15: NetIncome £22.1M / DebtService £16.67M = 1.33x ← Minimum

DSCR_Min = 1.33
```

**Interpretation:** Even in the worst year, the project generates 1.33x the cash needed to service debt.

### Rating Impact
```
DSCR_Min ≥ 1.50 → AAA (70 bps spread)
DSCR_Min ≥ 1.35 → AA  (90 bps spread)
DSCR_Min ≥ 1.25 → A   (120 bps spread)
DSCR_Min ≥ 1.15 → BBB (180 bps spread)
DSCR_Min ≥ 1.05 → BB  (300+ bps spread)
DSCR_Min <  1.05 → B  (unfinanceable)
```

### Typical Targets
- **Senior AAA:** 1.45-1.60x
- **Senior AA:** 1.30-1.45x
- **Senior A:** 1.20-1.35x
- **Mezzanine:** 1.10-1.20x

---

## 3. **DSCR_Avg** 📊

### What It Is
The **average** Debt Service Coverage Ratio across the entire loan term.

### Why It Matters
- Shows overall strength of cash flow coverage
- Higher average = more breathing room for unexpected issues
- Used for sensitivity analysis and stress testing
- Indicates how much "fat" exists in the structure

### Formula
```
DSCR_Avg = Average of (NetIncome[t] / DebtService[t]) for all periods t
```

### Example
```
Year 1-25 DSCRs: [1.35, 1.37, 1.39, 1.41, ..., 1.45, 1.42]
Sum = 35.25
Count = 25 years

DSCR_Avg = 35.25 / 25 = 1.41x
```

**Interpretation:** On average over 25 years, the project generates 1.41x the debt service requirement.

### Relationship to DSCR_Min
```
Ideal: DSCR_Avg > DSCR_Min by 0.10-0.20x
Warning: DSCR_Avg ≈ DSCR_Min (flat cashflow, no growth cushion)
Good: DSCR_Avg = 1.50, DSCR_Min = 1.35 (15 bps cushion)
```

---

## 4. **SeniorRating** ⭐

### What It Is
The credit rating assigned to the senior debt tranche based on DSCR_Min and other structural features.

### Why It Matters
- **Directly impacts cost of capital:** AAA pays 70 bps, BBB pays 180 bps
- **Investor eligibility:** Many institutional investors require investment-grade (≥BBB)
- **Repo eligibility:** Central banks typically only accept AAA/AA
- **Pricing power:** Higher rating = more demand = tighter spreads

### How It's Determined
```
Primary Driver: DSCR_Min
Secondary Factors:
  - Tenant credit quality
  - Contract length
  - Collateral quality
  - Jurisdiction
  - Structural features (wrap, liquidity, etc.)
```

### Rating Matrix
```
DSCR_Min ≥ 1.50 → AAA
  ├─ Credit Spread: 70 bps
  ├─ Repo Eligible: Yes
  └─ Investor Universe: Broadest

DSCR_Min ≥ 1.35 → AA
  ├─ Credit Spread: 90 bps
  ├─ Repo Eligible: Yes
  └─ Investor Universe: Very broad

DSCR_Min ≥ 1.25 → A
  ├─ Credit Spread: 120 bps
  ├─ Repo Eligible: Sometimes
  └─ Investor Universe: Broad

DSCR_Min ≥ 1.15 → BBB
  ├─ Credit Spread: 180 bps
  ├─ Repo Eligible: No
  └─ Investor Universe: Investment-grade only

DSCR_Min ≥ 1.05 → BB (High Yield)
  ├─ Credit Spread: 300-500 bps
  └─ Investor Universe: HY/opportunistic

DSCR_Min < 1.05 → B or lower
  └─ Typically unfinanceable
```

### Example
```
DSCR_Min = 1.38
Rating Matrix Lookup: 1.38 ≥ 1.35 → AA rating
Credit Spread: 90 bps
Repo Eligible: Yes
```

**Interpretation:** AA-rated senior debt with 90 bps spread over base rate.

### Impact on Economics
```
£400M Senior Debt @ 25 years
Rating AAA (70 bps): Total Interest = £400M × 70bps × 25Y = £70M
Rating AA (90 bps):  Total Interest = £400M × 90bps × 25Y = £90M
Rating A (120 bps):  Total Interest = £400M × 120bps × 25Y = £120M

Difference AAA→A: £50M additional interest cost over life
```

---

## 5. **EquityIRR** 💹

### What It Is
The Internal Rate of Return (IRR) on the equity investment, representing the annual return to equity investors.

### Why It Matters
- **Primary metric for sponsors/developers:** "What's my return?"
- **Hurdle rates:** Most sponsors require 15-20% IRR minimum
- **Risk/Return trade-off:** Higher leverage → higher IRR → higher risk
- **Exit timing:** IRR highly sensitive to exit year and terminal value

### Formula (Simplified)
```
Annual Cash Flow to Equity = NetIncome - Senior Interest - Mezz Interest
EquityIRR = (Annual CF / Equity Investment) × 100%

(Actual IRR uses NPV calculation with exit proceeds)
```

### Example
```
TotalProjectCost: £920M
SeniorNotional: £390M
EquityNotional: £530M

NetIncome: £22.5M/year
Senior Interest: £21.45M/year (5.5% × £390M)
CF to Equity: £1.05M/year

Simplified IRR = (1.05M / 530M) × 100 = 0.2%
(Actual IRR with growth and exit: ~18%)
```

### Components
```
Cash Flows:
  - Year 0: -£530M (equity investment)
  - Year 1-25: +£1.05M/year (annual distributions)
  - Year 25: +£400M (exit proceeds/refinance)

IRR Calculation: Solve for r where NPV = 0
NPV = -530 + 1.05/(1+r) + 1.05/(1+r)^2 + ... + (1.05+400)/(1+r)^25 = 0
```

### Typical Targets
- **Core Infrastructure:** 10-15% IRR
- **Core-Plus:** 15-18% IRR
- **Value-Add:** 18-22% IRR
- **Opportunistic:** 22%+ IRR

### Sensitivity Drivers
```
Most Sensitive To:
1. Leverage (more debt = higher IRR)
2. Exit timing (earlier exit = higher IRR if value created)
3. Rent growth (CPI escalation boosts cashflows)
4. Interest rates (higher rates = lower debt → lower IRR)
```

---

## 6. **WACC** 💵

### What It Is
The Weighted Average Cost of Capital - the blended cost of all capital in the structure (senior, mezz, equity).

### Why It Matters
- **Discount rate for valuation:** Lower WACC = higher project value
- **Competitiveness:** Lower WACC = ability to bid higher for assets
- **Efficiency metric:** How cheaply can you finance the project?
- **Ranking objective:** Minimize WACC for maximum efficiency

### Formula
```
WACC = (Weight_Senior × Cost_Senior) +
       (Weight_Mezz × Cost_Mezz) +
       (Weight_Equity × Cost_Equity)

Where:
  Weight = Notional / TotalProjectCost
  Cost = Interest Rate or IRR Target
```

### Example
```
TotalProjectCost: £920M

Senior: £390M @ 5.5% → Weight: 42.4% × 5.5% = 2.33%
Mezz:   £0M @ 0% → Weight: 0% × 0% = 0%
Equity: £530M @ 17% → Weight: 57.6% × 17% = 9.79%

WACC = 2.33% + 0% + 9.79% = 12.12%
```

**Interpretation:** The blended cost of capital for this structure is 12.12%.

### Impact on Valuation
```
Annual NOI: £22.5M
WACC: 12.12%
Exit Cap Rate: 10%

Present Value = NOI / WACC = 22.5M / 0.1212 = £185.6M (perpetuity)

If WACC drops to 10%:
Present Value = 22.5M / 0.10 = £225M (+21% increase!)
```

### Optimization Strategy
```
Maximize Leverage (cheapest capital):
  Senior Debt @ 5.5% is cheaper than Equity @ 17%
  Therefore: Max out senior debt to minimize WACC

But constrained by:
  - DSCR requirements
  - Rating targets
  - Lender risk appetite
```

### Typical Ranges
- **Investment-Grade Infrastructure:** 8-12%
- **Core Real Estate:** 6-10%
- **Value-Add Development:** 12-15%
- **High-Yield/Opportunistic:** 15%+

---

## 7. **Day1Cash** 💎

### What It Is
Cash generated on Day 1 (at financial close) from monetizing structural features like credit wraps, derivative positions, and advance rates.

### Why It Matters
- **Immediate liquidity** to sponsor
- **Reduces net equity required**
- **Credit enhancement monetization**
- **Can improve project returns significantly**

### Components
```
Day1Cash Sources:
1. Monoline Wrap Monetization
   - If AAA wrap on AA debt → value = spread differential × notional × duration

2. Derivative Upfront Payments
   - Zero-Coupon Inflation Swaps (if in-the-money)
   - Currency swaps (if favorable)

3. Advance Rate Uplifts
   - Lender provides > 100% advance on certain costs

4. Fee Rebates
   - Structuring fees rebated to sponsor
```

### Example
```
SeniorNotional: £400M
Rating: AA (90 bps spread)

Monoline Wrap: Upgrade AA → AAA
  - AAA Spread: 70 bps
  - Spread Differential: 20 bps
  - Duration: 15 years
  - Wrap Value: £400M × 20bps × 15Y = £12M

ZCiS (Inflation Swap):
  - Notional: 50% × £400M = £200M
  - In-the-money by 1.5%
  - Upfront Value: £200M × 1.5% = £3M

Total Day1Cash: £12M + £3M = £15M
```

**Interpretation:** Sponsor receives £15M in cash at closing, reducing net equity required from £530M to £515M.

### Impact on Returns
```
Without Day1Cash:
  Equity Required: £530M
  Annual CF: £1.05M
  IRR: ~0.2% (simplified)

With Day1Cash:
  Equity Required: £530M - £15M = £515M
  Annual CF: £1.05M (same)
  IRR: ~0.2% (slightly better due to lower base)

Exit Impact:
  Exit Year 10: £515M equity + 10 years CF + Exit Proceeds
  Day1Cash improves IRR by ~50-100 bps
```

### Typical Amounts
- **No Enhancement:** £0
- **Basic Wrap:** £5M - £15M (1-3% of notional)
- **Full Enhancement Package:** £20M - £50M (5-10% of notional)

---

## 8. **SeniorWAL** ⏱️

### What It Is
The Weighted Average Life of the senior debt - the average time until principal is repaid, weighted by principal amount outstanding.

### Why It Matters
- **Lender duration risk:** Longer WAL = more interest rate risk
- **Repo eligibility:** Central banks limit WAL (typically ≤20 years)
- **Pricing:** Longer WAL = higher spread required
- **Refinance risk:** Longer WAL = more time to market conditions changing

### Formula
```
WAL = Σ (Principal Outstanding[t] × t) / Total Principal

For Bullet: WAL ≈ Full Tenor
For Annuity: WAL ≈ 0.55 × Tenor
For Sculpted: WAL = custom calculation
```

### Example
```
Annuity Loan:
  Tenor: 25 years
  Amortization: Level payments

WAL ≈ 25 × 0.55 = 13.75 years

Bullet Loan:
  Tenor: 10 years
  Amortization: None until maturity

WAL = 10 years
```

**Interpretation:** For the annuity loan, the average principal is outstanding for 13.75 years.

### Impact on Eligibility
```
Central Bank Repo Requirements:
  - Rating: AAA or AA
  - WAL: ≤ 20 years
  - Jurisdiction: Eligible country

If WAL = 13.75 years → Repo Eligible ✓
If WAL = 25 years → Not Repo Eligible ✗
```

### Amortization Type Comparison
```
£400M Senior @ 25 Years:

Bullet:
  - WAL: 25 years
  - Annual Payment: £22M interest only
  - Balloon: £400M at year 25

Annuity:
  - WAL: 13.75 years
  - Annual Payment: £29M (P+I)
  - Balloon: £0

Sculpted:
  - WAL: 15-18 years (custom)
  - Annual Payment: Variable
  - Balloon: Variable
```

### Optimal WAL
```
Lender Preference: 7-15 years (manageable duration)
Sponsor Preference: 15-25 years (minimize principal payments)
Rating Agency: 10-20 years (balance refinance risk)

Sweet Spot: 12-15 years
```

---

## 9. **RepoEligible** ✅

### What It Is
A boolean (Yes/No) flag indicating whether the senior debt qualifies for central bank repurchase (repo) operations.

### Why It Matters
- **Critical for bank lenders:** Repo-eligible bonds can be pledged for liquidity
- **Lower funding costs:** Banks charge less if they can repo the paper
- **Broader investor base:** Central banks can hold repo-eligible paper
- **Liquidity:** More liquid secondary market
- **Pricing:** Repo-eligible bonds trade 10-30 bps tighter

### Eligibility Criteria
```
Must meet ALL conditions:

1. SeniorRepoEligibleFlag_44 = true
   (Structural feature allows repo)

2. SeniorRating ∈ {AAA, AA}
   (Minimum AA rating required)

3. SeniorWAL ≤ MaxWAL_Senior_80
   (Typically 20 years maximum)

4. JurisdictionEligibility_79 = "CB_RepoEligible"
   (Must be in eligible country/legal framework)

5. Additional factors:
   - Currency: Must be central bank currency
   - Documentation: Must meet repo master agreement
   - Collateral: Must be unencumbered
```

### Example
```
Scenario A:
  Rating: AA ✓
  WAL: 13.75 years ✓
  Jurisdiction: UK ✓
  Flag: true ✓
  → RepoEligible = Yes

Scenario B:
  Rating: A ✗ (fails)
  WAL: 12 years ✓
  Jurisdiction: UK ✓
  Flag: true ✓
  → RepoEligible = No

Scenario C:
  Rating: AAA ✓
  WAL: 25 years ✗ (fails - too long)
  Jurisdiction: UK ✓
  Flag: true ✓
  → RepoEligible = No
```

### Economic Impact
```
£400M Senior Debt @ 25 Years

Not Repo-Eligible:
  - Base Rate: 5.0%
  - Credit Spread: 120 bps (A rating)
  - Total Cost: 6.20%
  - Annual Interest: £24.8M

Repo-Eligible:
  - Base Rate: 5.0%
  - Credit Spread: 70 bps (AAA rating)
  - Repo Discount: -20 bps
  - Total Cost: 5.50%
  - Annual Interest: £22.0M

Savings: £2.8M/year × 25 years = £70M lifetime savings!
```

### Why Lenders Care
```
Bank's Perspective:
  - Repo-eligible bond can be pledged to central bank
  - Bank gets liquidity at policy rate (e.g., 5%)
  - Bank lends at 5.7% (70 bps spread)
  - Net margin: 70 bps

Non-repo bond:
  - Bank must fund from deposits (cost 4.5%)
  - Bank lends at 6.2% (120 bps spread)
  - Net margin: 170 bps

Paradox: Repo-eligible requires LOWER spread but is EASIER to sell!
```

---

## 10. **MezzNotional** 💰

### What It Is
The principal amount of mezzanine (subordinated) debt, sized using residual DSCR capacity after senior debt.

### Why It Matters
- **Additional leverage** beyond senior debt limit
- **Lower cost than equity** (8-12% vs 17%+)
- **Improves returns** by replacing expensive equity with cheaper mezz
- **But:** Adds complexity, covenants, and refinance risk

### How It's Calculated
```
Step 1: Size senior debt to TargetDSCRSenior (e.g., 1.35x)
Step 2: Calculate residual DSCR capacity
Step 3: Size mezzanine to TargetDSCRMezz (e.g., 1.15x)

Residual Capacity = (NetIncome / DSCR_Min) - Senior Debt Service
MezzNotional = PV of (Residual Capacity, MezzCoupon, MezzTenor)
```

### Example
```
NetIncome: £22.5M/year
Senior Debt Service: £21.45M/year (DSCR = 1.35)

Residual Capacity:
  Available for Mezz = (22.5M / 1.15) - 21.45M
                     = 19.57M - 21.45M
                     = -£1.88M (negative = no capacity!)

If Senior DSCR was 1.45:
  Senior DS = 22.5M / 1.45 = £15.52M
  Available for Mezz = (22.5M / 1.15) - 15.52M
                     = 19.57M - 15.52M
                     = £4.05M/year

  MezzNotional @ 8% for 10 years:
    ≈ £4.05M × 8.11 (annuity factor) = £32.8M
```

**Interpretation:** With a senior DSCR of 1.45, project can support £32.8M of mezzanine debt.

### Capital Stack Example
```
TotalProjectCost: £920M

Without Mezzanine:
  Senior: £390M (42%)
  Equity: £530M (58%)
  WACC: 12.12%

With Mezzanine:
  Senior: £390M (42%)
  Mezz:   £100M (11%)
  Equity: £430M (47%)
  WACC: (0.42×5.5%) + (0.11×8%) + (0.47×17%) = 11.2%

Improvement: 92 bps lower WACC!
Equity Savings: £100M less equity required
```

### Typical Ranges
- **No Mezz:** £0 (senior + equity only)
- **Light Mezz:** £25M - £75M (3-8% of total)
- **Heavy Mezz:** £100M - £200M (10-20% of total)

---

## 11. **EquityNotional** 💵

### What It Is
The amount of equity capital required from the sponsor/developer to fund the project.

### Why It Matters
- **Sponsor's capital at risk**
- **Higher equity = lower leverage = lower returns**
- **Goal: Minimize while maintaining target IRR**
- **Determines equity investor economics**

### Formula
```
EquityNotional = TotalProjectCost - SeniorNotional - MezzNotional
```

### Example
```
TotalProjectCost: £920M
SeniorNotional: £390M
MezzNotional: £0M

EquityNotional = 920M - 390M - 0M = £530M
Equity %: 530M / 920M = 57.6%
```

**Interpretation:** Sponsor must invest £530M of equity capital (58% of total cost).

### Leverage Analysis
```
Scenario A - Low Leverage:
  Senior: £300M (33%)
  Equity: £620M (67%)
  → High equity requirement
  → Lower IRR (~12%)
  → Lower risk

Scenario B - Moderate Leverage:
  Senior: £390M (42%)
  Equity: £530M (58%)
  → Balanced structure
  → Target IRR (~17%)
  → Moderate risk

Scenario C - High Leverage:
  Senior: £500M (54%)
  Mezz: £100M (11%)
  Equity: £320M (35%)
  → Minimum equity
  → High IRR (~23%)
  → Higher risk, tight DSCR
```

### Impact on Returns
```
NetIncome: £22.5M/year (constant across scenarios)

Low Leverage (£620M equity):
  CF to Equity: 22.5M - (300M × 5.5%) = 22.5M - 16.5M = £6M
  IRR: 6M / 620M = 0.97%

High Leverage (£320M equity):
  CF to Equity: 22.5M - (500M × 5.5%) - (100M × 8%)
              = 22.5M - 27.5M - 8M = -£13M (negative!)
  IRR: Cannot sustain this leverage

Optimal Leverage (£530M equity):
  CF to Equity: 22.5M - 21.45M = £1.05M
  IRR: 0.2% current yield (+ growth + exit = 18% IRR)
```

### Equity Investor Considerations
```
Prefer Lower Equity When:
  - Strong cashflows (high DSCR)
  - Investment-grade tenant
  - Long-term contract
  - Low interest rates

Prefer Higher Equity When:
  - Volatile cashflows
  - Development risk
  - Higher interest rates
  - Seeking lower risk/stable returns
```

---

## 12. **CompositeScore** 🎯

### What It Is
A weighted score (0-100) that ranks scenarios based on multiple KPIs, used to identify the "best" overall structure.

### Why It Matters
- **Ranking objective:** Sort 150,000 scenarios to find top performers
- **Multi-dimensional optimization:** Balance competing goals (maximize debt, minimize WACC, maximize rating)
- **Customizable weights:** User defines what matters most
- **Simplifies decision-making:** Single number to compare scenarios

### Formula
```
CompositeScore =
  w1 × (SeniorNotional / 1B) +              // Maximize debt raising
  w2 × (20 - WACC) / 20 +                   // Minimize WACC
  w3 × (Day1Cash / 100M) +                  // Maximize Day 1 cash
  w4 × Min(DSCR_Min / 2, 1) +               // Target DSCR
  w5 × RatingScore                          // Maximize rating

Default Weights (CompositeWeights_110):
  w1 = 0.35 (Senior Raise)
  w2 = 0.25 (WACC)
  w3 = 0.20 (Day 1 Cash)
  w4 = 0.10 (DSCR)
  w5 = 0.10 (Rating)
```

### Rating Score Mapping
```
AAA → 1.0
AA  → 0.8
A   → 0.6
BBB → 0.4
BB  → 0.2
B   → 0.0
```

### Example Calculation
```
Scenario A:
  SeniorNotional: £390M
  WACC: 12.12%
  Day1Cash: £12M
  DSCR_Min: 1.35
  Rating: AA

CompositeScore =
  0.35 × (390M / 1000M) +           = 0.1365
  0.25 × (20 - 12.12) / 20 +        = 0.0985
  0.20 × (12M / 100M) +             = 0.0240
  0.10 × Min(1.35 / 2, 1) +         = 0.0675
  0.10 × 0.8                        = 0.0800
                                    ________
                              Total = 0.4065 = 40.65/100


Scenario B (Better):
  SeniorNotional: £450M
  WACC: 10.5%
  Day1Cash: £15M
  DSCR_Min: 1.42
  Rating: AAA

CompositeScore =
  0.35 × (450M / 1000M) +           = 0.1575
  0.25 × (20 - 10.5) / 20 +         = 0.1188
  0.20 × (15M / 100M) +             = 0.0300
  0.10 × Min(1.42 / 2, 1) +         = 0.0710
  0.10 × 1.0                        = 0.1000
                                    ________
                              Total = 0.4773 = 47.73/100

Scenario B ranks higher (better overall balance)
```

### Customization Strategies
```
Maximize Debt Focus:
  - Senior Raise: 0.60
  - WACC: 0.20
  - Day1Cash: 0.10
  - DSCR: 0.05
  - Rating: 0.05

Minimize Risk Focus:
  - Rating: 0.40
  - DSCR: 0.30
  - Senior Raise: 0.15
  - WACC: 0.10
  - Day1Cash: 0.05

Balanced Approach (Default):
  - All weights relatively even
  - Senior Raise weighted highest (sponsor priority)
```

### Ranking Process
```
1. Calculate CompositeScore for all scenarios
2. Sort descending (highest score first)
3. Apply hard filters (remove non-viable)
4. Export top N scenarios (e.g., top 100)

Result: Best scenarios appear first in results table
```

---

## 13. **Viable** ✔️

### What It Is
A boolean (Yes/No) flag indicating whether the scenario passes all hard filters and is considered acceptable.

### Why It Matters
- **Binary gate:** Viable scenarios are kept, non-viable are excluded
- **Enforces minimum standards:** DSCR floor, rating floor, eligibility
- **Reduces result set:** From 150,000 total to ~50,000 viable
- **Regulatory/policy compliance:** Must meet institutional investment criteria

### Hard Filters (Default)
```
HardFilters_111 = [
  "DSCR>=1.30",
  "RepoEligible=Yes",
  "SeniorRating>=AAA"
]

Viable = true IF AND ONLY IF all filters pass
```

### Filtering Logic
```python
def check_viability(scenario):
  viable = True

  # Filter 1: DSCR >= 1.30
  if scenario.DSCR_Min < 1.30:
    viable = False
    return viable

  # Filter 2: RepoEligible = Yes
  if scenario.RepoEligible != True:
    viable = False
    return viable

  # Filter 3: SeniorRating >= AAA
  if scenario.SeniorRating not in ['AAA']:
    viable = False
    return viable

  return viable  # All filters passed
```

### Example
```
Scenario A:
  DSCR_Min: 1.35 ✓ (≥1.30)
  RepoEligible: Yes ✓
  SeniorRating: AA ✗ (not AAA)
  → Viable = No

Scenario B:
  DSCR_Min: 1.52 ✓ (≥1.30)
  RepoEligible: Yes ✓
  SeniorRating: AAA ✓
  → Viable = Yes

Scenario C:
  DSCR_Min: 1.28 ✗ (<1.30)
  RepoEligible: Yes ✓
  SeniorRating: AAA ✓
  → Viable = No (fails DSCR)
```

### Viability Statistics
```
Total Scenarios Generated: 150,000

Filtering Results:
  - Pass DSCR Filter: 98,000 (65%)
  - Pass Repo Filter: 45,000 (30%)
  - Pass Rating Filter: 35,000 (23%)
  - Pass ALL Filters: 28,000 (19%)

Viable Scenarios: 28,000
Viability Rate: 19%
```

**Interpretation:** Only 19% of generated scenarios meet all institutional investment criteria.

### Impact on Results
```
Scenario List (Pre-Filter):
1. Score: 85, DSCR: 1.15, Rating: A, Viable: No
2. Score: 82, DSCR: 1.52, Rating: AAA, Viable: Yes ← Top Result
3. Score: 78, DSCR: 1.35, Rating: AA, Viable: No
4. Score: 76, DSCR: 1.48, Rating: AAA, Viable: Yes
5. Score: 74, DSCR: 1.20, Rating: BBB, Viable: No

Scenario List (Post-Filter):
1. Score: 82, DSCR: 1.52, Rating: AAA ← Best Viable
2. Score: 76, DSCR: 1.48, Rating: AAA
3. Score: 71, DSCR: 1.51, Rating: AAA
...
```

### Customizing Filters
```
Conservative Filters (Tighter):
  - "DSCR>=1.40"
  - "RepoEligible=Yes"
  - "SeniorRating>=AAA"
  - "SeniorWAL<=15"
  → Result: Fewer viable (~10%), but highest quality

Moderate Filters (Default):
  - "DSCR>=1.30"
  - "RepoEligible=Yes"
  - "SeniorRating>=AAA"
  → Result: Balanced (~20% viable)

Aggressive Filters (Relaxed):
  - "DSCR>=1.20"
  - "SeniorRating>=A"
  → Result: More viable (~40%), but includes riskier structures
```

---

## 🎯 Summary: How the KPIs Work Together

### The Optimization Problem
```
Goal: Maximize EquityIRR
Subject to:
  - DSCR_Min ≥ 1.30
  - SeniorRating ≥ AAA
  - RepoEligible = Yes
  - Viable = Yes
```

### The Trade-offs
```
More Debt (↑ SeniorNotional):
  ✓ Reduces EquityNotional
  ✓ Increases EquityIRR
  ✗ Decreases DSCR_Min
  ✗ May downgrade SeniorRating
  ✗ May lose RepoEligible
  ✗ May make Viable = No

Lower Interest Rate (↓ SeniorCoupon):
  ✓ Reduces debt service
  ✓ Increases DSCR_Min
  ✓ Improves WACC
  ✗ Harder to find lenders

Higher Revenue (↑ GrossMonthlyRent):
  ✓ Increases NetIncome
  ✓ Increases DSCR_Min
  ✓ Increases SeniorNotional
  ✓ Improves all KPIs
  ✗ May not be realistic
```

### Typical "Sweet Spot" Scenario
```
SeniorNotional: £425M (46% LTV)
DSCR_Min: 1.45
DSCR_Avg: 1.52
SeniorRating: AAA
EquityIRR: 18.5%
WACC: 10.8%
Day1Cash: £18M
SeniorWAL: 14.2 years
RepoEligible: Yes
MezzNotional: £50M
EquityNotional: £445M
CompositeScore: 78.3
Viable: Yes

This scenario balances:
  - High leverage (£425M senior + £50M mezz)
  - Strong credit (AAA, 1.45 DSCR)
  - Repo eligibility (WAL < 15Y)
  - Good returns (18.5% IRR)
  - Efficient capital (10.8% WACC)
```

---

## 📊 Dashboard Display

### How KPIs Are Shown to User

```
┌─ SCENARIO #1 ─────────────────────────────────────┐
│                                                    │
│  CompositeScore: 78.3/100        Viable: ✓ Yes    │
│                                                    │
│  CAPITAL STRUCTURE                                 │
│  ├─ Senior:  £425M (46%)  @ 5.25%  [AAA]          │
│  ├─ Mezz:    £50M  (5%)   @ 8.50%  [A]            │
│  └─ Equity:  £445M (48%)  @ 18.5%                 │
│                                                    │
│  KEY METRICS                                       │
│  ├─ DSCR Min:      1.45x          ✓               │
│  ├─ DSCR Avg:      1.52x                          │
│  ├─ WACC:          10.8%          ✓ Low           │
│  ├─ Equity IRR:    18.5%          ✓ Target        │
│  ├─ Day 1 Cash:    £18M           ✓               │
│  ├─ Senior WAL:    14.2 years     ✓               │
│  └─ Repo Eligible: Yes            ✓               │
│                                                    │
│  [Use This Structure] [Export] [Details]          │
└────────────────────────────────────────────────────┘
```

---

## 🔍 Quick Reference Table

| KPI | What It Measures | Good Value | Bad Value | Impact |
|---|---|---|---|---|
| **SeniorNotional** | Max debt amount | £400M+ | <£200M | Higher = more leverage |
| **DSCR_Min** | Worst-case coverage | ≥1.45 | <1.20 | Lower = higher risk |
| **DSCR_Avg** | Average coverage | ≥1.50 | <1.30 | Indicates cushion |
| **SeniorRating** | Credit quality | AAA | <BBB | Lower = higher cost |
| **EquityIRR** | Equity return | ≥18% | <12% | Lower = poor returns |
| **WACC** | Blended cost | ≤11% | >15% | Higher = lower value |
| **Day1Cash** | Upfront monetization | £15M+ | £0 | More = less equity |
| **SeniorWAL** | Average life | 12-15Y | >20Y | Longer = less liquid |
| **RepoEligible** | CB repo access | Yes | No | Yes = cheaper funding |
| **MezzNotional** | Mezz debt amount | £50M+ | £0 | More = more leverage |
| **EquityNotional** | Equity required | <50% LTV | >70% LTV | Lower = better |
| **CompositeScore** | Overall ranking | ≥75 | <50 | Higher = better |
| **Viable** | Meets criteria | Yes | No | No = excluded |

---

**This documentation explains all 13 Primary Output KPIs used to evaluate and rank permutation scenarios.**

**Last Updated:** 2026-01-19
**Status:** Complete
