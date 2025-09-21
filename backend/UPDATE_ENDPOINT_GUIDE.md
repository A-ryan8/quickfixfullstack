# Update Complaint Status - Testing Guide

## New PUT Endpoint Added ✅

Your FastAPI backend now includes a new endpoint to update complaint statuses:

**PUT** `/api/complaints/{complaint_id}` - Update a complaint's status

## How to Test the New Endpoint

### 1. Start Your Server
```bash
cd backend
uvicorn main:app --reload
```

### 2. Test Using Interactive Documentation
1. Visit `http://localhost:8000/docs`
2. Find the **PUT** `/api/complaints/{complaint_id}` endpoint
3. Click "Try it out"
4. Enter a complaint ID (e.g., `1`)
5. In the request body, enter:
   ```json
   {
     "status": "In Progress"
   }
   ```
6. Click "Execute"

### 3. Test Using curl
```bash
# Update complaint ID 1 to "In Progress"
curl -X PUT "http://localhost:8000/api/complaints/1" \
     -H "Content-Type: application/json" \
     -d '{"status": "In Progress"}'

# Update complaint ID 1 to "Resolved"
curl -X PUT "http://localhost:8000/api/complaints/1" \
     -H "Content-Type: application/json" \
     -d '{"status": "Resolved"}'
```

### 4. Test Using Python Script
```bash
python test_api.py
```

## Expected Responses

### Success Response (200):
```json
{
  "id": 1,
  "description": "Pothole on Main Street causing vehicle damage",
  "location": "123 Main Street, Downtown",
  "imageUrl": "https://example.com/pothole-image.jpg",
  "status": "In Progress"
}
```

### Error Responses:
- **404**: Complaint not found
- **500**: Database connection failed or server error

## Status Values You Can Use

Common status values for testing:
- `"New"`
- `"In Progress"`
- `"Under Review"`
- `"Resolved"`
- `"Closed"`

## Validation Rules

The status field has these validation rules:
- **Required**: Must be provided
- **Length**: 1-50 characters
- **Type**: String

## Database Changes

When you update a complaint's status:
1. The `status` field in the database is updated
2. The `createdAt` timestamp remains unchanged
3. All other fields remain unchanged
4. The updated complaint is returned in the response

## Troubleshooting

### "Complaint not found" (404)
- Make sure the complaint ID exists in your database
- Check that you're using the correct ID number

### "Database connection failed" (500)
- Ensure your MySQL server is running
- Check your `.env` file configuration
- Verify database credentials

### "Failed to update complaint" (500)
- Check database permissions
- Ensure the `complaints` table exists
- Verify the table structure matches the expected schema
