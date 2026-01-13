# Hetzner Single Server Deployment Guide

Host Django + React + PostgreSQL + Redis on one server

## Overview

| Component | Technology | Port |
|-----------|------------|------|
| Backend | Django + Gunicorn | 8000 |
| Frontend | Nginx + React build | 80/443 |
| Database | PostgreSQL | 5432 |
| Cache/Broker | Redis | 6379 |
| Task Queue | Celery Worker | - |
| Scheduler | Celery Beat | - |

---

## Step 1: Create Hetzner Server

1. Go to [Hetzner Cloud Console](https://console.hetzner.cloud)
2. Create new project
3. Add server:
   - **Image**: Ubuntu 22.04
   - **Type**: **CX42** (Recommended) - 4 vCPU, 16GB RAM
   - **Location**: Frankfurt (or nearest to your users)
   - **SSH Key**: Add your public key
4. Note the server IP address

### Recommended Server Sizes

| Server Size | RAM | vCPU | Price | Best For |
|-------------|-----|------|-------|----------|
| CX22 | 4GB | 2 | €4.50/mo | Development/Small |
| CX32 | 8GB | 4 | €11.17/mo | Small Production |
| **CX42** | 16GB | 4 | €22.48/mo | **Recommended** |
| CCX62 | 64GB | 16 | €140/mo | High Traffic |

---

## Step 2: SSH and Basic Setup

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install essential tools
apt install -y curl wget git nginx certbot python3-certbot-nginx ufw

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
usermod -aG docker root

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

---

## Step 3: Clone Repository

```bash
# Clone your project
git clone https://github.com/viviztech/viviz-bulk-sender.git
cd viviz-bulk-sender

# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### Required Environment Variables

```env
# Django Settings
DEBUG=0
SECRET_KEY=your-super-secret-key-min-50-chars
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,api.your-domain.com,localhost,127.0.0.1

# Database
POSTGRES_DB=viviz_bulk_sender
POSTGRES_USER=viviz_user
POSTGRES_PASSWORD=secure-password-here
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://viviz_user:secure-password-here@db:5432/viviz_bulk_sender

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Green API
GREEN_API_ID=your-green-api-id
GREEN_API_TOKEN=your-green-api-token
GREEN_API_URL=https://api.green-api.com

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://api.your-domain.com

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe (optional)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

---

## Step 4: Configure Docker Compose

The project already has `docker-compose.yml`. Verify it includes:

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    restart: always
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GREEN_API_ID=${GREEN_API_ID}
      - GREEN_API_TOKEN=${GREEN_API_TOKEN}
      - GREEN_API_URL=${GREEN_API_URL}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
      - EMAIL_HOST_USER=${EMAIL_HOST_USER}
      - EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    networks:
      - viviz_network

  frontend:
    build: ./frontend
    restart: always
    environment:
      - VITE_API_URL=${VITE_API_URL:-http://localhost:8000/api/v1}
    depends_on:
      - backend
    networks:
      - viviz_network

  celery_worker:
    build: ./backend
    restart: always
    command: celery -A config worker --loglevel=info
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      - db
      - redis
    networks:
      - viviz_network

  celery_beat:
    build: ./backend
    restart: always
    command: celery -A config beat --loglevel=info
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      - db
      - redis
    networks:
      - viviz_network

  db:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - viviz_network

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - viviz_network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/var/www/static:ro
      - media_volume:/var/www/media:ro
    depends_on:
      - backend
      - frontend
    networks:
      - viviz_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  viviz_network:
    driver: bridge
```

---

## Step 5: Configure Nginx

Create `nginx.conf` in project root:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    keepalive_timeout 65;

    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Frontend
    server {
        server_name your-domain.com www.your-domain.com;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API requests proxy to backend
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Admin static files
        location /static/ {
            alias /var/www/static/;
        }

        # Media files
        location /media/ {
            alias /var/www/media/;
        }
    }

    # API Subdomain (optional)
    server {
        server_name api.your-domain.com;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /var/www/static/;
        }

        location /media/ {
            alias /var/www/media/;
        }
    }
}
```

---

## Step 6: Start Services

```bash
# Build and start all containers
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Check logs for specific service
docker-compose logs backend
docker-compose logs nginx
```

---

## Step 7: Run Database Migrations

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

---

## Step 8: Configure SSL with Let's Encrypt

```bash
# Get SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Get API subdomain certificate (if using)
certbot --nginx -d api.your-domain.com

# Auto-renew certificates
certbot renew --dry-run
```

Add to crontab:
```bash
# Add to crontab
crontab -e

# Add this line for automatic renewal
0 2 * * * /usr/bin/certbot renew --quiet
```

---

## Step 9: Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22
ufw allow 80
ufw allow 443

# Enable firewall
ufw enable

# Check status
ufw status
```

---

## Step 10: Set Up Systemd Services

Create service files for auto-start on boot:

```bash
# Create viviz service
cat > /etc/systemd/system/viviz.service << EOF
[Unit]
Description=Viviz Bulk Sender
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/root/viviz-bulk-sender
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Enable service
systemctl enable viviz
systemctl start viviz
systemctl status viviz
```

---

## Step 11: Verify Installation

Access your application:

| Service | URL |
|---------|-----|
| Frontend | http://your-domain.com |
| Admin Panel | http://your-domain.com/admin/ |
| API | http://your-domain.com/api/v1/ |
| API Docs | http://your-domain.com/api/v1/schema/swagger/ |

---

## Resource Usage (CX42 - 16GB RAM)

With ~1000-5000 active users, expected usage:

| Component | RAM Usage | Notes |
|-----------|-----------|-------|
| PostgreSQL | 1-2 GB | Caches queries |
| Redis | 100-500 MB | Cache + broker |
| Backend (Gunicorn) | 500-800 MB | 4 workers |
| Celery Workers | 300-500 MB | 2 workers |
| Nginx | 50-100 MB | Reverse proxy |
| **Total** | **2-4 GB** | Leaves 12-14 GB free |

---

## Scaling Options

### Vertical Scaling (Upgrade Server)
```bash
# In Hetzner console
# Resize CX42 to CCX62 (more RAM/CPU)
# No migration needed - just resize
```

### Horizontal Scaling (Future)
- Add load balancer
- Separate database to managed service
- Use Hetzner managed PostgreSQL

---

## Maintenance Commands

```bash
# View logs
docker-compose logs -f

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Update code
git pull origin main
docker-compose up -d --build

# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Clean up unused images
docker system prune -a

# Backup database
docker-compose exec db pg_dump -U viviz_user viviz_bulk_sender > backup.sql

# Restore database
docker-compose exec -T db psql -U viviz_user viviz_bulk_sender < backup.sql
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check `docker-compose ps` and logs |
| Database connection failed | Verify `DATABASE_URL` in .env |
| CORS errors | Check `CORS_ALLOWED_ORIGINS` |
| Static files 404 | Run `collectstatic` |
| Celery not working | Check Redis connection |
| Out of memory | Upgrade server or add swap |

### Check Logs
```bash
# All logs
docker-compose logs

# Backend logs
docker-compose logs backend

# Nginx logs
docker-compose logs nginx
```

### Restart Everything
```bash
docker-compose down
docker-compose up -d
```

---

## Estimated Monthly Cost

| Item | Cost |
|------|------|
| Hetzner CX42 Server | €22.48 |
| Domain (optional) | €10-15 |
| **Total** | **€22-37/month** |

This setup handles **5000-10000 daily active users** comfortably.
