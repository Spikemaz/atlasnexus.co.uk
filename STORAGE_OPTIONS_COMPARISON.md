# Storage Options for Permutation Data - Complete Comparison

## 📊 The Problem

**Permutation Dataset Size:**
- 1,000,000 scenarios × 50 fields × 100 bytes = **5GB uncompressed**
- Compressed (gzip level 9): **500MB per project**
- 500 projects: **250GB total**

**MongoDB Free Tier:**
- 512MB total (all collections)
- GridFS works but consumes entire quota with one result
- Not sustainable

---

## 🏆 All Viable Solutions (Ranked)

### 1. ✅ **Vercel Blob Storage** (BEST - Already in Your Stack)

**Free Tier:**
- 500GB storage
- 100GB bandwidth/month
- Zero setup (already using it)

**Pricing Beyond Free:**
- Storage: $0.15/GB/month
- Bandwidth: $0.30/GB

**Pros:**
- ✅ **Huge free tier** (500GB covers 1000 projects)
- ✅ **Already integrated** (blob_storage.py exists)
- ✅ **Serverless-native** (works with Vercel hosting)
- ✅ **CDN delivery** (fast global access)
- ✅ **Simple API** (put, get, delete)
- ✅ **Zero infrastructure management**

**Cons:**
- ❌ Vercel lock-in (but easy to migrate if needed)
- ❌ No query capabilities (must load entire file)

**Cost at Scale (2000 projects = 1TB):**
```
Storage: (1000GB - 500GB free) × $0.15 = $75/month
Bandwidth: (200GB - 100GB free) × $0.30 = $30/month
Total: $105/month
```

**Recommendation:** ⭐⭐⭐⭐⭐ **Use This!**

---

### 2. ✅ **Cloudflare R2** (CHEAPEST Paid Option)

**Free Tier:**
- 10GB storage
- Unlimited egress (bandwidth FREE!)

**Pricing:**
- Storage: $0.015/GB/month
- Egress: **$0** (completely free!)
- Class A operations: $4.50/million
- Class B operations: $0.36/million

**Pros:**
- ✅ **Zero egress fees** (huge win if bandwidth is high)
- ✅ **S3-compatible API** (easy migration path)
- ✅ **Cheapest storage** ($0.015/GB vs Vercel $0.15/GB)
- ✅ **No vendor lock-in** (standard S3 API)

**Cons:**
- ❌ Smaller free tier (10GB vs Vercel 500GB)
- ❌ Requires separate signup/configuration
- ❌ Not integrated with Vercel (need SDK)

**Cost at Scale (1TB):**
```
Storage: 1000GB × $0.015 = $15/month
Egress: $0 (free!)
Operations: ~$5/month (estimate)
Total: $20/month
```

**Recommendation:** ⭐⭐⭐⭐ Great if you outgrow Vercel's free tier

---

### 3. ⚠️ **AWS S3** (Industry Standard)

**Free Tier (12 months):**
- 5GB storage
- 20,000 GET requests
- 2,000 PUT requests

**Pricing After Free Tier:**
- Storage: $0.023/GB/month (Standard)
- Egress: $0.09/GB (first 10TB/month)
- PUT requests: $0.005/1000
- GET requests: $0.0004/1000

**Pros:**
- ✅ **Industry standard** (S3 API everywhere)
- ✅ **Mature ecosystem** (lots of tools)
- ✅ **Infinite scalability**
- ✅ **Multiple storage classes** (can use Glacier for archives)

**Cons:**
- ❌ **Complex pricing** (many line items)
- ❌ **Egress fees** ($0.09/GB adds up)
- ❌ **Requires AWS account/credit card**
- ❌ **More configuration** than Vercel Blob

**Cost at Scale (1TB):**
```
Storage: 1000GB × $0.023 = $23/month
Egress: 100GB × $0.09 = $9/month
Requests: ~$3/month
Total: $35/month
```

**Recommendation:** ⭐⭐⭐ Good if you're already on AWS

---

### 4. ⚠️ **DigitalOcean Spaces** (Simple S3 Alternative)

**Pricing:**
- $5/month for 250GB storage + 1TB bandwidth
- Overage: $0.02/GB storage, $0.01/GB bandwidth

**Pros:**
- ✅ **Simple flat pricing** ($5/month predictable)
- ✅ **S3-compatible**
- ✅ **Generous bandwidth** (1TB included)
- ✅ **Easy to understand**

**Cons:**
- ❌ **No free tier**
- ❌ **Fixed $5 minimum** even for small usage
- ❌ **Limited to 250GB** at base price

**Cost at Scale (1TB):**
```
Base: $5 (250GB + 1TB bandwidth)
Overage: 750GB × $0.02 = $15/month
Total: $20/month
```

**Recommendation:** ⭐⭐⭐ Good for predictable pricing

---

### 5. ⚠️ **MongoDB Atlas** (Current Approach - GridFS)

**Free Tier:**
- 512MB total storage
- Shared cluster

**Pricing:**
- M10 (10GB): $57/month
- M20 (20GB): $140/month
- M30 (40GB): $315/month

