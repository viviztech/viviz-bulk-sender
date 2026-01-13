# Railway Deployment Guide for Viviz Bulk Sender

This guide provides step-by-step instructions for deploying the Viviz Bulk Sender SaaS platform on Railway.

## Prerequisites

- **GitHub Account** with repository access
- **Railway Account** (sign up at https://railway.app)
- **Green API Account** (https://greenapi.com)
- **Stripe Account** (for payment processing - optional)

## Architecture Overview

Railway will host:
1. **Backend** - Django API with PostgreSQL database, Redis cache
2. **Frontend** - React application
3. **PostgreSQL** - Primary database (managed by Railway)
4. **Redis** - Celery broker and caching (managed by Railway)

---

## Step 1: Prepare Your Repository

### 1.1 Push Code to GitHub

```bash
cd /Users/ganeshthangavel/Sites/viviz-bulk-sender
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 1.2 Verify File Structure

Ensure these files exist in your repository:
```
viviz-bulk-sender/
├── backend/
│   ├── Dockerfile.production
│   ├── railway.json
│   ├── requirements.txt
│   └── gunicorn.conf.py
├── frontend/
│   ├── Dockerfile
│   ├── railway.json
│   ├── package.json
│   └── vite.config.ts
├── railway.json (root)
└── docker-compose.yml (optional for local testing)
```

---

## Step 2: Set Up Railway Project

### 2.1 Create New Railway Project

1. Go to https://railway.app and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `viviztech/viviz-bulk-sender`
5. Click **"Deploy Now"**

### 2.2 Configure Backend Service

1. In Railway dashboard, find the backend service
2. Click **"Settings"** tab
3. Configure:

**Service Name**: `viviz-backend`

**Build Command**:
```bash
cd backend && pip install -r requirements.txt
```

**Start Command**:
```bash
cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --config gunicorn.conf.py
```

**Root Directory**: `backend`

### 2.3 Configure Frontend Service

1. Click **"New Service"** → **"Deploy from GitHub"**
2. Select same repository
3. Configure:

**Service Name**: `viviz-frontend`

**Build Command**:
```bash
cd frontend && npm install && npm run build
```

**Start Command**:
```bash
npx serve -s dist -l $PORT
```

**Root Directory**: `frontend`

---

## Step 3: Set Up Database Services

### 3.1 PostgreSQL Database

1. Click **"New Service"** → **"Database"** → **"PostgreSQL"**
2. Railway will create and attach a PostgreSQL instance
3. Note the **DATABASE_URL** - this will be auto-injected as environment variable

### 3.2 Redis Database

1. Click **"New Service"** → **"Database"** → **"Redis"**
2. Railway will create and attach a Redis instance
3. Note the **REDIS_URL** - this will be auto-injected

---

## Step 4: Configure Environment Variables

### 4.1 Backend Environment Variables

Go to Backend service → **Variables** tab and add:

```env
# Django Settings
DEBUG=0
SECRET_KEY=your-super-secret-key-here (generate: python -c "import secrets; print(secrets.token_hex(50))")

# Database (auto-filled by Railway)
DATABASE_URL=postgresql://user:password@hostname:5432/dbname

# Redis (auto-filled by Railway)
REDIS_URL=redis://:password@hostname:6379/0
CELERY_BROKER_URL=redis://:password@hostname:6379/0

# Green API Configuration
GREEN_API_ID=your-green-api-id
GREEN_API_TOKEN=your-green-api-token
GREEN_API_URL=https://api.green-api.com

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS Settings
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.up.railway.app

# Email Settings (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe (optional - for payments)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Domain (optional)
ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
```

### 4.2 Frontend Environment Variables

Go to Frontend service → **Variables** tab and add:

```env
VITE_API_URL=https://your-backend-service.up.railway.app/api/v1
VITE_WS_URL=wss://your-backend-service.up.railway.app/ws
VITE_GREEN_API_URL=https://api.green-api.com
```

---

## Step 5: Configure Green API Webhooks

### 5.1 Get Railway Backend URL

1. Go to Backend service → **Deployments**
2. Copy the **Production URL** (e.g., `https://viviz-backend.up.railway.app`)

### 5.2 Set Green API Webhook URL

In Green API dashboard, set webhook URL to:
```
https://your-backend-url/api/v1/green-api/webhook/
```

### 5.3 Configure Green API Instance

Make sure your Green API instance has:
- **Webhook enabled**: Yes
- **Webhook URL**: Set above
- **Incoming message webhook**: Enabled
- **Outgoing message webhook**: Enabled

---

## Step 6: Run Database Migrations

### 6.1 Using Railway CLI

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Link to project
cd /Users/ganeshthangavel/Sites/viviz-bulk-sender
railway link

# Run migrations
railway run --service viviz-backend python manage.py migrate

# Create superuser
railway run --service viviz-backend python manage.py createsuperuser
```

### 6.2 Using Railway Dashboard

1. Go to Backend service → **Deployments**
2. Click **"Run Command"**
3. Execute:
   ```bash
   python manage.py migrate
   ```
4. After success, run:
   ```bash
   python manage.py createsuperuser
   ```

---

## Step 7: Connect Frontend to Backend

### 7.1 Update Frontend Environment Variable

1. Go to Frontend service → **Variables**
2. Update `VITE_API_URL` with actual backend URL:
   ```
   VITE_API_URL=https://viviz-backend.up.railway.app/api/v1
   ```

### 7.2 Redeploy Frontend

1. Go to Frontend service → **Deployments**
2. Click **"Deploy"** to rebuild with new environment variable

---

## Step 8: Configure Custom Domain (Optional)

### 8.1 Add Domain in Railway

1. Go to Project → **Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your custom domain (e.g., `app.viviz.com`)
4. Configure DNS as instructed by Railway

### 8.2 Update Django Settings

Add to Backend environment variables:
```env
ALLOWED_HOSTS=app.viviz.com,.railway.app,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://app.viviz.com
```

### 8.3 Update CORS Settings

```env
CORS_ALLOWED_ORIGINS=https://app.viviz.com
```

---

## Step 9: Set Up Celery Worker

### 9.1 Create Celery Service

1. Click **"New Service"** → **"Deploy from GitHub"**
2. Select same repository
3. Configure:

**Service Name**: `viviz-celery`

**Build Command**:
```bash
cd backend && pip install -r requirements.txt
```

**Start Command**:
```bash
cd backend && celery -A config worker --loglevel=info
```

**Root Directory**: `backend`

**Environment Variables**: Same as backend (DATABASE_URL, REDIS_URL, etc.)

### 9.2 Set Cron Tasks (Optional)

For scheduled tasks, add a beat service:
```bash
celery -A config beat --loglevel=info
```

Create a separate service for beat or combine in one command:
```bash
celery -A config worker --loglevel=info --beat
```

---

## Step 10: Monitor and Debug

### 10.1 View Logs

1. Go to any service → **Logs** tab
2. View real-time logs for debugging

### 10.2 Check Deployment Status

1. Go to Project → **Deployments**
2. View status of all services (Building, Deploying, Deployed)

### 10.3 Common Issues

**Database Connection Error**:
- Verify `DATABASE_URL` is set correctly
- Ensure migrations ran successfully

**CORS Error**:
- Check `CORS_ALLOWED_ORIGINS` includes frontend URL
- Verify `ALLOWED_HOSTS` includes backend URL

**Static Files Not Loading**:
- Run `python manage.py collectstatic` in backend
- Configure WhiteNoise or use S3 for static files

**Celery Not Processing**:
- Verify Redis service is running
- Check CELERY_BROKER_URL is correct
- Check Celery worker logs

---

## Step 11: Set Up Stripe Webhooks (Optional)

### 11.1 Get Webhook Endpoint

Your Stripe webhook URL will be:
```
https://your-backend-url/api/v1/subscriptions/webhook/
```

### 11.2 Configure in Stripe Dashboard

1. Go to Stripe Dashboard → **Developers** → **Webhooks**
2. Add endpoint URL above
3. Select events: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`
4. Copy webhook signing secret

### 11.3 Add to Environment Variables

```env
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

---

## Step 12: Production Checklist

- [ ] All services deployed and running
- [ ] Database migrations completed
- [ ] Superuser created
- [ ] Green API webhooks configured
- [ ] Environment variables set for all services
- [ ] Custom domain configured (optional)
- [ ] SSL certificate auto-generated by Railway
- [ ] Logs showing no errors
- [ ] Frontend can communicate with backend
- [ ] Test sending a WhatsApp message
- [ ] Set up monitoring and alerts

---

## Quick Reference: Service URLs

After deployment, you'll have:

| Service | URL |
|---------|-----|
| Backend API | https://viviz-backend.up.railway.app |
| API Docs | https://viviz-backend.up.railway.app/api/v1/schema/swagger/ |
| Admin Panel | https://viviz-backend.up.railway.app/admin/ |
| Frontend | https://viviz-frontend.up.railway.app |

---

## Scaling Options

### Vertical Scaling (More Resources)
1. Go to Service → **Settings** → **Resources**
2. Increase **Plan** (e.g., from Hobby to Professional)
3. More CPU and RAM available

### Horizontal Scaling (Multiple Replicas)
1. Go to Service → **Settings**
2. Enable **Scale from 0** or set min/max replicas
3. Railway will auto-scale based on load

### Add Redis for Caching
1. Use existing Redis service
2. Configure Django cache in settings:
```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL"),
    }
}
```

---

## Rollback Procedure

1. Go to Project → **Deployments**
2. Find previous working deployment
3. Click **"Rollback"** button
4. Confirm rollback

---

## Support

- **Railway Docs**: https://docs.railway.app
- **Green API Docs**: https://greenapi.com/en/docs/
- **Django Docs**: https://docs.djangoproject.com
- **Railway Community**: https://discord.gg/railway
