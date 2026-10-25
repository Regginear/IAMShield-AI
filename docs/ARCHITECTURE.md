# System Architecture

## Overview

IAMShield AI is a full-stack application designed to autonomously synthesize least-privilege IAM policies. The system follows a modern three-tier architecture with a React frontend, FastAPI backend, and database layer.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React Frontend (Vite)                               │   │
│  │  - Dashboard                                         │   │
│  │  - Policy Management                                 │   │
│  │  - Policy Synthesis                                  │   │
│  │  - Audit Logs                                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │  API GATEWAY      │
                  │  - CORS            │
                  │  - Authentication  │
                  │  - Rate Limiting   │
                  └─────────┬─────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend                                     │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │ API Routes                                   │   │   │
│  │  │ - /auth          (Authentication)            │   │   │
│  │  │ - /users         (User Management)            │   │   │
│  │  │ - /roles         (RBAC)                       │   │   │
│  │  │ - /policies      (Policy Management)          │   │   │
│  │  │ - /synthesis     (Policy Generation)          │   │   │
│  │  │ - /logs          (Audit Logging)              │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │ Services Layer                               │   │   │
│  │  │ - AuthService    (JWT, Tokens)               │   │   │
│  │  │ - UserService    (User Operations)           │   │   │
│  │  │ - PolicyService  (Policy CRUD)               │   │   │
│  │  │ - SynthesisEngine (Policy Generation)        │   │   │
│  │  │ - AnalysisEngine (Access Pattern Analysis)   │   │   │
│  │  │ - ValidationEngine (Policy Validation)       │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQLAlchemy ORM                                      │   │
│  │  - Models                                            │   │
│  │  - Query Builders                                    │   │
│  │  - Session Management                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  MySQL / PostgreSQL                                 │   │
│  │  - Users Table                                       │   │
│  │  - Roles Table                                       │   │
│  │  - Policies Table                                    │   │
│  │  - Access Patterns Table                             │   │
│  │  - Audit Logs Table                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer (React + Tailwind CSS)

**Key Components:**
- **Dashboard**: Overview of policies, recent activities
- **Policy Management**: Create, read, update, delete policies
- **Policy Synthesis**: UI for generating policies from access patterns
- **User Management**: Manage users and roles
- **Audit Viewer**: View audit logs and history

**Technologies:**
- React 18+
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)
- React Router (navigation)

### 2. Backend Layer (FastAPI)

**Core Components:**

#### Authentication & Authorization
- JWT token generation and validation
- Password hashing with bcrypt
- Role-based access control (RBAC)

#### API Endpoints
- **Auth Routes** (`/api/auth/`)
  - Register, login, refresh token
  
- **User Routes** (`/api/users/`)
  - CRUD operations for users
  
- **Role Routes** (`/api/roles/`)
  - CRUD operations for roles
  
- **Policy Routes** (`/api/policies/`)
  - CRUD operations for policies
  
- **Synthesis Routes** (`/api/synthesis/`)
  - Analyze access patterns
  - Generate policy recommendations
  - Validate policies
  
- **Audit Routes** (`/api/logs/`)
  - Retrieve audit logs

#### Business Logic Services

**AuthService**
- User authentication
- Token generation and validation
- Permission checking

**UserService**
- User CRUD operations
- Role assignment
- User activity tracking

**PolicyService**
- Policy CRUD operations
- Policy versioning
- Status management

**SynthesisEngine**
- Analyzes access patterns
- Generates least-privilege policies
- Provides recommendations

**AnalysisEngine**
- Processes access logs
- Identifies access patterns
- Detects anomalies

**ValidationEngine**
- Validates policy syntax
- Checks for security best practices
- Detects conflicts and redundancies

### 3. Database Layer

**Tables:**

- **users**: User authentication and profile data
- **roles**: Available roles in the system
- **user_roles**: Association between users and roles
- **policies**: Stored IAM policies
- **access_patterns**: Historical access patterns
- **audit_logs**: General audit logging
- **policy_audit_logs**: Policy-specific change tracking

## Data Flow

### Policy Synthesis Flow

```
User Input
  │
  ├─► Access Pattern Analysis
  │   └─► Filter by timeframe, resource, user
  │
  ├─► Permission Extraction
  │   └─► Identify required resources and actions
  │
  ├─► Conflict Resolution
  │   └─► Handle overlapping permissions
  │
  ├─► Policy Optimization
  │   └─► Apply least-privilege principles
  │
  ├─► Policy Generation
  │   └─► Create policy documents
  │
  └─► Policy Validation
      └─► Check security best practices
      └─► Generate recommendations
```

## Security Features

1. **Authentication**
   - JWT-based stateless authentication
   - Secure token storage and validation

2. **Authorization**
   - Role-based access control (RBAC)
   - Endpoint-level permission checks

3. **Data Protection**
   - Password hashing (bcrypt)
   - SQL injection prevention (SQLAlchemy ORM)
   - Input validation (Pydantic)

4. **API Security**
   - CORS protection
   - Rate limiting (to be implemented)
   - HTTPS enforcement (in production)

5. **Audit Trail**
   - All policy changes logged
   - User action tracking
   - Compliance reporting

## Deployment Considerations

### Development
- Run locally with `npm run dev` (frontend) and `python -m uvicorn ...` (backend)
- Use hot reloading for faster development

### Production
- Use Docker containers
- Implement load balancing
- Use managed database services
- Implement CI/CD with GitHub Actions
- Use environment variables for sensitive data
- Enable HTTPS/TLS
- Implement API rate limiting

## Scalability

1. **Horizontal Scaling**
   - Multiple backend instances behind load balancer
   - Stateless design allows easy scaling

2. **Database Optimization**
   - Indexes on frequently queried columns
   - Query optimization
   - Connection pooling

3. **Caching**
   - Cache frequently accessed policies
   - Cache role permissions
   - Implement Redis for session management

## Future Enhancements

- [ ] Multi-cloud policy generation (AWS, Azure, GCP)
- [ ] Machine learning for anomaly detection
- [ ] Policy compliance checking
- [ ] Integration with actual cloud platforms
- [ ] Real-time policy recommendations
- [ ] Advanced audit reporting and analytics
- [ ] Export/import functionality
- [ ] Policy versioning and rollback

---

**Last Updated**: 2026-09-02
