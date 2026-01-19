# Complete Variables and Tables Documentation

## 📊 MONGODB COLLECTIONS/TABLES

### Cloud Database Collections (cloud_database.py)

#### 1. **users** Collection
Primary user accounts and authentication data.

**Fields:**
```javascript
{
  _id: ObjectId,
  email: string (unique, indexed),
  username: string,
  full_name: string,
  account_type: string, // "admin", "analyst", "sponsor", "viewer"
  is_admin: boolean,
  admin_approved: boolean,
  password: string (hashed with werkzeug),
  password_expiry: datetime,
  email_verified: boolean,
  created_at: datetime,
  login_count: integer,
  last_login: datetime,
  preferences: {
    timezone: string,
    theme: string // "dark" or "light"
  }
}
```

**Indexes:**
- email (unique)
- created_at
- is_admin

---

#### 2. **registrations** Collection
User registration applications pending approval.

**Fields:**
```javascript
{
  _id: ObjectId,
  email: string (unique, indexed),
  full_name: string,
  phone: string,
  country_code: string, // "+44", "+1", etc.
  company_name: string,
  company_number: string,
  job_title: string,
  business_address: string,
  generated_password: string,
  verification_token: string,
  approval_token: string,
  email_verified: boolean,
  admin_approved: boolean,
  created_at: datetime (indexed),
  ip_address: string
}
```

**Indexes:**
- email (unique)
- created_at

---

#### 3. **projects** Collection
User projects and securitization data.

**Fields:**
```javascript
{
  _id: ObjectId,
  user_email: string (indexed),
  projects: [{
    id: string, // "proj_xxx"
    projectId: string,
    title: string,
    description: string,
    value: number,
    progress: number, // 0-100
    status: string, // "draft", "active", "completed", "on_hold"
    details: string,
    currency: string, // "EUR", "USD", "GBP", "JPY", "AED"
    grossITLoad: number, // MW
    pue: number, // 1.0-2.5
    capexCost: number,
    capexRate: number,
    landPurchaseFees: number,
    grossMonthlyRent: number,
    opex: number,
    seriesId: string,
    created_at: datetime,
    updated_at: datetime,
    created_by: string,
    gate1_completed: boolean,
    gate2_completed: boolean,
    gate3_completed: boolean,
    gate2_data: object,
    gate3_data: object,
    meta: {
      projectTitle: string,
      locationCountry: string,
      status: string,
      capexCurrency: string,
      kwhCurrency: string,
      grossITLoadMW: number,
      pue: number,
      grossMonthlyRent: number,
      opexPercent: number,
      constructionStart: date,
      constructionDurationMonths: number
    },
    capex: {
      internal: {
        perMW: number,
        architectural: number,
        civilStructural: number,
        substations: number,
        undergroundUtilities: number,
        crusaderModules: number,
        bess: number,
        mainContractorInstallation: number,
        photovoltaicSystem: number,
        landscaping: number,
        preliminariesGeneral: number,
        mainContractorMargin: number
      },
      market: {
        perMW: number,
        architectural: number,
        civilStructural: number,
        substations: number,
        undergroundUtilities: number,
        crusaderModules: number,
        bess: number,
        mainContractorInstallation: number,
        photovoltaicSystem: number,
        landscaping: number,
        preliminariesGeneral: number,
        mainContractorMargin: number
      }
    },
    rollups: {
      capexCostPriceEUR: number,
      grandTotalEUR: number
    },
    schedule: object,
    engineInput: object,
    lastModified: datetime
  }],
  series: array,
  order: array, // Project ordering for display
  updated_at: datetime (indexed)
}
```

**Indexes:**
- user_email
- updated_at

---

#### 4. **files** Collection
Uploaded files (Excel templates, documents).

**Fields:**
```javascript
{
  _id: ObjectId,
  user_email: string (indexed),
  filename: string,
  data: binary (GridFS reference or base64),
  uploaded_at: datetime,
  file_type: string, // "excel", "pdf", "csv"
  file_size: number, // bytes
  metadata: object
}
```

**Indexes:**
- user_email
- uploaded_at

---

#### 5. **admin_actions** Collection
Audit log for administrative actions.

**Fields:**
```javascript
{
  _id: ObjectId,
  user_or_ip: string (indexed),
  action: string (indexed), // "ban_ip", "unlock_ip", "approve_user", etc.
  details: object,
  timestamp: datetime (indexed, descending sort),
  ip_address: string,
  admin_email: string
}
```

**Indexes:**
- action
- timestamp (descending)
- user_or_ip

---

#### 6. **ip_tracking** Collection
IP address access tracking.

