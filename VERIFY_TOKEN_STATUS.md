# Verify Vercel Blob Token Configuration

## 🔍 Quick Verification Steps

### Method 1: Check Vercel Dashboard (30 seconds)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select project: **atlasnexus.co.uk**
3. Click **Settings** (top navigation)
4. Click **Environment Variables** (left sidebar)
5. Look for: `BLOB_READ_WRITE_TOKEN`

**If you see it:**
- ✅ Token is configured
- Value should show: `vercel_blob_rw_7ceE5...` (partially hidden)
- Check it's set for: Production, Preview, Development

**If you DON'T see it:**
- ❌ Token not configured yet
- Follow setup steps in VERCEL_TOKEN_SETUP.md

---

### Method 2: Check Deployment Logs (1 minute)

1. Go to **Deployments** tab
2. Click on the **latest deployment**
3. Click **"View Function Logs"** or **"Runtime Logs"**
4. Search for: `[BLOB]`

**What to look for:**

✅ **Token is SET:**
```
[BLOB] Permutation Results Storage initialized successfully
```

❌ **Token NOT set:**
```
[BLOB] Warning: BLOB_READ_WRITE_TOKEN environment variable not set
[BLOB] Permutation storage will not work until token is configured
```

---

### Method 3: Test on Production Site (2 minutes)

**Only if you want to test live:**

1. Go to your production site
2. Open browser console (F12 → Console tab)
3. Try to create/save a project
4. Watch for any `[BLOB]` messages in server logs

**Note:** This only works if permutation features are used

---

## 📋 If Token is NOT Set - Quick Setup

### Copy this token:
```
vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS
```

### Steps:
1. Vercel Dashboard → Settings → Environment Variables
2. Click "Add New"
3. Name: `BLOB_READ_WRITE_TOKEN`
4. Value: Paste token above
5. Environments: ✅ Production, ✅ Preview, ✅ Development
6. Save

### After Setting:
1. Go to Deployments tab
2. Click latest deployment
3. Click **"Redeploy"** button (three dots menu → Redeploy)
4. Wait 1-2 minutes for deployment
5. Check logs again for success message

---

## ✅ Verification Checklist

- [ ] Logged into Vercel Dashboard
- [ ] Found Settings → Environment Variables
- [ ] Located `BLOB_READ_WRITE_TOKEN` entry
- [ ] Verified it's set for all 3 environments
- [ ] Checked deployment logs show "initialized successfully"
- [ ] (Optional) Tested creating a project on production site

---

## 🚨 Common Issues

### Issue: Token exists but logs still show warning

**Solution:** Redeploy after setting token
- Environment variables only take effect after deployment
- Go to Deployments → Latest → Redeploy

### Issue: Can't find Environment Variables in Settings

**Solution:** Check permissions
- You must be project owner or have admin access
- External collaborators may not see this section

### Issue: Token shows but still not working

**Solution:** Check token value
- Must be exactly: `vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS`
- No extra spaces before/after
- No quotes around the value

---

## 📊 What Happens When Token is Set

### Before Token (Current State):
```
❌ Vercel Blob: Disabled
❌ Permutation storage: Not available
❌ Large dataset uploads: Fails
```

### After Token (Target State):
```
✅ Vercel Blob: Active (500GB free tier)
✅ Permutation storage: Available
✅ Large dataset uploads: Working
✅ 10:1 compression ratio
✅ MongoDB metadata integration
```

---

## 🎯 Expected Behavior After Configuration

### 1. Server Logs Will Show:
```
[BLOB] Permutation Results Storage initialized successfully
```

### 2. Storage Stats Available:
```python
# Can call from admin panel:
from permutation_results_storage import permutation_storage
stats = permutation_storage.get_storage_stats()

# Returns:
{
    'project_count': 0,
    'total_compressed_bytes': 0,
    'total_compressed_gb': 0.0,
    'average_compression_ratio': 0
}
```

### 3. Permutation Features Work:
- Save results to Vercel Blob
- Load results from Vercel Blob
- Track storage usage
- Delete old results

---

## 💡 Pro Tips

### Check Token Status via CLI (if Vercel CLI installed):
```bash
vercel env ls
```

### Pull latest environment variables:
```bash
vercel env pull
```

### Test locally with .env file:
The `.env` file in your project root already has the token:
```bash
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS
```

Run locally:
```bash
python app.py
```

Check console for `[BLOB] Permutation Results Storage initialized successfully`

---

## 📞 Need Help?

If you're stuck:

1. **Screenshot the Environment Variables page** and check if `BLOB_READ_WRITE_TOKEN` is listed
2. **Check deployment logs** for the exact error message
3. **Try redeploying** - this fixes 90% of issues

---

## ✅ Final Confirmation

**Token is SET if ALL of these are true:**

- [ ] `BLOB_READ_WRITE_TOKEN` appears in Environment Variables
- [ ] Set for Production, Preview, and Development
- [ ] Latest deployment logs show "initialized successfully"
- [ ] No warning messages about token not being set

**If all checked:** ✅ You're good to go!
**If any unchecked:** ⚠️ Follow setup steps above

---

**Last updated:** 2026-01-19
**Token provided:** `vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS`
**Documentation:** See VERCEL_TOKEN_SETUP.md for detailed instructions