**Pros:**
- ✅ **Already using it** (zero setup)
- ✅ **Query capabilities** (can filter permutations)
- ✅ **Integrated with your backend**

**Cons:**
- ❌ **Tiny free tier** (512MB = one project)
- ❌ **Extremely expensive** ($57/10GB vs R2 $0.15/10GB)
- ❌ **Not designed for blob storage**
- ❌ **16MB document limit** (must use GridFS)

**Cost at Scale (1TB):**
```
Need 100× M10 clusters = $5,700/month
Or 1× M400 (1.5TB): $1,630/month
Total: $1,630 - $5,700/month (!!)
```

**Recommendation:** ⭐ **Avoid for blob storage** (use MongoDB only for metadata)

---

### 6. ❌ **PostgreSQL + Binary Columns** (Not Recommended)

**Providers:**
- Supabase: 500MB free
- Neon: 512MB free
- Railway: $5/month (10GB)

**Pros:**
- ✅ **SQL queries** (can filter permutations)
- ✅ **Relational data** (joins possible)

**Cons:**
- ❌ **Not designed for large blobs**
- ❌ **Performance degrades** with large binary data
- ❌ **Expensive** ($5-20/month for 10-50GB)
- ❌ **VACUUM overhead** (bloat issues)

**Recommendation:** ⭐ Avoid (use Postgres for structured data only)

---

## 📊 Side-by-Side Comparison

| Solution | Free Tier | Cost/GB | Egress Fee | Setup Complexity | Speed | Recommendation |
|----------|-----------|---------|------------|------------------|-------|----------------|
| **Vercel Blob** | **500GB** | $0.15 | $0.30/GB | ⭐⭐⭐⭐⭐ (zero) | ⭐⭐⭐⭐⭐ (CDN) | ⭐⭐⭐⭐⭐ **BEST** |
| **Cloudflare R2** | 10GB | **$0.015** | **$0** | ⭐⭐⭐⭐ (moderate) | ⭐⭐⭐⭐ (fast) | ⭐⭐⭐⭐ Great backup |
| **AWS S3** | 5GB | $0.023 | $0.09/GB | ⭐⭐⭐ (complex) | ⭐⭐⭐⭐ (fast) | ⭐⭐⭐ If on AWS already |
| **DigitalOcean** | None | $0.02 | $0.01/GB | ⭐⭐⭐⭐ (simple) | ⭐⭐⭐⭐ (fast) | ⭐⭐⭐ Predictable cost |
| **MongoDB Atlas** | 512MB | $5.70 | Included | ⭐⭐⭐⭐⭐ (already using) | ⭐⭐⭐ (query lag) | ⭐ **Avoid** |
| **PostgreSQL** | 500MB | $0.50 | Included | ⭐⭐⭐ (moderate) | ⭐⭐ (slow for blobs) | ⭐ Avoid |

---

## 🎯 Recommended Architecture

### **Hybrid Approach (Best of Both Worlds)**

**1. MongoDB Atlas (Free Tier) - Metadata Only**
```javascript
// Store only small metadata (5KB per project)
{
  "project_id": "proj_123",
  "blob_url": "https://blob.vercel-storage.com/...",
  "permutation_count": 1000000,
  "compressed_size": 524288000,
  "summary": {
    "avg_irr": 14.8,
    "best_scenario_id": "perm_425801"
  },
  "timestamp": "2026-01-19T14:30:00"
}

// Total: 5KB × 500 projects = 2.5MB ✅
// Leaves 509.5MB free for users, projects, etc.
```

**2. Vercel Blob - Large Permutation Files**
```
permutation-results/
├── proj_123_1737297600.json.gz (500MB)
├── proj_456_1737298200.json.gz (500MB)
└── proj_789_1737299400.json.gz (500MB)

Total: 250GB (within 500GB free tier) ✅
```

**3. Query Pattern:**
```python
# Fast dashboard view (metadata only from MongoDB)
def get_project_summary(project_id):
    metadata = db.permutation_metadata.find_one({'project_id': project_id})
    return {
        'permutation_count': metadata['permutation_count'],
        'avg_irr': metadata['summary']['avg_irr'],
        'execution_time': metadata['summary']['execution_time']
    }
    # Response time: 50ms ✅

# Full results (only when needed, from Vercel Blob)
def get_full_results(project_id):
    metadata = db.permutation_metadata.find_one({'project_id': project_id})
    blob_url = metadata['blob_url']

    # Download from Vercel Blob
    compressed_data = requests.get(blob_url).content
    decompressed = gzip.decompress(compressed_data)
    results = json.loads(decompressed)

    return results['permutations']  # 1M scenarios
    # Response time: 2-3 seconds (acceptable for detailed view)
```

---

## 💡 Optimization Strategies

### 1. **Lazy Loading (Pagination)**
```python
# Don't load all 1M permutations at once
# Load 1000 at a time as user scrolls
def get_permutation_page(project_id, page=1, page_size=1000):
    results = load_from_blob(project_id)
    start = (page - 1) * page_size
    end = start + page_size
    return results['permutations'][start:end]
```

