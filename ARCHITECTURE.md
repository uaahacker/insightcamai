# Architecture Overview

Complete guide to the CCTV Analytics system architecture.

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Browser / Mobile Client                         │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ HTTPS
                             ▼
        ┌────────────────────────────────────────┐
        │   Nginx Reverse Proxy / Load Balancer   │
        │  - SSL/TLS Termination                 │
        │  - Static Asset Caching                │
        │  - Request Routing                     │
        │  - Gzip Compression                    │
        └────────────┬──────────────────────────┘
                     │
        ┌────────────┴──────────────────────┐
        │                                   │
        ▼                                   ▼
┌──────────────────────┐      ┌──────────────────────┐
│   React Frontend     │      │  Django REST API     │
│  (Vite)              │      │  (Gunicorn)          │
│  - Pages/Components  │      │  - REST Endpoints    │
│  - State Management  │      │  - Authentication    │
│  - API Integration   │      │  - Business Logic    │
│  - Zustand Store     │      │  - Permission Checks │
└──────────────────────┘      └─────────┬────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │  PostgreSQL  │  │    Redis     │  │    Celery    │
            │   Database   │  │   Cache &    │  │    Worker    │
            │              │  │   Message    │  │              │
            │  - Models    │  │   Broker     │  │  - Task Queue│
            │  - Relational│  │              │  │  - Background│
            │  - Records   │  │  - Caching   │  │    Processing│
            │  - User Data │  │  - Sessions  │  │  - Async Jobs│
            └──────────────┘  └──────────────┘  └──────────────┘
                    │
                    └────────────┬─────────────────┐
                                 │                 │
                    ┌────────────▼───┐   ┌────────▼──────────┐
                    │ Celery Beat    │   │  Vision Worker    │
                    │ (Scheduler)    │   │  (AI Processing)  │
                    │                │   │                   │
                    │ - Health Check │   │  - YOLOv8 Models  │
                    │ - Snapshots    │   │  - Object Track.  │
                    │ - Analytics    │   │  - Event Creation │
                    │ - Rules        │   │  - Stream Decode  │
                    └────────────────┘   └───────────────────┘
```

## Core Components

### 1. Frontend Layer (React + Vite)

**Location**: `frontend/`

**Key Files**:
- `src/pages/`: Route pages (Dashboard, CameraList, etc.)
- `src/components/`: Reusable React components
- `src/stores/`: Zustand state management
- `src/api/`: Axios HTTP client with interceptors
- `src/hooks/`: Custom React hooks

**Technology Stack**:
- React 18.2.0
- TypeScript 5.0
- Vite 5.0 (bundler)
- Tailwind CSS 3.3.0
- Zustand 4.4.2 (state)
- Axios 1.6.0 (HTTP)
- React Router 6.20.0 (routing)

**Responsibilities**:
- User interface and interactions
- Form validation and submission
- State management
- Real-time updates (via polling/WebSocket)
- Asset caching
- Error handling and user feedback

### 2. API Gateway (Nginx)

**Location**: `nginx/nginx.conf`

**Responsibilities**:
- HTTPS/SSL termination
- Request routing to backend services
- Static file serving (React build)
- Gzip compression
- Security headers
- Rate limiting (configurable)
- Cache management
- WebSocket support (for future real-time features)

**Configuration**:
```nginx
server {
    listen 443 ssl;
    
    # Route to React frontend
    location / {
        proxy_pass http://frontend:5173;
    }
    
    # Route to Django API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Authorization $http_authorization;
    }
    
    # Static files
    location /static/ {
        alias /app/static/;
        expires 30d;
    }
}
```

### 3. Application Server (Django + DRF)

**Location**: `backend/config/` and `backend/apps/`

**Structure**:
```
backend/
├── config/              # Django project settings
│   ├── settings/        # Environment-specific configs
│   ├── urls.py          # URL routing
│   └── celery_app.py    # Celery configuration
├── apps/                # Django apps
│   ├── accounts/        # User authentication
│   ├── organizations/   # Multi-tenancy
│   ├── cameras/         # Camera management
│   ├── events/          # Analytics events
│   ├── alerts/          # Alert management
│   ├── rules/           # Rule engine
│   ├── notifications/   # Email/Webhook delivery
│   ├── analytics/       # Metrics & aggregation
│   ├── subscriptions/   # Billing & plans
│   ├── auditlogs/       # Compliance logging
│   └── vision_worker/   # AI processing
└── core/                # Shared utilities
    ├── permissions.py   # RBAC
    ├── security.py      # Encryption
    ├── exceptions.py    # Error handling
    └── serializers.py   # Base mixins
