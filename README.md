# AI-Powered CCTV Analytics as a Service (SaaS)

A complete, production-ready full-stack web application for AI-powered video analytics. Organizations can connect their existing CCTV/IP cameras, run real-time AI analytics, and receive intelligent alerts and reports—all without replacing their cameras.

## 📋 Features

### Core Analytics
- **People Detection & Counting**: Real-time detection and tracking of people in camera feeds
- **Entry/Exit Counting**: Track people entering and exiting defined areas
- **Intrusion Detection**: Alert on unauthorized entry to restricted zones
- **Loitering Detection**: Identify people spending unusual amounts of time in areas
- **Object Detection**: Detect and track objects (vehicles, packages, etc.)

### Camera Management
- **Multi-Stream Support**: RTSP, RTSP-S, HTTP MJPEG, DVR/NVR connections
- **Camera Health Monitoring**: Automatic health checks and status reporting
- **Encrypted Credentials**: Secure storage of camera usernames and passwords
- **Stream Testing**: Test connections before saving
- **Multi-Site Organization**: Organize cameras by location/branch

### Alerts & Notifications
- **Smart Rule Engine**: Create custom rules triggered by analytics events
- **Multiple Channels**: Email, webhooks (SMS/WhatsApp ready for future)
- **Alert Management**: Acknowledge and track alert history
- **Cooldown Logic**: Prevent alert fatigue with deduplication
- **Webhook Signing**: Secure webhook delivery with HMAC signatures

### Dashboard & Reports
- **Real-time Dashboard**: Live camera feeds and event streams
- **Analytics Dashboard**: People count trends, peak hours, occupancy patterns
- **Event Timeline**: Chronological view of all detected events
- **Daily/Weekly Reports**: Comprehensive analytics reports
- **Customizable Alerts**: Configurable notification channels and recipients

### Multi-Tenant Architecture
- **Organization Management**: Support multiple organizations
- **Role-Based Access Control**: Admin, Manager, Viewer roles
- **Team Management**: Invite users and manage permissions
- **Audit Logging**: Track all actions for compliance
- **Trial-Ready**: Built-in trial subscription plan

### Security & Privacy
- **JWT Authentication**: Secure token-based authentication
- **Encrypted Secrets**: Camera credentials encrypted at rest
- **RBAC**: Fine-grained permission system
- **SSL/TLS Ready**: HTTPS support via Nginx
- **Privacy-First**: No facial recognition by default
- **Compliance Ready**: Audit trails and retention policies

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│              Tailwind CSS, TypeScript, Zustand              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Nginx Reverse Proxy                          │
│              SSL/TLS, Security Headers, Routing               │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼────────┐ ┌───▼──────────┐ ┌▼─────────────┐
│  Django REST   │ │   Celery     │ │  Celery Beat │
│     API        │ │   Worker     │ │  (Scheduler) │
│ (Gunicorn)     │ │ (Task Queue) │ │              │
└─────────┬──────┘ └───────┬──────┘ └──────────────┘
          │                │
        ┌─┴────┬───────────┤
        │      │           │
┌───────▼──┐ ┌─▼────────┐ ┌▼──────────────┐
│ PostgreSQL│ │  Redis   │ │ Vision Worker │
│ Database  │ │  Cache & │ │ (YOLOv8 AI)   │
│           │ │  Message │ │  + FFmpeg     │
│ (Multi-   │ │  Broker  │ │               │
│  tenant)  │ └──────────┘ └───────────────┘
└───────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- (Optional) Python 3.11+ for local development

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/cctv-analytics.git
cd cctv-analytics
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the setup script**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Or use Make:
```bash
make setup
```

4. **Access the application**
- Frontend: http://localhost:5173
- API: http://localhost:8000/api/v1
- Admin Panel: http://localhost:8000/admin

### Default Credentials (Change in Production)
- Username: `admin`
- Email: `admin@example.com`
- Password: (Set during first run)

## 📖 Usage Guide

### Adding a Camera

1. Create an organization: `/setup`
2. Go to Dashboard → Add Camera
3. Enter camera details:
   - Name and description
   - Connection type (RTSP, HTTP MJPEG, DVR/NVR)
   - Host/IP address and port
   - Username and password (encrypted)
   - Stream path or full RTSP URL
