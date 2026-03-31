# API Reference Guide

Complete reference for CCTV Analytics REST API endpoints.

## Base Information

- **Base URL:** `https://yourdomain.com/api/v1`
- **Authentication:** JWT Bearer Token
- **Response Format:** JSON
- **Pagination:** Limit/Offset (default limit: 20, max: 100)

## Authentication

### Register User

```http
POST /auth/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### Login User

```http
POST /auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response (200):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "first_name": "John"
    }
}
```

### Refresh Token

```http
POST /auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Get Current User

```http
GET /auth/users/me/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### Change Password

```http
POST /auth/users/change_password/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
    "old_password": "oldpassword123",
    "new_password": "newpassword456",
    "new_password_confirm": "newpassword456"
}
```

**Response (200):**
```json
{
    "status": "success",
    "message": "Password changed successfully"
}
```

## Organizations

### List Organizations

```http
GET /organizations/?limit=20&offset=0
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "count": 5,
    "next": "https://api.example.com/organizations/?offset=20",
    "previous": null,
    "results": [
        {
            "id": "org-uuid-1",
            "name": "Retail Store A",
            "slug": "retail-store-a",
            "plan": "professional",
            "members_count": 3,
            "cameras_count": 5,
            "created_at": "2024-01-15T10:30:00Z",
            "members": [
                {
                    "id": "user-uuid-1",
                    "email": "manager@store.com",
                    "role": "admin"
                }
            ],
            "sites": []
        }
    ]
}
```

### Create Organization

```http
POST /organizations/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "New Retail Store",
    "privacy_confirmed": true
}
```

**Response (201):**
```json
{
    "id": "org-uuid-new",
    "name": "New Retail Store",
    "slug": "new-retail-store",
    "plan": "trial",
    "created_by": "user-uuid",
    "created_at": "2024-01-20T14:30:00Z"
}
```

### Get Organization Details

```http
GET /organizations/org-uuid/
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "id": "org-uuid",
    "name": "Retail Store A",
    "slug": "retail-store-a",
    "plan": "professional",
    "members_count": 3,
    "cameras_count": 5,
    "created_at": "2024-01-15T10:30:00Z",
    "members": [
        {
            "id": "user-uuid-1",
            "email": "manager@store.com",
            "role": "admin"
        },
        {
            "id": "user-uuid-2",
            "email": "operator@store.com",
            "role": "manager"
        }
    ],
    "sites": [
        {
            "id": "site-uuid-1",
            "name": "Main Branch",
            "location": "123 Main St, City",
            "coordinates": {
                "lat": 40.7128,
                "lng": -74.0060
            }
        }
    ]
}
```

### Add Member to Organization

```http
POST /organizations/org-uuid/invite_member/
Authorization: Bearer <token>
Content-Type: application/json

{
    "email": "newmember@example.com",
    "role": "manager"
}
```

**Response (201):**
```json
{
    "id": "invitation-uuid",
    "email": "newmember@example.com",
    "role": "manager",
    "status": "pending",
    "expires_at": "2024-01-27T14:30:00Z"
}
```

### Update Member Role

```http
PATCH /organizations/org-uuid/members/member-uuid/
Authorization: Bearer <token>
Content-Type: application/json

{
    "role": "admin"
}
```

**Response (200):**
```json
{
    "id": "member-uuid",
    "user_email": "member@example.com",
    "role": "admin",
    "joined_at": "2024-01-15T10:30:00Z"
}
```

## Cameras

### List Cameras

```http
GET /cameras/?organization=org-uuid&limit=20&offset=0
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "count": 5,
    "results": [
        {
            "id": "camera-uuid-1",
            "name": "Store Entrance",
            "site": "site-uuid-1",
            "site_name": "Main Branch",
            "connection_type": "rtsp",
            "host": "192.168.1.100",
            "port": "554",
            "stream_protocol": "rtsp",
            "stream_path": "/stream1",
            "health_status": "online",
            "last_health_check": "2024-01-20T15:30:00Z",
            "consecutive_failures": 0,
            "is_enabled": true,
            "people_detection": true,
            "people_counting": true,
            "line_crossing": false,
            "intrusion_detection": false,
            "created_at": "2024-01-15T10:30:00Z",
            "health_logs": [
                {
                    "id": "log-uuid",
                    "status": "online",
                    "latency_ms": 45,
                    "checked_at": "2024-01-20T15:30:00Z"
                }
            ],
            "snapshots": []
        }
    ]
}
```

### Create Camera

```http
POST /cameras/
Authorization: Bearer <token>
Content-Type: application/json

