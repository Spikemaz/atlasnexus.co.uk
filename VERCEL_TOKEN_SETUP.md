# Vercel Blob Token Setup Instructions

## 🔑 Your Vercel Blob Token

```
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS
```

---

## 📋 Quick Setup (2 Minutes)

### Method 1: Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: **atlasnexus.co.uk**
3. Click **Settings** (top menu)
4. Click **Environment Variables** (left sidebar)
5. Click **"Add New"** button
6. Enter:
   ```
   Name: BLOB_READ_WRITE_TOKEN
   Value: vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS
   ```
7. Select environments:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
8. Click **"Save"**
9. **Redeploy** the latest deployment

---

### Method 2: Vercel CLI

If you have Vercel CLI installed:

```bash
cd "c:\Users\marcu\Desktop\Marcus Folder\Project1"

# Set for production
vercel env add BLOB_READ_WRITE_TOKEN production
# When prompted, paste: vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS

# Set for preview
vercel env add BLOB_READ_WRITE_TOKEN preview
# When prompted, paste: vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS

# Set for development
vercel env add BLOB_READ_WRITE_TOKEN development
# When prompted, paste: vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS

# Trigger redeploy
vercel --prod
```

---

## ✅ Verification Steps

### 1. Check Environment Variable is Set

In Vercel Dashboard:
- Go to Settings → Environment Variables
- Look for `BLOB_READ_WRITE_TOKEN`
- Should show: `vercel_blob_rw_7ceE5O...` (partially hidden)

### 2. Check Deployment Logs

After redeploying:
1. Go to **Deployments** tab
2. Click on latest deployment
3. Click **"View Function Logs"**
4. Look for:
   ```
   [BLOB] Permutation Results Storage initialized successfully
   ```

**If you see this instead:**
```
[BLOB] Warning: BLOB_READ_WRITE_TOKEN environment variable not set
```
→ Token not configured correctly, redeploy after setting

### 3. Test Permutation Storage

1. Login to production site
2. Go to any project
3. Run permutation engine
4. Check browser console for:
   ```
   [BLOB] Compressing permutation results for project proj_xxx...
   [BLOB] Compressed X bytes → Y bytes
   [BLOB] Compression ratio: 10.0:1
   [BLOB] Uploading to Vercel Blob: permutation-results/proj_xxx_timestamp.json.gz
   [BLOB] Upload successful!
   [BLOB] URL: https://7cee5o6mxixmhwr2.public.blob.vercel-storage.com/...
   [BLOB] Metadata saved to MongoDB
   ```

---

## 🔍 Token Details

- **Store ID:** `7ceE5O6mxIxmHWR2`
- **Region:** London
- **Type:** Read-Write Token
- **Format:** `vercel_blob_rw_{STORE_ID}_{TOKEN_HASH}`

---

## 🚨 Troubleshooting

### Issue: Token not working after setting

**Solution:**
1. Verify token is exactly: `vercel_blob_rw_7ceE5O6mxIxmHWR2_hBoPeA8jmV9AzKhMzqWkEj4D28DNuS`
2. No extra spaces or quotes
3. Set for all three environments
4. **Must redeploy** after setting environment variable

### Issue: "Upload failed: 401"

**Solution:**
- Token is invalid or expired
- Regenerate token in Vercel Dashboard → Storage → Blob
- Update environment variable
- Redeploy

### Issue: "Upload failed: 403"

**Solution:**
- Token doesn't have write permissions
- Ensure you copied the "Read-Write Token" not "Read-Only"
- Regenerate if needed

---

## 📊 What This Enables

Once configured, you'll be able to:

✅ Store permutation results (up to 500GB free tier)
✅ Compress data with 10:1 ratio (5GB → 500MB)
✅ Track storage usage across all projects
✅ Delete old permutation results
✅ Load permutation results instantly

---

## 💰 Cost Breakdown

**Free Tier:**
- 500GB storage (1000 projects × 500MB each)
- 100GB bandwidth/month
- **Cost:** $0

**Paid Tier (if exceeded):**
- Storage: $0.15/GB/month
- Bandwidth: $0.30/GB
- Example: 1TB = $105/month (vs MongoDB $1,630/month)

---

## 🔒 Security Notes

- **Token Type:** Read-Write (can upload and delete)
- **Access:** Private (requires token to access)
- **Storage:** Token stored in Vercel environment variables (encrypted)
- **Best Practice:** Never commit token to git (already in .gitignore)

---

## 📝 Next Steps

1. **Set environment variable** using Method 1 or 2 above
2. **Redeploy** to apply changes
3. **Test** with a small permutation run
4. **Verify** in Vercel Blob Storage dashboard
5. **Monitor** storage usage over time

---

## ✅ Checklist

- [ ] Token copied exactly (no spaces/quotes)
- [ ] Environment variable set in Vercel Dashboard
- [ ] Set for Production, Preview, and Development
- [ ] Redeployed after setting variable
- [ ] Checked logs for "initialized successfully" message
- [ ] Tested permutation upload
- [ ] Verified file appears in Vercel Blob Storage
- [ ] Confirmed metadata saved to MongoDB

---

**Once complete, permutation storage will be fully operational! 🚀**

**Estimated setup time:** 2-5 minutes
**Status:** Ready to configure
