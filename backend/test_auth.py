#!/usr/bin/env python3
"""
Test script for role-based authentication
Run this after setting up admin users in Firebase
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", headers=None, data=None, expected_status=None):
    """Test an API endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if expected_status and response.status_code != expected_status:
            print(f"❌ Expected {expected_status}, got {response.status_code}")
        else:
            print(f"✅ Status {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)[:200]}...")
        except:
            print(f"Response: {response.text[:200]}...")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🔐 Testing Role-Based Authentication")
    print("=" * 50)
    
    # Test public endpoints (should work without auth)
    print("\n📖 Testing Public Endpoints...")
    test_endpoint("/api/complaints/public", expected_status=200)
    test_endpoint("/api/test-db", expected_status=200)
    
    # Test admin endpoints without auth (should fail)
    print("\n🚫 Testing Admin Endpoints Without Auth...")
    test_endpoint("/api/complaints", expected_status=401)
    test_endpoint("/api/complaints/stats", expected_status=401)
    
    # Test user endpoints without auth (should fail)
    print("\n🚫 Testing User Endpoints Without Auth...")
    test_endpoint("/api/complaints", method="POST", data={"title": "Test"}, expected_status=401)
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("✅ Public endpoints should return 200")
    print("❌ Protected endpoints should return 401 without auth")
    print("\n🔑 To test with authentication:")
    print("1. Get a Firebase ID token from your app")
    print("2. Set the token in the headers:")
    print("   headers = {'Authorization': 'Bearer YOUR_TOKEN'}")
    print("3. Re-run the tests with proper headers")
    
    print("\n📚 Next Steps:")
    print("1. Set up admin users in Firebase (see ADMIN_SETUP.md)")
    print("2. Test with real Firebase tokens")
    print("3. Verify admin vs user access levels")

if __name__ == "__main__":
    main()
