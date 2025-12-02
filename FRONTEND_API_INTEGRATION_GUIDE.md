# 🎯 Frontend API Integration Guide

## Backend Setup Summary

- **Base URL**: `http://localhost:8000/api`
- **Authentication**: JWT (Bearer tokens)
- **Database**: PostgreSQL with multi-tenant support
- **Current API Version**: Production-ready
- **Server Status**: Running and fully functional

---

## 1. AUTHENTICATION

### Login Endpoint

```
POST /api/token/
Content-Type: application/json

{
  "username": "parent_username",
  "password": "parent_password",
  "tenant_slug": "new-kindergarten"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Token Lifetime:**

- Access token: 4 hours
- Refresh token: 7 days

### Refresh Token

```
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Authorization Header Format

```
Authorization: Bearer <access_token>
```

### Example Login Request (JavaScript/React)

```javascript
const login = async (username, password, tenantSlug) => {
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, tenant_slug: tenantSlug }),
  });

  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  return data;
};
```

---

## 2. CHILDREN ENDPOINTS

### Get My Child (Parent View)

```
GET /api/children/me/
Authorization: Bearer <token>

Response:
{
  "id": 2,
  "name": "Ahmed",
  "classroom": {
    "id": 5,
    "name": "Class A"
  },
  "birthdate": "2018-05-15",
  "avatar": "url_to_image",
  "allergies": "peanuts",
  "gender": "male",
  "created_at": "2025-12-02T16:00:00Z"
}
```

### List All Children (Admin Only)

```
GET /api/children/
Authorization: Bearer <admin_token>

Response: [{ child objects }]
```

### Create Child

```
POST /api/children/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Child Name",
  "parent_name": "Parent Name",
  "classroom": 5,
  "birthdate": "2020-01-15",
  "allergies": "milk",
  "conditions": "asthma",
  "doctor": "Dr. Smith",
  "emergency_contact_name": "Uncle John",
  "emergency_contact_phone": "+1234567890",
  "emergency_contact_relation": "uncle",
  "gender": "male",
  "height": 110.50,
  "medication": "inhaler"
}
```

### Get Classrooms

```
GET /api/children/classes/
Authorization: Bearer <token>

Response:
[
  {
    "id": 5,
    "name": "Class A",
    "capacity": 20,
    "created_at": "2025-12-02T16:00:00Z"
  }
]
```

### Get Classroom Details

```
GET /api/children/classes/<id>/
Authorization: Bearer <token>

Response:
{
  "id": 5,
  "name": "Class A",
  "capacity": 20,
  "created_at": "2025-12-02T16:00:00Z"
}
```

### Update Classroom

```
PUT /api/children/classes/<id>/
PATCH /api/children/classes/<id>/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Updated Class Name",
  "capacity": 25
}
```

### Delete Classroom

```
DELETE /api/children/classes/<id>/
Authorization: Bearer <admin_token>
```

---

## 3. EXTRA HOUR REQUESTS (Parent Workflow)

### Create Extra Hour Request

```
POST /api/attendance/extra-hours/
Authorization: Bearer <parent_token>
Content-Type: application/json

{
  "child": 2,
  "hours": 2,
  "date": "2025-12-05"
}

Response:
{
  "id": 1,
  "child": 2,
  "hours": 2,
  "date": "2025-12-05",
  "status": "pending",
  "created_at": "2025-12-02T20:14:00Z"
}
```

### View My Requests (Parent Can See Their Status)

```
GET /api/attendance/my-requests/
Authorization: Bearer <parent_token>

Response:
[
  {
    "id": 1,
    "child": {
      "id": 2,
      "name": "Ahmed"
    },
    "hours": 2,
    "date": "2025-12-05",
    "status": "pending",
    "created_at": "2025-12-02T20:14:00Z"
  },
  {
    "id": 2,
    "child": {
      "id": 2,
      "name": "Ahmed"
    },
    "hours": 1,
    "date": "2025-12-04",
    "status": "approved",
    "created_at": "2025-12-02T19:00:00Z"
  }
]
```

### View Pending Requests (Admin Only)

```
GET /api/attendance/extra/
Authorization: Bearer <admin_token>

Returns all pending extra hour requests from all parents
```

### Approve/Reject Request (Admin Only)

```
POST /api/attendance/extra/<id>/action/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "action": "approved"
}

Valid actions: "approved" or "rejected"

Response:
{
  "success": true,
  "status": "approved"
}
```

---

## 4. EVENTS ENDPOINTS

### Create Event

**Option 1: Create for ALL classrooms (default)**

```
POST /api/planning/events/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "title": "School Trip",
  "description": "Visit to museum",
  "date": "2025-12-15T10:00:00Z"
}

Response:
{
  "message": "Event created for 3 classrooms",
  "count": 3
}
```

**Option 2: Create for SPECIFIC classroom**

```
POST /api/planning/events/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "title": "Class Party",
  "description": "Birthday party",
  "date": "2025-12-20T14:00:00Z",
  "classroom_id": 5
}

Response:
{
  "id": 1,
  "title": "Class Party",
  "description": "Birthday party",
  "date": "2025-12-20T14:00:00Z",
  "classroom": {
    "id": 5,
    "name": "Class A"
  },
  "created_at": "2025-12-02T20:14:00Z"
}
```

### Get Events

