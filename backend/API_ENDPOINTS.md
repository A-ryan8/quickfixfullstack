# API Endpoints Documentation

## Available Endpoints

### 1. Health Check Endpoints
- **GET** `/` - Welcome message
- **GET** `/api/test` - Basic API test
- **GET** `/api/test-db` - Database connection test

### 2. Complaint Management
- **GET** `/api/complaints` - Get all complaints
- **POST** `/api/complaints` - Create a new complaint
- **PUT** `/api/complaints/{complaint_id}` - Update a complaint's status

#### Get All Complaints Response:
```json
[
  {
    "id": 1,
    "description": "Pothole on Main Street causing vehicle damage",
    "location": "123 Main Street, Downtown",
    "imageUrl": "https://example.com/pothole-image.jpg",
    "status": "New",
    "createdAt": "2025-09-19T19:30:00.000Z"
  }
]
```

#### Create Complaint Request Body:
```json
{
  "description": "Pothole on Main Street causing vehicle damage",
  "location": "123 Main Street, Downtown", 
  "imageUrl": "https://example.com/pothole-image.jpg"
}
```

#### Create Complaint Response:
```json
{
  "id": 1,
  "description": "Pothole on Main Street causing vehicle damage",
  "location": "123 Main Street, Downtown",
  "imageUrl": "https://example.com/pothole-image.jpg", 
  "status": "New"
}
```

#### Update Complaint Request Body:
```json
{
  "status": "In Progress"
}
```

#### Update Complaint Response:
```json
{
  "id": 1,
  "description": "Pothole on Main Street causing vehicle damage",
  "location": "123 Main Street, Downtown",
  "imageUrl": "https://example.com/pothole-image.jpg", 
  "status": "In Progress"
}
```

## Testing the API

### Using the Interactive Documentation
1. Start the server: `uvicorn main:app --reload`
2. Visit `http://localhost:8000/docs`
3. Use the "Try it out" feature to test endpoints
4..\venv\Scripts\Activate.ps1
main_simple_complaints.py

### Using the Test Script
```bash
python test_api.py
```

### Using curl
```bash
# Test database connection
curl http://localhost:8000/api/test-db

# Get all complaints
curl http://localhost:8000/api/complaints

# Create a complaint
curl -X POST "http://localhost:8000/api/complaints" \
     -H "Content-Type: application/json" \
     -d '{
       "description": "Broken streetlight on Oak Avenue",
       "location": "456 Oak Avenue, Midtown",
       "imageUrl": "https://example.com/streetlight.jpg"
     }'

# Update a complaint's status
curl -X PUT "http://localhost:8000/api/complaints/1" \
     -H "Content-Type: application/json" \
     -d '{
       "status": "In Progress"
     }'
```

## Database Schema

The `complaints` table has the following structure:
- `id` (INT, AUTO_INCREMENT, PRIMARY KEY)
- `description` (TEXT, NOT NULL)
- `location` (VARCHAR(255), NOT NULL) 
- `imageUrl` (VARCHAR(500), NOT NULL)
- `status` (VARCHAR(50), DEFAULT 'New')
- `createdAt` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