**Fields:**
```javascript
{
  _id: string ('tracking'),
  data: {
    [ip_address]: {
      page: string,
      timestamp: datetime,
      user_email: string,
      count: integer,
      user_agent: string,
      location: string
    }
  }
}
```

---

#### 7. **login_attempts** Collection
Aggregated login attempt data.

**Fields:**
```javascript
{
  _id: ObjectId,
  ip: string,
  email: string,
  failed_count: integer,
  last_attempt: datetime,
  lockout_until: datetime,
  attempted_passwords: array
}
```

---

#### 8. **login_attempts_log** Collection
Individual login attempt records.

**Fields:**
```javascript
{
  _id: ObjectId,
  email: string (indexed),
  ip: string,
  user_agent: string (indexed),
  success: boolean,
  error: string,
  timestamp: datetime (indexed, descending sort),
  location: string
}
```

**Indexes:**
- email
- user_agent
- timestamp (descending)

---

#### 9. **ip_rules** Collection
Whitelist/blacklist IP rules (allow/deny).

**Fields:**
```javascript
{
  _id: ObjectId,
  type: string, // "allow" or "deny"
  cidr: string, // IP or CIDR range (e.g., "192.168.1.0/24")
  note: string,
  created_by: string,
  created_at: datetime,
  expires_at: datetime, // optional
  priority: integer
}
```

---

#### 10. **trash** Collection
Soft-deleted items with 30-day TTL.

**Fields:**
```javascript
{
  _id: ObjectId,
  project_data: object,
  deleted_by: string,
  original_owner: string,
  deleted_at: datetime (TTL index, 30 days),
  type: string, // "project", "series", "file"
  item_type: string,
  restore_path: string
}
```

**TTL Index:**
- deleted_at (expires after 30 days)

---

#### 11. **project_changes** Collection
Change request tracking.

**Fields:**
```javascript
{
  _id: ObjectId,
  project_id: string,
  user_email: string (indexed),
  changes: object,
  status: string, // "pending", "approved", "rejected"
  created_at: datetime,
  reviewed_at: datetime,
  reviewed_by: string,
  review_notes: string
}
```

**Indexes:**
- user_email
- status
- created_at

---

#### 12. **permutation_snapshots** Collection
Snapshots of project data for permutation engine.

**Fields:**
```javascript
{
  _id: ObjectId,
  project_id: string (unique, indexed),
  snapshot_data: object,
  created_at: datetime (indexed),
  approved: boolean,
  version: integer (indexed),
  created_by: string
}
```

**Indexes:**
- project_id (unique)
- version
- created_at

---

#### 13. **permutation_metadata** Collection
Metadata for Vercel Blob storage permutation results.

**Fields:**
```javascript
{
  _id: ObjectId,
  project_id: string,
  blob_url: string,
  blob_pathname: string,
  executed_by: string,
  permutation_count: integer,
  compressed_size: integer, // bytes
  uncompressed_size: integer, // bytes
  compression_ratio: number, // e.g., 10.0
  timestamp: datetime,
  summary: {
    viable_count: integer,
    best_irr: number,
    best_dscr: number,
    avg_wacd: number,
    total_scenarios: integer
  }
}
```

---

### Securitization Database Collections (database_v2.py)

#### 14. **gate1_projects** Collection
Basic project information and specifications.

**Fields:**
```javascript
{
  _id: ObjectId,
  project_id: string (unique, indexed),
  user_id: string (indexed),
  project_name: string,
  asset_type: string, // "Data Center", "Solar", "Wind", etc.
  total_asset_value: number,
  target_rating: string, // "AAA", "AA", "A", "BBB", etc.
  structure_type: string, // "Senior", "Mezzanine", "Hybrid"
  description: string,
  created_at: datetime (indexed),
  last_modified: datetime (indexed),
  gate1_status: string, // "draft", "submitted", "approved"
  gate2_status: string,
  gate3_status: string,
  location: string,
  currency: string
}
```

**Indexes:**
- project_id (unique)
- user_id
- created_at
- last_modified

---

#### 15. **gate2_derived** Collection
Derived fields and securitization calculations.

**Fields:**
```javascript
{
  _id: ObjectId,
  project_id: string (unique, indexed),
  user_id: string (indexed),
  credit_enhancement_pct: number, // percentage
  credit_enhancement_amount: number,
  senior_tranche_pct: number,
  senior_tranche_amount: number,
  expected_loss_rate: number, // percentage
  expected_loss_amount: number,
  required_capital: number,
  estimated_yield: number, // percentage
  estimated_spread: number, // basis points
  calculations_performed_at: datetime,
  created_at: datetime,
  last_modified: datetime,
  gate2_status: string, // "draft", "calculated", "approved"
  waterfall: {
    senior_interest: number,
    senior_principal: number,
    mezzanine_interest: number,
    mezzanine_principal: number,
    equity_distribution: number
  }
}
```

