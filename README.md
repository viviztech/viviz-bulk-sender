# Viviz Bulk Sender - WhatsApp Marketing Platform

A comprehensive SaaS platform for bulk WhatsApp messaging with CRM integration, chat inbox, media sharing, message scheduling, and analytics. Built using Django (backend) and React (frontend), integrated with Green API for WhatsApp communication.

## Features

- 📱 **Bulk WhatsApp Messaging** - Send messages to thousands of contacts at once
- 👥 **Contact Management** - CRM with tags, segments, and activity tracking
- 💬 **Chat Inbox** - Real-time messaging with auto-reply capabilities
- 📊 **Analytics Dashboard** - Track message delivery, open rates, and engagement
- 📅 **Message Scheduling** - Schedule campaigns for future delivery
- 🖼️ **Media Sharing** - Send images, videos, documents, and audio
- 💳 **SaaS Billing** - Tiered subscriptions with Stripe integration
- 🔐 **Multi-Tenancy** - Organization-based access control

## Tech Stack

- **Backend**: Django 5.x with Django REST Framework
- **Frontend**: React 18 with TypeScript
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **API**: Green API (Python SDK)
- **Payment**: Stripe
- **Containerization**: Docker

## Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/viviztech/viviz-bulk-sender.git
cd viviz-bulk-sender
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- API Documentation: http://localhost:8000/api/docs/

### Docker Deployment

```bash
cd backend
docker-compose up -d
```

## Project Structure

```
viviz-bulk-sender/
├── backend/
│   ├── apps/
│   │   ├── authentication/  # User auth & JWT tokens
│   │   ├── tenants/         # Multi-tenancy management
│   │   ├── contacts/        # CRM contact management
│   │   ├── campaigns/       # Bulk messaging campaigns
│   │   ├── messages/        # Message sending & scheduling
│   │   ├── chats/           # Chat inbox & auto-reply
│   │   ├── analytics/       # Statistics & reporting
│   │   ├── subscriptions/   # SaaS billing & Stripe
│   │   └── green_api/       # Green API integration
│   └── config/              # Django settings & configuration
├── frontend/
│   └── src/
│       ├── pages/           # React page components
│       ├── components/      # Reusable components
│       ├── context/         # React context providers
│       └── api/             # API configuration
└── plans/                   # Architecture documentation
```

## Deployment

### Railway Deployment

1. **Backend**
```bash
cd backend
railway init
railway up
```

2. **Frontend**
```bash
cd frontend
railway init
railway up
```

See [`backend/env.example`](backend/env.example) and [`frontend/.env.example`](frontend/.env.example) for required environment variables.

## API Documentation

Once the backend is running, visit `/api/schema/` for Swagger documentation or `/api/docs/` for ReDoc.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.
