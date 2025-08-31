# AtlasNexus Project Structure

## 🎯 Clean & Optimized Project Layout

### 📁 Root Files (Essential Only)
```
Project1/
├── app.py                    # Main Flask application - DO NOT DELETE
├── requirements.txt          # Python dependencies for Vercel
├── vercel.json              # Vercel deployment configuration
├── local.bat                # Run locally (double-click)
├── live.bat                 # Open live site
├── README.txt               # Basic instructions
├── email_config.py          # Email configuration (Gmail)
├── market_news_service.py   # Market news for dashboard
├── real_news_service.py     # Real news feed service
└── securitization_engine.py # Project-specific features
```

### 📁 Folders
```
├── data/                    # Database files (JSON)
│   ├── users.json          # User accounts
│   ├── registrations.json  # Pending registrations
│   ├── admin_actions.json  # Admin activity log
│   ├── ip_lockouts.json    # Security lockouts
│   └── ip_tracking.json    # IP monitoring
│
├── templates/              # HTML Templates
│   ├── Gate1.html         # First security gate
│   ├── Gate2.html         # Login/Register page
│   ├── dashboard.html     # Main dashboard
│   ├── admin_panel.html   # Admin control panel
│   ├── securitisation_engine.html  # Project features
│   ├── permutation_engine.html     # Advanced engine
│   ├── awaiting_verification.html  # Email verification
│   ├── registration-submitted.html # After registration
│   ├── 404.html           # Error page
│   ├── terms.html         # Terms of service
│   ├── privacy.html       # Privacy policy
│   ├── compliance.html    # Compliance info
│   ├── data-protection.html # Data protection
│   ├── security.html      # Security info
│   └── contact.html       # Contact page
│
├── static/                 # Static assets
│   ├── favicon.ico        # Site icon
│   ├── favicon.svg        # Site icon (vector)
│   ├── js/                # JavaScript files (if any)
│   └── templates/         # Excel templates for users
│       ├── AtlasNexus_Individual_Project_Template.xlsx
│       ├── AtlasNexus_Pipeline_Template.xlsx
│       ├── initial_submission_template.html
│       └── final_submission_template.html
│
├── My Core Files/          # External client information
│   └── External Client information/  # Project documents
│
└── venv/                   # Python virtual environment
```

## ✅ What Was Removed (35 files)
- All test files (test_*.py)
- All verification scripts (verify_*.py)
- All cleanup scripts (cleanup_*.py, final_*.py)
- Test HTML files (test_*.html)
- Documentation files (*.md - except this one)
- Temporary files (cookies.txt, ip_attempts_log.json)
- JavaScript fragments (fix_templates.js, permutation_parameters.js)

## 🔒 Functionality Preserved
- ✅ Gate1 Security (30-min timer, passwords: SpikeMaz, RedAMC)
- ✅ Gate2 Login/Registration
- ✅ Email verification system
- ✅ Admin panel with full user management
- ✅ Dashboard with market data
- ✅ Project-specific sections
- ✅ All navigation links
- ✅ Database persistence
- ✅ Live deployment

## 🚀 How to Run
- **Local**: Double-click `local.bat` or run `python app.py`
- **Live**: Visit https://atlasnexus.co.uk

## 👤 Admin Access
- Email: spikemaz8@aol.com
- Password: SpikeMaz

## 🔑 Gate1 Passwords
- SpikeMaz
- RedAMC

## 📝 Notes
- Only ONE Flask server running on port 5000
- Project folder is now clean and manageable
- All core functionality intact
- Ready for continued development on project-specific features