# Permutation Engine - Claude Code Development Transcript

## Project Overview
- **Type**: Real Estate/Infrastructure Finance Permutation Engine  
- **Purpose**: Analyzes different financing scenarios for data center projects
- **Core Logic**: Debt/equity structures, interest rates, operational parameters, and cash flow modeling
- **Total Parameters**: 83 inputs (47 fixed, 30 variable, 6 calculated)

## Fixed Inputs (From Project Data)
These values are set once per project and don't vary across permutations:

1. **GrossITLoad_01** = 100 (MW)
2. **PUE_02** = 1.2 (Power Usage Effectiveness)
3. **TotalProjectInternalCosts_15** = "CONDITIONAL £ FORMATTING TO HERE"
4. **AnnualDebtServiceSenior_20** = "PQ PLACEHOLDER" 
5. **MaxSeniorDebt_21** = "PQ PLACEHOLDER"
6. **MaxSeniorAsPercentageOfCosts_22** = "PQ PLACEHOLDER"
7. **WACDSeniorTraunche_23** = "PQ PLACEHOLDER"
8. **24_AFStrategy** = "PQ PLACEHOLDER"
9. **25_TypeOfAFRun** = "PQ PLACEHOLDER" 
10. **26_AFUsedYears** = "PQ PLACEHOLDER"
11. **27_AFCeiling** = "calc in power query one per query"
12. **28_AFDeltaYears** = "PQ PLACEHOLDER"
13. **29_ResidualAFValue** = "PQ PLACEHOLDER"
14. **30_PlaceableAt10YAF** = "PQ PLACEHOLDER"
15. **AF Option (Years) - Mezz** = "calc in PQ multi"
16. **AF Lookup - Mezz (Amortising)** = "calc in PQ multi"
17. **AF Value - Mezz (Fully Amortising)** = "calc in PQ multi"
18. **Annual Debt Service (£) - Mezz** = "calc in PQ multi"
19. **Blended Senior + Mezz WACD (%)** = "calc in power query multi"
20. **Blended DSCR** = "calc in power query multi"
21. **Min Equity Contribution (£)** = "calc in power query multi"
22. **Developer Equity IRR (%)** = "calc in power query multi"
23. **Equity as % of Project Cost** = "calc in power query multi"
24. **Total Capital Stack (£)** = "calc in power query multi"
25. **Overraise Amount (£)** = "calc in power query multi"
26. **Residual Equity Needed (£)** = "calc in power query multi"
27. **Effective Equity Value Multiple** = "Manually FILL COLUMN"
28. **Equity Sale Uplift (%)** = "Manually FILL COLUMN"
29. **Equity Sold (£)** = "Manually FILL COLUMN"
30. **Equity Retained (£)** = "calc in power query multi"
31. **Equity Retained Value (£)** = "calc in power query multi"
32. **Residual Upside Capture Mechanism** = "Yes,No"
33. **TRS Applied?** = "Yes,No"
34. **Equity IRR (%)** = "calc in power query multi"
35. **EQUITY as % of Project Cost** = "calc in power query multi"
36. **Equity IRR Ranking** = "calc in power query one per query"
37. **Total Equity Value (£)** = "calc in power query multi"
38. **Platform Value Realised (£)** = "calc in power query multi"
39. **Effective Total Value (£)** = "calc in power query multi"
40. **Total Capital Stack (£)** = "calc in power query multi"
41. **Senior as % of Capital Stack** = "calc in power query multi"
42. **Mezz as % of Capital Stack** = "calc in power query multi"
43. **Equity as % of Capital Stack** = "calc in power query multi"
44. **Blended WACD (%)** = "calc in power query multi"
45. **Blended DSCR** = "calc in power query multi"
46. **Blended IRR (%)** = "calc in power query multi"
47. **Viability Flag** = "calc in power query one per query"

## Variable Inputs (User Configurable Ranges)
These create the permutations - users can set min/max/increment values:

### Financial Parameters
1. **GrossMonthlyRent_04**: £120 to £220 (6 steps, £20 increments)
2. **OPEX_06**: 15% to 30% (4 steps, 5% increments) 
3. **CapexCostPrice_08**: £7,500,000 (Bare bones) or £11,000,000 (Market rate)
4. **CapexMarketRate_09**: £11,000,000 (Market data centre rate)
5. **LandPurchaseFees_10**: £10,000,000 (All land fees)
6. **TotalStructuringFees_13**: £33,305,000 (For testing purposes)

### Senior Debt Parameters  
7. **TargetDSCRSenior_16**: 1.5x to 1.8x (7 steps, 0.05x increments)
8. **SeniorCoupon_17**: 3.0% to 5.0% (9 steps, 0.25% increments)
9. **SeniorTenor_18**: 5 to 30 years (7 steps, ~4.2 year increments)
10. **23_LeaseTermYears**: 5 to 30 years (7 steps, ~4.2 year increments)
11. **Senior Amortisation Type**: Options from PowerQuery

### Mezzanine Debt Parameters
12. **Effective DSCR Buffer (%)**: 35% to 50% (3 steps, 7.5% increments)
13. **Target DSCR - Mezz**: 8.25% to 135% (7 steps, ~21% increments)  
14. **Mezz Coupon (%)**: 6.0% to 8.75% (11 steps, 0.27% increments)
15. **Mezz Tenor Years**: 5 to 30 years (7 steps, ~4.2 year increments)

