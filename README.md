# 🏆 sPre - Sport Prediction Platform

A comprehensive sport match analysis and prediction system built with Django, Next.js, and Supabase.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-purple.svg)](https://supabase.com/)

## 📋 Project Overview

sPre is a data-driven platform designed to analyze sports matches and predict outcomes using statistical methods and machine learning techniques. The platform provides real-time match data, advanced analytics, and user-friendly predictions.

### ✨ Key Features

- 📊 **Real-time Match Data** - Live updates from external APIs
- 🔮 **Smart Predictions** - ML-powered outcome predictions
- 📈 **Interactive Analytics** - Visual data exploration
- 👤 **User Management** - Secure authentication and profiles
- 🎯 **Confidence Scores** - Prediction reliability metrics
- 🏅 **Multi-Sport Support** - Football, Basketball, Tennis, and more

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.x with Django REST Framework
- **Language**: Python 3.11+
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: JWT + Supabase Auth
- **Real-time**: Supabase Realtime
- **Task Queue**: Celery + Redis (optional)

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **UI Library**: React 18+
- **Styling**: Tailwind CSS
- **State Management**: React Context / Zustand
- **Data Fetching**: SWR / React Query

### Infrastructure
- **Database & Auth**: Supabase
- **Storage**: Supabase Storage
- **Hosting**: Vercel (Frontend) + Heroku/Railway (Backend)
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account
- Git

### 1. Clone Repository

```bash
git clone https://github.com/zaferkucuk/sPre.git
cd sPre
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements/dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Test Supabase connection
python test_supabase_connection.py

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

**Backend will be available at**: http://localhost:8000

### 3. Database Setup

Follow the [Database Setup Guide](./database/SETUP.md) to:
1. Create Supabase project
2. Apply migrations
3. Seed initial data

### 4. Frontend Setup (Coming Soon)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local

# Start development server
npm run dev
```

**Frontend will be available at**: http://localhost:3000

## 📁 Project Structure

```
sPre/
├── backend/                    ✅ COMPLETE
│   ├── apps/
│   │   ├── core/              # Core services & utilities
│   │   ├── matches/           # Matches, teams, leagues API
│   │   ├── users/             # User management
│   │   ├── analytics/         # Analytics engine
│   │   └── datasources/       # External API integrations
│   ├── config/                # Django settings
│   ├── requirements/          # Python dependencies
│   ├── API_GUIDE.md          # Complete API documentation
│   └── SETUP_GUIDE.md        # Detailed setup instructions
│
├── database/                   ✅ COMPLETE
│   ├── migrations/            # Database migrations
│   ├── seed.sql              # Initial data
│   ├── SETUP.md              # Setup guide
│   └── CHECKLIST.md          # Setup checklist
│
├── frontend/                   🚧 IN PROGRESS
│   └── (Next.js to be created)
│
├── docs/                      # Additional documentation
├── PROGRESS.md               # Development progress tracker
└── README.md                 # This file
```

## 📖 Documentation

### Setup & Configuration
- **[Backend Setup Guide](./backend/SETUP_GUIDE.md)** - Complete backend installation
- **[Database Setup](./database/SETUP.md)** - Supabase configuration
- **[Setup Checklist](./database/CHECKLIST.md)** - Quick setup checklist

### API & Development
- **[API Guide](./backend/API_GUIDE.md)** - Complete API documentation
- **[Core Services](./backend/apps/core/README.md)** - Service layer documentation
- **[Progress Tracker](./PROGRESS.md)** - Development status

## 🎯 API Endpoints

### Sports & Leagues
```bash
GET  /api/matches/sports/              # List all sports
GET  /api/matches/sports/{id}/         # Sport details
GET  /api/matches/leagues/             # List leagues
GET  /api/matches/leagues/{id}/        # League details
```

### Teams & Matches
```bash
GET  /api/matches/teams/               # List teams
GET  /api/matches/teams/{id}/          # Team details
GET  /api/matches/teams/{id}/matches/  # Team matches
GET  /api/matches/matches/             # List matches
GET  /api/matches/matches/{id}/        # Match details
```

### Predictions (Auth Required)
```bash
POST /api/matches/predictions/create/  # Create prediction
GET  /api/matches/predictions/         # User predictions
```

### System
```bash
GET  /api/matches/health/              # Health check
```

See [API_GUIDE.md](./backend/API_GUIDE.md) for detailed documentation.

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.core

# With coverage
pytest --cov=apps --cov-report=html
```

### Test Supabase Connection

```bash
cd backend
python test_supabase_connection.py
```

Expected output:
```
✅ Supabase client created successfully!
✅ Found 3 sports
✅ Found 7 leagues
✅ Found teams
✅ Found 5 matches
🎉 All tests passed!
```

## 📊 Development Status

### ✅ Completed (Phase 1)

- [x] Backend architecture with Django + Supabase
- [x] Complete service layer with connection pooling
- [x] 11 REST API endpoints
- [x] Comprehensive error handling
- [x] JWT authentication setup
- [x] Database schema and migrations
- [x] Unit tests for core functionality
- [x] API documentation
- [x] Setup guides

### 🚧 In Progress (Phase 2)

- [ ] Frontend with Next.js
- [ ] Authentication UI
- [ ] Core pages (Dashboard, Matches, Predictions)
- [ ] External data source integration

### 📋 Planned (Phase 3+)

- [ ] ML-based prediction engine
- [ ] Advanced analytics dashboard
- [ ] Real-time match updates
- [ ] Mobile app

See [PROGRESS.md](./PROGRESS.md) for detailed status.

## 🏗️ Architecture

### Backend Architecture

```
┌─────────────────────────────────────┐
│         API Layer (Views)           │
│  - REST endpoints                   │
│  - Request validation               │
│  - Response formatting              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Business Logic (Services)       │
│  - SupabaseService                  │
│  - Data validation                  │
│  - Complex queries                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Data Access (Supabase Client)    │
│  - Connection pooling               │
│  - Query building                   │
│  - Error handling                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Supabase (PostgreSQL)       │
│  - Sports, Leagues, Teams           │
│  - Matches, Predictions             │
│  - Analytics, Statistics            │
└─────────────────────────────────────┘
```

## 🔒 Security

- **Authentication**: JWT tokens with Supabase Auth
- **Authorization**: Row Level Security (RLS) in Supabase
- **Input Validation**: Comprehensive validation at all layers
- **Error Handling**: Sanitized error messages
- **CORS**: Configured for allowed origins only
- **Environment Variables**: Sensitive data in .env files

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 👤 Author

**Zafer Küçük**
- GitHub: [@zaferkucuk](https://github.com/zaferkucuk)
- Project: [sPre](https://github.com/zaferkucuk/sPre)

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - Web framework
- [Supabase](https://supabase.com/) - Backend platform
- [Next.js](https://nextjs.org/) - React framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API toolkit

---

## 📞 Support

For questions or issues:
1. Check the [documentation](./docs/)
2. Search [existing issues](https://github.com/zaferkucuk/sPre/issues)
3. Create a [new issue](https://github.com/zaferkucuk/sPre/issues/new)

---

**Project Status**: Backend Complete ✅ | Frontend In Progress 🚧

Last Updated: October 18, 2025