```

**Django Apps**:

#### accounts/
- Custom User model with email-based auth
- JWT token generation/refresh
- Password management
- User profile data

#### organizations/
- Multi-tenant organization structure
- User roles (owner, admin, manager, viewer)
- Team membership management
- Invitation system
- Sites/locations within org

#### cameras/
- Camera configuration CRUD
- Credential encryption (Fernet)
- Stream connection testing
- Health monitoring
- Snapshot/clip storage
- Analytics metadata

#### events/
- Event type taxonomy
- Event logging and storage
- Event filtering and search
- Snapshot attachment
- Processing status tracking

#### alerts/
- Alert triggered from events/rules
- Status workflow (triggered→acknowledged→resolved)
- User acknowledgment tracking
- Alert history
- Severity levels

#### rules/
- Rule definition engine
- Condition evaluation
- Action execution (email, webhook, dashboard alert)
- Cooldown/deduplication logic
- Execution logging/audit

#### notifications/
- Multi-channel delivery (email, webhook)
- Retry logic for failed deliveries
- Webhook signing (HMAC-SHA256)
- Channel configuration
- Delivery tracking

#### analytics/
- Daily metrics aggregation
- Hourly time-series data
- People count trends
- Peak hour detection
- Event summarization
- Dashboard summary queries

#### subscriptions/
- Subscription plans (trial, starter, pro, enterprise)
- Organization subscription tracking
- Billing cycle management
- Feature limits enforcement
- Stripe integration ready

#### auditlogs/
- Activity logging for compliance
- User action tracking
- Resource change tracking
- IP address and user agent logging
- Queryable audit trail

#### vision_worker/
- YOLOv8 inference
- Object tracking (centroid-based)
- People detection and counting
- Event generation
- Frame processing pipeline
- FFmpeg stream conversion

### 4. Database Layer (PostgreSQL)

**Location**: `postgres` container

**Key Tables**:
```sql
-- Users & Auth
users (id, email, password_hash, ...)

-- Organizations
organizations (id, name, slug, plan, ...)
organization_members (id, organization_id, user_id, role, ...)
organization_invitations (id, organization_id, email, ...)

-- Cameras
cameras (id, organization_id, name, host, port, ...)
camera_health_logs (id, camera_id, status, latency_ms, ...)
snapshots (id, camera_id, image, timestamp, ...)
video_clips (id, camera_id, video, start_time, end_time, ...)

-- Analytics
events (id, camera_id, event_type, severity, data, ...)
alerts (id, event_id, rule_id, status, severity, ...)
rules (id, organization_id, condition, threshold, actions, ...)
rule_executions (id, rule_id, triggered_at, ...)

-- Notifications
notification_channels (id, organization_id, type, recipients, ...)
notification_deliveries (id, channel_id, status, ...)

-- Analytics Aggregations
daily_analytics (id, camera_id, date, peak_count, ...)
hourly_analytics (id, camera_id, hour, people_count, ...)
analytics_snapshots (id, camera_id, timestamp, people_count, ...)

-- Audit
audit_logs (id, organization_id, user_id, action, resource_type, ...)
```

**Indexes**:
- (organization_id) on cameras, rules, events, alerts
- (camera_id, occurred_at DESC) on events
- (status, created_at DESC) on alerts
- (camera_id, checked_at DESC) on health_logs

**Connection Management**:
- Pool size: 10-20 connections
- Max age: 600 seconds
- Idle timeout: 300 seconds

### 5. Cache Layer (Redis)

**Location**: `redis` container

**Functions**:
- Session storage
- Cache (Django cache framework)
- Message broker for Celery
- Real-time data (leaderboards, counters)
- Rate limiting state

**Key Patterns**:
```
sessions:{session_id} → session data
cache:{key} → cached results
celery:* → task queue
celery-results:{task_id} → task results
```

**Memory Management**:
- Eviction policy: allkeys-lru
- Max memory: 512MB (configurable)
- Persistence: AOF (append-only file)

### 6. Task Queue (Celery + Beat)

**Location**: `celery_worker` and `celery_beat` containers

**Task Types**:

#### Regular Tasks (Queue: default)
```python
# Notification delivery
send_email_alert(rule_id, event_id, recipient)
deliver_webhook(rule_id, event_id, webhook_url)
retry_failed_notifications()

