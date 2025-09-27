# Admin Setup Guide

## Setting Up Role-Based Authorization

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Firebase Admin Role Setup

To grant admin access to users, you need to set custom claims in Firebase. Here are the methods:

#### Method 1: Using Firebase Admin SDK (Recommended)

Create a script to set admin roles:
.\venv\Scripts\Activate.ps1
python main_simple_complaints.py
```python
# set_admin_role.py
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Set admin role for a user
def set_admin_role(email: str):
    try:
        user = auth.get_user_by_email(email)
        auth.set_custom_user_claims(user.uid, {'role': 'admin'})
        print(f"Admin role set for {email}")
    except Exception as e:
        print(f"Error: {e}")

# Usage
set_admin_role("admin@yourdomain.com")
```

#### Method 2: Using Firebase Console

1. Go to Firebase Console → Authentication → Users
2. Find the user you want to make admin
3. Click on the user → Custom Claims
4. Add custom claim: `{"role": "admin"}`

#### Method 3: Using Firebase Functions

```javascript
// Firebase Cloud Function
const functions = require('firebase-functions');
const admin = require('firebase-admin');

exports.setAdminRole = functions.https.onCall(async (data, context) => {
  // Verify the user is authenticated
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }

  // Set admin role
  await admin.auth().setCustomUserClaims(context.auth.uid, { role: 'admin' });
  
  return { message: 'Admin role set successfully' };
});
```

### 3. Testing the Setup

#### Test Admin Access

```bash
# Get a Firebase ID token for an admin user
# Then test admin endpoints:

curl -X GET "http://localhost:8000/api/complaints" \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"

# Should return complaints if user has admin role
# Should return 403 Forbidden if user doesn't have admin role
```

#### Test Regular User Access

```bash
# Test public endpoint (no auth required)
curl -X GET "http://localhost:8000/api/complaints/public"

# Test authenticated user endpoint
curl -X POST "http://localhost:8000/api/complaints/1/upvote" \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"
```

### 4. Available Endpoints

#### Admin-Only Endpoints (Require admin role):
- `GET /api/complaints` - Get all complaints
- `GET /api/complaints/stats` - Get complaint statistics
- `POST /api/complaints/recalculate-priorities` - Recalculate priorities
- `POST /api/complaints/generate-ai` - Generate AI content
- `PUT /api/complaints/{id}` - Update complaint status
- `DELETE /api/complaints/{id}` - Delete complaint

#### Authenticated User Endpoints (Require valid token):
- `POST /api/complaints` - Create complaint
- `POST /api/complaints/{id}/upvote` - Upvote complaint

#### Public Endpoints (No authentication required):
- `GET /api/complaints/public` - View complaints (read-only)
- `GET /api/test-db` - Test database connection

### 5. Error Responses

- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Valid token but insufficient permissions
- `500 Internal Server Error`: Server or database error

### 6. Security Notes

- All admin operations are logged
- JWT tokens are verified against Firebase
- Custom claims are checked for role-based access
- Public endpoints are read-only
- User actions are tracked via authenticated user ID
