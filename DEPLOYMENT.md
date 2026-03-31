# Deployment Guide

This guide covers deploying CCTV Analytics from development to production environments.

## Prerequisites

### Infrastructure Requirements

**Minimum Setup (Small to Medium):**
- 2 CPU cores
- 4 GB RAM
- 20 GB SSD
- 100 Mbps network

**Recommended Setup (Medium to Large):**
- 4+ CPU cores
- 16 GB+ RAM
- 100+ GB SSD
- 1 Gbps network

**For High-Traffic/Multiple Vision Workers:**
- 8+ CPU cores
- 32+ GB RAM
- GPU acceleration (NVIDIA RTX 3090+ or A100)
- 10 Gbps network

### Software Prerequisites

- Linux (Ubuntu 20.04+ recommended)
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Certbot (for HTTPS)

## Deployment Methods

### 1. Docker Compose (Recommended for Small-Medium)

Best for: Single server deployments, development/staging, small production environments.

#### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### Step 2: Clone Repository

```bash
cd /opt
sudo git clone https://github.com/yourusername/cctv-analytics.git
cd cctv-analytics
sudo chown -R $USER:$USER .
```

#### Step 3: Configure Environment

```bash
cp .env.example .env

# Edit with your production values
nano .env
```

**Critical Settings:**
```env
# Security
DEBUG=False
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DB_PASSWORD=<generate-strong-password>
DB_HOST=postgres
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com (or your provider)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-specific-password>
EMAIL_FROM_ADDRESS=noreply@yourdomain.com

# Security/Encryption
ENCRYPTION_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')

# Redis/Cache
REDIS_PASSWORD=<generate-strong-password>

# Storage (local or S3)
STORAGE_TYPE=local
# OR for S3:
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...

# Celery
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/1
```

#### Step 4: Deploy with Docker Compose

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Run migrations (first time only)
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Collect static files
docker compose exec backend python manage.py collectstatic --noinput

# Create subscription plans
docker compose exec backend python manage.py shell < scripts/seed_plans.py

# Verify health
curl http://localhost:8000/api/v1/health/check/
```

#### Step 5: Configure HTTPS with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate (requires domain DNS pointing to server)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Update nginx.conf with SSL paths
sudo nano /path/to/nginx/nginx.conf
```

Add to `nginx.conf`:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL best practices
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Rest of config...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

```bash
# Restart containers
docker compose restart nginx

# Auto-renew certificates
sudo certbot renew --dry-run  # Test renewal
sudo systemctl enable certbot.timer
```

#### Step 6: Setup Backups

```bash
# Daily backup script (backup.sh)
#!/bin/bash
BACKUP_DIR="/backups/cctv-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
docker compose exec -T postgres pg_dump -U postgres cctv_analytics > $BACKUP_DIR/db.sql

# Backup media files
cp -r ./volumes/media $BACKUP_DIR/

# Backup encryption keys (keep secure!)
cp .env $BACKUP_DIR/.env.bak

# Upload to S3
aws s3 sync $BACKUP_DIR s3://your-backup-bucket/

# Keep only last 30 days
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

```bash
# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/cctv-analytics/backup.sh
```

#### Step 7: Monitoring

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f backend
docker compose logs -f celery_worker

# Monitor resources
docker stats

# Health checks
curl -s http://localhost:8000/api/v1/health/check/ | jq
```

### 2. Kubernetes (Recommended for Large/Enterprise)

Best for: High-availability, auto-scaling, multi-region deployments.

#### Step 1: Install Kubernetes Tools

```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
kubectl version --client
helm version
```

#### Step 2: Create Kubernetes Manifests

**Namespace:**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cctv-analytics
```

**Database StatefulSet:**
```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: cctv-analytics
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: cctv_analytics
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: cctv-analytics
spec:
  clusterIP: None
  ports:
  - port: 5432
  selector:
    app: postgres
```

**Redis Deployment:**
```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: cctv-analytics
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command:
        - redis-server
        - "--requirepass"
        - "$(REDIS_PASSWORD)"
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: cctv-analytics
spec:
  selector:
    app: redis
  ports:
  - port: 6379
  type: ClusterIP
```

**Django Deployment:**
```yaml
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: cctv-analytics
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: yourusername/cctv-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          value: "False"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secret
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: backend-secret
              key: secret-key
        livenessProbe:
          httpGet:
            path: /api/v1/health/check/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health/check/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: cctv-analytics
spec:
  selector:
    app: backend
  ports:
  - port: 8000
  type: LoadBalancer
```

**Celery Worker Deployment:**
```yaml
# k8s/celery-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
  namespace: cctv-analytics
spec:
  replicas: 2
  selector:
    matchLabels:
      app: celery-worker
  template:
    metadata:
      labels:
        app: celery-worker
    spec:
      containers:
      - name: celery-worker
        image: yourusername/cctv-backend:latest
        command: ["celery", "-A", "config", "worker", "-l", "info"]
        env:
        - name: CELERY_BROKER_URL
          valueFrom:
            secretKeyRef:
              name: backend-secret
              key: celery-broker-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Vision Worker with GPU:**
