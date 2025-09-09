"""
Check MongoDB connection and stats
"""
import requests

def check_db_status():
    """Check database status endpoint"""
    
    print("=" * 60)
    print("DATABASE STATUS CHECK")
    print("=" * 60)
    
    # Check the debug endpoint
    response = requests.get("https://atlasnexus.co.uk/debug/database-status")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n📊 MongoDB Connection Status:")
        print(f"   URI Configured: {data.get('mongodb_uri_configured', False)}")
        print(f"   Cloud DB Available: {data.get('cloud_db_available', False)}")
        print(f"   Cloud DB Connected: {data.get('cloud_db_connected', False)}")
        print(f"   Environment: {data.get('environment', 'unknown')}")
        
        if 'database_stats' in data:
            stats = data['database_stats']
            if isinstance(stats, dict) and stats.get('connected'):
                print("\n✅ REAL MongoDB Stats:")
                print(f"   Storage Used: {stats.get('storage_used_mb', 0)} MB")
                print(f"   Storage Limit: {stats.get('storage_limit_mb', 512)} MB")  
                print(f"   Usage: {stats.get('storage_percentage', 0)}%")
                print(f"   Database: {stats.get('database_name', 'N/A')}")
                
                if 'collections' in stats:
                    print("\n📁 Document Counts:")
                    for collection, count in stats['collections'].items():
                        print(f"   {collection}: {count}")
            else:
                print(f"\n❌ Database stats error: {stats}")
        
        print("\n" + "=" * 60)
        if data.get('cloud_db_connected'):
            print("✅ YES - MongoDB tracker shows REAL usage data!")
            print("The stats come directly from MongoDB Atlas.")
        else:
            print("⚠️ MongoDB not connected - check environment variables")
        print("=" * 60)
        
    else:
        print(f"\n[X] Failed to get status: {response.status_code}")
        print(response.text[:500])

if __name__ == "__main__":
    check_db_status()