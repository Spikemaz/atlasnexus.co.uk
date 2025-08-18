# AtlasNexus Synchronization Strategy

## Two-Version Architecture (RECOMMENDED)

### Why Two Versions?
1. **Zero Downtime** - Users never experience broken features
2. **Safe Testing** - Test locally without affecting live users
3. **Rollback Safety** - Can quickly revert if issues arise
4. **Professional Development** - Industry standard practice

### Current Setup:
- **Local (Development)**: `app.py` → http://localhost:5000
- **Live (Production)**: `app_live.py` → https://atlasnexus.co.uk

### Synchronization Process:

```
LOCAL CHANGES → AUTO-SYNC → LIVE VERSION → GIT PUSH → VERCEL DEPLOY
     app.py    →  (2 sec)  →  app_live.py  →   git   →  atlasnexus.co.uk
```

### Files That Need Syncing:
1. `app.py` → `app_live.py` (with TESTING_MODE changed)
2. `templates/*.html` → Same templates (shared)
3. `static/css/*.css` → Same styles (shared)
4. `static/js/*.js` → Same scripts (shared)

### Key Differences:
| Feature | Local | Live |
|---------|-------|------|
| TESTING_MODE | True | False |
| Debug Mode | True | False |
| Passwords | Not Required | Required |
| Error Display | Full | Limited |

### Commands:
```bash
# Start local development
python run_local.py

# Start auto-sync (watches for changes)
python auto_sync.py

# Manual sync once
python auto_sync.py --once

# Deploy to live
git add -A
git commit -m "Your message"
git push
```

### Best Practices:
1. Always test locally first
2. Let auto-sync handle the file updates
3. Check both versions before pushing
4. Keep TESTING_MODE difference intact
5. Never edit app_live.py directly

### Current Issues to Fix:
- [ ] Animations not working on local
- [ ] Ensure all API endpoints synced
- [ ] Verify all templates use same base