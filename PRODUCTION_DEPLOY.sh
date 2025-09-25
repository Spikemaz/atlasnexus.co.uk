#!/usr/bin/env bash
# PRODUCTION DEPLOYMENT SCRIPT
# Phase-1 v2 with QA Micro-Suite + Canary (admin-only)
set -Eeuo pipefail

### --- Config ---
APP_HOME="${APP_HOME:-/srv/atlasnexus}"
PYBIN="${PYBIN:-$APP_HOME/.venv/bin}"
DOMAIN="${DOMAIN:-atlasnexus.co.uk}"
BIND_ADDR="${BIND_ADDR:-0.0.0.0:8000}"
WORKERS="${WORKERS:-4}"
THREADS="${THREADS:-8}"
TIMEOUT="${TIMEOUT:-120}"

### --- Required env ---
need() { [[ -n "${!1:-}" ]] || { echo "❌ Missing env: $1" >&2; exit 1; }; }
need SECRET_KEY
need REDIS_URL
need MONGODB_URI
export APP_ENV="${APP_ENV:-prod}" FLASK_ENV=production

echo "➡️  Deploying to $APP_HOME for domain https://$DOMAIN"

### --- Prepare Python env ---
mkdir -p "$APP_HOME"
cd "$APP_HOME"
if [[ ! -x "$PYBIN/python" ]]; then
  echo "🐍 Creating venv at $APP_HOME/.venv"
  python3 -m venv "$APP_HOME/.venv"
fi

"$PYBIN/pip" install --upgrade pip wheel >/dev/null
if [[ -f requirements_prod.txt ]]; then
  "$PYBIN/pip" install -r requirements_prod.txt
else
  echo "⚠️  requirements_prod.txt not found, installing minimal set"
  "$PYBIN/pip" install gunicorn Flask
fi

### --- Sanity import ---
"$PYBIN/python" - <<'PY'
import importlib
import sys
for mod in ("wsgi","production_config"):
    try:
        importlib.import_module(mod)
    except Exception as e:
        print(f"❌ Import failed for {mod}: {e}", file=sys.stderr); sys.exit(1)
print("✅ Import sanity OK")
PY

### --- Try systemd unit (preferred), else foreground gunicorn ---
UNIT_FILE=/etc/systemd/system/atlasnexus.service
if [[ -w /etc/systemd/system ]]; then
  echo "📝 Writing systemd unit: $UNIT_FILE"
  sudo tee "$UNIT_FILE" >/dev/null <<UNIT
[Unit]
Description=AtlasNexus (Phase-1 v2) - gunicorn
After=network.target

[Service]
Environment=APP_ENV=$APP_ENV
Environment=FLASK_ENV=production
Environment=SECRET_KEY=$SECRET_KEY
Environment=REDIS_URL=$REDIS_URL
Environment=MONGODB_URI=$MONGODB_URI
WorkingDirectory=$APP_HOME
ExecStart=$PYBIN/gunicorn "wsgi:app" --workers $WORKERS --threads $THREADS --timeout $TIMEOUT --bind $BIND_ADDR
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT

  sudo systemctl daemon-reload
  sudo systemctl enable atlasnexus --now
  sleep 2
  sudo systemctl --no-pager --full status atlasnexus || true
else
  echo "▶️  Launching gunicorn (foreground)"
  exec "$PYBIN/gunicorn" "wsgi:app" --workers "$WORKERS" --threads "$THREADS" --timeout "$TIMEOUT" --bind "$BIND_ADDR"
fi

### --- Health check (expects TLS terminator/Nginx in front) ---
echo "🔎 Health check via reverse proxy…"
curl -sS -D- -o /dev/null "https://$DOMAIN/api/phase1/health?t=$(date +%s)" \
  -H "Cache-Control: no-cache" -H "Pragma: no-cache" | awk 'BEGIN{ok=0}
  /X-Commit-SHA:/ {ok++} /X-Ruleset-Version:/ {ok++} /X-Env:/ {ok++} /X-Build-ID:/ {ok++} /X-Request-ID:/ {ok++}
  {print}
  END{ if(ok<5){exit 8} }'

echo "✅ Deploy complete"