```
GET /api/planning/events/
GET /api/planning/events/?classroom_id=5
Authorization: Bearer <token>

Response: [{ event objects }]
```

---

## 5. REPORTS ENDPOINTS

### Get Reports for Child

```
GET /api/reports/?child=2
Authorization: Bearer <parent_token>

Response:
[
  {
    "id": 1,
    "child": 2,
    "date": "2025-12-02",
    "content": "Ahmed was happy today",
    "created_at": "2025-12-02T15:30:00Z"
  }
]
```

### Create Report (Admin)

```
POST /api/reports/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "child": 2,
  "date": "2025-12-02",
  "content": "Ahmed was happy today"
}
```

---

## 6. ATTENDANCE ENDPOINTS

### Get Today's Summary

```
GET /api/attendance/summary/
Authorization: Bearer <admin_token>

Response:
{
  "present": 15,
  "absent": 2
}
```

### Get Today's Attendance

```
GET /api/attendance/
Authorization: Bearer <admin_token>

Response:
[
  {
    "id": 1,
    "child": { "id": 2, "name": "Ahmed" },
    "date": "2025-12-02",
    "status": "present",
    "created_at": "2025-12-02T08:00:00Z"
  }
]
```

### Bulk Update Attendance

```
POST /api/attendance/update/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "records": [
    { "child_id": 2, "status": "present" },
    { "child_id": 3, "status": "absent" }
  ]
}
```

---

## 7. IMPORTANT NOTES FOR FRONTEND

### Multi-Tenant Architecture

- Users belong to specific tenants
- All data is automatically filtered by tenant
- Tenant slug is required for login

### Authentication

- CSRF tokens are **NOT required** for API endpoints (already disabled for mobile)
- Use JWT tokens instead
- Store tokens in localStorage or secure storage

### Error Responses

All error responses follow this format:

```json
{
  "error": "Description of error",
  "detail": "Additional details if available"
}

HTTP Status Codes:
- 200: Success
- 201: Created
- 204: No Content (successful deletion)
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error
```

### Pagination

List endpoints support pagination:

```
GET /api/children/?page=1&page_size=10
```

### Ordering

- Children & Clubs: Ordered by name (A-Z)
- Reports: Ordered by date (newest first)
- Events: Ordered by date (earliest first)
- Extra Hour Requests: Ordered by date (newest first)

### Response Timestamps

All timestamps are in ISO 8601 format with timezone:

```
"2025-12-02T20:14:00Z"
```

---

## 8. ENVIRONMENT SETUP

Create a `.env` file in your frontend project:

```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_TOKEN_KEY=kindergarten_access_token
REACT_APP_REFRESH_KEY=kindergarten_refresh_token
REACT_APP_TENANT_SLUG=new-kindergarten
```

Or for Vue.js:

```
VUE_APP_API_URL=http://localhost:8000/api
VUE_APP_TOKEN_KEY=kindergarten_access_token
VUE_APP_REFRESH_KEY=kindergarten_refresh_token
VUE_APP_TENANT_SLUG=new-kindergarten
```

---

## 9. TEST CREDENTIALS

### Admin User

- **Username**: admin
- **Password**: admin123
- **Tenant Slug**: default
- **Role**: Admin (can manage all resources)

### Parent User

- **Username**: tenant-user
- **Password**: tenant123
- **Tenant Slug**: new-kindergarten
- **Role**: Parent (can view own child, request extra hours)

---

## 10. API DOCUMENTATION

**Interactive API Documentation Available At:**

- Swagger UI: `http://localhost:8000/api/swagger/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

---

## 11. COMMON FRONTEND IMPLEMENTATION PATTERNS

### React Hook for API Calls

```javascript
const useApi = () => {
  const getAuthHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json',
  });

  const apiCall = async (endpoint, options = {}) => {
    const response = await fetch(`http://localhost:8000/api${endpoint}`, {
      ...options,
      headers: getAuthHeaders(),
    });

    if (response.status === 401) {
      // Token expired, refresh
      const refreshResponse = await fetch(
        'http://localhost:8000/api/token/refresh/',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            refresh: localStorage.getItem('refresh_token'),
          }),
        },
      );
      const data = await refreshResponse.json();
      localStorage.setItem('access_token', data.access);

      // Retry original call
      return apiCall(endpoint, options);
    }

    return response.json();
  };

  return { apiCall };
};
```

---

## 12. WORKFLOW EXAMPLES

### Parent Flow: Request Extra Hours

1. Parent logs in with username, password, tenant_slug
2. Get access token from response
3. Fetch child info: `GET /api/children/me/`
4. Submit extra hour request: `POST /api/attendance/extra-hours/`
5. View request status: `GET /api/attendance/my-requests/`
6. Check for response (status: pending/approved/rejected)

### Admin Flow: Manage Extra Hours

1. Admin logs in
2. View pending requests: `GET /api/attendance/extra/`
3. Approve/reject: `POST /api/attendance/extra/<id>/action/`
4. Parent sees updated status when they refresh

### Event Creation Flow

1. Admin creates event with or without classroom_id
2. If no classroom_id: Event created for ALL classrooms
3. If classroom_id provided: Event created for THAT classroom only
4. Parents/children see events: `GET /api/planning/events/`

---

**Ready to integrate! Share this document with your frontend AI/developer.**
