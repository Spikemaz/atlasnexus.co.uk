# AtlasNexus System Access Guide

## 🌐 Live Site Access
**URL:** https://atlasnexus.co.uk

## 🔐 Security Gates

### Gate 1: Site Password
- **Password:** `RedAMC`
- Required for all users to access the site

### Gate 2: User Authentication
Login with your credentials after passing Gate 1

## 👤 User Accounts

### Admin Account
- **Email:** spikemaz8@aol.com  
- **Password:** [your password]
- **Access Level:** Full administrative control

### Test Account (External)
- **Email:** moore2marcus@gmail.com
- **Password:** password
- **Access Level:** External user (client)

## 📋 Features by Access Level

### Admin Features (spikemaz8@aol.com)
1. **Dashboard** (`/dashboard`)
   - View all projects across all users
   - Create/edit/delete any project
   - Load projects into permutation engine

2. **Admin Panel** (`/admin-panel`)
   - View all registered users
   - Approve/reject registrations
   - Delete registrations
   - Monitor user activity
   - View login attempts
   - Manage user passwords

3. **Permutation Engine** (`/dashboard#permutation`)
   - Load any project data
   - Configure securitization parameters
   - Run permutation calculations
   - 116 configuration fields
   - Generate securitization reports

4. **Project Management**
   - Create projects with full data
   - Save to MongoDB cloud
   - Snapshot system for permutations
   - Change tracking and approval

### External User Features
1. **Dashboard** (`/dashboard`)
   - View only their own projects
   - Create new projects
   - Edit their existing projects
   - Delete their projects

2. **Project Data Fields**
   - Title and description
   - Location
   - Status (draft/active/completed)
   - Financial metrics (value, currency)
   - Technical specs (IT load, PUE)
   - CapEx and OpEx data
   - Monthly rent and fees

## 🗄️ Data Storage
All data is stored in **MongoDB Atlas Cloud**:
- Users and registrations
- Projects and project data
- Admin actions and logs
- Permutation snapshots
- Change requests

## 📊 Workflow

### For Clients:
1. Register at `/register`
2. Wait for admin approval
3. Login at `/secure-login`
4. Create projects in dashboard
5. Save project data

### For Admin:
1. Login with admin account
2. Review registrations in admin panel
3. Approve/reject users
4. Load client projects into permutation engine
5. Run securitization calculations
6. Generate reports

## 🔧 Technical Details

### MongoDB Collections:
- `users` - User accounts
- `registrations` - Pending registrations
- `projects` - Project data by user
- `admin_actions` - Audit log
- `permutation_snapshots` - Project snapshots
- `project_changes` - Change requests

### API Endpoints:
- `/api/projects` - Project CRUD operations
- `/api/permutation/projects` - Admin project access
- `/admin/delete-registration` - Delete registrations
- `/admin/verify-email` - Manual email verification

## 🚀 Quick Start

### Access as Admin:
1. Go to https://atlasnexus.co.uk
2. Enter site password: `RedAMC`
3. Login with: spikemaz8@aol.com
4. Access admin panel: Click "Admin Panel" in header

### Test External User Flow:
1. Go to https://atlasnexus.co.uk
2. Enter site password: `RedAMC`
3. Login with: moore2marcus@gmail.com / password
4. Create a test project
5. Save and verify it persists

## 📱 Features Available Online:

✅ Full user registration system
✅ Email verification (manual override for admin)
✅ Project creation and management
✅ MongoDB cloud storage (no local files)
✅ Permutation engine with 116 fields
✅ Admin panel with user management
✅ Delete button for registrations
✅ Project loading into permutation engine
✅ Cross-device data persistence
✅ Secure two-gate access system

## 🔒 Security Features:
- Two-factor gate system
- Session-based authentication
- IP tracking and lockouts
- Admin-only endpoints
- Encrypted passwords
- MongoDB secure cloud storage

## 📈 Recent Updates:
- Added delete button for registrations
- Fixed project ID loading issue
- Removed local storage fallbacks
- MongoDB-only data persistence
- Enhanced admin panel features

---

**Note:** All features are fully functional online. No local server needed. Data persists across devices and sessions through MongoDB Atlas cloud storage.