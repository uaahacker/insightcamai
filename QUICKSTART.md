# Quick Start Guide

Get CCTV Analytics running in minutes!

## Option 1: Docker Compose (Easiest - 5 minutes)

### Step 1: Install Docker

**Windows:**
- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Mac:**
```bash
brew install docker docker-compose
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Step 2: Clone Project

```bash
git clone https://github.com/yourusername/cctv-analytics.git
cd cctv-analytics
```

### Step 3: Configure Environment

```bash
cp .env.example .env
```

**Edit `.env`** - Key changes (rest can stay as-is):
```env
# Line 2: Change SECRET_KEY to random value
SECRET_KEY=django-insecure-replace-this-with-random-string

# Line 4: Change DEBUG (already set to False)
# Line 5: ALLOWED_HOSTS for your domain
ALLOWED_HOSTS=localhost,127.0.0.1

# Lines 10-13: Database (can stay as-is for local testing)
# Lines 18-22: Email (optional for testing, but recommended)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# ^ This prints emails to console instead of sending

# Line 42: Change encryption key
ENCRYPTION_KEY=paste-32-byte-fernet-key-here
```

**Generate encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Step 4: Launch System

```bash
docker compose up -d
```

**Wait ~30 seconds for services to start**, then:

```bash
# Create superuser (admin account)
docker compose exec backend python manage.py createsuperuser

# When prompted:
# Email: admin@example.com
# Password: your-secure-password
# Password (again): your-secure-password
```

### Step 5: Access Application

- **Frontend**: http://localhost:5173
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs/

Login with superuser credentials you just created.

### Verify Everything Works

```bash
# Check health
curl http://localhost:8000/api/v1/health/check/

# View logs
docker compose logs -f

# See running containers
docker compose ps
```

## Option 2: Local Development Setup (15 minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Redis 7

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure database
cp ../.env.example ../.env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

**Backend running on**: http://localhost:8000

### Frontend Setup (new terminal)

```bash
cd frontend
npm install
npm run dev
```

**Frontend running on**: http://localhost:5173

### Celery Workers (new terminals)

```bash
# Terminal 1: Celery Worker
cd backend
celery -A config worker -l info

# Terminal 2: Celery Beat (scheduler)
cd backend
celery -A config beat -l info
```

## First Time Setup

### 1. Create Organization

**Via Web UI:**
1. Go to http://localhost:5173
2. Sign up with new email
3. Create organization
4. Accept camera privacy terms

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/organizations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Security System",
    "privacy_confirmed": true
  }'
```

### 2. Add Camera

**Via Web UI:**
1. Dashboard → Add Camera
2. Enter camera details:
   - **Name**: "Store Entrance"
   - **Connection Type**: RTSP
   - **Host**: 192.168.1.100 (your camera IP)
   - **Port**: 554
   - **Username**: admin
   - **Password**: camera-password
   - **Stream Path**: /stream1
3. Click "Test Connection"
4. Enable analytics (People Detection, Counting)
5. Save

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/cameras/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization": "org-uuid",
    "name": "Store Entrance",
    "connection_type": "rtsp",
    "host": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "camera-password",
    "stream_path": "/stream1",
    "people_detection": true,
    "people_counting": true
  }'
```

### 3. View Dashboard

- Real-time metrics
- Camera status
- Recent events
- Live alerts

### 4. Create Alert Rule (Optional)

**Via Web UI:**
1. Dashboard → Rules
2. Create New Rule
3. Example: Alert if people count > 5
   - **Condition**: People count exceeds
   - **Threshold**: 5
   - **Action**: Email alert
   - **Recipients**: your@email.com
4. Save & Enable

## Common Issues

### "Connection refused" to Docker services
```bash
# Ensure Docker is running
docker ps

# Restart services
docker compose restart
```

### Database errors
```bash
# Reset database (⚠️ DANGER: Deletes data)
docker compose down -v
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### Celery tasks not running
```bash
# Check Redis connection
docker compose exec redis redis-cli ping

# Check Celery status
docker compose exec celery_worker celery -A config inspect active
```

### Can't login
```bash
# Reset superuser password
docker compose exec backend python manage.py changepassword admin
```

### Port already in use
```
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8000
kill -9 <PID>
```

## What Happens Next?

### Data Collection
- **Snapshots**: Stored every 60 seconds (7 days retention)
- **Events**: Created when conditions detected
- **Analytics**: Aggregated hourly and daily

### Analytics Pipeline
```
Camera Stream → AI Detection → Events → Rules → Alerts → Notifications
                   (YOLOv8)
```

### View Your Data

**Dashboard:**
- http://localhost:5173/dashboard - Overview and metrics

**API Examples:**
```bash
# Get events
curl http://localhost:8000/api/v1/events/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get analytics
curl http://localhost:8000/api/v1/analytics/summary/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# List alerts
curl http://localhost:8000/api/v1/alerts/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Next Steps

### Adding More Features
1. **Additional Cameras**: Repeat "Add Camera" process
2. **More Rules**: Create rules for different conditions
3. **Team Management**: Invite team members to organization
4. **Notification Channels**: Set up email, webhooks, etc.

### Production Deployment
See **DEPLOYMENT.md** for:
- SSL/HTTPS setup
- Kubernetes deployment
- Database backups
- Monitoring & logging

### Developer Customization
See **CONTRIBUTING.md** for:
- Adding new analytics features
- Custom detection algorithms
- Extending the API
- Building additional pages

## Useful Commands

```bash
# View logs
docker compose logs -f backend      # Backend logs
docker compose logs -f celery_worker # Task logs
docker compose logs -f vision_worker # AI processing logs

# Database access
docker compose exec postgres psql -U postgres cctv_analytics

# Django shell
docker compose exec backend python manage.py shell

# Create backup
docker compose exec -T postgres pg_dump -U postgres cctv_analytics > backup.sql

# Stop all services
docker compose down

# Stop and remove data
docker compose down -v

# View running services
docker compose ps

# Check service status
curl http://localhost:8000/api/v1/health/check/ | python -m json.tool
```

## Performance Tips

### For Local Testing
```env
# .env adjustments
VISION_WORKER_ENABLED=False        # Disable AI if not needed
SNAPSHOT_RETENTION_DAYS=1          # Keep fewer snapshots
DEBUG=True                         # Detailed error messages
```

### For Light Load
```bash
# Single celery worker
docker compose up -d --scale celery_worker=1

# Single vision worker
docker compose up -d --scale vision_worker=1
```

### For Multiple Cameras
```bash
# Scale workers
docker compose up -d --scale celery_worker=3 --scale vision_worker=2
```

## Getting Help

- **Documentation**: See `docs/` folder
- **Issues**: GitHub Issues
- **API Docs**: http://localhost:8000/api/docs/
- **Email**: support@example.com

## Video Walkthrough (Optional)

Check YouTube channel for full setup video:
- Part 1: Installation
- Part 2: Adding cameras
- Part 3: Creating rules
- Part 4: Viewing analytics

---

🎉 **You're ready to go!** Start detecting people, create rules, and monitor your cameras!

For advanced configuration, see the main README.md or deployment documentation.