### 2. **Pre-computed Filters**
```python
# Store pre-filtered subsets in metadata
metadata = {
    'summary': {
        'tier1_count': 125000,
        'tier1_avg_irr': 16.2,
        'tier1_scenarios': [1, 42, 103, ...]  # IDs only
    }
}

# Load only Tier 1 scenarios when filter applied
def get_tier1_scenarios(project_id):
    metadata = db.permutation_metadata.find_one({'project_id': project_id})
    tier1_ids = metadata['summary']['tier1_scenarios']

    # Load full results
    results = load_from_blob(project_id)

    # Filter to Tier 1 only
    tier1_permutations = [
        p for p in results['permutations']
        if p['id'] in tier1_ids
    ]
    return tier1_permutations  # Only 125,000 instead of 1M
```

### 3. **Compressed Transfer**
```python
# Send compressed data to browser, decompress client-side
@app.route('/api/permutation/results/<project_id>')
def get_permutation_results_compressed(project_id):
    metadata = db.permutation_metadata.find_one({'project_id': project_id})
    blob_url = metadata['blob_url']

    # Return blob URL for client-side download
    return jsonify({
        'blob_url': blob_url,
        'compressed_size': metadata['compressed_size'],
        'permutation_count': metadata['permutation_count']
    })

// Frontend: Download and decompress in browser
async function loadPermutations(projectId) {
    const response = await fetch(`/api/permutation/results/${projectId}`);
    const { blob_url } = await response.json();

    // Download compressed data
    const compressedData = await fetch(blob_url).then(r => r.arrayBuffer());

    // Decompress in browser (using pako.js)
    const decompressed = pako.ungzip(new Uint8Array(compressedData), { to: 'string' });
    const results = JSON.parse(decompressed);

    return results.permutations;
}
```

---

## 🚀 Migration Path

### Phase 1: Immediate (Use Vercel Blob)
1. Create `permutation_blob_storage.py`
2. Update `app.py` endpoints
3. Deploy to Vercel
4. **Result:** Free tier supports 1000 projects ✅

### Phase 2: If You Outgrow Free Tier (> 500GB)
1. Evaluate usage patterns
2. If read-heavy: Migrate to Cloudflare R2 (free egress)
3. If write-heavy: Stay on Vercel (simpler)
4. **Cost:** $20-100/month for 1TB

### Phase 3: Enterprise Scale (> 10TB)
1. Consider AWS S3 + CloudFront CDN
2. Or use Cloudflare R2 (still cheapest)
3. Implement tiered storage (hot/cold data)
4. **Cost:** $150-500/month for 10TB

---

## ✅ Final Recommendation

### **Use Vercel Blob Storage**

**Why:**
1. ✅ **Massive free tier** (500GB = 1000 projects)
2. ✅ **Zero setup** (already in your stack)
3. ✅ **Fast** (CDN-delivered)
4. ✅ **Affordable scaling** ($105/month for 1TB vs MongoDB $1,630)
5. ✅ **Simple API** (put, get, delete - no complex configuration)

**Backup Plan:**
- If you exceed 500GB → Migrate to Cloudflare R2 ($15/month for 1TB)
- S3-compatible API makes migration easy (one day of work)

**Implementation:**
1. See [PERMUTATION_BLOB_STORAGE.md](PERMUTATION_BLOB_STORAGE.md) for complete code
2. Copy `permutation_blob_storage.py` to your project
3. Update `app.py` endpoints
4. Deploy and enjoy free storage! 🚀

---

## 📊 Cost Projection (5 Years)

### Scenario: Growing from 100 → 5000 projects

| Year | Projects | Storage | Vercel Blob | Cloudflare R2 | MongoDB Atlas |
|------|----------|---------|-------------|---------------|---------------|
| 1 | 100 | 50GB | **$0** (free tier) | **$0.75/mo** | $285/mo |
| 2 | 500 | 250GB | **$0** (free tier) | **$3.75/mo** | $1,425/mo |
| 3 | 1000 | 500GB | **$0** (free tier) | **$7.50/mo** | $2,850/mo |
| 4 | 2500 | 1.25TB | **$112/mo** | **$18.75/mo** | $7,125/mo |
| 5 | 5000 | 2.5TB | **$300/mo** | **$37.50/mo** | $14,250/mo |

**Total 5-Year Cost:**
- **Vercel Blob:** $4,944 (years 4-5 only)
- **Cloudflare R2:** $816 (all years)
- **MongoDB Atlas:** $309,180 (!!!)

**Winner:** Start with Vercel (free for 3 years), switch to R2 if needed

---

## 🎓 Key Takeaways

1. **MongoDB is NOT for blob storage** - 385× more expensive than alternatives
2. **Vercel Blob is perfect for your use case** - free, fast, already integrated
3. **Cloudflare R2 is the backup plan** - cheapest paid option, free egress
4. **Hybrid architecture is optimal** - metadata in MongoDB, blobs in Vercel
5. **You have 3 years of free storage** - plenty of time to grow before paying

**Start coding with Vercel Blob today! 🚀**