**Indexes:**
- project_id (unique)
- user_id

---

#### 16. **gate3_variables** Collection
Permutation engine variables.

**Fields:**
```javascript
{
  _id: ObjectId,
  project_id: string (unique, indexed),
  user_id: string (indexed),
  permutation_variables: {
    [variable_name]: {
      type: string, // "range", "fixed", "calculated"
      min_value: number,
      max_value: number,
      step_size: number,
      calculated_steps: number,
      description: string,
      unit: string, // "MW", "%", "EUR", etc.
      enabled: boolean
    }
  },
  variable_count: integer,
  max_permutations: integer,
  current_permutations: integer,
  last_results_id: string,
  last_results_created: datetime,
  created_at: datetime,
  last_modified: datetime,
  gate3_status: string, // "draft", "running", "completed"
  ranking_objective: string // "maximize_irr", "minimize_risk", etc.
}
```

**Indexes:**
- project_id (unique)
- user_id

---

#### 17. **permutation_results** Collection
Results from permutation analysis runs.

**Fields:**
```javascript
{
  _id: ObjectId,
  result_id: string,
  project_id: string (indexed),
  user_id: string (indexed),
  created_at: datetime (indexed),
  result_type: string, // "full", "summary", "export"
  total_permutations: integer,
  execution_time_seconds: number,
  results: object, // Array of scenario results
  summary: {
    avg_irr: number,
    max_npv: number,
    min_dscr: number,
    best_scenario: integer,
    worst_scenario: integer,
    viable_scenarios: integer,
    invalid_scenarios: integer
  },
  filters_applied: object,
  ranking_method: string
}
```

**Indexes:**
- project_id
- user_id
- created_at

---

#### 18. **audit_log** Collection (database_v2.py)
Comprehensive audit trail for all user actions.

**Fields:**
```javascript
{
  _id: ObjectId,
  user_id: string (indexed),
  action: string (indexed), // "create_project", "update_gate2", etc.
  project_id: string (indexed),
  details: object,
  timestamp: datetime (indexed, descending sort),
  ip_address: string,
  user_agent: string,
  changes: object, // Before/after values
  result: string // "success" or "failure"
}
```

**Indexes:**
- user_id
- action
- project_id
- timestamp (descending)

---

## 🟦 JAVASCRIPT GLOBAL VARIABLES (dashboard.html)

### Session & Authentication Variables
```javascript
let isAdmin = false;                    // Admin privilege flag
let accountType = 'viewer';             // User account type
let userEmail = '';                     // Current user email
let is_admin = false;                   // Admin indicator
let isAuthenticated = false;            // Authentication status
```

### UI State Variables
```javascript
let lastScrollTop = 0;                  // Scroll position tracking
let currentTab = 'dashboard';           // Active tab identifier
let currentSection = 'dashboard';       // Active section display
let targetSection = '';                 // Target section for navigation
let allSections = [];                   // Array of all dashboard sections
let currentPage = 1;                    // Current page number
let itemsPerPage = 20;                  // Items per page
let sortColumn = '';                    // Current sort column
let sortDirection = 'asc';              // Sort direction
let searchQuery = '';                   // Search query string
```

### Dashboard Data Variables
```javascript
let comprehensiveData = {};             // Global admin dashboard data object
let dashboardStats = {};                // Dashboard statistics
let marketData = {};                    // Market data object
let analyticsData = {};                 // Analytics data object
let portfolioData = {};                 // Portfolio data
let riskMetrics = {};                   // Risk metrics
```

### Permutation Engine Variables
```javascript
let scenarios = [];                     // Array of scenario permutation data
let permutationConfig = {};             // Configuration for permutation engine
let permutationVariables = {};          // Permutation variables object
let viableCount = 0;                    // Count of viable scenarios
let invalidCount = 0;                   // Count of invalid scenarios
let bestIRR = 0;                        // Best IRR achieved in permutations
let bestDSCR = 0;                       // Best DSCR achieved in permutations
let avgWACD = 0;                        // Average WACD
let permutations = [];                  // Permutation result objects
let results = [];                       // Analysis results
let permutationResults = [];            // Generated scenario results
let currentPermutationProject = null;   // Current project being permutated
let isPermutationRunning = false;       // Permutation engine status
```

### Project Variables
```javascript
let projects = [];                      // List of user projects
let allProjects = [];                   // All projects (admin view)
let projectsData = [];                  // Projects data array
let currentEditingProject = null;       // Currently editing project
let currentSponsorProjectId = '';       // Current sponsor project ID
let sponsorUploadedData = null;         // Uploaded sponsor data
let selectedProjectId = '';             // Selected project for operations
```

