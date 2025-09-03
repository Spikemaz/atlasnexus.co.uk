# Vercel Environment Variables Setup

## Required Environment Variables for AtlasNexus

Please ensure these environment variables are set in your Vercel project settings:
https://vercel.com/marcus-moores-projects/atlasnexus-securitization/settings/environment-variables

### 1. MongoDB Connection
```
MONGODB_URI = mongodb+srv://marcusbmoore1992_db_user:w6SbBmfO0MQhbXud@cluster0.oduikdo.mongodb.net/atlasnexus?retryWrites=true&w=majority&appName=Cluster0
```

### 2. Email Configuration (if not already set)
```
GMAIL_USER = your-gmail@gmail.com
GMAIL_APP_PASSWORD = your-app-specific-password
```

### 3. Blob Storage (optional)
```
BLOB_READ_WRITE_TOKEN = your-vercel-blob-token
```

## How to Add Environment Variables

1. Go to: https://vercel.com/marcus-moores-projects/atlasnexus-securitization/settings/environment-variables
2. Click "Add New"
3. Enter the Key (e.g., MONGODB_URI)
4. Enter the Value (paste the connection string)
5. Select environments: Production, Preview, Development
6. Click "Save"
7. Redeploy your application for changes to take effect

## Verify MongoDB Connection

After setting the environment variable:
1. Go to the Functions tab in Vercel
2. Check the logs for your app function
3. Look for: "[DATABASE] MongoDB connected successfully"

## Test the Connection

Once deployed, the following endpoints should work:
- `/api/projects` - User projects (requires auth)
- `/api/permutation/projects` - All projects (admin only)
- `/api/permutation/project/<id>` - Specific project (admin only)

## Troubleshooting

If MongoDB is not connecting:
1. Check the environment variable is set correctly
2. Verify the MongoDB URI is valid
3. Check MongoDB Atlas whitelist includes Vercel IPs (0.0.0.0/0 for any IP)
4. Review Vercel function logs for connection errors