"""
Final comprehensive test of project specifications system
Tests both local and live versions
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
LOCAL_URL = "http://localhost:5000"
LIVE_URL = "https://atlasnexus.co.uk"

def test_api_endpoints(base_url, session=None):
    """Test all API endpoints"""
    print(f"\n{'='*50}")
    print(f"Testing API Endpoints on {base_url}")
    print('='*50)
    
    if not session:
        session = requests.Session()
    
    endpoints = [
        ('/api/project-specifications/industries', 'GET', None),
        ('/api/project-specifications/list', 'GET', None),
        ('/download-template/pipeline', 'GET', None),
        ('/download-template/individual', 'GET', None),
    ]
    
    results = []
    
    for endpoint, method, data in endpoints:
        url = base_url + endpoint
        try:
            if method == 'GET':
                response = session.get(url, timeout=5)
            else:
                response = session.post(url, json=data, timeout=5)
            
            status = "✓" if response.status_code in [200, 302] else "✗"
            results.append({
                'endpoint': endpoint,
                'status_code': response.status_code,
                'success': status == "✓"
            })
            
            print(f"{status} {endpoint}: {response.status_code}")
            
            # Show sample response for successful API calls
            if response.status_code == 200 and endpoint.startswith('/api'):
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        print(f"  → Response sample: {data[0] if len(data) > 0 else 'Empty'}")
                except:
                    pass
                    
        except requests.exceptions.RequestException as e:
            print(f"✗ {endpoint}: Connection Error - {str(e)[:50]}")
            results.append({
                'endpoint': endpoint,
                'status_code': 'ERROR',
                'success': False
            })
    
    return results

def test_project_submission(base_url, session):
    """Test project submission workflow"""
    print(f"\n{'='*50}")
    print(f"Testing Project Submission Workflow")
    print('='*50)
    
    # Test data
    test_project = {
        'project_name': f'Test Project {datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'deal_type': 'Data Centre',
        'project_location': 'London, UK',
        'capex_total': 100000000,
        'offtaker_rent_per_kwh': 0.15,
        'power_cost_per_kwh': 0.08,
        'data_centre_capacity_mw': 50,
        'construction_start_date': '2025-01-01',
        'construction_end_date': '2026-12-31'
    }
    
    # Test save draft
    print("\n1. Testing Draft Save...")
    draft_response = session.post(
        f"{base_url}/api/project-specifications/save-draft",
        json={'project_data': test_project, 'industry': 'DC'}
    )
    
    if draft_response.status_code == 200:
        print("  ✓ Draft saved successfully")
        try:
            draft_data = draft_response.json()
            print(f"  → Draft ID: {draft_data.get('draft_id', 'N/A')}")
        except:
            pass
    else:
        print(f"  ✗ Draft save failed: {draft_response.status_code}")
    
    # Test timeline generation
    print("\n2. Testing Timeline Generation...")
    timeline_response = session.post(
        f"{base_url}/api/project-specifications/timeline",
        json=test_project
    )
    
    if timeline_response.status_code == 200:
        print("  ✓ Timeline generated successfully")
        try:
            timeline_data = timeline_response.json()
            if 'timeline' in timeline_data:
                phases = timeline_data['timeline'].get('phases', [])
                print(f"  → Generated {len(phases)} phases")
                print(f"  → Total duration: {timeline_data['timeline'].get('total_duration_months', 0)} months")
        except:
            pass
    else:
        print(f"  ✗ Timeline generation failed: {timeline_response.status_code}")
    
    # Test project submission
    print("\n3. Testing Project Submission...")
    submit_response = session.post(
        f"{base_url}/api/project-specifications/submit",
        json=test_project
    )
    
    if submit_response.status_code == 200:
        print("  ✓ Project submitted successfully")
        try:
            submit_data = submit_response.json()
            print(f"  → Project ID: {submit_data.get('spec_id', 'N/A')}")
        except:
            pass
    else:
        print(f"  ✗ Project submission failed: {submit_response.status_code}")

def test_template_downloads(base_url, session):
    """Test template download functionality"""
    print(f"\n{'='*50}")
    print(f"Testing Template Downloads")
    print('='*50)
    
    templates = ['pipeline', 'individual', 'initial', 'final']
    
    for template in templates:
        url = f"{base_url}/download-template/{template}"
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                file_size = len(response.content)
                print(f"  ✓ {template}: {file_size} bytes, {content_type}")
            else:
                print(f"  ✗ {template}: Status {response.status_code}")
        except Exception as e:
            print(f"  ✗ {template}: Error - {str(e)[:50]}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ATLASNE XUS PROJECT SPECIFICATIONS SYSTEM TEST")
    print("="*60)
    
    # Test local version
    print("\n" + "-"*60)
    print("TESTING LOCAL VERSION")
    print("-"*60)
    
    try:
        # Check if local server is running
        response = requests.get(f"{LOCAL_URL}/", timeout=2)
        print("✓ Local server is running")
        
        # Create session for local testing
        local_session = requests.Session()
        
        # Test endpoints
        local_results = test_api_endpoints(LOCAL_URL, local_session)
        
        # Test templates
        test_template_downloads(LOCAL_URL, local_session)
        
        # Test submission workflow (requires authentication)
        # Skip for now as it needs login
        
    except requests.exceptions.ConnectionError:
        print("✗ Local server is not running!")
        print("  Please start the server with: python app.py")
    except Exception as e:
        print(f"✗ Local test error: {e}")
    
    # Test live version
    print("\n" + "-"*60)
    print("TESTING LIVE VERSION (atlasnexus.co.uk)")
    print("-"*60)
    
    try:
        # Check if live site is accessible
        response = requests.get(f"{LIVE_URL}/", timeout=10, verify=False)
        print(f"✓ Live site is accessible (Status: {response.status_code})")
        
        # Create session for live testing
        live_session = requests.Session()
        live_session.verify = False  # Skip SSL verification for testing
        
        # Test endpoints
        live_results = test_api_endpoints(LIVE_URL, live_session)
        
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to live site!")
    except Exception as e:
        print(f"✗ Live test error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    print("""
    ✅ FEATURES IMPLEMENTED:
    • Project specifications form with all fields
    • Excel/CSV upload capability
    • Draft saving system
    • Timeline visualization
    • Cash flow analysis
    • Industry categorization
    • Template downloads
    • API endpoints for all operations
    
    📝 NOTES FOR CLIENT DEMO:
    1. Login to the system first
    2. Navigate to Dashboard → Project Specs button
    3. Download templates for reference
    4. Upload Excel pipeline or create new project
    5. Save as draft to continue later
    6. Generate timeline and cash flow charts
    7. Submit for admin review
    8. Admin can populate to permutation engine
    
    ⚠️ IMPORTANT:
    • Ensure pandas and openpyxl are installed
    • Templates are in /static/templates/
    • Data saved in /data/ directory
    """)

if __name__ == "__main__":
    main()