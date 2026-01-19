# Vercel Blob Storage - Deployment Checklist

## ✅ Completed Steps

- [x] Updated `permutation_results_storage.py` with improved implementation
- [x] Created comprehensive documentation in `VERCEL_BLOB_IMPLEMENTATION_STATUS.md`
- [x] Committed changes to git
- [x] Pushed to GitHub (commit: a5db4bf)
- [x] Vercel deployment triggered automatically

---

## ⚠️ Critical Next Step: Set Environment Variable

**You MUST complete this step for the implementation to work:**

### 1. Get Your Vercel Blob Token

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: **atlasnexus.co.uk**
3. Click **Storage** tab
4. Click **Blob** section
5. Look for **"Read-Write Token"** or **"API Token"**
6. Click **"Copy"** or **"Create Token"**

### 2. Set Environment Variable

1. In Vercel Dashboard, go to **Settings** → **Environment Variables**
2. Click **"Add New"**
3. Enter:
   ```
   Name: BLOB_READ_WRITE_TOKEN
   Value: [paste your token here]
   ```
4. Select environments:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
5. Click **"Save"**

### 3. Redeploy (if needed)

If the current deployment completes before you set the token:
1. Go to **Deployments** tab
2. Click **"Redeploy"** on the latest deployment
3. Or push a small change to trigger new deployment

---

## 🧪 Testing Steps (After Token is Set)

### 1. Check Deployment Logs

```bash
# View logs in Vercel Dashboard or use CLI:
vercel logs --follow
```

**Look for:**
```
[BLOB] Permutation Results Storage initialized successfully
```

**If you see this instead, token is missing:**
```
[BLOB] Warning: BLOB_READ_WRITE_TOKEN environment variable not set
```

### 2. Test Permutation Execution

**Via Dashboard:**
1. Login to your production site
2. Go to a project
3. Run permutation engine
4. Check browser console and network tab

**Expected Console Output:**
```
[BLOB] Compressing permutation results for project proj_xxx...
[BLOB] Compressed X bytes → Y bytes
[BLOB] Compression ratio: 10.0:1
[BLOB] Uploading to Vercel Blob: permutation-results/proj_xxx_timestamp.json.gz
[BLOB] Upload successful!
[BLOB] URL: https://7cee5o6mxixmhwr2.public.blob.vercel-storage.com/...
[BLOB] Metadata saved to MongoDB
```

### 3. Test Permutation Loading

1. Try to load previously saved permutation results
2. Check console for:
```
[BLOB] Loading permutation results for project proj_xxx
[BLOB] Fetching from: https://...
[BLOB] Size: XXX bytes (compressed)
[BLOB] Decompressing...
[BLOB] Successfully loaded X permutations
```

### 4. Verify Storage in Vercel Dashboard

1. Go to Vercel Dashboard → Storage → Blob
2. Look for files in `permutation-results/` folder
3. Check file sizes (should be ~500MB for large datasets)

### 5. Verify MongoDB Metadata

**Using MongoDB Compass or Atlas Dashboard:**
1. Connect to your MongoDB cluster
2. Look for `permutation_metadata` collection
3. Check documents - should be ~5KB each
4. Verify structure:
   ```json
   {
     "project_id": "proj_xxx",
     "blob_url": "https://...",
     "permutation_count": 1000000,
     "compressed_size": 524288000,
     "compression_ratio": 10.0,
     "timestamp": "2026-01-19T..."
   }
   ```

---

## 🚨 Troubleshooting

### Issue: "Vercel Blob storage not configured"

**Symptom:** Console shows token warning
**Solution:**
1. Verify `BLOB_READ_WRITE_TOKEN` is set in Vercel
2. Check token has correct permissions (read-write)
3. Redeploy after setting token

### Issue: "Upload failed: 401"

**Symptom:** Upload fails with 401 status
**Solution:**
1. Token is invalid or expired
2. Generate new token in Vercel Dashboard
3. Update environment variable
4. Redeploy