4. Test connection before saving
5. Enable analytics modules
6. Save and start monitoring

### Creating Rules

Rules allow you to set up automated responses to analytics events:

1. Go to Rules section
2. Create new rule
3. Define trigger condition:
   - People count exceeds threshold
   - Line crossing detected
   - Intrusion detected
   - Loitering detected
   - Camera offline
4. Set time windows (optional)
5. Choose actions:
   - Dashboard alert
   - Email notification
   - Webhook delivery
6. Set cooldown period (prevent alert fatigue)
7. Save and enable

### Managing Alerts

- **Dashboard**: View active and recent alerts
- **Acknowledge**: Mark alerts as acknowledged
- **Resolve**: Mark alerts as resolved
- **History**: View alert history and patterns
- **Channels**: Configure notification channels

### Viewing Analytics

- **Dashboard**: High-level metrics and trends
- **Daily View**: Detailed daily analytics
- **Hourly View**: Granular hourly breakdowns
- **Reports**: Generate and export reports (future)

## 🛠️ Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=cctv_analytics
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=postgres
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password

# AI/Vision
VISION_WORKER_ENABLED=True
SNAPSHOT_RETENTION_DAYS=7

# Security
ENCRYPTION_KEY=32-byte-encryption-key for credentials

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Scaling Considerations

- **Multiple Vision Workers**: Scale AI processing
  ```bash
  docker compose up -d --scale vision_worker=3
  ```

- **Database Optimization**: Add indexes, configure connection pooling
- **Redis Cluster**: For high-throughput deployments
- **CDN**: For static assets and media
- **Load Balancer**: Nginx/HAProxy for multiple API servers

## 📊 Database Schema Highlights

Key models:
- **User**: Custom user model with email-based auth
- **Organization**: Multi-tenant support with RBAC
- **Camera**: Camera configuration with encrypted credentials
- **Event**: Analytics events (people detected, intrusions, etc.)
- **Alert**: Triggered alerts with status tracking
- **Rule**: Custom rule definitions with conditions/actions
- **NotificationDelivery**: Delivery tracking for webhooks/emails
- **AuditLog**: Compliance and security audit trail

See `backend/apps/*/models.py` for detailed schema.

## 🔐 Security

### Built-in Security Features
- ✅ JWT authentication with access/refresh tokens
- ✅ Encrypted credential storage (Fernet cipher)
- ✅ Role-based access control (RBAC)
- ✅ Tenant isolation in all queries
- ✅ CORS configuration
- ✅ Security headers (X-Frame-Options, CSP, HSTS)
- ✅ Brute-force protection ready
- ✅ Audit logging for compliance
- ✅ Webhook HMAC signing

### Production Recommendations
```bash
# Update secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Use environment-specific settings
DJANGO_SETTINGS_MODULE=config.settings.production

# Enable HTTPS and HSTS
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# Configure strong database passwords
# Use service-to-service authentication
# Enable WAF/DDoS protection
# Set up monitoring and alerting
```

## 🎬 Streaming Solution

The system uses **FFmpeg + HLS** for browser-compatible streaming:

**Why HLS?**
- Browser-native support (Safari, Chrome, Firefox)
- Adaptive bitrate capability
- Works with existing RTSP cameras
- Secure stream proxying through Django
- Cross-origin compatible

**Architecture:**
```
Camera (RTSP) → FFmpeg → HLS Segments → Browser (Video.js)
```

Stream endpoints are protected by JWT authentication and organization isolation.

## 📦 Deployment

### Docker Compose (Development/Small Production)
```bash
docker compose up -d
```

### Kubernetes (Enterprise)
```bash
# See docs/kubernetes/ for Helm charts and manifests
kubectl apply -f k8s/
```

### Manual/VPS Deployment
```bash
# See docs/deployment/ for detailed instructions
```

## 🧪 Testing

### Run Backend Tests
```bash
make test
```

### Run Specific App Tests
```bash
docker compose exec backend python manage.py test apps.cameras.tests
```

### Coverage Report
```bash
docker compose exec backend coverage run --source='apps' manage.py test
docker compose exec backend coverage report
```

## 📚 API Documentation

### OpenAPI/Swagger

