#!/usr/bin/env bash
# EMERGENCY ROLLBACK — set canary to 0% and (optionally) disable flags
set -Eeuo pipefail

LIVE="${LIVE:-https://atlasnexus.co.uk}"
need() { [[ -n "${!1:-}" ]] || { echo "❌ Missing env: $1"; exit 1; }; }
need ADMIN_TOKEN

echo "🚨 Rolling back canary to 0% on $LIVE"
curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
  -X POST "$LIVE/api/phase1/rollback" -d '{"target_percentage":0,"reason":"operator_rollback"}'

# Optional: flip off phase1 flags (versioned)
echo "🔎 Fetching flags version"
FLAGS=$(curl -sS -H "X-Admin-Token:$ADMIN_TOKEN" "$LIVE/api/phase1/flags") || FLAGS="{}"
VERSION=$(printf "%s" "$FLAGS" | sed -n 's/.*"version"[[:space:]]*:[[:space:]]*\([0-9]\+\).*/\1/p' | head -1)

if [[ -n "$VERSION" ]]; then
  echo "🛑 Disabling phase1 flags (version $VERSION → $(($VERSION+1)))"
  curl -sS -H "Content-Type: application/json" -H "X-Admin-Token:$ADMIN_TOKEN" \
    -X POST "$LIVE/api/phase1/flags" -d "{
      \"version\": $VERSION,
      \"changes\": {
        \"phase1_core\": false,
        \"deterministic_seed\": false,
        \"perm_chunking\": false
      }
    }" || true
else
  echo "⚠️  Could not parse flags version; skipping flag disable."
fi

echo "✅ Rollback procedure finished"