# Analytics
create_daily_analytics_summary(camera_id, date)
aggregate_hourly_analytics(camera_id, hour)

# Maintenance
cleanup_old_snapshots(retention_days)
```

#### Vision Tasks (Queue: vision)
```python
# Stream processing
process_camera_stream(camera_id)
convert_stream_to_hls(camera_id, rtsp_url)

# AI inference
detect_people(frame_data)
track_objects(frame_data, previous_tracks)
```

**Scheduled Tasks (Beat)**:
```python
# Every 5 minutes
check_camera_health()

# Every minute
process_pending_rules()

# Daily at 2 AM
cleanup_old_snapshots()

# Every hour
create_hourly_analytics_summary()
```

### 7. AI Processing (Vision Worker)

**Location**: `vision_worker` container

**Technology Stack**:
- YOLOv8 (object detection)
- OpenCV (image processing)
- PyTorch (deep learning)
- FFmpeg (stream decoding)
- ByteTrack algorithm (object tracking)

**Processing Pipeline**:
```
RTSP Stream → FFmpeg Decode → Frame Extraction
    ↓
   YOLOv8 → Person Detection (class 0)
    ↓
Object Tracking → Centroid Assignment
    ↓
Analytics Computation → People Count, Coordinates
    ↓
Event Generation → Create Event Objects
    ↓
Database Storage → Save to Analytics
```

**Key Features**:
- Frame skipping (process every 5th frame for efficiency)
- Confidence thresholding (>50% for person class)
- Centroid-based tracking
- Event debouncing (don't spam events)
- GPU acceleration ready (CUDA/TensorRT)

**Detection Methods** (Expandable):
- `detect_people()`: Count people in frame
- `detect_line_crossing()`: Objects crossing line
- `detect_intrusion()`: People in restricted zone
- `detect_loitering()`: Person in area > threshold time
- `detect_parking()`: Vehicle space occupancy

## Data Flow Examples

### Example 1: User Creates Camera and Receives Alert

```
1. Frontend: POST /api/v1/cameras/
   ↓
2. Django: Validate data, encrypt password, save to DB
   ↓
3. Vision Worker: process_camera_stream task scheduled
   ↓
4. Vision Worker: Connect to camera, process frames
   ↓
5. Vision Worker: Detect people, create Event
   ↓
6. Django: Event created in database
   ↓
7. Celery: process_pending_rules task runs
   ↓
8. Django: Rule matched, evaluate condition
   ↓
9. Celery: send_email_alert task scheduled
   ↓
10. Notification Worker: Send email via SMTP
   ↓
11. Frontend: User receives email notification
```

### Example 2: Dashboard Loads Analytics

```
1. Frontend: GET /api/v1/analytics/summary/
   ↓
2. Django: Fetch from cache (5-min TTL)
   ↓
3. If cache miss:
   - Query daily_analytics table
   - Sum people counts across all cameras
   - Calculate peak hours
   - Cache result
   ↓
4. Frontend: Display dashboard with metrics
```

### Example 3: Health Check Runs

```
1. Celery Beat: Timer trigger every 5 minutes
   ↓
2. Celery: Dispatch check_camera_health task
   ↓
3. Vision Worker: For each enabled camera:
   - Test stream connection using FFprobe
   - Measure latency
   - Record status
   ↓
4. Database: Create/update CameraHealthLog
   ↓
5. Database: Update camera health_status field
   ↓
6. Dashboard: Show camera status in real-time
```

## Security Architecture

### Authentication Flow

```
1. User: POST /auth/register/ with email + password
   ↓
2. Django: Hash password with PBKDF2
   ↓
3. Database: Store hashed password
   ↓
4. User: POST /auth/login/ with email + password
   ↓
5. Django: Verify password hash, generate JWT tokens
   ↓
6. Frontend: Store tokens (access, refresh) in memory
   ↓
7. Frontend: Include access token in Authorization header
   ↓
8. Django: Middleware validates token signature and expiry
   ↓
9. Request: Proceeds if valid, 401 if invalid/expired
```

### Authorization (RBAC)

```
Organization
├── Owner (full control)
├── Admin (manage cameras, rules, members)
├── Manager (configure cameras, view analytics)
└── Viewer (read-only access)

Resource Access:
- query.filter(organization=request.user.organization)
- permission_classes = [IsOrganizationMember, IsOrganizationAdmin]
```

### Data Encryption

```
Camera Credentials:
Plain password → Fernet cipher → Base64 encrypted → Database