Access interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login and get tokens
- `GET /api/v1/auth/users/me/` - Get current user

#### Cameras
- `GET /api/v1/cameras/` - List cameras
- `POST /api/v1/cameras/` - Create camera
- `POST /api/v1/cameras/test_connection/` - Test stream
- `GET /api/v1/cameras/{id}/health_logs/` - Health history

#### Analytics
- `GET /api/v1/analytics/summary/` - Dashboard summary
- `GET /api/v1/analytics/daily/` - Daily metrics
- `GET /api/v1/analytics/hourly/` - Hourly metrics

#### Events & Alerts
- `GET /api/v1/events/` - List events
- `GET /api/v1/alerts/` - List alerts
- `POST /api/v1/alerts/{id}/acknowledge/` - Acknowledge alert

#### Rules
- `GET /api/v1/rules/` - List rules
- `POST /api/v1/rules/` - Create rule
- `GET /api/v1/rules/executions/` - Rule execution history

## 📊 Monitoring & Logging

### Health Checks
```bash
curl http://localhost:8000/api/v1/health/check/
```

Response includes database, cache, and service status.

### Logs
```bash
# View all logs
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery_worker
```

### Sentry Integration (Optional)
```python
# In config/settings/production.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

## 🚀 Performance Optimization

### Caching Strategy
- Camera list and health status: 5 min
- Analytics dashboards: 1 min
- Static assets: 30 days

### Database Optimization
- Indexes on frequently queried fields
- Connection pooling (DB_CONN_MAX_AGE=600)
- Lazy loading of large querysets

### AI Optimization
- Process frames every 5 seconds (configurable)
- Adaptive quality based on available resources
- GPU support (CUDA/TensorRT ready)

### Frontend Optimization
- Code splitting with Vite
- Lazy loading of routes
- Image optimization
- Service worker ready (PWA support)

## 🔮 Roadmap / V2 Improvements

### Short Term
- [ ] ONVIF camera discovery
- [ ] Advanced heatmap visualization
- [ ] Queue length estimation
- [ ] Parking ocupancy detection (MVP ready)
- [ ] Face blur/privacy masking
- [ ] Video clip export

### Medium Term
- [ ] WhatsApp/SMS integration
- [ ] Stripe billing integration
- [ ] Mobile app (React Native)
- [ ] Advanced queue analytics
- [ ] Behavioral analytics (staff vs customer)
- [ ] License plate recognition (optional, privacy-conscious)

### Long Term
- [ ] Edge deployment (on-camera processing)
- [ ] Kubernetes auto-scaling
- [ ] GPU acceleration (NVIDIA, TPU)
- [ ] Advanced person re-identification
- [ ] Anomaly detection
- [ ] Predictive analytics

## 📋 Known Limitations & Future Enhancements

- **Streaming**: Currently HLS with 2-10 second latency. WebRTC could reduce this.
- **Facial Recognition**: Not enabled; would require additional privacy controls
- **Video Storage**: Events stored as snapshots, not full video (configurable future feature)
- **ONVIF**: Scaffold in place, full discovery in v2
- **Billing**: Stripe integration ready but not activation gates yet
- **Mobile**: Web-responsive but native mobile app planned

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

See CONTRIBUTING.md for detailed guidelines.

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Database Connection Error**
```bash
# Check database health
docker compose exec postgres pg_isready
# Reset database
docker compose down -v && docker compose up -d
```

**Videos/Snapshots Not Showing**
```bash
# Ensure media directory exists and is writable
docker compose exec backend python manage.py shell
# Check file permissions
```

**Celery Tasks Not Running**
```bash
# Check Redis connection
docker compose exec redis redis-cli ping
# Check Celery logs
docker compose logs -f celery_worker
```

### Support Resources
- **Documentation**: See `docs/` folder
- **Issues**: GitHub Issues for bug reports
- **Email**: support@example.com
- **Slack Community**: (Future)

## 📞 Contact

- **Email**: info@cctvanalytics.example
- **Twitter**: @cctvanalytics
- **Website**: https://www.cctvanalytics.example

---

**Built with** ❤️ using Django, React, YOLOv8, and modern web technologies.

Made for retail shops, parking facilities, warehouses, malls, clinics, schools, and any organization needing intelligent video analytics.