### Form State Variables
```javascript
let hasUnsavedChanges = false;          // Unsaved changes indicator
let formData = {};                      // Form data object
let validationErrors = [];              // Validation error messages
```

### Upload/File Variables
```javascript
let uploadedFile = null;                // Currently uploaded file
let uploadedFileName = '';              // Uploaded file name
let uploadedFileData = null;            // Uploaded file data
```

### Modal/Dialog Variables
```javascript
let pendingDeleteItem = null;           // Item pending deletion
let pendingDeleteType = '';             // Type of item to delete
let isModalOpen = false;                // Modal open state
```

### Chart/Visualization Variables
```javascript
let analyticsChart = null;              // Analytics chart instance
let spreadChart = null;                 // Spread chart instance
let capitalStackChart = null;           // Capital stack chart instance
let fearGreedChart = null;              // Fear & Greed index chart
```

### Timer/Interval Variables
```javascript
let tickerInterval = null;              // Market ticker interval
let updateInterval = null;              // Data update interval
let autoSaveInterval = null;            // Auto-save interval
```

### Trash/Deletion Variables
```javascript
let trashItems = [];                    // Items in trash
let selectedTrashItems = [];            // Selected trash items
let trashFilter = 'all';                // Trash filter
```

### Admin Panel Variables
```javascript
let adminUsers = [];                    // Admin user list
let adminRegistrations = [];            // Admin registrations list
let adminIPRules = [];                  // Admin IP rules list
let adminAuditLog = [];                 // Admin audit log
```

### Currency/Format Variables
```javascript
let currentCurrency = 'EUR';            // Current currency
let currencySymbols = {                 // Currency symbol map
  'EUR': '€',
  'USD': '$',
  'GBP': '£',
  'JPY': '¥',
  'AED': 'د.إ'
};
```

---

## 🆔 FORM FIELD IDs BY SECTION

### Main Dashboard Section
```
main-dashboard                 - Main container
navBar                        - Navigation bar
navToggleIcon                 - Navigation toggle icon
tickerContainer               - Market ticker container
marketTicker                  - Market ticker element
currentDate                   - Current date display
aumCounter                    - Assets under management counter
dealsCounter                  - Deals counter
activeDealsCount              - Active deals count
```

### Dashboard Statistics
```
dashboard-perm-count          - Total permutations count
dashboard-viable-count        - Viable scenarios count
dashboard-invalid-count       - Invalid scenarios count
dashboard-best-irr            - Best IRR badge
dashboard-avg-wacd            - Average WACD badge
dashboard-engine-status       - Engine status indicator
stat-total                    - Total stats
stat-viable                   - Viable stats
stat-irr                      - IRR stats
stat-dscr                     - DSCR stats
```

### Market Section
```
market-section                - Market view container
market-ticker                 - Market ticker
liveNewsSection               - Live news container
liveNewsContainer             - News items container
aiNewsContainer               - AI analysis container
btnLiveNews                   - Live news button
btnAIAnalysis                 - AI analysis button
fear-greed-chart              - Fear/Greed index chart
issuanceVolume                - Issuance volume
activeDeals                   - Active deals
avgSpreadChange               - Average spread change
```

### Permutation Engine Section
```
permutation-section           - Permutation engine container
est-scenarios                 - Estimated scenarios display
est-time                      - Estimated time display
quick-stats                   - Quick stats display
project-selector              - Project selector dropdown
results-tbody                 - Results table body
run-permutation-btn           - Run permutation button
export-results-btn            - Export results button
clear-results-btn             - Clear results button
```

