# Viviz Bulk Sender - Deployment Guide

This guide covers multiple deployment options for the Viviz Bulk Sender SaaS platform.

## Table of Contents

1. [Quick Start with Docker Compose](#1-quick-start-with-docker-compose)
2. [Render](#2-render)
3. [DigitalOcean App Platform](#3-digitalocean-app-platform)
4. [Hetzner Cloud](#4-hetzner-cloud)
5. [AWS Elastic Beanstalk](#5-aws-elastic-beanstalk)
6. [Google Cloud Run](#6-google-cloud-run)
7. [Custom VPS with Nginx](#7-custom-vps-with-nginx)

---

## 1. Quick Start with Docker Compose

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM

### Quick Start

```bash
# Clone and navigate to project
cd viviz-bulk-sender

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access the application
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# Admin Panel: http://localhost:8000/admin/
```

### Production Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    restart: always
    environment:
      - DEBUG=0
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    networks:
      - viviz_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - backend
    networks:
      - viviz_network

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    restart: always
    command: celery -A config worker --loglevel=info
    environment:
      - DEBUG=0
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - viviz_network

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    restart: always
    command: celery -A config beat --loglevel=info
    environment:
      - DEBUG=0
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
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

Run with:
```bash
docker-compose -f docker-compose.production.yml up -d
```

---

## 2. Render

Render is a cloud platform that offers free tier for web services and PostgreSQL. This guide covers complete deployment with backend, frontend, and background workers.

### Prerequisites

- GitHub account with repository access
- Render account (free tier available for web services, $7/month for PostgreSQL)
- **Python 3.11** (configured in Dockerfile)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Render                                │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  viviz-backend  │───▶│  PostgreSQL     │                 │
│  │  (Web Service)  │    │  ($7/month)     │                 │
│  └─────────────────┘    └─────────────────┘                 │
│          │                                                    │
│          │    ┌─────────────────┐                           │
│          └───▶│  External       │                           │
│               │  Redis          │                           │
│               │  (Upstash/      │                           │
│               │   Redis Cloud)  │                           │
│               └─────────────────┘                           │
│                                                            │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │ viviz-frontend  │    │ viviz-celery    │                 │
│  │  (Web Service)  │    │  (Background    │                 │
│  └─────────────────┘    │   Worker)        │                 │
│                         └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘

Frontend → API Calls → Backend → Redis (Celery) → Database
```

---

### Step 1: Prepare Your Repository

```bash
# Make sure your code is pushed to GitHub
cd viviz-bulk-sender
git status
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

**Verify your repository structure:**
```
viviz-bulk-sender/
├── backend/
│   ├── Dockerfile.production  ✅ Already created
│   ├── requirements.txt       ✅ Already fixed
│   └── ...
├── frontend/
│   ├── Dockerfile.production  ✅ Already created
│   ├── nginx.conf            ✅ Already created
│   └── ...
└── .dockerignore             ✅ Already created
```

---

### Step 2: Create PostgreSQL Database

> **Note:** Render's free tier doesn't include PostgreSQL. You'll need the $7/month Starter plan or use an external provider.

#### Option A: Render PostgreSQL (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   | Field | Value |
   |-------|-------|
   | **Name** | `viviz-db` |
   | **Database** | `viviz_bulk_sender` |
   | **User** | `viviz` |
   | **Plan** | Starter ($7/month) |
   | **Region** | Oregon (or closest to you) |
4. Click **"Create Database"**
5. **Wait 2-3 minutes** for provisioning
6. In the **"Connections"** section, note:
   - **Internal Database URL**: `postgres://user:password@host:5432/dbname`
   - **External Database URL**: `postgres://user:password@host:5432/dbname` (for local development)

#### Option B: External PostgreSQL (Free)

If you want to avoid the $7/month, use a free external provider:

- **Supabase** (https://supabase.com) - Free tier available
- **Neon** (https://neon.tech) - Free tier available
- **Railway** (https://railway.app) - $5 credit/month

---

### Step 3: Create Redis Instance

> ⚠️ **Render does NOT offer managed Redis** (the service is deprecated). Use an external free provider:

#### Option A: Upstash (Recommended - Free Tier)

1. Go to [Upstash Console](https://console.upstash.com)
2. Click **"Create Database"**
3. Configure:
   | Field | Value |
   |-------|-------|
   | **Name** | `viviz-redis` |
   | **Region** | Choose closest to Render region |
   | **Plan** | Free |
4. Click **"Create"**
5. In **"REST API"** tab, copy the **Redis URL**:
   ```
   redis://default:password@your-redis-host.upstash.io:6379
   ```

#### Option B: Redis Cloud (Free Tier)

1. Go to [Redis Cloud](https://redis.com/cloud/tryfree/)
2. Sign up and verify email
3. Click **"Create Database"**:
   | Field | Value |
   |-------|-------|
   | **Name** | `viviz-redis` |
   | **Plan** | Fixed (30MB) - Free |
4. Click **"Create"**
5. In **"Configuration"** tab, copy the **Endpoint** URL

---

### Step 4: Generate Required Secrets

Before creating services, generate secure random keys:

```bash
# Generate SECRET_KEY (at least 50 characters)
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Output: abc123... (copy this)

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Output: xyz789... (copy this)
```

---

### Step 5: Create Backend Web Service

1. **Create Backend Service:**
   - Go to Render Dashboard → **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select the `viviz-bulk-sender` repository

2. **Configure Service:**
   | Field | Value |
   |-------|-------|
   | **Name** | `viviz-backend` |
   | **Branch** | `main` |
   | **Runtime** | `Docker` |
   | **Dockerfile Path** | `backend/Dockerfile.production` |
   | **Build Command** | (leave empty) |
   | **Start Command** | (leave empty) |

3. **Add Environment Variables:**
   Click **"Advanced"** → **"Add Environment Variables"**:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `DEBUG` | `0` | Production mode |
   | `SECRET_KEY` | `[生成的SECRET_KEY]` | Django secret key |
   | `JWT_SECRET_KEY` | `[生成的JWT_SECRET_KEY]` | JWT signing key |
   | `DATABASE_URL` | `[PostgreSQL Internal URL]` | From Step 2 |
   | `REDIS_URL` | `[Upstash/Redis Cloud URL]` | From Step 3 |
   | `CELERY_BROKER_URL` | `[Same as REDIS_URL]` | Celery broker |
   | `GREEN_API_ID` | `[Your Green API ID]` | Green API instance ID |
   | `GREEN_API_TOKEN` | `[Your Green API Token]` | Green API instance token |
   | `ALLOWED_HOSTS` | `*` | Or your custom domain |
   | `CORS_ALLOWED_ORIGINS` | `*` | Or your frontend URL |

4. **Create Service:**
   - Click **"Create Web Service"**
   - Wait for build (3-5 minutes)
   - Check **"Logs"** tab for progress

5. **Verify Backend:**
   - Once deployed, visit: `https://viviz-backend.onrender.com`
   - Should see Django welcome page or API response

---

### Step 6: Create Frontend Web Service

1. **Create Frontend Service:**
   - Go to Render Dashboard → **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select the `viviz-bulk-sender` repository

2. **Configure Service:**
   | Field | Value |
   |-------|-------|
   | **Name** | `viviz-frontend` |
   | **Branch** | `main` |
   | **Runtime** | `Docker` |
   | **Dockerfile Path** | `frontend/Dockerfile.production` |
   | **Build Command** | (leave empty) |
   | **Start Command** | (leave empty) |

3. **Add Environment Variable:**
   Click **"Advanced"** → **"Add Environment Variables"**:

   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://viviz-backend.onrender.com` |

4. **Create Service:**
   - Click **"Create Web Service"**
   - Wait for build (2-3 minutes)

5. **Verify Frontend:**
   - Visit: `https://viviz-frontend.onrender.com`
   - Should see the Viviz Bulk Sender login page

---

### Step 7: Create Celery Background Worker (Optional)

For background task processing (sending bulk messages):

1. **Create Worker:**
   - Go to Render Dashboard → **"New +"** → **"Background Worker"**
   - Connect your GitHub repository

2. **Configure Worker:**
   | Field | Value |
   |-------|-------|
   | **Name** | `viviz-celery-worker` |
   | **Branch** | `main` |
   | **Runtime** | `Docker` |
   | **Dockerfile Path** | `backend/Dockerfile.production` |
   | **Start Command** | `celery -A config worker --loglevel=info` |

3. **Add Environment Variables:**
   Copy ALL environment variables from the backend service (Step 5.3)

4. **Create Worker:**
   - Click **"Create Background Worker"**
   - Worker will start processing background tasks

---

### Step 8: Run Database Migrations

1. Go to **viviz-backend** service → **"Shell"** tab
2. Run:
   ```bash
   python manage.py migrate
   ```
3. Wait for migrations to complete

---

### Step 9: Create Superuser

1. In the **Shell** tab, run:
   ```bash
   python manage.py createsuperuser
   ```
2. Enter:
   - **Email**: your-email@example.com
   - **Username**: admin
   - **Password**: (strong password)

3. Access admin panel: `https://viviz-backend.onrender.com/admin/`

---

### Step 10: Configure Green API Webhooks

1. Go to [Green API Dashboard](https://green-api.com/)
2. Open your instance settings
3. Set **Webhook URL**:
   ```
   https://viviz-backend.onrender.com/api/v1/green-api/webhook/
   ```
4. Save settings

---

### Step 11: Update Environment Variables for Production

After successful deployment, update environment variables for better security:

**Backend Service → Environment Variables:**

| Key | New Value |
|-----|----------|
| `ALLOWED_HOSTS` | `viviz-frontend.onrender.com,yourdomain.com` |
| `CORS_ALLOWED_ORIGINS` | `https://viviz-frontend.onrender.com,https://yourdomain.com` |

**Click "Save Changes" and trigger a redeploy.**

---

### Step 12: Configure Custom Domain (Optional)

**Backend:**
1. Go to **viviz-backend** → **Settings**
2. Scroll to **"Custom Domains"**
3. Click **"Add Domain"**
4. Enter: `api.yourdomain.com`
5. Follow DNS instructions (add CNAME or A record)

**Frontend:**
1. Go to **viviz-frontend** → **Settings**
2. Scroll to **"Custom Domains"**
3. Click **"Add Domain"**
4. Enter: `yourdomain.com`
5. Follow DNS instructions

---

### Troubleshooting

#### Error: `Exit Code 128` (Git Clone Failed)

**Cause:** Render cannot clone your repository.

**Solutions:**
1. **Reconnect GitHub:**
   - Go to Service → **Settings** → **GitHub**
   - Click **"Disconnect"** then **"Connect"**
   - Re-authorize and select repository

2. **Check Repository Access:**
   - Go to [GitHub Settings → Applications](https://github.com/settings/installations)
   - Ensure **Render** has access to `viviz-tech/viviz-bulk-sender`

3. **Delete and Recreate Service:**
   - Delete the failing service
   - Create a new service with fresh GitHub connection

#### Error: `pip install failed`

**Cause:** Invalid package in requirements.txt

**Solutions:**
1. Check requirements.txt for typos or non-existent packages
2. The following have been fixed:
   - ❌ `uuid>=1.30` (removed - built-in Python module)
   - ❌ `django-rest-framework-simplejwt-cached-claims>=1.1.2` (removed - doesn't exist)

#### Error: `Database connection failed`

**Cause:** Incorrect DATABASE_URL or database not ready

**Solutions:**
1. Verify PostgreSQL status is "Available" (green dot)
2. Copy **Internal Database URL** from Connections section
3. Ensure URL format: `postgres://user:password@host:5432/dbname`

#### Error: `502 Bad Gateway`

**Cause:** Backend service failed or not responding

**Solutions:**
1. Check **Logs** tab for errors
2. Verify all environment variables are set
3. Check if Gunicorn started correctly

#### Error: `Static files not loading`

**Solution:**
1. Go to **Shell** tab
2. Run: `python manage.py collectstatic`
3. Static files will be served from the backend service

---

### Complete Environment Variables Summary

**Backend Service:**
```
DEBUG=0
SECRET_KEY=[generate with: python -c "import secrets; print(secrets.token_urlsafe(50))"]
JWT_SECRET_KEY=[generate with: python -c "import secrets; print(secrets.token_urlsafe(50))"]
DATABASE_URL=postgres://user:password@host:5432/dbname
REDIS_URL=redis://:password@host:6379
CELERY_BROKER_URL=${REDIS_URL}
GREEN_API_ID=your-instance-id
GREEN_API_TOKEN=your-instance-token
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=*
```

**Frontend Service:**
```
VITE_API_URL=https://viviz-backend.onrender.com
```

---

### Estimated Monthly Cost

| Service | Plan | Monthly Cost |
|---------|------|-------------|
| Backend | Free (Docker) | $0 |
| Frontend | Free (Docker) | $0 |
| PostgreSQL | Starter | $7 |
| Redis | Upstash Free | $0 |
| Celery Worker | Free (Docker) | $0 |
| **Total** | | **$7/month**

---

## 3. DigitalOcean App Platform

### Step 1: Prepare Your Repository

Push your code to GitHub with this structure:
```
viviz-bulk-sender/
├── backend/
│   ├── Dockerfile.production
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── ...
└── docker-compose.yml
```

### Step 2: Create DigitalOcean App

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Select **GitHub** as source
4. Choose your repository
5. DigitalOcean will auto-detect the services

### Step 3: Configure Backend Service

```yaml
# backend/Dockerfile.production
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

Configure in DigitalOcean:
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Run Command**: `gunicorn --bind 0.0.0.0:8000 config.wsgi:application`
- **HTTP Port**: `8000`

### Step 4: Configure Frontend Service

```yaml
# frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Configure in DigitalOcean:
- **Build Command**: `cd frontend && npm install && npm run build`
- **Run Command**: `npx serve -s dist -l 3000`
- **HTTP Port**: `3000`

### Step 5: Add Database

1. In DigitalOcean dashboard, click **"Add Resource"**
2. Select **"Database"** → **"PostgreSQL"**
2. Select **"Redis"** (for Celery broker)

### Step 6: Configure Environment Variables

Add these in **"Environment Variables"** tab:

**Backend**:
```
DEBUG=0
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
CELERY_BROKER_URL=redis://...
GREEN_API_ID=your-green-api-id
GREEN_API_TOKEN=your-green-api-token
VITE_API_URL=https://your-frontend-app.ondigitalocean.app
```

**Frontend**:
```
VITE_API_URL=https://your-backend-app.ondigitalocean.app
```

### Step 7: Configure Webhooks

In Green API dashboard, set webhook URL to:
```
https://your-backend-app.ondigitalocean.app/api/v1/green-api/webhook/
```

### Step 8: Deploy

1. Review and click **"Launch App"**
2. Wait for build and deployment
3. Run migrations via DigitalOcean console or connect via SSH

---

## 3. Hetzner Cloud

### Step 1: Create Server

1. Sign up at [Hetzner Cloud](https://hetzner.cloud)
2. Create a new project
3. Add a server:
   - **Image**: Ubuntu 22.04
   - **Type**: CX42 (8GB RAM, 4 vCPU) or larger
   - **Location**: Choose nearest to your users
   - **SSH Key**: Add your SSH key

### Step 2: Server Setup

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
apt install -y git

# Install Nginx
apt install -y nginx certbot python3-certbot-nginx
```

### Step 3: Clone and Configure

```bash
# Clone repository
git clone https://github.com/viviztech/viviz-bulk-sender.git
cd viviz-bulk-sender

# Create environment file
cp .env.example .env
nano .env
```

### Step 4: Configure Nginx

```nginx
# /etc/nginx/sites-available/viviz-bulk-sender
server {
    server_name api.viviz.com;

    location / {
        proxy_pass http://localhost:8000;
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

server {
    server_name viviz.com www.viviz.com;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/viviz-bulk-sender /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d viviz.com -d www.viviz.com
certbot --nginx -d api.viviz.com
```

### Step 5: Start Services

```bash
# Start with Docker Compose
docker-compose -f docker-compose.production.yml up -d

# Run migrations
docker-compose -f docker-compose.production.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

### Step 6: Setup Systemd Service (Optional)

```ini
# /etc/systemd/system/viviz.service
[Unit]
Description=Viviz Bulk Sender
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/root/viviz-bulk-sender
ExecStart=/usr/local/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.production.yml down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable viviz
systemctl start viviz
systemctl status viviz
```

---

## 4. AWS Elastic Beanstalk

### Prerequisites

- AWS Account
- AWS CLI installed and configured
- EB CLI installed: `pip install awsebcli`

### Step 1: Create Application Version

```bash
# Initialize EB application
cd viviz-bulk-sender
eb init -p docker viviz-bulk-sender --region us-east-1

# Create environment
eb create production --instance-type t3.medium --key-name your-key-pair
```

### Step 2: Configure Environment

Create `.ebextensions/django.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: config.wsgi:application
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
    /media: media
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.medium
  aws:ec2:instances:
    InstanceTypes: t3.medium
```

### Step 3: Configure Database

1. Go to AWS RDS → Create Database
2. Select PostgreSQL
3. Note the connection endpoint and credentials

### Step 4: Configure Environment Variables

In AWS Elastic Beanstalk console:
- Go to **Configuration** → **Software**
- Add environment variables:
  ```
  DEBUG=0
  SECRET_KEY=your-secret-key
  DATABASE_URL=postgresql://user:password@endpoint:5432/dbname
  REDIS_URL=redis://...
  GREEN_API_ID=...
  GREEN_API_TOKEN=...
  ```

### Step 5: Deploy

```bash
# Deploy updates
eb deploy
```

### Step 6: Configure S3 for Static Files

```python
# config/storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
```

Update settings to use S3 for static/media files.

---

## 5. Google Cloud Run

### Prerequisites

- Google Cloud Account
- gcloud CLI installed

### Step 1: Set Up Project

```bash
# Create project
gcloud projects create viviz-bulk-sender

# Set active project
gcloud config set project viviz-bulk-sender

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Set Up Database

1. Go to Cloud SQL → Create Instance
2. Select PostgreSQL
3. Note the connection string

### Step 3: Build and Deploy Backend

```bash
# Build backend image
cd backend
gcloud builds submit --tag gcr.io/viviz-bulk-sender/backend

# Deploy backend
gcloud run deploy backend \
  --image gcr.io/viviz-bulk-sender/backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEBUG=0,SECRET_KEY=...,DATABASE_URL=...
```

### Step 4: Build and Deploy Frontend

```bash
# Build frontend image
cd frontend
gcloud builds submit --tag gcr.io/viviz-bulk-sender/frontend

# Deploy frontend
gcloud run deploy frontend \
  --image gcr.io/viviz-bulk-sender/frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vires VITE_API_URL=https://backend-url
```

### Step 5: Configure Cloud SQL Connection

```bash
# Deploy with Cloud SQL connector
gcloud run deploy backend \
  --image gcr.io/viviz-bulk-sender/backend \
  --add-cloudsql-instances PROJECT:REGION:INSTANCE \
  --set-env-vars DATABASE_URL=postgresql://user:password@/cloudsql/PROJECT:REGION:INSTANCE/dbname
```

---

## 6. Custom VPS with Nginx

### Step 1: Server Setup

```bash
# SSH into server
ssh root@your-server-ip

# Update and install dependencies
apt update && apt upgrade -y
apt install -y python3-pip python3-venv git nginx

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Step 2: Clone and Setup Virtual Environment

```bash
# Clone repository
git clone https://github.com/viviztech/viviz-bulk-sender.git
cd viviz-bulk-sender/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example ../.env
```

### Step 3: Configure Gunicorn

```ini
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
```

### Step 4: Create Systemd Service

```ini
# /etc/systemd/system/viviz-backend.service
[Unit]
Description=Viviz Bulk Sender Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/viviz-bulk-sender/backend
Environment="PATH=/var/www/viviz-bulk-sender/backend/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=/var/www/viviz-bulk-sender/backend/venv/bin/gunicorn \
  --config gunicorn.conf.py \
  config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
systemctl daemon-reload
systemctl enable viviz-backend
systemctl start viviz-backend
systemctl status viviz-backend
```

### Step 5: Configure Nginx

```nginx
# /etc/nginx/sites-available/viviz
upstream viviz_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    server_name api.viviz.com;

    location / {
        proxy_pass http://viviz_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /var/www/viviz-bulk-sender/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/viviz-bulk-sender/backend/media/;
    }
}

server {
    server_name viviz.com www.viziv.com;

    root /var/www/viviz-bulk-sender/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://viviz_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/viviz /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d viviz.com -d www.viviz.com -d api.viviz.com
```

### Step 6: Setup Redis

```bash
apt install -y redis-server
systemctl enable redis-server
systemctl start redis-server
```

### Step 7: Setup Celery

```ini
# /etc/systemd/system/viviz-celery.service
[Unit]
Description=Viviz Bulk Sender Celery Worker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/viviz-bulk-sender/backend
Environment="PATH=/var/www/viviz-bulk-sender/backend/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=/var/www/viviz-bulk-sender/backend/venv/bin/celery \
  -A config worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/viviz-celerybeat.service
[Unit]
Description=Viviz Bulk Sender Celery Beat
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/viviz-bulk-sender/backend
Environment="PATH=/var/www/viviz-bulk-sender/backend/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=/var/www/viviz-bulk-sender/backend/venv/bin/celery \
  -A config beat --loglevel=info

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable viviz-celery
systemctl enable viviz-celerybeat
systemctl start viviz-celery
systemctl start viviz-celerybeat
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DEBUG` | Yes | Set to `0` for production |
| `SECRET_KEY` | Yes | Django secret key (min 50 chars) |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `CELERY_BROKER_URL` | Yes | Celery broker URL |
| `GREEN_API_ID` | Yes | Green API instance ID |
| `GREEN_API_TOKEN` | Yes | Green API instance token |
| `VITE_API_URL` | Frontend | Backend API URL |
| `JWT_SECRET_KEY` | Yes | JWT signing key |
| `ALLOWED_HOSTS` | Yes | Comma-separated allowed hosts |
| `CORS_ALLOWED_ORIGINS` | Yes | Comma-separated CORS origins |

---

## Security Checklist

- [ ] Use HTTPS in production (SSL/TLS certificate)
- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use environment variables for sensitive data
- [ ] Enable firewall (ufw): `ufw allow 80,443,22`
- [ ] Keep system and dependencies updated
- [ ] Regular backups of database
- [ ] Monitor logs and set up alerts

---

## Monitoring & Logging

### Setup with PM2 (Node) or Supervisor (Python)

```bash
# Install supervisor
apt install -y supervisor

# Create config
cat > /etc/supervisor/conf.d/viviz.conf << EOF
[program:viviz-backend]
command=/var/www/viviz-bulk-sender/backend/venv/bin/gunicorn --config /var/www/viviz-bulk-sender/backend/gunicorn.conf.py config.wsgi:application
directory=/var/www/viviz-bulk-sender/backend
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/viviz/backend.log
stderr_logfile=/var/log/viviz/backend.error.log
EOF

supervisorctl reread
supervisorctl update
```

### Setup Logrotate

```bash
# /etc/logrotate.d/viviz
/var/log/viviz/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart viviz-backend > /dev/null 2>&1 || true
    endscript
}
```

---

## Backup & Restore

### Database Backup

```bash
# PostgreSQL backup
pg_dump -U postgres -Fc viviz_bulk_sender > backup_$(date +%Y%m%d).dump

# Automated daily backup
# Add to crontab: 0 2 * * * /path/to/backup.sh
```

### Restore Database

```bash
# PostgreSQL restore
pg_restore -U postgres -d viviz_bulk_sender backup_20240101.dump
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check backend service status and Nginx logs |
| Database connection error | Verify `DATABASE_URL` and database is running |
| CORS errors | Add frontend URL to `CORS_ALLOWED_ORIGINS` |
| Static files not loading | Run `collectstatic` and check Nginx alias |
| Celery not processing | Check Redis connection and Celery worker logs |
| Memory issues | Increase server RAM or optimize workers |
| SSL certificate error | Renew with `certbot renew` |
