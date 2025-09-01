# MongoDB Setup Guide for AtlasNexus

## Problem
Your projects and series are not saving to the cloud database because MongoDB is not configured on Vercel.

## Solution - Configure MongoDB on Vercel

### Step 1: Get Your MongoDB Connection String
1. Go to https://cloud.mongodb.com
2. Sign in to your MongoDB Atlas account
3. Click on your cluster (or create one if you haven't)
4. Click "Connect" button
5. Choose "Connect your application"
6. Copy the connection string (it looks like: `mongodb+srv://username:password@cluster.mongodb.net/database`)
7. Replace `<password>` with your actual password
8. Replace `database` with `atlasnexus`

### Step 2: Add to Vercel Environment Variables
1. Go to https://vercel.com/dashboard
2. Click on your `atlasnexus-securitization` project
3. Go to "Settings" tab
4. Click "Environment Variables" in the left sidebar
5. Add a new variable:
   - Name: `MONGODB_URI`
   - Value: Your MongoDB connection string from Step 1
   - Environment: Select all (Production, Preview, Development)
6. Click "Save"

### Step 3: Redeploy Your Application
1. Go to the "Deployments" tab in Vercel
2. Click the three dots on the latest deployment
3. Click "Redeploy"
4. Wait for deployment to complete

### Step 4: Verify Connection
1. Once deployed, go to: https://atlasnexus.co.uk/debug/db-status
2. You should see:
   - `mongodb_uri_configured: true`
   - `cloud_db_connected: true`
   - Database statistics

## Important: MongoDB Atlas Network Access
Make sure your MongoDB Atlas cluster allows connections from anywhere:
1. In MongoDB Atlas, go to "Network Access"
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere"
4. Add `0.0.0.0/0` as the IP address
5. Click "Confirm"

## Local Testing (Optional)
For local testing without exposing your MongoDB URI in code:
1. Create a file `mongodb_uri.txt` in the project root
2. Add your MongoDB connection string to this file
3. The file is already in .gitignore so it won't be committed

## Test Your Connection
Run the test script locally:
```bash
python check_mongodb.py
```

## What This Fixes
- Projects and series will be saved to MongoDB cloud database
- Data will be accessible from any device, anywhere in the world
- User accounts will maintain their projects across sessions
- No more "Failed to save changes" errors

## Current Status
The code is ready and deployed. You just need to:
1. Add the MONGODB_URI environment variable to Vercel
2. Redeploy the application

Once done, all your project management features will work with cloud storage!