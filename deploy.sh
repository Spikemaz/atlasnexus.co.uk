#!/bin/bash
# Phase-1 Production Deployment Script

echo "===== Phase-1 Production Deployment ====="
echo "Setting production environment variables..."

# Set production environment
export APP_ENV=prod
export RULESET_VERSION=v1.0
export PHASE1_MAX_CARD=250000
export REDIS_URL=redis://localhost:6379/2
export SESSION_COOKIE_DOMAIN=.atlasnexus.co.uk
export COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "1489855")
export BUILD_ID=phase1_$(date +%Y%m%d_%H%M)
export PHASE1_ADMIN_TOKEN=phase1-admin-secure-token
export PHASE1_CORE_ENABLED=true

echo "Environment configured:"
echo "  APP_ENV=$APP_ENV"
echo "  RULESET_VERSION=$RULESET_VERSION"
echo "  COMMIT_SHA=$COMMIT_SHA"
echo "  BUILD_ID=$BUILD_ID"

# For Vercel deployment, create .env.production
cat > .env.production << EOF
APP_ENV=prod
RULESET_VERSION=v1.0
PHASE1_MAX_CARD=250000
REDIS_URL=redis://localhost:6379/2
SESSION_COOKIE_DOMAIN=.atlasnexus.co.uk
COMMIT_SHA=$COMMIT_SHA
BUILD_ID=$BUILD_ID
PHASE1_ADMIN_TOKEN=phase1-admin-secure-token
PHASE1_CORE_ENABLED=true
EOF

echo ".env.production file created for Vercel"

# Deploy to Vercel (if available)
if command -v vercel &> /dev/null; then
    echo "Deploying to Vercel..."
    vercel --prod --env-file .env.production
else
    echo "Vercel CLI not found. Please deploy manually with .env.production"
fi

echo "Deployment complete!"