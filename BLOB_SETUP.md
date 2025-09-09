# Vercel Blob Storage Setup

## Your Store Details ✅
- **Store ID:** `store_7ceE5O6mxIxmHWR2`
- **Region:** London, United Kingdom (LHR1)
- **Public URL:** `https://7cee5o6mxixmhwr2.public.blob.vercel-storage.com`
- **Storage:** 100 GB (Pro Plan)

## Setup Instructions

### 1. Get Your Token
1. Go to https://vercel.com/dashboard/stores/blob/store_7ceE5O6mxIxmHWR2
2. Click on "Manage" or "Settings"
3. Find and copy the `Read/Write Token`

### 2. Add to Vercel Environment Variables
1. Go to your project: https://vercel.com/marcus-moores-projects/atlasnexus-securitization/settings/environment-variables
2. Add new variable:
   - **Key:** `BLOB_READ_WRITE_TOKEN`
   - **Value:** [paste your token]
   - **Environment:** Production, Preview, Development
3. Click "Save"

### 3. Redeploy
After adding the environment variable, redeploy your project:
- Either push a commit to trigger automatic deployment
- Or manually redeploy from Vercel dashboard

## What This Enables

### Permutation Results Storage
- Store millions of permutation results
- Automatic compression (60-80% size reduction)
- Global CDN access from London region
- No size limits up to 5GB per file
- 100GB total storage

### Storage Examples
- 1,000 permutations = ~0.5 MB
- 10,000 permutations = ~5 MB
- 100,000 permutations = ~50 MB
- 1,000,000 permutations = ~500 MB
- 10,000,000 permutations = ~5 GB

### How It Works
1. Admin runs permutation engine
2. Results compress with GZIP
3. Store in Vercel Blob (London)
4. Get unique URL for results
5. Access worldwide via CDN

## Testing

Once token is added:
1. Login as admin at https://atlasnexus.co.uk
2. Go to Dashboard → Permutation Engine
3. Load project "Securitization Test 20250909_1628"
4. Click "Run Permutation"
5. Results will store in blob
6. Check console for storage confirmation

## API Endpoints

### Execute Permutation
```
POST /api/permutation/execute
{
  "projectId": "project_id",
  "parameters": {...}
}
```

### Get Results
```
GET /api/permutation/results/{project_id}
```

## Troubleshooting

If blob storage doesn't work:
1. Check token is set in Vercel environment
2. Verify deployment includes the token
3. Check browser console for errors
4. Results will fallback to MongoDB if blob fails

## Benefits of Blob Storage

✅ **100 GB storage** with Pro plan
✅ **Global CDN** from London
✅ **5 GB max file** size
✅ **Fast worldwide** access
✅ **Automatic scaling**
✅ **No database limits**

Your blob storage is ready - just add the token!