### Permutation Input Fields (110 variables)
```
GrossITLoad_02                - Gross IT Load (MW)
GrossITLoad_02_min            - Min IT Load
GrossITLoad_02_max            - Max IT Load
GrossITLoad_02_range          - Enable IT Load range
PUE_03                        - PUE Factor
PUE_03_min                    - Min PUE
PUE_03_max                    - Max PUE
PUE_03_range                  - Enable PUE range
CapexCostPrice_04             - Capex Cost Price (EUR/kW)
CapexCostPrice_04_min         - Min Capex Cost
CapexCostPrice_04_max         - Max Capex Cost
CapexCostPrice_04_range       - Enable Capex range
GrossMonthlyRent_07           - Gross Monthly Rent (EUR/kW/month)
GrossMonthlyRent_07_min       - Min Monthly Rent
GrossMonthlyRent_07_max       - Max Monthly Rent
GrossMonthlyRent_07_range     - Enable Rent range
OPEX_08                       - Operating Expenses (%)
OPEX_08_min                   - Min OPEX
OPEX_08_max                   - Max OPEX
OPEX_08_range                 - Enable OPEX range
SeniorCoupon_38               - Senior Coupon Rate (%)
SeniorCoupon_38_min           - Min Senior Coupon
SeniorCoupon_38_max           - Max Senior Coupon
SeniorCoupon_38_range         - Enable Coupon range
TargetDSCRSenior_37           - Target DSCR Senior
TargetDSCRSenior_37_min       - Min DSCR
TargetDSCRSenior_37_max       - Max DSCR
TargetDSCRSenior_37_range     - Enable DSCR range
SeniorTenorY_39               - Senior Tenor (Years)
SeniorTenorY_39_min           - Min Tenor
SeniorTenorY_39_max           - Max Tenor
SeniorTenorY_39_range         - Enable Tenor range
LeaseTermYears_22             - Lease Term (Years)
LeaseTermYears_22_min         - Min Lease Term
LeaseTermYears_22_max         - Max Lease Term
LeaseTermYears_22_range       - Enable Lease Term range
RankingObjective_109          - Ranking objective selector
MaxPermutations_108           - Max permutations limit
```

### Sponsor Form Fields - Project Meta
```
sponsor-projectTitle          - Project title
sponsor-status                - Project status
sponsor-locationCountry       - Country location
sponsor-leaseType             - Lease type
sponsor-leaseCommenceDate     - Lease commence date
sponsor-occupancy             - Occupancy rate slider
sponsor-occupancy-value       - Occupancy value display
sponsor-grossMonthlyRent      - Monthly rent (EUR/kW/month)
sponsor-opexPercent           - Opex percentage
sponsor-pue                   - PUE factor
sponsor-itLoad                - IT load (MW)
sponsor-gridConnectionRate    - Grid connection rate
sponsor-grossFacilityPower    - Gross facility power (MW)
sponsor-constructionStart     - Construction start date
sponsor-constructionDurationMonths - Construction duration
```

### Sponsor Form - Land & Infrastructure
```
sponsor-landPurchase          - Land purchase cost
sponsor-gridConnectionCosts   - Grid connection costs
sponsor-stampDutyStructure    - Stamp duty structure
sponsor-stampDutyFixed        - Stamp duty fixed amount
sponsor-stampDutyPercent      - Stamp duty percentage
sponsor-landTotal             - Land total display
sponsor-landLocationQuality   - Land location quality
sponsor-landBreakdownPurchase - Land purchase breakdown
sponsor-landBreakdownGrid     - Grid connection breakdown
sponsor-landBreakdownStamp    - Stamp duty breakdown
```

### Sponsor Form - CapEx Internal
```
sponsor-capexInternalPerMW    - Internal CapEx per MW
sponsor-buildArchitectural    - Architectural costs
sponsor-buildCivilStructural  - Civil/Structural costs
sponsor-buildSubstations      - Substations costs
sponsor-buildUndergroundUtilities - Underground utilities
sponsor-buildCrusaderModules  - Crusader modules
sponsor-buildBess             - BESS costs
sponsor-buildMainContractorInstallation - Installation
sponsor-buildPhotovoltaicSystem - PV system
sponsor-buildLandscaping      - Landscaping
sponsor-buildPreliminariesGeneral - Preliminaries
sponsor-buildMainContractorMargin - Contractor margin
sponsor-capexInternalTotal    - Internal CapEx total display
sponsor-capexInternalBase     - Internal base display
sponsor-contingencyInternal   - Internal contingency display
```

### Sponsor Form - CapEx Market
```
sponsor-capexMarketPerMW      - Market CapEx per MW
sponsor-marketArchitectural   - Market architectural
sponsor-marketCivilStructural - Market civil/structural
sponsor-marketSubstations     - Market substations
sponsor-marketUndergroundUtilities - Market utilities
sponsor-marketCrusaderModules - Market modules
sponsor-marketBess            - Market BESS
sponsor-marketMainContractorInstallation - Market installation
sponsor-marketPhotovoltaicSystem - Market PV
sponsor-marketLandscaping     - Market landscaping
sponsor-marketPreliminariesGeneral - Market preliminaries
sponsor-marketMainContractorMargin - Market margin
sponsor-capexMarketTotal      - Market CapEx total display
sponsor-capexMarketBase       - Market base display
sponsor-contingencyMarket     - Market contingency display
```

### Sponsor Form - Fees
```
sponsor-feesDM                - Development Management fees
sponsor-feesManagement        - Management fee amount
sponsor-feesManagementPercent - Management fee percentage
sponsor-feesTotal             - Fees total display
sponsor-feesBreakdownDM       - DM fees breakdown
sponsor-feesBreakdownMgmt     - Management fees breakdown
sponsor-feesBreakdownDay1     - Day 1 fees breakdown
```

