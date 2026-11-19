# IAMShield AI API

Base URL: `http://127.0.0.1:8000`

Interactive documentation: `http://127.0.0.1:8000/api/docs`

## Authentication

Register or sign in to receive a JWT:

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
POST /api/auth/password-reset/request
POST /api/auth/password-reset/confirm
```

Send the token for protected operations:

```http
Authorization: Bearer <access_token>
```

Protected endpoints include policy creation, policy decisions, audit logs, and
policy history.

## Access patterns

```http
GET  /api/access-patterns
POST /api/access-patterns
POST /api/access-patterns/bulk
```

Bulk request:

```json
{
  "events": [
    {
      "resource": "arn:aws:s3:::example-bucket/*",
      "action": "s3:GetObject",
      "access_count": 12,
      "status": "allowed"
    }
  ]
}
```

## Synthesis and validation

```http
POST /api/synthesis/analyze
POST /api/synthesis/validate
```

Analysis request:

```json
{ "timeframe_days": 30, "resource_type": null }
```

The response contains the generated policy document, observed permissions,
recommendations, and a transparent prototype confidence score.

## Policy lifecycle

```http
GET   /api/policies
POST  /api/policies
GET   /api/policies/{policy_id}
PATCH /api/policies/{policy_id}/status
GET   /api/policies/{policy_id}/history
GET   /api/policies/{policy_id}/versions
POST  /api/policies/{policy_id}/lifecycle
POST  /api/policies/{policy_id}/rollback
GET   /api/policies/{policy_id}/export
```

Policy creation and status updates require authentication:

```json
{
  "status": "approved",
  "reason": "Reviewed by the administrator"
}
```

Approval records a review decision in the local database. It does not deploy
the policy to a cloud provider.

## Audit

```http
GET /api/audit-logs
```

Audit records include sign-ins, registrations, policy creation, and approval or
rejection decisions. This endpoint requires authentication.

## Monitoring

```http
GET /api/monitoring/summary
```

Returns local application metrics such as audit-event count, policy count, and
approved/draft counts. It is an MVP observability endpoint, not a distributed
production monitoring system.

## Health

```http
GET /health
```

Returns the service status and application version.
