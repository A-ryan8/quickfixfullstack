#!/usr/bin/env python3
"""
Test script for API endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_complaints():
    """Test getting complaints"""
    print("\nTesting get complaints...")
    try:
        response = requests.get(f"{BASE_URL}/api/complaints/public")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            complaints = response.json()
            print(f"Found {len(complaints)} complaints")
            for complaint in complaints[:3]:  # Show first 3
                print(f"  - {complaint['title']} ({complaint['status']})")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_stats():
    """Test getting statistics"""
    print("\nTesting get stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/complaints/stats/public")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"Stats: {stats}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_complaint():
    """Test creating a complaint"""
    print("\nTesting create complaint...")
    try:
        data = {
            "title": f"Test Complaint {datetime.now().strftime('%H:%M:%S')}",
            "description": "This is a test complaint created by the API test script",
            "location": "Test Location"
        }
        
        response = requests.post(f"{BASE_URL}/api/complaints/submit", data=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            complaint = response.json()
            print(f"Created complaint: {complaint['title']} (ID: {complaint['id']})")
            return complaint['id']
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_upvote_complaint(complaint_id):
    """Test upvoting a complaint"""
    if not complaint_id:
        print("\nSkipping upvote test - no complaint ID")
        return False
        
    print(f"\nTesting upvote complaint {complaint_id}...")
    try:
        data = {
            "user_id": "test_user_123"
        }
        
        response = requests.post(f"{BASE_URL}/api/complaints/{complaint_id}/upvote", data=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Upvote successful!")
            return True
        elif response.status_code == 409:
            print("User already upvoted (expected)")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 API Test Suite")
    print("=" * 50)
    
    # Test root endpoint
    test_root_endpoint()
    
    # Test get complaints
    test_get_complaints()
    
    # Test get stats
    test_get_stats()
    
    # Test create complaint
    complaint_id = test_create_complaint()
    
    # Test upvote
    test_upvote_complaint(complaint_id)
    
    print("\n" + "=" * 50)
    print("Test suite completed!")

if __name__ == "__main__":
    main()