### Sponsor Form - ABS Day 1 Close Fees (15 fields)
```
sponsor-internalArrangerFee   - Internal Arranger Fee (% of Debt)
sponsor-externalArrangerFee   - External Arranger Fee (% of Debt)
sponsor-legalIssuer           - Legal Counsel - Issuer
sponsor-legalUnderwriter      - Legal Counsel - Underwriter
sponsor-ratingAgency          - Rating Agency
sponsor-trusteeSetup          - Trustee Setup
sponsor-payingAgentSetup      - Paying Agent Setup
sponsor-financialAdvisors     - Financial/Tax Advisors
sponsor-technicalAdvisors     - Technical/Engineering Advisors
sponsor-insuranceAdvisor      - Insurance Advisor
sponsor-listingFees           - Listing/Regulatory Fees
sponsor-spvSetup              - SPV Setup
sponsor-swapFee               - Swap Execution Fee
sponsor-greenBondFee          - Green Bond/ESG Verification
sponsor-otherTransactionCosts - Other Transaction Costs
sponsor-totalDay1Fees         - Total Day 1 Close Fees (display)
```

### Sponsor Form - Developer Economics
```
sponsor-developerProfit       - Developer Profit (EUR)
sponsor-developerMarginPercent - Developer Margin (%)
sponsor-darkProfit            - DARK Development Profit
sponsor-grandTotal            - Grand Total (Internal)
sponsor-grandTotalMarket      - Grand Total (Market)
```

### Sponsor Form - NOI Calculation
```
sponsor-noiGrossRevenue       - NOI Gross Revenue
sponsor-noiOtherOpex          - NOI Other Opex
sponsor-noiElectricity        - NOI Electricity
sponsor-noiBeforeAMF          - NOI Before AMF
sponsor-noiAMF                - NOI Asset Management Fee
sponsor-noiForDebtService     - NOI Available for Debt Service
```

### Sponsor Form - Coverage Methods
```
sponsor-seniorCoverageMethods - Senior coverage methods
sponsor-seniorCoveragePercent - Senior coverage %
sponsor-seniorMethodCost      - Senior method cost
sponsor-seniorCoverageMethod  - Senior coverage method selector
sponsor-mezzCoverageMethods   - Mezzanine coverage methods
sponsor-mezzCoveragePercent   - Mezzanine coverage %
sponsor-mezzMethodCost        - Mezzanine method cost
sponsor-mezzCoverageMethod    - Mezzanine coverage method selector
```

### Sponsor Form - Timeline
```
sponsor-timeline-today        - Timeline today marker
sponsor-timeline-day1         - Timeline Day 1 marker
sponsor-timeline-duration     - Timeline duration bar
sponsor-timeline-revenue      - Timeline revenue start
sponsor-timeline-operating    - Timeline operating period
sponsor-timeline-maturity     - Timeline maturity date
sponsor-timeline-complete     - Timeline completion
```

### Currency Display Fields
```
sponsor-capex-currency        - CapEx currency selector
sponsor-kwh-currency          - kWh currency selector
abs-fees-currency             - ABS fees currency display
capex-market-currency         - Market CapEx currency
capex-internal-currency       - Internal CapEx currency
land-currency                 - Land currency
land-currency-display         - Land currency display
fees-currency                 - Fees currency
developer-currency            - Developer currency
developer-profit-currency-display - Developer profit display
grid-currency-display         - Grid currency display
stamp-currency-display        - Stamp duty currency
```

### Project Management Section
```
projects-section              - Projects section container
add-project-btn               - Add new project button
projects-grid                 - Projects grid container
project-card-{id}             - Individual project card
edit-project-modal            - Edit project modal
edit-project-title            - Edit title field
edit-project-description      - Edit description
edit-project-value            - Edit value field
edit-project-progress         - Edit progress
edit-project-status           - Edit status
edit-project-currency         - Edit currency
edit-project-gross-it-load    - Edit IT load
edit-project-pue              - Edit PUE
edit-project-capex-cost       - Edit capex cost
edit-project-capex-rate       - Edit capex rate
edit-project-monthly-rent     - Edit monthly rent
edit-project-opex             - Edit opex
edit-project-land-fees        - Edit land fees
edit-project-details          - Edit details
save-project-btn              - Save project button
cancel-edit-btn               - Cancel edit button
```

### Trash Section
```
trash-section                 - Trash management section
trash-grid                    - Trash items grid
trash-loading                 - Trash loading indicator
trash-empty                   - Empty trash button
trash-btn                     - Trash button
delete-confirm-modal          - Deletion confirmation modal
delete-confirm-message        - Confirmation message
confirm-delete-btn            - Confirm deletion button
cancel-delete-btn             - Cancel deletion button
```