### Equity Parameters
16. **Debt Headroom (%)**: 15% to 25% (3 steps, 5% increments)
17. **Target Equity IRR (%)**: 14% to 19% (6 steps, 1% increments)

### Optional/Manual Parameters
18. **Currency_00**: Multi-option dropdown
19. **AFSenior_19**: PowerQuery placeholder options
20. **TRS Strike Value (£)**: Manual input (leave blank initially)
21. **TRS Retained Upside (%)**: Manual input (leave blank initially)
22. **Notes / Use Case**: Manual text input (leave blank initially)
23. **Platform Sale Uplift (%)**: Manual input (leave blank initially)

### Calculated Variable Inputs (Multi-step calculations)
24. **Annuity Factor - Mezz**: Calculated in PowerQuery
25. **Remaining NOI (£)**: Calculated in PowerQuery  
26. **Annual Mezz Debt Service (£)**: Calculated in PowerQuery
27. **Max Mezz Debt (£)**: Calculated in PowerQuery
28. **Max Mezz as % of Costs (%)**: Calculated in PowerQuery
29. **WACD - Mezz (%)**: Calculated in PowerQuery
30. **Lease Term Years - Mezz**: Calculated in PowerQuery

## Calculated Inputs (Formula-Based)
These are computed from other inputs using specific formulas:

1. **NetITLoad_03** = GrossITLoad_01 ÷ PUE_02
2. **GrossIncome_05** = GrossMonthlyRent_04 × 12
3. **NetIncome_07** = GrossIncome_05 × (1 - OPEX_06)
4. **DeveloperProfit_11** = Calculated based on project costs and margins
5. **DeveloperMargin_12** = Calculated based on developer profit structure
6. **TotalProjectMarketCosts_14** = Sum of all market-rate project costs

## Supporting Data Sheets
- **Currency**: Foreign exchange rates and currency options
- **Bonds**: Bond/debt instrument reference data
- **Tenants**: Tenant creditworthiness and lease data
- **Rating**: Credit rating mappings and risk factors

## Key Business Logic & Formulas

### Core Financial Calculations
```javascript
// Basic operational calculations
NetITLoad = GrossITLoad / PUE;
GrossIncome = GrossMonthlyRent * 12;
NetIncome = GrossIncome * (1 - OPEX);

// Debt service calculations (using annuity factors)
AnnualDebtService = DebtAmount * AnnuityFactor;
DSCR = NetIncome / AnnualDebtService;
MaxDebtCapacity = NetIncome / (TargetDSCR * AnnuityFactor);

// Equity calculations
EquityRequired = TotalProjectCosts - MaxSeniorDebt - MaxMezzDebt;
EquityIRR = IRR(EquityCashFlows);
```

### Permutation Logic
1. Generate all combinations of variable inputs within specified ranges
2. For each combination, calculate all derived/formula fields
3. Apply viability filters (DSCR thresholds, IRR minimums, etc.)
4. Rank results by key metrics (IRR, returns, risk)
5. Flag viable vs. non-viable scenarios

## Web Application Requirements

### Frontend Components
- **Input Panel**: Range sliders, dropdowns, number inputs for all 30 variable parameters
- **Calculation Engine**: Real-time computation as inputs change
- **Results Grid**: Sortable, filterable table showing all permutation results
- **Visualization**: Charts showing IRR vs. risk, sensitivity analysis
- **Export Tools**: CSV/Excel download of results

### Backend Architecture
- **Calculation Engine**: Node.js service handling financial formulas
- **Permutation Generator**: Creates all valid input combinations
- **Data Storage**: Database for scenarios, results, and user preferences
- **API Endpoints**: RESTful services for calculations and data retrieval

### Key Features Needed
1. **Batch Processing**: Handle large numbers of permutations efficiently
2. **Real-time Updates**: Instant recalculation as inputs change
3. **Filtering System**: Filter results by viability, IRR ranges, etc.
4. **Comparison Tools**: Side-by-side scenario comparison
5. **Sensitivity Analysis**: Show impact of key variable changes
6. **Save/Load**: Store and retrieve scenarios
7. **Responsive Design**: Mobile and desktop compatibility

### Technical Specifications
- **Frontend**: React with Material-UI or similar for form controls
- **State Management**: Redux or Context API for complex state
- **Charts**: D3.js or Chart.js for visualizations  
- **Backend**: Node.js with Express
- **Database**: PostgreSQL for structured financial data
- **API**: GraphQL or REST for data operations
- **Deployment**: Docker containers with CI/CD pipeline

## Priority Development Order
1. **Phase 1**: Core calculation engine with basic 6 calculated inputs
2. **Phase 2**: Variable input forms and permutation generator  
3. **Phase 3**: Results display and basic filtering
4. **Phase 4**: Advanced features (charts, export, save/load)
5. **Phase 5**: Performance optimization and mobile responsiveness

This transcript provides Claude Code with everything needed to build a comprehensive permutation engine matching your Excel model's functionality.