{
    "organization": "org-uuid",
    "name": "Store Entrance",
    "site": "site-uuid-1",
    "connection_type": "rtsp",
    "host": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "camerasecret",
    "stream_protocol": "rtsp",
    "stream_path": "/stream1",
    "stream_profile": "main",
    "people_detection": true,
    "people_counting": true,
    "line_crossing": false,
    "intrusion_detection": false
}
```

**Response (201):**
```json
{
    "id": "camera-uuid-new",
    "name": "Store Entrance",
    "organization": "org-uuid",
    "health_status": "untested",
    "is_enabled": true,
    "created_at": "2024-01-20T14:30:00Z"
}
```

### Test Camera Connection

```http
POST /cameras/test_connection/
Authorization: Bearer <token>
Content-Type: application/json

{
    "connection_type": "rtsp",
    "host": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "camerasecret",
    "stream_protocol": "rtsp",
    "stream_path": "/stream1"
}
```

**Response (200) - Success:**
```json
{
    "success": true,
    "message": "Stream connection successful",
    "latency_ms": 45,
    "stream_url": "rtsp://192.168.1.100:554/stream1"
}
```

**Response (400) - Failure:**
```json
{
    "success": false,
    "error": "Connection timeout",
    "message": "Unable to connect to camera. Check host, port, and credentials."
}
```

### Get Camera Health Logs

```http
GET /cameras/camera-uuid/health_logs/?limit=50
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "results": [
        {
            "id": "log-uuid",
            "camera": "camera-uuid",
            "status": "online",
            "latency_ms": 45,
            "error_message": null,
            "checked_at": "2024-01-20T15:30:00Z"
        },
        {
            "id": "log-uuid-2",
            "camera": "camera-uuid",
            "status": "online",
            "latency_ms": 52,
            "error_message": null,
            "checked_at": "2024-01-20T15:25:00Z"
        }
    ]
}
```

### Enable/Disable Camera

```http
POST /cameras/camera-uuid/enable/
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "id": "camera-uuid",
    "is_enabled": true,
    "message": "Camera enabled"
}
```

## Events

### List Events

```http
GET /events/?camera=camera-uuid&event_type=people_detection&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `organization`: Filter by organization (required for most users)
- `camera`: Filter by specific camera
- `event_type`: Filter by event type
- `severity`: Filter by severity (low, medium, high, critical)
- `processed`: Filter by processed status (true/false)
- `occurred_after`: Filter by start date (ISO format)
- `occurred_before`: Filter by end date (ISO format)

**Response (200):**
```json
{
    "count": 125,
    "results": [
        {
            "id": "event-uuid",
            "camera": "camera-uuid",
            "camera_name": "Store Entrance",
            "event_type": "people_detection",
            "severity": "medium",
            "data": {
                "people_count": 5,
                "coordinates": [[100, 200], [150, 250]]
            },
            "snapshot_url": "/media/snapshots/2024/01/20/event-uuid.jpg",
            "occurred_at": "2024-01-20T15:30:00Z",
            "created_at": "2024-01-20T15:30:05Z",
            "is_processed": false
        }
    ]
}
```

### Mark Event as Processed

```http
POST /events/event-uuid/mark_processed/
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "id": "event-uuid",
    "is_processed": true,
    "processed_at": "2024-01-20T15:35:00Z"
}
```

## Alerts

### List Alerts

