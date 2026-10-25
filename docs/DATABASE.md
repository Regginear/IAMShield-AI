# Database Documentation

## Overview

IAMShield AI uses a relational database (MySQL/PostgreSQL) to store all application data. The database is designed to support user authentication, role-based access control, policy management, and comprehensive audit logging.

## Database Schema

### Users Table
Stores user account information and authentication data.

```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255),
  hashed_password VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Columns**:
- `id`: Unique identifier
- `username`: User login name (unique)
- `email`: User email address (unique)
- `full_name`: User's full name
- `hashed_password`: Bcrypt-hashed password
- `is_active`: Account status
- `is_admin`: Admin privileges flag
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Roles Table
Stores available roles for RBAC.

```sql
CREATE TABLE roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Columns**:
- `id`: Unique identifier
- `name`: Role name (unique)
- `description`: Role description
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Default Roles**:
- `admin` - Full system access
- `policy_manager` - Can manage IAM policies
- `policy_viewer` - Can view policies
- `analyst` - Can analyze access patterns
- `user` - Regular user access

### User-Roles Junction Table
Associates users with roles (many-to-many relationship).

```sql
CREATE TABLE user_roles (
  user_id INT NOT NULL,
  role_id INT NOT NULL,
  PRIMARY KEY (user_id, role_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (role_id) REFERENCES roles(id)
);
```

### Policies Table
Stores IAM policies.

```sql
CREATE TABLE policies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  policy_document LONGTEXT NOT NULL,
  status VARCHAR(50) DEFAULT 'draft',
  policy_type VARCHAR(100),
  resource_type VARCHAR(100),
  created_by INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  activated_at TIMESTAMP NULL,
  FOREIGN KEY (created_by) REFERENCES users(id)
);
```

**Columns**:
- `id`: Unique identifier
- `name`: Policy name
- `description`: Policy description
- `policy_document`: JSON policy document
- `status`: Policy status (draft, active, inactive, archived)
- `policy_type`: Type of policy (user, role, service)
- `resource_type`: AWS resource type (s3, ec2, iam, etc.)
- `created_by`: User ID who created the policy
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `activated_at`: When policy became active

**Status Values**:
- `draft` - Policy not yet activated
- `active` - Policy in use
- `inactive` - Policy disabled but kept
- `archived` - Policy archived for historical records

### Access Patterns Table
Stores historical access patterns for analysis.

```sql
CREATE TABLE access_patterns (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  resource VARCHAR(500) NOT NULL,
  action VARCHAR(100) NOT NULL,
  access_count INT DEFAULT 1,
  first_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  source_ip VARCHAR(50),
  status VARCHAR(50) DEFAULT 'allowed',
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Columns**:
- `id`: Unique identifier
- `user_id`: User who accessed the resource
- `resource`: AWS ARN or resource identifier
- `action`: IAM action performed (GetObject, PutObject, etc.)
- `access_count`: Number of times accessed
- `first_accessed`: First access timestamp
- `last_accessed`: Most recent access timestamp
- `source_ip`: IP address of the request
- `status`: Access status (allowed, denied)

### Audit Logs Table
General audit logging for user actions.

```sql
CREATE TABLE audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  action VARCHAR(255) NOT NULL,
  resource_type VARCHAR(100),
  resource_id VARCHAR(500),
  details TEXT,
  status VARCHAR(50) DEFAULT 'success',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Columns**:
- `id`: Unique identifier
- `user_id`: User who performed action
- `action`: Action performed
- `resource_type`: Type of resource affected
- `resource_id`: ID of affected resource
- `details`: Additional details
- `status`: Action status (success, failure)
- `created_at`: Action timestamp

### Policy Audit Logs Table
Specific audit trail for policy changes.

```sql
CREATE TABLE policy_audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  policy_id INT NOT NULL,
  change_type VARCHAR(50) NOT NULL,
  old_value LONGTEXT,
  new_value LONGTEXT,
  changed_by INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (policy_id) REFERENCES policies(id),
  FOREIGN KEY (changed_by) REFERENCES users(id)
);
```

**Columns**:
- `id`: Unique identifier
- `policy_id`: Policy that was changed
- `change_type`: Type of change (created, updated, activated, deleted)
- `old_value`: Previous policy value
- `new_value`: New policy value
- `changed_by`: User who made the change
- `created_at`: Change timestamp

## Relationships

```
Users (1) ──────→ Policies (Many)
   ↓
Roles (Many-to-Many via user_roles)
   ↑
Users

Users (1) ──────→ Audit Logs (Many)

Users (1) ──────→ Access Patterns (Many)

Policies (1) ──────→ Policy Audit Logs (Many)

Users (1) ──────→ Policy Audit Logs (Many)
```

## Indexes

For performance optimization:
- `users.username` - Fast user lookup by username
- `users.email` - Fast user lookup by email
- `roles.name` - Fast role lookup
- `policies.name` - Fast policy lookup
- `policies.status` - Filter policies by status
- `access_patterns.user_id` - Find patterns for user
- `access_patterns.resource` - Find access to resource
- `access_patterns.action` - Find specific actions
- `audit_logs.user_id` - Find user actions
- `audit_logs.created_at` - Time-based filtering

## Migrations

Database migration scripts are stored in `database/migrations/`.

To apply migrations:

**MySQL**:
```bash
mysql -u username -p database_name < database/migrations/001_initial_schema.sql
```

**PostgreSQL**:
```bash
psql -U username -d database_name -f database/migrations/001_initial_schema.sql
```

## Data Retention Policies

- **Audit Logs**: Retain for 1 year
- **Access Patterns**: Retain for 90 days (for synthesis)
- **Policy History**: Retain indefinitely
- **User Data**: Retain while account is active, archive on deletion

## Backup & Recovery

### MySQL Backup
```bash
mysqldump -u root -p iamshield > backup_$(date +%Y%m%d_%H%M%S).sql
```

### MySQL Restore
```bash
mysql -u root -p iamshield < backup.sql
```

### PostgreSQL Backup
```bash
pg_dump -U postgres iamshield > backup_$(date +%Y%m%d_%H%M%S).sql
```

### PostgreSQL Restore
```bash
psql -U postgres iamshield < backup.sql
```

## Connection Strings

**MySQL**:
```
mysql+pymysql://username:password@localhost:3306/iamshield
```

**PostgreSQL**:
```
postgresql://username:password@localhost:5432/iamshield
```

## Query Examples

### Get all active policies for a user
```sql
SELECT p.* FROM policies p
WHERE p.created_by = ? AND p.status = 'active';
```

### Get access patterns for a specific user
```sql
SELECT * FROM access_patterns
WHERE user_id = ?
ORDER BY last_accessed DESC;
```

### Get recent policy changes
```sql
SELECT pal.*, u.username FROM policy_audit_logs pal
JOIN users u ON pal.changed_by = u.id
ORDER BY pal.created_at DESC
LIMIT 10;
```

### Get audit trail for specific resource
```sql
SELECT * FROM audit_logs
WHERE resource_id = ?
ORDER BY created_at DESC;
```

---

**Last Updated**: 2026-09-02
