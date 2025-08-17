# AtlasNexus Deployment Verification Checklist

## Local Server (http://localhost:5000)
Status: ✅ Running

### Security Gate 1 - Site Authentication
- [ ] Coat of arms logo visible
- [ ] Password field accepts: **RedAMC** or **PartnerAccess**
- [ ] After 3 failed attempts: Warning popup with support/last attempt options
- [ ] After 4th failed attempt: 45-minute countdown page
- [ ] Secret menu: Click bottom-left corner 4 times, password: **Ronabambi**
- [ ] After 5th failed attempt: Black screen with red text

### Security Gate 2 - User Login/Registration
- [ ] Redirects here after successful Gate 1
- [ ] Login form for existing users
- [ ] Registration form for new users
- [ ] Admin login: **marcus@atlasnexus.co.uk** / **MarcusAdmin2024**

### Dashboard
- [ ] Shows after successful login
- [ ] Admin link visible for Marcus account

### Admin Panel
- [ ] Accessible only to Marcus after login
- [ ] Shows user management interface

## Live Site (https://www.atlasnexus.co.uk)
Status: To be verified

### Deployment Steps
1. **Commit changes to Git:**
   ```bash
   git add -A
   git commit -m "Fix security gates and synchronize local/live versions"
   git push origin main
   ```

2. **Vercel will auto-deploy** (connected to GitHub)
   - Monitor at: https://vercel.com/dashboard
   - Or manually deploy: `vercel --prod`

3. **Test live site** using same checklist above

## Current Configuration
- **GitHub Repo:** https://github.com/Spikemaz/atlasnexus.co.uk.git
- **Vercel Project:** atlasnexus-securitization
- **Main File:** app_vercel.py
- **Security Passwords:**
  - Internal: RedAMC
  - External: PartnerAccess
  - Secret Unlock: Ronabambi
- **Admin Access:**
  - Email: marcus@atlasnexus.co.uk
  - Password: MarcusAdmin2024

## Files Status
- ✅ app_vercel.py - Fixed and ready
- ✅ templates/site_auth.html - Gate 1 implemented
- ✅ templates/secure_login.html - Gate 2 implemented
- ✅ templates/dashboard.html - Present
- ✅ templates/admin_simple.html - Present
- ✅ vercel.json - Configured
- ✅ requirements.txt - Dependencies listed

## Next Steps
1. Open browser to **http://localhost:5000** to test local version
2. Open browser to **https://www.atlasnexus.co.uk** to check live version
3. Compare both versions to ensure they match
4. If changes needed, edit locally and push to GitHub for auto-deployment