```yaml
# k8s/vision-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vision-worker
  namespace: cctv-analytics
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vision-worker
  template:
    metadata:
      labels:
        app: vision-worker
    spec:
      nodeSelector:
        accelerator: gpu
      containers:
      - name: vision-worker
        image: yourusername/cctv-vision:latest
        command: ["celery", "-A", "config", "worker", "-l", "info", "-Q", "vision"]
        resources:
          requests:
            memory: "2Gi"
            cpu: "2"
            nvidia.com/gpu: 1
          limits:
            memory: "4Gi"
            cpu: "4"
            nvidia.com/gpu: 1
```

#### Step 3: Create Secrets

```bash
# Create secrets
kubectl create namespace cctv-analytics

# Database secret
kubectl create secret generic db-secret \
  --from-literal=password=$(openssl rand -base64 20) \
  -n cctv-analytics

# Backend secret
kubectl create secret generic backend-secret \
  --from-literal=secret-key=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())') \
  --from-literal=database-url="postgresql://user:pass@postgres:5432/cctv_analytics" \
  --from-literal=celery-broker-url="redis://default:password@redis:6379/0" \
  -n cctv-analytics

# Redis secret
kubectl create secret generic redis-secret \
  --from-literal=password=$(openssl rand -base64 20) \
  -n cctv-analytics
```

#### Step 4: Deploy

```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/celery-worker.yaml
kubectl apply -f k8s/vision-worker.yaml

# Check rollout
kubectl rollout status deployment/backend -n cctv-analytics

# Get services
kubectl get svc -n cctv-analytics
```

#### Step 5: Ingress for HTTPS (with Nginx Ingress Controller)

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cctv-ingress
  namespace: cctv-analytics
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
    secretName: cctv-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

```bash
# Deploy cert-manager first
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.0

# Apply ingress
kubectl apply -f k8s/ingress.yaml
```

### 3. Systemd Service (Alternative to Docker)

For environments without Docker:

```ini
# /etc/systemd/system/cctv-backend.service
[Unit]
Description=CCTV Analytics Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=cctv
WorkingDirectory=/opt/cctv-analytics/backend
Environment="VIRTUAL_ENV=/opt/cctv-analytics/venv"
Environment="PATH=/opt/cctv-analytics/venv/bin:$PATH"
ExecStart=/opt/cctv-analytics/venv/bin/gunicorn \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable cctv-backend
sudo systemctl start cctv-backend
```

## Post-Deployment

### Initial Setup

```bash
# Create superuser (if not done already)
docker compose exec backend python manage.py createsuperuser

# Admin panel: http://yourdomain.com/admin

# Seed subscription plans
docker compose exec backend python manage.py shell < scripts/seed_plans.py

# Create initial organization
# Use admin panel or API
curl -X POST http://localhost:8000/api/v1/organizations/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Test Org", "privacy_confirmed": true}'
```

### Monitoring & Maintenance

**Daily Checks:**
```bash
# Check service status
docker compose ps

# Check disk usage
df -h

# Check database size
docker compose exec postgres psql -U postgres cctv_analytics -c "\l+"
```

**Weekly Tasks:**
- Review error logs
- Check backup completion
- Verify HTTPS certificate renewal
- Review analytics/performance metrics

**Monthly Tasks:**
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review and optimize slow queries
- Clean up old logs
- Validate disaster recovery procedures

## Scaling Considerations

### Horizontal Scaling

```bash
# Scale vision workers
docker compose up -d --scale vision_worker=3

# In Kubernetes: 
kubectl scale deployment vision-worker --replicas=5 -n cctv-analytics
```

### Load Balancing

Use HAProxy or NGinx Load Balancer in front of multiple backend instances:

```nginx
upstream backend_pool {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend_pool;
    }
}
```

### Database Optimization

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_camera_org ON cameras(organization_id);
CREATE INDEX idx_event_camera_timestamp ON events(camera_id, occurred_at DESC);
CREATE INDEX idx_alert_status ON alerts(status, triggered_at DESC);

-- Enable query logging for slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
```

## Troubleshooting

### Common Issues

**Out of Memory:**
```bash
# Monitor memory usage
docker stats

# Increase limits in docker-compose.yml
# Or reduce celery workers, vision processor skips

# Clear Redis cache
redis-cli FLUSHDB
```

**Database Connection Errors:**
```bash
# Check PostgreSQL health
docker compose exec postgres pg_isready

# View connection count
docker compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Increase max connections if needed
```

**Celery Tasks Not Running:**
```bash
# Check Redis connectivity
docker compose exec redis redis-cli ping

# Check celery logs
docker compose logs -f celery_worker

# Monitor queue
docker compose exec backend celery -A config inspect active
```

**SSL Certificate Issues:**
```bash
# Check cert validity
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout

# Renew immediately
sudo certbot renew --force-renewal

# Check renewal logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

## Conclusion

For more help:
- Check logs: `docker compose logs -f`
- Review docs in `docs/` folder
- Open GitHub Issue
- Contact support@example.com
