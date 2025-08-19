# Vercel Environment Variables Setup

## IMPORTANT: Set these in Vercel Dashboard

Go to: https://vercel.com/[your-username]/[your-project]/settings/environment-variables

Add these environment variables:

1. **SENDER_EMAIL**
   - Value: `atlasnexushelp@gmail.com`
   - Description: Gmail account for sending emails

2. **SENDER_PASSWORD**  
   - Value: `rrpwfkigrubimqnf`
   - Description: Gmail App Password (NOT regular password)
   - ⚠️ Mark as: SENSITIVE

3. **ADMIN_EMAIL**
   - Value: `spikemaz8@aol.com`
   - Description: Where admin notifications are sent

## How to Add in Vercel:

1. Go to your Vercel dashboard
2. Click on your project (atlasnexus)
3. Go to Settings → Environment Variables
4. Add each variable above
5. Make sure to mark SENDER_PASSWORD as sensitive
6. Click Save

## Notes:
- These variables are used when email_config.py doesn't exist (production)
- The app automatically falls back to environment variables on Vercel
- Never commit email_config.py to git - it's for local development only