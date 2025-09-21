# backend/test_api.py
import requests
import json

# Test the complaint creation API
def test_create_complaint():
    url = "http://localhost:8000/api/complaints"
    
    # Sample complaint data
    complaint_data = {
        "description": "Pothole on Main Street causing vehicle damage",
        "location": "123 Main Street, Downtown",
        "imageUrl": "https://example.com/pothole-image.jpg"
    }
    
    try:
        response = requests.post(url, json=complaint_data)
        
        if response.status_code == 200:
            print("✅ Complaint created successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_update_complaint():
    url = "http://localhost:8000/api/complaints/1"  # Assuming complaint with ID 1 exists
    
    # Sample status update data
    status_data = {
        "status": "In Progress"
    }
    
    try:
        response = requests.put(url, json=status_data)
        
        if response.status_code == 200:
            print("✅ Complaint updated successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_get_complaints():
    url = "http://localhost:8000/api/complaints"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ Complaints fetched successfully!")
            complaints = response.json()
            print(f"Found {len(complaints)} complaints")
            if complaints:
                print(f"First complaint: {complaints[0]}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_db_connection():
    url = "http://localhost:8000/api/test-db"
    
    try:
        response = requests.get(url)
        print(f"Database test: {response.json()}")
    except Exception as e:
        print(f"❌ Error testing database: {e}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_db_connection()
    test_get_complaints()
    test_create_complaint()
    test_update_complaint()
