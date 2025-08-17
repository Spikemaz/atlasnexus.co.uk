# 🔄 Keeping Local and Live in Sync

## The Setup

We have two versions of the app:
1. **app.py** - Local development (TESTING_MODE = True)
2. **app_live.py** - Production deployment (TESTING_MODE = False)

Both share the SAME templates folder, so visual changes are automatic!

## How to Keep Them Synchronized

### Automatic Sync (Templates)
✅ **Templates are already shared!** 
- Any change to templates/* affects both versions
- Dashboard, login pages, etc. will look identical

### What's Different
- **app.py**: No password requirements (TESTING_MODE = True)
- **app_live.py**: Full security (passwords required)

### When Adding New Features

1. **Develop locally** using app.py
2. **Test** without passwords
3. **Copy routes** to app_live.py when ready
4. **Deploy** with `git push`

### Quick Commands

```bash
# Local development
python app.py

# Test live version locally
python app_live.py

# Deploy to live
git add -A
git commit -m "Your message"
git push origin main
```

### Important Files

| File | Purpose | Shared? |
|------|---------|---------|
| templates/*.html | All UI templates | ✅ YES |
| app.py | Local development | ❌ NO |
| app_live.py | Production | ❌ NO |
| static/* | CSS/JS/Images | ✅ YES |

### Security Note
app_live.py always has:
- TESTING_MODE = False
- Password requirements
- Gate 1: SpikeMaz
- Gate 2: spikemaz8@aol.com / SpikeMaz

This keeps the live site secure while you develop!