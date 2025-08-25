# AtlasNexus Pre-Flight Checklist
## Manual Testing Guide

### Quick Version Check
Visit: https://atlasnexus.co.uk/version
- Should show version 2.1.0
- All features should be marked as True

### 1. Gate1 Testing (Site Authentication)
URL: https://atlasnexus.co.uk/

**Test A: Timer Display**
- Enter wrong password 3 times (not "AtlasNexus2024!")
- Verify timer shows "30:00" (not 31:00)
- Timer should count down from 30 minutes

**Test B: Override Password**
- While locked out, enter "Ronabambi"
- Should reset attempts to 3
- Page should refresh with no lockout

### 2. Gate2 Testing (User Login)
URL: https://atlasnexus.co.uk/secure-login

**Test A: Market Ticker Visibility**
- After passing Gate1, check ticker at top
- Should see scrolling market data
- Background should be dark gradient
- Text should be white/colored

**Test B: Ticker Drag**
- Click and drag ticker left/right
- Should move smoothly without spinning
- Should resume auto-scroll after 2 seconds

### 3. Admin Login & Dashboard
**Credentials:**
- Email: spikemaz8@aol.com
- Password: SpikeMaz

**Dashboard Checks:**
- Market ticker visible and scrolling
- Date showing current date
- No "Admin" button in header
- Only "Control Panel" and "Securitization" buttons

### 4. Admin Panel Testing
URL: https://atlasnexus.co.uk/admin-panel

**All Users Tab:**
- Should show admin account
- Online/Offline sections
- Edit button works
- Delete button works
- Freeze/Unfreeze toggle works
- Account type dropdown (admin/internal/external)

**Registrations Tab:**
- Approve/Reject buttons present
- Can set password when approving

**IP Management Tab:**
- Shows IP tracking data
- Ban/Unban buttons work
- Shows login attempts

**Analytics Tab:**
- Shows system statistics
- User growth chart
- Activity metrics

### 5. Security Features
**Test IP Tracking:**
- All page visits should be tracked
- Check IP Management tab for your IP

**Test Login Lockout:**
- Wrong password 5 times triggers lockout
- IP gets temporarily banned

### 6. Data Verification
**Users:**
- Only admin account exists
- spikemaz8@aol.com with password SpikeMaz

**Clean State:**
- No pending registrations
- No locked IPs (unless you tested lockout)
- Clean login attempt logs

## Final Deployment Status
- GitHub: Latest code pushed
- Vercel: Auto-deployed from GitHub
- Version: 2.1.0
- All 17 features: Implemented

## Support Information
- Site Password: AtlasNexus2024!
- Override Code: Ronabambi
- Admin Email: spikemaz8@aol.com
- Admin Password: SpikeMaz

## If Issues Found
1. Check browser console for errors
2. Try clearing browser cache
3. Check /version endpoint for deployment status
4. Verify Vercel deployment completed

All systems should be fully operational. Ready for manual verification!