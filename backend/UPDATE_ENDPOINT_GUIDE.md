# Update Endpoint Guide

## Overview
This guide explains how to update complaint endpoints in the Civic Complaint Management API.

## Endpoint Updates

### 1. Update Complaint Status
```
PUT /api/complaints/{complaint_id}
```

**Request Body:**
```json
{
  "status": "pending|in_progress|resolved"
}
```

**Response:**
```json
{
  "message": "Complaint status updated successfully"
}
```

### 2. Update Complaint Details
```
PUT /api/complaints/{complaint_id}/details
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated Description",
  "location": "Updated Location"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Updated Title",
  "description": "Updated Description",
  "location": "Updated Location",
  "status": "pending",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Authentication
- Admin endpoints require Firebase JWT token with admin role
- User endpoints require Firebase JWT token

## Error Handling
- 400: Invalid request data
- 401: Authentication required
- 403: Admin access required
- 404: Complaint not found
- 500: Internal server error

## Examples

### Update Status (Admin)
```bash
curl -X PUT "http://localhost:8000/api/complaints/1" \
  -H "Authorization: Bearer <admin_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

### Update Details (Admin)
```bash
curl -X PUT "http://localhost:8000/api/complaints/1/details" \
  -H "Authorization: Bearer <admin_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fixed Pothole",
    "description": "Pothole has been repaired",
    "location": "Main Street, Downtown"
  }'
```