### Admin Panel
```
adminPanel                    - Admin panel container
adminTabContent               - Admin tab content
admin-users-tab               - Admin users tab
admin-registrations-tab       - Admin registrations tab
admin-ip-rules-tab            - Admin IP rules tab
admin-audit-log-tab           - Admin audit log tab
user-selector                 - User selector dropdown
placeholder-content           - Placeholder content area
```

### Upload Modal
```
uploadModal                   - Upload modal
uploadSponsorTab              - Upload sponsor tab
uploadSponsorPreview          - Upload preview button
sponsorPreviewContent         - Sponsor preview content
manualSponsorTab              - Manual sponsor tab
sponsor-editor-section        - Sponsor editor section
```

### Analytics Section
```
analytics-section             - Analytics container
analyticsChart                - Analytics chart canvas
spreadChart                   - Spread chart canvas
capital-stack-viz             - Capital stack visualization
```

### Risk Management Section
```
risk-section                  - Risk management container
metric-irr                    - IRR metric display
metric-dscr                   - DSCR metric display
metric-leverage               - Leverage metric display
metric-rating                 - Rating metric display
metric-coverage               - Coverage metric display
```

### Compliance & Documents
```
compliance-section            - Compliance management
documents-section             - Documents display
document-upload-btn           - Document upload button
document-list                 - Document list container
```

### Portfolio Section
```
portfolio-section             - Portfolio management
portfolio-summary             - Portfolio summary
portfolio-performance         - Portfolio performance
portfolio-allocation          - Portfolio allocation
```

### Data Section
```
data-section                  - Data sources section
assetFilter                   - Asset class filter
imported-data-display         - Imported data display
data-refresh-btn              - Data refresh button
```

### Support Section
```
support-section               - Support section
support-form                  - Support form
support-message               - Support message textarea
support-submit-btn            - Support submit button
```

---

## 🐍 PYTHON VARIABLES AND DATA STRUCTURES (app.py)

### Global Configuration Variables
```python
DATA_DIR = 'data'                       # Data directory path
UPLOAD_FOLDER = 'uploads'               # Upload directory
MAX_FILE_SIZE = 10 * 1024 * 1024       # 10MB max file size
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'pdf'}
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')
```

### Global Data Structures
```python
users = {}                              # Dictionary of all users
registrations = {}                      # Dictionary of registrations
login_attempts = {}                     # Dictionary of login attempts
ip_lockouts = {}                        # Dictionary of IP lockout data
admin_actions = []                      # List of admin actions log
projects = {}                           # Dictionary of projects by user
expired_registrations = []              # List of expired registrations
ip_tracking = {}                        # IP access tracking data
```

### Session Variables (stored per IP)
```python
session[f'site_authenticated_{ip}']     # Site authentication flag
session[f'user_authenticated_{ip}']     # User authentication flag
session[f'is_admin_{ip}']               # Admin flag
session[f'user_email_{ip}']             # User email
session[f'account_type_{ip}']           # Account type
session[f'login_count_{ip}']            # Login count
session['ip_address']                   # IP address
session['data_changed']                 # Data change indicator
```

### User Data Structure
```python
user = {
    'email': str,                       # User email
    'username': str,                    # Username
    'full_name': str,                   # Full name
    'account_type': str,                # Account type
    'is_admin': bool,                   # Admin flag
    'admin_approved': bool,             # Approval status
    'password': str,                    # Hashed password
    'password_expiry': datetime,        # Password expiration
    'email_verified': bool,             # Email verification
    'created_at': datetime,             # Account creation
    'login_count': int,                 # Total logins
    'last_login': datetime,             # Last login time
    'preferences': {
        'timezone': str,                # Timezone setting
        'theme': str                    # Theme preference
    }
}
```

### Registration Data Structure
```python
registration = {
    'email': str,                       # User email
    'full_name': str,                   # Full name
    'phone': str,                       # Phone number
    'country_code': str,                # Country code
    'company_name': str,                # Company name
    'company_number': str,              # Company registration
    'job_title': str,                   # Job title
    'business_address': str,            # Business address
    'generated_password': str,          # Secure password
    'verification_token': str,          # Email verification token
    'approval_token': str,              # Admin approval token
    'email_verified': bool,             # Email verification status
    'admin_approved': bool,             # Admin approval status
    'created_at': datetime,             # Registration timestamp
    'ip_address': str                   # Registration IP
}
```