On retrieval:
Base64 encrypted → Fernet decipher → Plain password (in memory only)

Webhook Signatures:
Payload → HMAC-SHA256(payload, secret) → X-Signature header
Receiver verifies: HMAC matches expected signature
```

## Scaling Strategies

### Horizontal Scaling

**Scale Frontend**:
```bash
# Deploy multiple React frontend instances behind load balancer
# Stateless, scales linearly
docker compose up -d --scale frontend=3
```

**Scale API Worker**:
```bash
# Deploy multiple Gunicorn instances
# Shared database: linear scaling
# Load balance with Nginx upstream
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

**Scale Celery Workers**:
```bash
# Add more workers for parallel processing
docker compose up -d --scale celery_worker=5

# Or separate queues for different task types
celery -A config worker -Q default,vision -l info
```

**Scale Vision Workers**:
```bash
# GPU-accelerated workers on separate hardware
docker compose up -d --scale vision_worker=3

# Each worker processes different cameras
```

### Vertical Scaling

**Database Optimization**:
- Connection pooling
- Query optimization
- Indexes on hot columns
- Caching frequently accessed data
- Read replicas for analytics queries

**Cache Optimization**:
- Redis cluster for high availability
- Cache prewarming for popular queries
- Longer TTLs for stable data

**Hardware Upgrades**:
- More CPU cores for Django/Python
- More RAM for Redis/PostgreSQL
- GPU for vision processing (CUDA acceleration)

## Performance Optimization

### Frontend
- Code splitting with Vite
- Lazy loading of routes
- Image optimization
- Browser caching (via Nginx)
- Service worker for offline support

### Backend
- Query optimization (select_related, prefetch_related)
- Database indexes on filter fields
- Pagination (limit/offset)
- Caching with Redis
- Compression (gzip)

### Database
- Connection pooling
- Slow query logging
- Index analysis
- Partitioning for large tables

### Vision Processing
- Frame skipping (every 5th frame)
- Model quantization
- Batch processing
- GPU acceleration
- Adaptive quality

## Deployment Architectures

### Development
```
Single server with all services in Docker Compose
Suitable for: Learning, testing, small teams
```

### Production Small (Single Server)
```
Docker Compose deployment
Load: ~100 cameras, ~1000 events/minute
CPU: 4 cores
RAM: 16 GB
```

### Production Medium (Multi-Server)
```
Load Balancer → Multiple Backend Servers
              → PostgreSQL (Primary + Read Replica)
              → Redis Cluster
              → Multiple Celery Workers
              → Multiple Vision Workers

Load: ~500 cameras, ~10,000 events/minute
Auto-scaling groups
```

### Production Enterprise (Kubernetes)
```
Multiple Kubernetes clusters
RDS PostgreSQL (managed)
ElastiCache Redis (managed)
Auto-scaling based on metrics
Multi-region disaster recovery
```

## Extension Points

### Adding New Analytics
1. Create detection method in `vision_worker/processor.py`
2. Add event type to `events/models.py`
3. Create rule condition in `rules/models.py`
4. Update UI to allow rule creation

### Adding New Notification Channels
1. Create channel type in `notifications/models.py`
2. Create delivery task in `notifications/tasks.py`
3. Update rule execution logic

### Adding New Database Features
1. Create Django migration
2. Update models and serializers
3. Add API endpoints
4. Update tests and documentation

## Monitoring & Observability

### Metrics to Monitor
- API response times (p50, p95, p99)
- Database query duration
- Celery task queue depth
- Memory usage (Python, PostgreSQL, Redis)
- Disk I/O and storage
- Camera health status
- Error rates per endpoint

### Logs to Aggregate
- Django application logs
- Celery task logs
- PostgreSQL query logs
- Nginx access logs
- Vision worker processing logs

### Health Checks
- PostgreSQL connectivity
- Redis connectivity
- Celery worker status
- API endpoint response

See [MONITORING_GUIDE.md](docs/monitoring/) for detailed setup.

## Conclusion

This architecture provides:
- ✅ Scalability (horizontal and vertical)
- ✅ High availability (multi-worker design)
- ✅ Security (encryption, RBAC, audit trails)
- ✅ Flexibility (modular Django apps)
- ✅ Performance (caching, optimization)
- ✅ Maintainability (clear separation of concerns)
- ✅ Extensibility (hooks for new features)

The system is designed to handle growth from single server to enterprise-scale deployments efficiently.
