#!/bin/bash

echo "================================"
echo "PROJECT CRUD FLOW TEST"
echo "================================"
echo ""

# Base URL
URL="https://atlasnexus.co.uk"
COOKIE_JAR="test_cookies.txt"

# Clean up old cookies
rm -f $COOKIE_JAR

echo "Step 1: Getting initial page..."
curl -s -c $COOKIE_JAR -o /dev/null $URL
echo "✓ Initial cookies saved"

echo ""
echo "Step 2: Site authentication..."
curl -s -b $COOKIE_JAR -c $COOKIE_JAR \
  -X POST \
  -d "site_password=Nexus2025##" \
  $URL/site-auth \
  -o site_auth_response.html

echo "✓ Site auth attempted"

echo ""
echo "Step 3: User login..."
curl -s -b $COOKIE_JAR -c $COOKIE_JAR \
  -X POST \
  -d "email=spikemaz8@aol.com&password=Darla123*&site_password=Nexus2025##" \
  $URL/auth \
  -o login_response.json

echo "✓ Login attempted"
echo "Response:"
cat login_response.json | head -100

echo ""
echo "Step 4: Get projects..."
curl -s -b $COOKIE_JAR \
  $URL/api/projects \
  -o projects.json

echo "✓ Projects fetched"
echo "Projects response (first 200 chars):"
head -c 200 projects.json

echo ""
echo ""
echo "Step 5: Create test project..."
TIMESTAMP=$(date +%s)
curl -s -b $COOKIE_JAR -c $COOKIE_JAR \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"projects\":[{\"title\":\"Test Project $TIMESTAMP\",\"value\":1000000}]}" \
  $URL/api/projects \
  -o create_response.json

echo "✓ Project creation attempted"
echo "Response:"
cat create_response.json | head -100

echo ""
echo "================================"
echo "Check https://atlasnexus.co.uk manually"
echo "to verify project operations"
echo "================================"