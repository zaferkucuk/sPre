# 🚀 sPre Backend Setup Guide

Complete setup guide for the sPre backend with Django and Supabase.

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- PostgreSQL (for local development, optional)
- Supabase account
- Git

## 🔧 Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/zaferkucuk/sPre.git
cd sPre/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Development environment
pip install -r requirements/dev.txt

# Production environment
pip install -r requirements/prod.txt
```

### 4. Setup Supabase

Follow the [Database Setup Guide](../database/SETUP.md) to:

1. Create Supabase project
2. Apply database migrations
3. Seed initial data
4. Get API keys

### 5. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Supabase)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ALGORITHM=HS256

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# External APIs (optional)
FOOTBALL_API_KEY=your-football-api-key
ODDS_API_KEY=your-odds-api-key

# Logging
LOG_LEVEL=INFO
```

### 6. Run Database Migrations

```bash
# Django migrations (creates auth tables)
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 8. Test Supabase Connection

```bash
python test_supabase_connection.py
```

Expected output:
```
✅ Supabase client created successfully!
✅ Found 3 sports
✅ Found 7 leagues
✅ Found teams
✅ Found 5 matches
✅ RLS is configured
🎉 All tests passed!
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Server will start at `http://localhost:8000`

### 10. Verify Installation

Open browser and visit:

- API Root: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/
- Health Check: http://localhost:8000/api/matches/health/
- API Docs: http://localhost:8000/api/docs/ (if configured)

## 🧪 Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.core

# With coverage
pytest --cov=apps

# Generate coverage report
pytest --cov=apps --cov-report=html
```

## 🔍 Project Structure

```
backend/
├── apps/
│   ├── core/              # Core utilities and services
│   │   ├── services/
│   │   │   ├── supabase_client.py
│   │   │   └── supabase_service.py
│   │   ├── exceptions.py
│   │   ├── decorators.py
│   │   └── tests.py
│   ├── users/             # User management
│   ├── matches/           # Matches, teams, leagues
│   ├── analytics/         # Analytics and statistics
│   └── datasources/       # External data sources
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── logs/                  # Application logs
├── .env                   # Environment variables
├── manage.py
└── test_supabase_connection.py
```

## 🐳 Docker Setup (Optional)

```bash
# Build image
docker build -t spre-backend .

# Run container
docker run -p 8000:8000 --env-file .env spre-backend

# With docker-compose
docker-compose up
```

## 🌍 Environment-Specific Setup

### Development

```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py runserver
```

### Production

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 🔐 Security Checklist

### Development

- [x] DEBUG=True is acceptable
- [x] Using development server is acceptable
- [x] Simple SECRET_KEY is acceptable

### Production

- [ ] Set DEBUG=False
- [ ] Use strong SECRET_KEY (generate new)
- [ ] Configure ALLOWED_HOSTS
- [ ] Use HTTPS only
- [ ] Set secure cookie settings
- [ ] Enable CSRF protection
- [ ] Configure CORS properly
- [ ] Use environment variables
- [ ] Enable logging
- [ ] Set up monitoring

## 📊 Database Management

### Apply Migrations

```bash
python manage.py migrate
```

### Create New Migration

```bash
python manage.py makemigrations
```

### Database Shell

```bash
# Django shell
python manage.py shell

# Direct database shell
python manage.py dbshell
```

### Backup Database

```bash
# From Supabase dashboard
# Settings > Database > Backups

# Or using pg_dump
pg_dump DATABASE_URL > backup.sql
```

## 🛠️ Development Tools

### Django Extensions

```bash
# Shell with auto-import
python manage.py shell_plus

# Show URLs
python manage.py show_urls

# Generate secret key
python manage.py generate_secret_key
```

### Django Debug Toolbar

Access at: http://localhost:8000/__debug__/

### API Testing

```bash
# Using httpie
http GET http://localhost:8000/api/matches/sports/

# Using curl
curl http://localhost:8000/api/matches/sports/
```

## 🐛 Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements/dev.txt --force-reinstall
```

### Database Connection Errors

```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
python test_supabase_connection.py
```

### Migration Errors

```bash
# Reset migrations (careful!)
python manage.py migrate --fake-initial

# Or start fresh
python manage.py migrate --run-syncdb
```

### Port Already in Use

```bash
# Use different port
python manage.py runserver 8001

# Or kill process on port 8000
# On Linux/Mac:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## 📝 Common Commands

```bash
# Start server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Shell
python manage.py shell
```

## 🚀 Deployment

### Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create spre-backend

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
```

### AWS/DigitalOcean

See deployment documentation for platform-specific instructions.

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Supabase Documentation](https://supabase.com/docs)
- [API Guide](./API_GUIDE.md)
- [Core Services Documentation](./apps/core/README.md)

## 💡 Tips

1. **Use virtual environment** - Always activate before working
2. **Keep .env secure** - Never commit to git
3. **Run tests** - Before committing changes
4. **Check logs** - In `backend/logs/` directory
5. **Use Django admin** - For quick data management
6. **Monitor Supabase** - Check dashboard for performance
7. **Update dependencies** - Regularly check for updates

## 🆘 Getting Help

- Check documentation
- Search existing issues on GitHub
- Create new issue with detailed information
- Contact maintainers

## ✅ Post-Setup Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Supabase project created
- [ ] Database migrations applied
- [ ] .env file configured
- [ ] Superuser created
- [ ] Connection test passed
- [ ] Development server running
- [ ] Health check passing
- [ ] Admin panel accessible
- [ ] API endpoints working
