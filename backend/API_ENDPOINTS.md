# Civic Complaint Management API Endpoints

## Base URL
```
http://localhost:8000
```

## Authentication
- **Admin endpoints**: Require Firebase JWT token with admin role
- **User endpoints**: Require Firebase JWT token
- **Public endpoints**: No authentication required

## Public Endpoints (No Authentication Required)

### 1. Get All Complaints (Public)
```
GET /api/complaints/public
```
**Response**: List of all complaints sorted by priority score

### 2. Submit Complaint (Public)
```
POST /api/complaints/submit
Content-Type: multipart/form-data

Fields:
- title: string (required)
- description: string (required)
- location: string (required)
- image: file (optional)
- pdf: file (optional)
```
**Response**: Created complaint object

### 3. Get Complaint Statistics (Public)
```
GET /api/complaints/stats/public
```
**Response**: Complaint statistics object

### 4. Upvote Complaint (Public)
```
POST /api/complaints/{complaint_id}/upvote
Content-Type: application/x-www-form-urlencoded

Fields:
- user_id: string (required)
```
**Response**: Success message

## Admin Endpoints (Require Admin Authentication)

### 1. Get All Complaints (Admin)
```
GET /api/complaints
Authorization: Bearer <admin_jwt_token>
```
**Response**: List of all complaints

### 2. Create Complaint (Admin)
```
POST /api/complaints
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

Body:
{
  "title": "string",
  "description": "string",
  "location": "string",
  "image_url": "string (optional)",
  "pdf_url": "string (optional)"
}
```
**Response**: Created complaint object

### 3. Get Complaint Statistics (Admin)
```
GET /api/complaints/stats
Authorization: Bearer <admin_jwt_token>
```
**Response**: Complaint statistics object

### 4. Recalculate Priorities
```
POST /api/complaints/recalculate-priorities
Authorization: Bearer <admin_jwt_token>
```
**Response**: Success message

### 5. Update Complaint Status
```
PUT /api/complaints/{complaint_id}
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

Body:
{
  "status": "pending|in_progress|resolved"
}
```
**Response**: Success message

### 6. Delete Complaint
```
DELETE /api/complaints/{complaint_id}
Authorization: Bearer <admin_jwt_token>
```
**Response**: Success message

## User Endpoints (Require User Authentication)

### 1. Create Complaint (User)
```
POST /api/complaints
Authorization: Bearer <user_jwt_token>
Content-Type: application/json

Body:
{
  "title": "string",
  "description": "string",
  "location": "string",
  "image_url": "string (optional)",
  "pdf_url": "string (optional)"
}
```
**Response**: Created complaint object

## Response Models

### Complaint Object
```json
{
  "id": 1,
  "title": "Pothole on Main Street",
  "description": "Large pothole causing traffic issues",
  "location": "Main Street, Downtown",
  "status": "pending",
  "priority_score": 85.5,
  "upvote_count": 12,
  "image_url": "/uploads/image.jpg",
  "pdf_url": "/uploads/report.pdf",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Complaint Statistics Object
```json
{
  "total_complaints": 150,
  "pending_complaints": 45,
  "resolved_complaints": 105,
  "resolved_today": 8
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Complaint not found"
}
```

### 409 Conflict
```json
{
  "detail": "User has already upvoted this complaint"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## CORS
The API supports CORS for all origins, methods, and headers to allow frontend integration.

## File Uploads
- Images and PDFs are stored in the `uploads/` directory
- Supported image formats: JPG, PNG, GIF, WebP
- Maximum file size: 10MB per file
- Files are accessible via `/uploads/{filename}` URL