### Issue: "Upload failed: 403"

**Symptom:** Upload fails with 403 status
**Solution:**
1. Token doesn't have write permissions
2. Ensure you copied the "Read-Write Token" not "Read-Only"
3. Generate new read-write token
4. Update environment variable

### Issue: "MongoDB not connected"

**Symptom:** Metadata save fails
**Solution:**
1. Check MongoDB connection string in environment
2. Verify MongoDB Atlas cluster is running
3. Check IP whitelist in MongoDB Atlas
4. Metadata will still be attempted on next save

### Issue: Blob uploaded but can't load

**Symptom:** Save works but load fails
**Solution:**
1. Check blob URL in MongoDB metadata
2. Verify blob is public or token has read access
3. Check Vercel Blob dashboard for file existence
4. Try re-uploading

---

## 📊 Monitoring

### Check Storage Usage

**Create admin endpoint in app.py (optional):**
```python
@app.route('/api/admin/storage-stats', methods=['GET'])
def get_storage_stats():
    # Add authentication check here
    from permutation_results_storage import permutation_storage
    stats = permutation_storage.get_storage_stats()
    return jsonify(stats)
```

**Stats returned:**
```json
{
    "project_count": 100,
    "total_compressed_bytes": 52428800000,
    "total_uncompressed_bytes": 524288000000,
    "total_permutations": 100000000,
    "total_compressed_gb": 48.8,
    "average_compression_ratio": 10.0
}
```

### Monitor Costs

**Vercel Blob Pricing:**
- First 500GB: Free
- Beyond 500GB: $0.15/GB/month
- Bandwidth: First 100GB free, then $0.30/GB

**Check usage:**
1. Vercel Dashboard → Usage
2. Look for Blob Storage metrics
3. Set up billing alerts if approaching limits

---

## 🎯 Success Criteria

- [ ] Environment variable `BLOB_READ_WRITE_TOKEN` set in Vercel
- [ ] Deployment successful (no errors)
- [ ] Logs show "Permutation Results Storage initialized successfully"
- [ ] Test permutation execution works
- [ ] Test permutation loading works
- [ ] Files appear in Vercel Blob Storage dashboard
- [ ] Metadata appears in MongoDB `permutation_metadata` collection
- [ ] Compression ratio ~10:1 achieved
- [ ] No 401/403 errors

---

## 📞 Support

**If you encounter issues:**

1. **Check logs:** Vercel Dashboard → Deployments → View Logs
2. **Check MongoDB:** Verify `permutation_metadata` collection exists
3. **Check Vercel Blob:** Verify storage is enabled and token is valid
4. **Review documentation:** See `VERCEL_BLOB_IMPLEMENTATION_STATUS.md`

**Common fixes:**
- Redeploy after setting environment variable
- Clear browser cache if frontend issues
- Verify MongoDB connection string
- Check IP whitelist in MongoDB Atlas

---

## 🔄 Rollback Plan (if needed)

If critical issues occur:

1. **Revert to previous commit:**
   ```bash
   git revert a5db4bf
   git push origin main
   ```

2. **Or checkout previous version:**
   ```bash
   git checkout 200e203 -- permutation_results_storage.py
   git commit -m "Rollback permutation storage"
   git push origin main
   ```

3. **Old implementation will still work** (uses different approach but functional)

---

## ✅ Current Status

**Deployment:** In Progress (triggered automatically by git push)
**Configuration:** Pending (BLOB_READ_WRITE_TOKEN needs to be set)
**Testing:** Pending (complete after token configuration)

**Next Action:** Set `BLOB_READ_WRITE_TOKEN` in Vercel Dashboard → Settings → Environment Variables

---

**Deployment initiated:** 2026-01-19
**Commit:** a5db4bf
**Branch:** main
**Status:** Waiting for environment variable configuration
