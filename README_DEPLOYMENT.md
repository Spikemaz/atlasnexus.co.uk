# AtlasNexus Deployment Guide

## Local Development
- Run `python app.py` for testing (no passwords required)
- Access at http://localhost:5000

## Live Production (atlasnexus.co.uk)
- Uses `app_live.py` with full security
- Gate 1 Password: `SpikeMaz`
- Gate 2 Login: `Spikemaz8@aol.com` / `SpikeMaz`

## Files Structure
- `app.py` - Local testing version (TESTING_MODE = True)
- `app_live.py` - Production version with security
- `app_minimal.py` - Backup minimal version

## Deployment to Vercel
1. Push to GitHub
2. Connect Vercel to your GitHub repo
3. Vercel will use `vercel.json` to deploy `app_live.py`
4. Set custom domain to atlasnexus.co.uk in Vercel settings

## Security Features (Production Only)
- 5 failed attempts = 45-minute IP block
- All failed attempts logged to security_log.txt
- Session timeout after 45 minutes of inactivity