```http
GET /alerts/?status=triggered&severity=high&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `status`: triggered, acknowledged, resolved
- `severity`: low, medium, high, critical
- `camera`: Filter by camera
- `triggered_after`: Filter by date

**Response (200):**
```json
{
    "count": 12,
    "results": [
        {
            "id": "alert-uuid",
            "event": "event-uuid",
            "camera": "camera-uuid",
            "camera_name": "Store Entrance",
            "rule": "rule-uuid",
            "title": "High People Count Alert",
            "message": "People count exceeded threshold (5 > 3)",
            "status": "triggered",
            "severity": "high",
            "triggered_at": "2024-01-20T15:30:00Z",
            "acknowledged_at": null,
            "acknowledged_by": null,
            "resolved_at": null
        }
    ]
}
```

### Acknowledge Alert

```http
POST /alerts/alert-uuid/acknowledge/
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "id": "alert-uuid",
    "status": "acknowledged",
    "acknowledged_at": "2024-01-20T15:35:00Z",
    "acknowledged_by": "user-uuid"
}
```

### Resolve Alert

```http
POST /alerts/alert-uuid/resolve/
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "id": "alert-uuid",
    "status": "resolved",
    "resolved_at": "2024-01-20T15:40:00Z"
}
```

## Rules

### List Rules

```http
GET /rules/?organization=org-uuid&enabled=true
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "count": 8,
    "results": [
        {
            "id": "rule-uuid",
            "organization": "org-uuid",
            "camera": "camera-uuid",
            "name": "High People Count Alert",
            "description": "Alert when people count exceeds 5",
            "condition": "people_count_exceeds",
            "threshold": 5,
            "start_time": null,
            "end_time": null,
            "severity": "high",
            "cooldown_minutes": 15,
            "is_enabled": true,
            "actions": [
                {
                    "type": "email",
                    "recipients": ["manager@store.com"]
                },
                {
                    "type": "webhook",
                    "url": "https://example.com/webhook",
                    "secret": "webhook-secret"
                }
            ],
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Create Rule

```http
POST /rules/
Authorization: Bearer <token>
Content-Type: application/json

{
    "organization": "org-uuid",
    "camera": "camera-uuid",
    "name": "After-Hours Intrusion Alert",
    "description": "Alert if anyone detected after 6 PM",
    "condition": "people_count_exceeds",
    "threshold": 0,
    "start_time": "18:00",
    "end_time": "06:00",
    "severity": "critical",
    "cooldown_minutes": 30,
    "is_enabled": true,
    "actions": [
        {
            "type": "email",
            "recipients": ["security@store.com", "owner@store.com"]
        },
        {
            "type": "webhook",
            "url": "https://example.com/security-webhook",
            "secret": "secret-key-123"
        }
    ]
}
```

**Response (201):**
```json
{
    "id": "rule-uuid-new",
    "organization": "org-uuid",
    "name": "After-Hours Intrusion Alert",
    "condition": "people_count_exceeds",
    "is_enabled": true,
    "created_at": "2024-01-20T14:30:00Z"
}
```

### Update Rule

```http
PATCH /rules/rule-uuid/
Authorization: Bearer <token>
Content-Type: application/json

{
    "threshold": 3,
    "cooldown_minutes": 20
}
```

**Response (200):**
```json
{
    "id": "rule-uuid",
    "threshold": 3,
    "cooldown_minutes": 20,
    "updated_at": "2024-01-20T15:00:00Z"
}
```

### Get Rule Executions

```http
GET /rules/rule-uuid/executions/?limit=50
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "count": 23,
    "results": [
        {
            "id": "execution-uuid",
            "rule": "rule-uuid",
            "event_data": {
                "people_count": 6,
                "timestamp": "2024-01-20T15:30:00Z"
            },
            "actions_executed": [
                {
                    "type": "email",
                    "status": "sent",
                    "timestamp": "2024-01-20T15:30:05Z"
                }
            ],
            "triggered_at": "2024-01-20T15:30:00Z"
        }
    ]
}
```

## Analytics

### Dashboard Summary

```http
GET /analytics/summary/?organization=org-uuid
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "organization_name": "Retail Store A",
    "total_cameras": 5,
    "online_cameras": 4,
    "offline_cameras": 1,
    "today_metrics": {
        "total_people": 245,
        "peak_count": 18,
        "peak_hour": 14,
        "total_events": 156,
        "critical_events": 3,
        "high_alerts": 5
    },
    "this_week_metrics": {
        "average_daily_people": 210,
        "total_people": 1470,
        "busiest_day": "Saturday",
        "busiest_hour": 14
    }
}
```

### Daily Analytics

```http
GET /analytics/daily/?camera=camera-uuid&days=30
Authorization: Bearer <token>
```

**Query Parameters:**
- `camera`: Camera UUID (required)
- `days`: Number of days to retrieve (default: 30, max: 365)
- `date_after`: Start date (ISO format)
- `date_before`: End date (ISO format)

**Response (200):**
```json
{
    "camera": "camera-uuid",
    "camera_name": "Store Entrance",
    "results": [
        {
            "id": "analytics-uuid",
            "date": "2024-01-20",
            "peak_people_count": 18,
            "average_people_count": 8.5,
            "total_people_entered": 42,
            "total_people_exited": 40,
            "total_events": 156,
            "critical_events": 3,
            "busy_hours": {
                "9": 4,
                "10": 5,
                "11": 6,
                "12": 8,
                "13": 7,
                "14": 9,
                "15": 8,
                "16": 6,
                "17": 5,
                "18": 4
            },
            "created_at": "2024-01-21T00:30:00Z"
        }
    ]
}
```

### Hourly Analytics

```http
GET /analytics/hourly/?camera=camera-uuid&hours=24
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "camera": "camera-uuid",
    "results": [
        {
            "id": "hourly-uuid",
            "hour": "2024-01-20T14:00:00Z",
            "people_count": 9,
            "events_count": 15,
            "created_at": "2024-01-20T15:00:00Z"
        }
    ]
}
```

## Notification Channels

### List Notification Channels

```http
GET /notification-channels/?organization=org-uuid
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "count": 3,
    "results": [
        {
            "id": "channel-uuid-1",
            "organization": "org-uuid",
            "name": "Main Alert Email",
            "channel_type": "email",
            "recipients": ["manager@store.com", "owner@store.com"],
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "channel-uuid-2",
            "organization": "org-uuid",
            "name": "Security Webhook",
            "channel_type": "webhook",
            "webhook_url": "https://example.com/webhook",
            "is_active": true,
            "created_at": "2024-01-15T10:35:00Z"
        }
    ]
}
```

### Create Notification Channel

```http
POST /notification-channels/
Authorization: Bearer <token>
Content-Type: application/json

{
    "organization": "org-uuid",
    "name": "Slack Alerts",
    "channel_type": "webhook",
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "webhook_secret": "slack-signing-secret",
    "is_active": true
}
```

**Response (201):**
```json
{
    "id": "channel-uuid-new",
    "name": "Slack Alerts",
    "channel_type": "webhook",
    "is_active": true,
    "created_at": "2024-01-20T14:30:00Z"
}
```

## Health Check

### System Health Status

```http
GET /health/check/
```

**Response (200) - Healthy:**
```json
{
    "status": "healthy",
    "services": {
        "database": {
            "status": "connected",
            "response_time_ms": 5
        },
        "cache": {
            "status": "connected",
            "response_time_ms": 3
        },
        "celery": {
            "status": "online",
            "active_tasks": 5
        }
    },
    "timestamp": "2024-01-20T15:30:00Z"
}
```

**Response (503) - Unhealthy:**
```json
{
    "status": "unhealthy",
    "services": {
        "database": {
            "status": "disconnected",
            "error": "Connection refused"
        },
        "cache": {
            "status": "connected"
        }
    },
    "timestamp": "2024-01-20T15:30:00Z"
}
```

## Error Responses

### Standard Error Format

```json
{
    "error": "error_code",
    "message": "Human-readable error message",
    "details": {
        "field_name": ["Field-specific error"]
    }
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no response content
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing/invalid authentication
- **403 Forbidden**: Not authorized to access resource
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limited
- **500 Server Error**: Internal server error
- **503 Service Unavailable**: Service temporarily down

### Example Error Response

```json
{
    "error": "validation_error",
    "message": "Invalid request data",
    "details": {
        "email": ["This field is required."],
        "password": ["Ensure this field has at least 8 characters."]
    }
}
```

## Pagination

All list endpoints support pagination with:

```http
GET /cameras/?limit=20&offset=0
```

**Response includes:**
```json
{
    "count": 150,
    "next": "https://api.example.com/cameras/?limit=20&offset=20",
    "previous": null,
    "results": [...]
}
```

## Rate Limiting

- Default: 1000 requests per hour per user
- Include `X-RateLimit-*` headers in responses
- When limit exceeded: 429 status with `Retry-After` header

## Webhook Delivery

Webhooks are signed with HMAC-SHA256 signature:

```python
import hmac
import hashlib

# Verify signature in receiver
payload = request.body
secret = "webhook-secret"
expected_signature = hmac.new(
    secret.encode(),
    payload,
    hashlib.sha256
).hexdigest()

# Compare with X-Signature header
if expected_signature != request.headers['X-Signature']:
    abort(401)
```

## Interactive API Documentation

- **Swagger UI**: https://yourdomain.com/api/docs/
- **ReDoc**: https://yourdomain.com/api/redoc/
- **OpenAPI Schema**: https://yourdomain.com/api/schema/

Test endpoints directly in the Swagger UI interface.
