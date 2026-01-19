# AtlasNexus Production Architecture

## 🏗️ Complete System Architecture

### Overview

Your production site (https://atlasnexus.co.uk) is a **full-stack application** with:
- **Frontend:** HTML/JavaScript/CSS (rendered by Flask)
- **Backend:** Python Flask API
- **Database:** MongoDB Atlas (cloud)
- **Hosting:** Vercel (serverless)
- **Storage:** Vercel Blob Storage (files) + MongoDB GridFS (large datasets)

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                                                                 │
│  ┌──────────────────┐        ┌──────────────────┐              │
│  │  dashboard.html  │◄──────►│  JavaScript      │              │
│  │  (Projects Form) │        │  Calculations    │              │
│  └──────────────────┘        └──────────────────┘              │
│           │                           │                         │
│           │ Form Submission           │ Real-time Calcs         │
│           ▼                           ▼                         │
└───────────┼───────────────────────────┼─────────────────────────┘
            │                           │
            │ HTTPS POST                │ Display Updates
            ▼                           │
┌─────────────────────────────────────────────────────────────────┐
│                    VERCEL (Hosting Platform)                    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     app.py (Flask API)                   │  │
│  │                                                          │  │
│  │  Routes:                                                 │  │
│  │  • /api/projects (CRUD operations)                      │  │
│  │  • /api/permutation/execute (Run calculations)          │  │
│  │  • /api/securitization/calculate                        │  │
│  │  └──────────────────────────────────────────────────────│  │
│           │                    │                    │          │
│           │                    │                    │          │
│           ▼                    ▼                    ▼          │
│  ┌──────────────┐   ┌──────────────────┐  ┌──────────────┐   │
│  │ cloud_db.py  │   │ permutation_     │  │ securitization│  │
│  │              │   │ engine.py        │  │ _engine.py    │  │
│  └──────────────┘   └──────────────────┘  └──────────────┘   │
│           │                    │                    │          │
└───────────┼────────────────────┼────────────────────┼──────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────┐  ┌──────────────────┐  ┌──────────────┐
│   MongoDB Atlas     │  │  Vercel Blob     │  │   GridFS     │
│   (Primary DB)      │  │  Storage         │  │  (Large Data)│
│                     │  │                  │  │              │
│ • Users             │  │ • Excel uploads  │  │ • Permutation│
│ • Projects          │  │ • Documents      │  │   results    │
│ • Registrations     │  │ • Attachments    │  │ • Snapshots  │
│ • Admin Actions     │  └──────────────────┘  └──────────────┘
│ • Permutation Logs  │
└─────────────────────┘
```

---

## 💾 Where Data is Stored

### 1. MongoDB Atlas (Primary Database)

**Connection:** `cloud_database.py` ([cloud_database.py:1-987](cloud_database.py#L1-L987))

**Location:** Cloud-hosted (free tier: 512MB)

**Collections:**

#### A. `users` Collection
```json
{
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "account_type": "sponsor|admin|internal",
  "password": "hashed_password",
  "created_at": "2026-01-19T12:00:00",
  "email_verified": true,
  "admin_approved": true,
  "preferences": {
    "timezone": "Europe/London",
    "theme": "dark"
  }
}
```

**Functions:**
- `cloud_db.load_users()` - Get all users
- `cloud_db.save_user(email, user_data)` - Save/update user

---

#### B. `projects` Collection

**Structure:**
```json
{
  "_id": ObjectId("..."),
  "user_email": "user@example.com",
  "projects": [
    {
      "id": "proj_1737297600000",
      "status": "draft|active|completed|archived|deleted",
      "title": "London DC Project",
      "created": "2026-01-19T12:00:00",
      "updated": "2026-01-19T13:30:00",

      // Project Metadata
      "meta": {
        "projectTitle": "London DC Project",
        "sponsor": "DARK Capital",
        "location": "London, UK",
        "projectCurrency": "GBP",
        "capexCurrency": "EUR"
      },

      // Power & Capacity
      "power": {
        "grossFacilityPower": 100,  // MW
        "pue": 1.25,
        "itLoad": 80,  // Calculated: 100 / 1.25
        "overheadPower": 20  // Calculated: 100 - 80
      },

      // Revenue Parameters
      "revenue": {
        "grossMonthlyRent": 1000000,
        "leaseType": "TripleNet",
        "occupancy": 95,
        "opexPercent": 5,
        "electricityRate": 100  // Only if Gross lease
      },

      // Build CapEx - Internal
      "capexInternal": {
        "buildArchitectural": 5000000,
        "buildCivilStructural": 15000000,
        "buildSubstations": 20000000,
        // ... 17 fields total
        "contingencyPercent": 10,
        "total": 110000000  // Base + Contingency
      },

      // Build CapEx - Market
      "capexMarket": {
        "marketArchitectural": 6000000,  // 20% higher
        "marketCivilStructural": 18000000,
        // ... 17 fields total
        "contingencyPercent": 10,
        "total": 132000000
      },

      // Land & Infrastructure
      "land": {
        "landLocationQuality": "urban",
        "landPurchase": 80000000,
        "gridConnectionQuality": "good",
        "gridConnectionCosts": 20000000,
        "stampDutyStructure": "company",
        "stampDutyPercent": 5,
        "stampDutyFixed": null,
        "total": 104000000  // Land + Grid + Stamp
      },

      // Fees
      "fees": {
        "feesDM": 2000000,
        "feesManagementPercent": 3,
        "feesManagement": 6000000,
        "total": 8000000
      },

      // Construction Interest Coverage
      "construction": {
        "seniorMethod": "dsra",
        "seniorMonths": 6,
        "mezzMethod": "capitalised",
        // ... coverage settings
      },

      // Calculated Totals (computed server-side)
      "calculated": {
        "internalGrandTotal": 220000000,
        "marketGrandTotal": 242000000,
        "darkProfit": 22000000,
        "developerMargin": 10.0,
        "noiGrossRevenue": 11400000,
        "noiElectricity": 0,
        "noiOtherOpex": 570000,
        "noiBeforeAMF": 10830000,
        "noiAMF": 108300,
        "noiForDebtService": 10721700
      }
    }
  ],
  "series": [],  // Project folders/organization
  "order": []    // Display order
}
```

**Functions:**
- `cloud_db.load_projects()` - Get all projects for all users
- `cloud_db.save_projects(user_email, project_data)` - Save user's projects

**Access in app.py:**
```python
# Load projects
projects_data = db_load_projects()

# Save project
success = db_save_project_data(user_email, {
    'projects': [project1, project2, ...],
    'series': [...],
    'order': [...]
})
```

---

#### C. `permutation_snapshots` Collection

**Purpose:** Track approved versions of projects before permutation runs

```json
{
  "_id": ObjectId("..."),
  "project_id": "proj_1737297600000",
  "user_email": "user@example.com",
  "snapshot": {
    // Complete project data at time of permutation
  },
  "version": 1,
  "approved": true,
  "timestamp": "2026-01-19T14:00:00"
}
```

**Functions:**
- `cloud_db.save_permutation_snapshot(project_id, snapshot_data)`
- `cloud_db.get_permutation_snapshot(project_id)`

---

#### D. `change_requests` Collection

**Purpose:** Track client modifications after permutation approval

```json
{
  "_id": ObjectId("..."),
  "project_id": "proj_1737297600000",
  "user_email": "user@example.com",
  "changes": {
    "grossFacilityPower": {"old": 100, "new": 120},
    "landPurchase": {"old": 80000000, "new": 90000000}
  },
  "status": "pending|approved|rejected",
  "submitted_at": "2026-01-19T15:00:00",
  "reviewed_by": "admin@example.com",
  "reviewed_at": "2026-01-19T15:30:00"
}
```

---

### 2. MongoDB GridFS (Large Binary Storage)

**Purpose:** Store large permutation results (millions of rows)

**Location:** Same MongoDB Atlas database, special GridFS collections

**Storage:**
- `fs.files` - Metadata about stored files
- `fs.chunks` - Actual file chunks (16MB each)

**What's Stored:**
```json
{
  "filename": "permutation_results_proj_1737297600000.json.gz",
  "metadata": {
    "project_id": "proj_1737297600000",
    "executed_by": "admin@example.com",
    "permutation_count": 1000000,
    "execution_time": "45 seconds",
    "timestamp": "2026-01-19T14:30:00"
  },
  "length": 125829120,  // ~120MB compressed
  "chunkSize": 16777216,
  "uploadDate": "2026-01-19T14:30:45"
}
```

**File:** `permutation_results_storage.py`

**Functions:**
```python
from permutation_results_storage import permutation_storage

# Save results
storage_result = permutation_storage.save_permutation_results(
    project_id="proj_123",
    user_email="admin@example.com",
    results_data={
        'permutations': [...1000000 scenarios...],
        'summary': {...},
        'parameters': {...}
    }
)

# Load results
results = permutation_storage.load_permutation_results(project_id="proj_123")
```

---

### 3. Vercel Blob Storage

**Purpose:** File uploads (Excel files, documents)

**Location:** Vercel's edge network

**File:** `blob_storage.py`

**What's Stored:**
- Excel file uploads from sponsors
- Project attachments
- User documents

**Functions:**
```python
from blob_storage import upload_document, get_user_documents

# Upload file
blob_url = upload_document(
    user_email="user@example.com",
    file_data=file_bytes,
    filename="project_data.xlsx",
    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Get user's files
files = get_user_documents(user_email="user@example.com")
```

**Database Record (in MongoDB):**
```json
{
  "_id": ObjectId("..."),
  "user_email": "user@example.com",
  "filename": "project_data.xlsx",
  "blob_url": "https://vercel-blob.com/abc123/project_data.xlsx",
  "size": 2048576,
  "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "uploaded_at": "2026-01-19T12:00:00"
}
```

---

## 🧮 Where Calculations Run

### 1. Frontend JavaScript (Real-time)

**Location:** `templates/dashboard.html` ([dashboard.html:8920-9243](templates/dashboard.html#L8920-L9243))

**What's Calculated:**
- IT Load: `grossFacilityPower / pue`
- Overhead Power: `grossFacilityPower - itLoad`
- Land Purchase: `MW × acres/MW × cost/acre`
- Grid Connection: `MW × cost/MW`
- Stamp Duty: `landPurchase × (rate% / 100)`
- Management Fee: Bidirectional `% ↔ €`
- CapEx Totals: `base + contingency`
- Developer Profit: `Market - Internal`
- NOI Waterfall: Complete Year 1 cash flow

**When:** As user types (instant feedback)

**Functions:**
```javascript
// Main calculation function
function calculateSponsorTotals() {
    // ... calculates all totals
}

// NOI calculation
function calculateNOIWaterfall() {
    const grossRevenue = monthlyRent × 12 × (occupancy / 100);
    const electricity = (leaseType === 'Gross') ? itLoad × 8760 × rate : 0;
    const opex = grossRevenue × (opexPercent / 100);
    const noi = grossRevenue - electricity - opex;
    const amf = noi × 0.01;
    const noiForDebt = noi - amf;
    // ... update display
}

// Developer profit
function calculateDeveloperProfit() {
    const profit = marketCapEx - internalCapEx;
    const margin = (profit / internalCapEx) × 100;
    // ... update display
}
```

**Storage:** Results displayed instantly, NOT stored until user clicks "Save Project"

---

### 2. Backend Python (Permutation Engine)

**Location:** `permutation_engine.py` / `permutation_engine_advanced.py`

**What's Calculated:**
- Thousands/millions of financing scenarios
- DSCR-based capital stack sizing
- LTV-based capital stack sizing
- IRR, NPV, equity returns for each scenario
- Tranche sizing (Senior, Mezz, Equity)
- Debt service coverage ratios
- Cash flow waterfalls
- Risk-adjusted returns

**When:** Admin triggers permutation run via `/api/permutation/execute`

**Example Flow:**
```python
# app.py endpoint
@app.route('/api/permutation/execute', methods=['POST'])
def execute_permutation():
    data = request.get_json()
    project_id = data.get('projectId')

    # Load project from MongoDB
    project = get_project_by_id(project_id)

    # Run permutation engine
    from permutation_engine_advanced import run_advanced_permutation_engine

    results = run_advanced_permutation_engine({
        'grossFacilityPower': project['power']['grossFacilityPower'],
        'internalCapEx': project['calculated']['internalGrandTotal'],
        'marketCapEx': project['calculated']['marketGrandTotal'],
        'noiForDebtService': project['calculated']['noiForDebtService'],
        'debtTenor': project['debt']['tenor'],
        // ... all parameters
    })

    # Results contain:
    # {
    #   'permutations': [
    #     {
    #       'id': 'perm_0001',
    #       'senior_size': 150000000,
    #       'senior_rate': 5.5,
    #       'mezz_size': 50000000,
    #       'mezz_rate': 9.0,
    #       'equity_size': 42000000,
    #       'senior_dscr': 1.35,
    #       'blended_dscr': 1.25,
    #       'irr': 15.2,
    #       'npv': 12500000,
    #       // ... thousands more fields
    #     },
    #     // ... 1,000,000 more permutations
    #   ],
    #   'summary': {
    #     'total_permutations': 1000000,
    #     'viable_count': 750000,
    #     'avg_irr': 14.8,
    #     'max_npv': 25000000
    #   }
    # }

    # Store results in GridFS (too large for MongoDB docs)
    storage_result = permutation_storage.save_permutation_results(
        project_id, email, results
    )

    return jsonify({'success': True, 'summary': results['summary']})
```

**Algorithm Details:**

1. **Input Hierarchy Processing:**
   ```python
   from phase1_components import input_hierarchy_processor

   processed = input_hierarchy_processor.process_input(
       input_level=InputLevel.MANUAL,  # or EXCEL, API
       raw_data=project_data
   )
   ```

2. **Reverse DSCR Calculation:**
   ```python
   from phase1_components import reverse_dscr_engine

   # Given NOI and target DSCR, calculate max debt
   max_senior_debt = reverse_dscr_engine.calculate_max_debt(
       noi=10721700,
       target_dscr=1.35,
       interest_rate=0.055,
       tenor=17
   )
   # Returns: €143,580,000
   ```

3. **Repo Eligibility Check:**
   ```python
   from phase1_components import repo_eligibility_engine

   eligible = repo_eligibility_engine.check_eligibility(
       jurisdiction=RepoJurisdiction.UK,
       asset_type='data_center',
       collateral_value=150000000
   )
   ```

4. **Viability Tiering:**
   ```python
   from phase1_components import viability_tiering_engine

   tier = viability_tiering_engine.assess_viability(
       dscr=1.35,
       ltv=0.65,
       irr=15.2,
       npv=12500000
   )
   # Returns: ViabilityTier.TIER_1 (optimal) or TIER_2, TIER_3
   ```

**Storage:** Results saved to GridFS, reference stored in MongoDB

---

### 3. Backend Python (Securitization Engine)

**Location:** `securitization_engine.py`

**What's Calculated:**
- ABS/CDO structuring
- Tranche waterfall distributions
- Credit enhancement calculations
- Risk-weighted returns
- Prepayment scenarios
- Default probability modeling

**When:** Admin triggers via `/api/securitization/calculate`

**Proprietary:** Algorithm details are hidden (competitive advantage)

---

## 🔄 Complete Data Flow Example

### Scenario: Sponsor Creates Project & Admin Runs Permutation

**Step 1: Sponsor Fills Form**
```
User opens: https://atlasnexus.co.uk/dashboard
├─ Loads: templates/dashboard.html
├─ JavaScript: calculateSponsorTotals() runs on each input
├─ Display updates: Real-time calculations shown
└─ User clicks: "Save Project"
```

**Step 2: Save to Database**
```javascript
// Frontend: Collect all form data
const projectData = {
    meta: { projectTitle: "London DC", ... },
    power: { grossFacilityPower: 100, ... },
    revenue: { grossMonthlyRent: 1000000, ... },
    capexInternal: { buildArchitectural: 5000000, ... },
    capexMarket: { marketArchitectural: 6000000, ... },
    land: { landPurchase: 80000000, ... },
    fees: { feesDM: 2000000, ... },
    calculated: {
        internalGrandTotal: 220000000,
        marketGrandTotal: 242000000,
        darkProfit: 22000000,
        noiForDebtService: 10721700
    }
};

// POST to backend
fetch('/api/projects/sponsor', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(projectData)
});
```

**Step 3: Backend Saves to MongoDB**
```python
# app.py
@app.route('/api/projects/sponsor', methods=['POST'])
def save_sponsor_project():
    data = request.get_json()
    user_email = session.get('user_email')

    # Add metadata
    project = {
        'id': f"proj_{int(time.time() * 1000)}",
        'status': 'draft',
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        **data
    }

    # Load existing projects
    projects_data = db_load_projects()
    user_projects = projects_data.get(user_email, {'projects': []})
    user_projects['projects'].append(project)

    # Save to MongoDB
    success = db_save_project_data(user_email, user_projects)

    return jsonify({'success': success, 'projectId': project['id']})
```

**MongoDB Insert:**
```javascript
db.projects.updateOne(
    { user_email: "user@example.com" },
    {
        $set: {
            user_email: "user@example.com",
            projects: [...existing, newProject],
            series: [],
            order: []
        }
    },
    { upsert: true }
)
```

**Step 4: Admin Loads Project into Permutation Engine**
```
Admin opens: https://atlasnexus.co.uk/permutation-engine
├─ Loads: templates/permutation_engine_v2.html
├─ Fetches: GET /api/permutation/projects
│   └─ Returns: All projects from all sponsors
├─ Admin selects: "London DC Project"
└─ Clicks: "Load into Engine"
```

**Step 5: Create Snapshot (Approved Version)**
```javascript
// Frontend
fetch('/api/permutation/snapshot', {
    method: 'POST',
    body: JSON.stringify({
        projectId: "proj_1737297600000",
        snapshotData: {
            version: 1,
            approved: true,
            snapshot: projectData  // Complete project at this moment
        }
    })
});
```

**MongoDB Insert:**
```javascript
db.permutation_snapshots.insertOne({
    project_id: "proj_1737297600000",
    user_email: "user@example.com",
    snapshot: { ...projectData },
    version: 1,
    approved: true,
    timestamp: ISODate("2026-01-19T14:00:00Z")
})
```

**Step 6: Execute Permutation**
```javascript
// Frontend: Admin configures permutation
const config = {
    projectId: "proj_1737297600000",
    parameters: {
        debtTenorRange: [15, 17, 20],  // years
        seniorRateRange: [5.0, 5.5, 6.0],  // %
        mezzRateRange: [8.0, 9.0, 10.0],  // %
        seniorDSCRTarget: [1.30, 1.35, 1.40],
        ltv Range: [0.60, 0.65, 0.70]
    }
};

// Trigger execution
fetch('/api/permutation/execute', {
    method: 'POST',
    body: JSON.stringify(config)
});
```

**Backend: Run Engine**
```python
# app.py
@app.route('/api/permutation/execute', methods=['POST'])
def execute_permutation():
    config = request.get_json()
    project_id = config['projectId']

    # Load project
    project = get_project_by_id(project_id)

    # Import permutation engine
    from permutation_engine_advanced import run_advanced_permutation_engine

    # Generate permutations
    # This creates 3 × 3 × 3 × 3 × 3 = 243 permutations
    # Advanced engine can generate millions
    results = run_advanced_permutation_engine({
        'noi': project['calculated']['noiForDebtService'],
        'internalCapEx': project['calculated']['internalGrandTotal'],
        'marketCapEx': project['calculated']['marketGrandTotal'],
        'parameters': config['parameters']
    })

    # Example result:
    # {
    #   'permutations': [
    #     {
    #       'id': 'perm_0001',
    #       'tenor': 17,
    #       'senior_rate': 5.5,
    #       'mezz_rate': 9.0,
    #       'senior_size': 143580000,  # Calculated from reverse DSCR
    #       'senior_dscr': 1.35,
    #       'mezz_size': 48420000,
    #       'equity_size': 50000000,
    #       'total_debt': 192000000,
    #       'ltv': 0.65,  # 192M / 242M market value
    #       'irr': 15.2,
    #       'npv': 12500000,
    #       'payback_period': 8.5,
    #       'tier': 'TIER_1'
    #     },
    #     // ... 242 more permutations
    #   ],
    #   'summary': {
    #     'total': 243,
    #     'viable': 195,
    #     'tier1_count': 42,
    #     'avg_irr': 14.8,
    #     'best_irr': 18.3,
    #     'execution_time': '2.1 seconds'
    #   }
    # }

    # Save results to GridFS (compressed JSON)
    import gzip
    import json
    compressed_data = gzip.compress(json.dumps(results).encode())

    storage_result = permutation_storage.save_permutation_results(
        project_id, email, results
    )

    return jsonify({
        'success': True,
        'summary': results['summary'],
        'storage': storage_result
    })
```

**GridFS Storage:**
```python
# permutation_results_storage.py
def save_permutation_results(project_id, user_email, results_data):
    # Compress results
    compressed = gzip.compress(json.dumps(results_data).encode())

    # Store in GridFS
    file_id = fs.put(
        compressed,
        filename=f"permutation_results_{project_id}.json.gz",
        metadata={
            'project_id': project_id,
            'executed_by': user_email,
            'permutation_count': len(results_data['permutations']),
            'timestamp': datetime.now().isoformat()
        }
    )

    return {'success': True, 'file_id': str(file_id)}
```

**Step 7: View Results**
```
Admin opens: Permutation Results Tab
├─ Fetches: GET /api/permutation/results/proj_1737297600000
├─ Backend: Loads from GridFS, decompresses
└─ Displays: Interactive table with 243 permutations
    ├─ Filters: By DSCR, IRR, Tier
    ├─ Sorts: By any column
    └─ Exports: To Excel
```

**Step 8: Client Modifies Project**
```
Sponsor edits: Gross Facility Power (100 MW → 120 MW)
├─ Frontend: Recalculates all dependent fields
├─ Clicks: "Save Changes"
└─ Backend: Detects change vs approved snapshot
    └─ Creates: Change Request in MongoDB
```

**MongoDB Insert:**
```javascript
db.change_requests.insertOne({
    project_id: "proj_1737297600000",
    user_email: "user@example.com",
    changes: {
        grossFacilityPower: { old: 100, new: 120 },
        itLoad: { old: 80, new: 96 },
        internalGrandTotal: { old: 220000000, new: 244000000 }
    },
    status: "pending",
    submitted_at: ISODate("2026-01-19T15:00:00Z")
})
```

**Step 9: Admin Reviews Change**
```
Admin opens: Change Requests Dashboard
├─ Sees: "London DC - Power increased to 120 MW"
├─ Reviews: Impact on calculations
└─ Approves/Rejects: Change request
    └─ If Approved: Re-run permutation engine
```

---

## 🗄️ Database Schema Summary

### MongoDB Collections

| Collection | Purpose | Size | Example Count |
|-----------|---------|------|---------------|
| `users` | User accounts | ~1KB/user | 50-100 users |
| `projects` | Project data | ~50KB/project | 500-1000 projects |
| `permutation_snapshots` | Approved versions | ~50KB/snapshot | 500-1000 snapshots |
| `change_requests` | Modification tracking | ~5KB/request | 200-500 requests |
| `admin_actions` | Audit log | ~1KB/action | 5000-10000 actions |
| `registrations` | Pending signups | ~1KB/reg | 20-50 pending |

### GridFS Storage

| Type | Purpose | Size | Example Count |
|------|---------|------|---------------|
| Permutation Results | Million-scenario outputs | 10-100MB/file | 200-500 files |
| Excel Snapshots | Uploaded spreadsheets | 1-5MB/file | 500-1000 files |

### Total Database Size Estimate

```
Users:          100 × 1KB =        100KB
Projects:       1000 × 50KB =      50MB
Snapshots:      1000 × 50KB =      50MB
Change Reqs:    500 × 5KB =        2.5MB
Admin Actions:  10000 × 1KB =      10MB
Registrations:  50 × 1KB =         50KB
──────────────────────────────────────
MongoDB Docs Total:            ~113MB

GridFS Results: 500 × 50MB =    25GB (compressed)
GridFS Excel:   1000 × 2MB =    2GB
──────────────────────────────────────
GridFS Total:                   ~27GB

GRAND TOTAL:                    ~27.1GB
```

**MongoDB Atlas Free Tier:** 512MB
**Your Usage:** ~113MB (documents only)
**Overflow:** GridFS results stored separately (can upgrade to paid tier or use Vercel Blob)

---

## 🚀 Vercel Deployment

**Platform:** Vercel (serverless hosting)

**Build Command:** `pip install -r requirements.txt`

**Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app`

**Environment Variables:**
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/atlasnexus
VERCEL_BLOB_READ_WRITE_TOKEN=vercel_blob_...
SECRET_KEY=your_flask_secret_key
FLASK_ENV=production
```

**Entry Point:** `wsgi.py` → imports `app.py`

**Serverless Functions:** Each API route becomes a serverless function

**Cold Start:** ~500ms (first request after idle)

**Warm Performance:** ~50-100ms (subsequent requests)

---

## 📊 Performance Characteristics

### Frontend Calculations (JavaScript)
- **Speed:** Instant (< 10ms)
- **Runs:** On every input change
- **Examples:** NOI, CapEx totals, Developer Profit

### Backend Calculations (Python)
- **Simple Queries:** 50-100ms
- **Project Save:** 200-500ms (includes MongoDB write)
- **Permutation Engine (243 scenarios):** 2-5 seconds
- **Permutation Engine (1M scenarios):** 30-60 seconds
- **GridFS Save:** 1-3 seconds (for 50MB file)

---

## 🔒 Security & Access Control

### User Roles

| Role | Can Create Projects | Can Edit Own | Can View All | Can Run Permutations |
|------|-------------------|--------------|--------------|---------------------|
| Sponsor | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Internal | ✅ Yes | ✅ Yes | ✅ Yes (read-only) | ❌ No |
| Admin | ✅ Yes | ✅ Yes | ✅ Yes (edit all) | ✅ Yes |

### API Authentication

**Session-based:** Flask session cookies

**IP Tracking:** `ip_management.py` tracks login attempts

**Rate Limiting:** `security_hardening.py` applies rate limits

---

## 📖 Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Main Flask application | 8800+ |
| `cloud_database.py` | MongoDB Atlas interface | 987 |
| `templates/dashboard.html` | Projects form (frontend) | 9300+ |
| `permutation_engine.py` | Basic permutation calculations | ~500 |
| `permutation_engine_advanced.py` | Advanced permutation engine | ~1500 |
| `permutation_results_storage.py` | GridFS storage handler | ~300 |
| `securitization_engine.py` | ABS/CDO calculations | ~800 |
| `phase1_components.py` | Input hierarchy, reverse DSCR, viability tiering | ~1200 |

---

## 🎯 Summary

**Where Data Lives:**
- **User accounts, projects, metadata:** MongoDB Atlas (cloud)
- **Large permutation results:** GridFS (MongoDB)
- **File uploads:** Vercel Blob Storage

**Where Calculations Run:**
- **Real-time UI updates:** Browser (JavaScript)
- **Permutation engine:** Vercel serverless (Python)
- **Securitization:** Vercel serverless (Python)

**Production URL:** https://atlasnexus.co.uk

**Database:** MongoDB Atlas (free tier, 512MB)

**Hosting:** Vercel (serverless, auto-scaling)

**Data Flow:** Browser ↔ Vercel (Flask API) ↔ MongoDB Atlas + GridFS
