# API Documentation

## Base URL

```
http://localhost:8000/api
```

## Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication Endpoints

#### Register User
- **URL**: `/auth/register`
- **Method**: `POST`
- **Auth**: No
- **Body**:
  ```json
  {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }
  ```
- **Response** (201):
  ```json
  {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_admin": false,
    "created_at": "2026-09-02T10:00:00",
    "updated_at": "2026-09-02T10:00:00"
  }
  ```

#### Login
- **URL**: `/auth/login`
- **Method**: `POST`
- **Auth**: No
- **Body**:
  ```json
  {
    "username": "johndoe",
    "password": "SecurePass123"
  }
  ```
- **Response** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }
  ```

#### Refresh Token
- **URL**: `/auth/refresh`
- **Method**: `POST`
- **Auth**: Yes (refresh token in header)
- **Response** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
  ```

### User Endpoints

#### Get All Users
- **URL**: `/users`
- **Method**: `GET`
- **Auth**: Yes
- **Query Parameters**:
  - `skip` (int): Number of records to skip (default: 0)
  - `limit` (int): Number of records to return (default: 10)
- **Response** (200):
  ```json
  [
    {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "is_admin": false,
      "created_at": "2026-09-02T10:00:00",
      "updated_at": "2026-09-02T10:00:00"
    }
  ]
  ```

#### Get User by ID
- **URL**: `/users/{user_id}`
- **Method**: `GET`
- **Auth**: Yes
- **Response** (200): Single user object

#### Create User (Admin only)
- **URL**: `/users`
- **Method**: `POST`
- **Auth**: Yes (Admin)
- **Body**:
  ```json
  {
    "username": "newuser",
    "email": "new@example.com",
    "password": "SecurePass123",
    "full_name": "New User"
  }
  ```
- **Response** (201): User object

#### Update User
- **URL**: `/users/{user_id}`
- **Method**: `PUT`
- **Auth**: Yes
- **Body**:
  ```json
  {
    "full_name": "Updated Name",
    "email": "updated@example.com"
  }
  ```
- **Response** (200): Updated user object

#### Delete User (Admin only)
- **URL**: `/users/{user_id}`
- **Method**: `DELETE`
- **Auth**: Yes (Admin)
- **Response** (200): `{"message": "User deleted successfully"}`

### Role Endpoints

#### Get All Roles
- **URL**: `/roles`
- **Method**: `GET`
- **Auth**: Yes
- **Response** (200): Array of role objects

#### Create Role (Admin only)
- **URL**: `/roles`
- **Method**: `POST`
- **Auth**: Yes (Admin)
- **Body**:
  ```json
  {
    "name": "policy_creator",
    "description": "Can create and manage policies"
  }
  ```
- **Response** (201): Role object

#### Assign Role to User
- **URL**: `/users/{user_id}/roles/{role_id}`
- **Method**: `POST`
- **Auth**: Yes (Admin)
- **Response** (200): `{"message": "Role assigned successfully"}`

### Policy Endpoints

#### Get All Policies
- **URL**: `/policies`
- **Method**: `GET`
- **Auth**: Yes
- **Query Parameters**:
  - `status` (string): Filter by status (draft, active, inactive, archived)
  - `policy_type` (string): Filter by type
  - `resource_type` (string): Filter by resource type
- **Response** (200): Array of policy objects

#### Get Policy by ID
- **URL**: `/policies/{policy_id}`
- **Method**: `GET`
- **Auth**: Yes
- **Response** (200): Policy object with details

#### Create Policy
- **URL**: `/policies`
- **Method**: `POST`
- **Auth**: Yes
- **Body**:
  ```json
  {
    "name": "S3 Read Only",
    "description": "Read-only access to S3 buckets",
    "policy_type": "user",
    "resource_type": "s3",
    "policy_document": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": ["s3:GetObject"],
          "Resource": "arn:aws:s3:::*/*"
        }
      ]
    }
  }
  ```
- **Response** (201): Created policy object

#### Update Policy
- **URL**: `/policies/{policy_id}`
- **Method**: `PUT`
- **Auth**: Yes
- **Body**: Partial policy update
- **Response** (200): Updated policy object

#### Activate Policy
- **URL**: `/policies/{policy_id}/activate`
- **Method**: `POST`
- **Auth**: Yes
- **Response** (200): `{"message": "Policy activated successfully"}`

#### Delete Policy
- **URL**: `/policies/{policy_id}`
- **Method**: `DELETE`
- **Auth**: Yes
- **Response** (200): `{"message": "Policy deleted successfully"}`

### Policy Synthesis Endpoints

#### Analyze Access Patterns
- **URL**: `/synthesis/analyze`
- **Method**: `POST`
- **Auth**: Yes
- **Body**:
  ```json
  {
    "user_id": 1,
    "timeframe_days": 30,
    "resource_type": "s3"
  }
  ```
- **Response** (200):
  ```json
  {
    "user_id": 1,
    "analysis_period_days": 30,
    "total_access_events": 150,
    "unique_resources": 5,
    "unique_actions": 3,
    "access_patterns": [
      {
        "resource": "arn:aws:s3:::bucket1",
        "action": "GetObject",
        "frequency": 100,
        "first_seen": "2026-08-03T10:00:00",
        "last_seen": "2026-09-02T10:00:00"
      }
    ]
  }
  ```

#### Generate Policy Recommendations
- **URL**: `/synthesis/generate`
- **Method**: `POST`
- **Auth**: Yes
- **Body**:
  ```json
  {
    "user_id": 1,
    "timeframe_days": 30,
    "resource_type": "s3"
  }
  ```
- **Response** (200):
  ```json
  {
    "policy_name": "S3-User-1-LeastPrivilege",
    "policy_document": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": ["s3:GetObject"],
          "Resource": "arn:aws:s3:::bucket1/*"
        }
      ]
    },
    "permissions": [
      {
        "resource": "arn:aws:s3:::bucket1",
        "action": "GetObject",
        "frequency": 100,
        "required": true
      }
    ],
    "recommendations": [
      "Consider adding time-based restrictions",
      "Monitor for unauthorized access patterns"
    ],
    "confidence_score": 0.95
  }
  ```

#### Validate Policy
- **URL**: `/synthesis/validate`
- **Method**: `POST`
- **Auth**: Yes
- **Body**:
  ```json
  {
    "policy_document": {
      "Version": "2012-10-17",
      "Statement": [...]
    },
    "policy_type": "user"
  }
  ```
- **Response** (200):
  ```json
  {
    "is_valid": true,
    "warnings": [
      "Policy allows wildcard actions"
    ],
    "errors": [],
    "recommendations": [
      "Restrict actions to specific operations"
    ]
  }
  ```

### Audit Log Endpoints

#### Get Audit Logs
- **URL**: `/logs`
- **Method**: `GET`
- **Auth**: Yes
- **Query Parameters**:
  - `skip` (int): Number of records to skip
  - `limit` (int): Number of records to return
  - `user_id` (int): Filter by user
  - `action` (string): Filter by action
- **Response** (200): Array of audit log objects

#### Get User Audit Logs
- **URL**: `/logs/user/{user_id}`
- **Method**: `GET`
- **Auth**: Yes
- **Response** (200): Array of user-specific logs

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request body"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Endpoints are rate-limited to prevent abuse:
- Public endpoints: 100 requests per 15 minutes
- Authenticated endpoints: 1000 requests per 15 minutes

## Pagination

For list endpoints, use:
- `skip` query parameter (default: 0)
- `limit` query parameter (default: 10, max: 100)

---

**Last Updated**: 2026-09-02
