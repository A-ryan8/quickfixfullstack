#!/usr/bin/env python3
"""
Test script for upvote functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
COMPLAINT_ID = 1  # Change this to an existing complaint ID
USER_ID = "test_user_123"

def test_upvote():
    """Test the upvote endpoint"""
    url = f"{BASE_URL}/api/complaints/{COMPLAINT_ID}/upvote"
    
    # Test data
    data = {
        "user_id": USER_ID
    }
    
    print(f"Testing upvote for complaint {COMPLAINT_ID}...")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        # Make the request
        response = requests.post(url, data=data)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Upvote successful!")
            print(f"Response: {response.json()}")
        elif response.status_code == 409:
            print("⚠️ User has already upvoted this complaint")
            print(f"Response: {response.json()}")
        elif response.status_code == 404:
            print("❌ Complaint not found")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_get_complaints():
    """Test getting complaints to see upvote counts"""
    url = f"{BASE_URL}/api/complaints/public"
    
    print(f"\nTesting get complaints...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            complaints = response.json()
            print(f"✅ Found {len(complaints)} complaints")
            
            for complaint in complaints:
                print(f"  - ID: {complaint['id']}, Title: {complaint['title']}, Upvotes: {complaint.get('upvote_count', 0)}")
        else:
            print(f"❌ Failed to get complaints: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_duplicate_upvote():
    """Test duplicate upvote prevention"""
    url = f"{BASE_URL}/api/complaints/{COMPLAINT_ID}/upvote"
    
    data = {
        "user_id": USER_ID
    }
    
    print(f"\nTesting duplicate upvote prevention...")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        # First upvote
        response1 = requests.post(url, data=data)
        print(f"First upvote - Status: {response1.status_code}")
        
        # Second upvote (should fail)
        response2 = requests.post(url, data=data)
        print(f"Second upvote - Status: {response2.status_code}")
        
        if response2.status_code == 409:
            print("✅ Duplicate upvote prevention working!")
        else:
            print("❌ Duplicate upvote prevention not working")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Upvote Functionality")
    print("=" * 50)
    
    # Test getting complaints first
    test_get_complaints()
    
    # Test upvoting
    test_upvote()
    
    # Test duplicate upvote prevention
    test_duplicate_upvote()
    
    print("\n" + "=" * 50)
    print("Test completed!")