### Project Data Structure
```python
project = {
    'id': str,                          # Project ID (proj_xxx)
    'projectId': str,                   # Alternative ID
    'title': str,                       # Project title
    'description': str,                 # Project description
    'value': float,                     # Project value
    'progress': int,                    # Progress (0-100)
    'status': str,                      # Project status
    'details': str,                     # Detailed information
    'currency': str,                    # Currency code
    'grossITLoad': float,               # Gross IT load (MW)
    'pue': float,                       # PUE factor
    'capexCost': float,                 # Capex cost
    'capexRate': float,                 # Capex rate
    'landPurchaseFees': float,          # Land fees
    'grossMonthlyRent': float,          # Monthly rent
    'opex': float,                      # Operating expenses
    'seriesId': str,                    # Series identifier
    'created_at': datetime,             # Creation timestamp
    'updated_at': datetime,             # Update timestamp
    'created_by': str,                  # Creator email
    'gate1_completed': bool,            # Gate 1 completion
    'gate2_completed': bool,            # Gate 2 completion
    'gate3_completed': bool,            # Gate 3 completion
    'gate2_data': dict,                 # Gate 2 data
    'gate3_data': dict,                 # Gate 3 data
    'meta': {
        'projectTitle': str,
        'locationCountry': str,
        'status': str,
        'capexCurrency': str,
        'kwhCurrency': str,
        'grossITLoadMW': float,
        'pue': float,
        'grossMonthlyRent': float,
        'opexPercent': float,
        'constructionStart': date,
        'constructionDurationMonths': int
    },
    'capex': {
        'internal': {...},              # Internal capex breakdown
        'market': {...}                 # Market capex breakdown
    },
    'rollups': {
        'capexCostPriceEUR': float,
        'grandTotalEUR': float
    }
}
```

### IP Lockout Structure
```python
lockout = {
    'ip': str,                          # IP address
    'lockout_type': str,                # Lockout type
    'lockout_time': datetime,           # Lockout timestamp
    'failed_attempts': int,             # Failed attempt count
    'failed_passwords': list,           # Attempted passwords
    'unlock_token': str,                # Unlock token
    'reason': str,                      # Lockout reason
    'banned_by': str                    # Admin who banned
}
```

### Login Attempt Structure
```python
attempt = {
    'ip': str,                          # IP address
    'email': str,                       # User email
    'password_attempted': str,          # Password hash/indicator
    'attempt_type': str,                # Attempt type
    'timestamp': datetime,              # Attempt timestamp
    'success': bool,                    # Success/failure flag
    'user_agent': str                   # Browser user agent
}
```

### Admin Action Structure
```python
action = {
    'action': str,                      # Action type
    'user_or_ip': str,                  # User email or IP
    'details': dict,                    # Action details
    'timestamp': datetime,              # Action timestamp
    'ip_address': str                   # Acting IP address
}
```

### Request Variables
```python
request.method                          # HTTP method
request.json                            # JSON data
request.form                            # Form data
request.files                           # Uploaded files
request.args                            # URL parameters
request.headers                         # Request headers
request.remote_addr                     # Remote IP address
request.user_agent                      # User agent
```

### Response Variables
```python
response = jsonify({...})               # JSON response
response.status_code                    # HTTP status code
response.headers                        # Response headers
```

---

## 📋 COMPLETE FIELD REFERENCE

### Currency Codes
```
EUR - Euro (€)
USD - US Dollar ($)
GBP - British Pound (£)
JPY - Japanese Yen (¥)
AED - UAE Dirham (د.إ)
```

### Project Status Values
```
draft         - Draft project
active        - Active project
completed     - Completed project
on_hold       - On hold
archived      - Archived
cancelled     - Cancelled
```

### Account Types
```
admin         - Administrator
analyst       - Data Analyst
sponsor       - Project Sponsor
viewer        - Read-only Viewer
```

### Lockout Types
```
24h           - 24 hour lockout
7d            - 7 day lockout
30d           - 30 day lockout
permanent     - Permanent ban
```

### IP Rule Types
```
allow         - Whitelist rule
deny          - Blacklist rule
```

### Permutation Ranking Objectives
```
maximize_irr          - Maximize IRR
minimize_risk         - Minimize Risk
maximize_npv          - Maximize NPV
balance_risk_return   - Balance Risk/Return
custom                - Custom objective
```

### Gate Status Values
```
draft         - Draft status
submitted     - Submitted for review
approved      - Approved
rejected      - Rejected
in_progress   - In progress
completed     - Completed
```

---

This documentation provides a complete reference of all variables, tables, collections, and data structures used throughout the Atlas Nexus application.

**Total Collections:** 18
**Total JavaScript Variables:** ~150
**Total Form Field IDs:** ~300
**Total Python Variables:** ~50
**Total Data Structures:** 12

**Last Updated:** 2026-01-19
**Version:** 1.0
**Status:** Complete
