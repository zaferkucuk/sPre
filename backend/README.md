# sPre Backend

Django REST API for sPre (Sport Prediction) platform.

## 🛠️ Tech Stack

- **Framework**: Django 5.0
- **API**: Django REST Framework
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: JWT (Simple JWT)
- **Language**: Python 3.11+

## 📁 Project Structure

```
backend/
├── config/                    # Django project configuration
│   ├── settings/
│   │   ├── base.py           # Base settings
│   │   ├── development.py    # Development settings
│   │   └── production.py     # Production settings
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI config
│   └── asgi.py               # ASGI config
│
├── apps/                      # Django applications
│   ├── users/                # User management & auth
│   ├── matches/              # Match data & predictions
│   ├── analytics/            # Data analysis & ML
│   └── datasources/          # External API integrations
│
├── requirements/              # Python dependencies
│   ├── base.txt              # Common dependencies
│   ├── dev.txt               # Development dependencies
│   └── prod.txt              # Production dependencies
│
└── manage.py                  # Django management script
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ (or Supabase account)
- pip and virtualenv

### Installation

1. **Create a virtual environment**:
```bash
python -m venv venv
```

2. **Activate the virtual environment**:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**:
```bash
# For development
pip install -r requirements/dev.txt

# For production
pip install -r requirements/prod.txt
```

4. **Configure environment variables**:
```bash
# Copy the example env file
cp ../.env.example .env

# Edit .env with your configuration
```

5. **Run migrations**:
```bash
python manage.py migrate
```

6. **Create a superuser**:
```bash
python manage.py createsuperuser
```

7. **Run the development server**:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 🔧 Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Supabase)
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# External API Keys
FOOTBALL_API_KEY=your-football-api-key
ODDS_API_KEY=your-odds-api-key

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 📚 API Documentation

### Authentication Endpoints

- **POST** `/api/auth/token/` - Obtain JWT token
- **POST** `/api/auth/token/refresh/` - Refresh JWT token
- **POST** `/api/auth/token/verify/` - Verify JWT token

### API Endpoints (Coming Soon)

- `/api/users/` - User management
- `/api/matches/` - Match data
- `/api/analytics/` - Analytics and predictions
- `/api/datasources/` - External data sources

## 🧪 Testing

Run tests with:
```bash
pytest
```

With coverage:
```bash
pytest --cov=apps
```

## 📝 Code Quality

Format code with Black:
```bash
black .
```

Sort imports with isort:
```bash
isort .
```

Lint with flake8:
```bash
flake8 .
```

Type checking with mypy:
```bash
mypy .
```

## 🐳 Docker (Optional)

Coming soon...

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Zafer Küçük - [@zaferkucuk](https://github.com/zaferkucuk)

---

For more information, see the main [project README](../README.md).
