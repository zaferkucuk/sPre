# Football-Data.org API Setup Guide

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Football-Data.org API key
# Get your FREE API key at: https://www.football-data.org/client/register
```

### 3. Setup Database Cache Table

```bash
python manage.py createcachetable
```

### 4. Test API Connection

#### Option A: Using Management Command
```bash
python manage.py test_football_api
```

#### Option B: Using Test Script
```bash
python test_api.py
```

#### Option C: Using Django Shell
```bash
python manage.py shell

# In shell:
from apps.matches.services.football_data_org_client import FootballDataOrgClient
client = FootballDataOrgClient()
result = client.test_connection()
print(result)
```

## 📋 Available Leagues (Free Tier)

- **PL** - Premier League (England)
- **PD** - La Liga (Spain)  
- **BL1** - Bundesliga (Germany)
- **SA** - Serie A (Italy)
- **FL1** - Ligue 1 (France)
- **DED** - Eredivisie (Netherlands)
- **PPL** - Primeira Liga (Portugal)
- **ELC** - Championship (England)

## 🔑 API Rate Limits

- **Free Tier**: 10 requests/minute
- **Caching**: Responses cached for 1 hour

## 🎯 Example Usage

```python
from apps.matches.services.football_data_org_client import FootballDataOrgClient

# Initialize client
client = FootballDataOrgClient()

# Get Premier League standings
standings = client.get_standings('PL')
for team in standings[:5]:
    print(f"{team['position']}. {team['team']['name']} - {team['points']} pts")

# Get recent matches
matches = client.get_matches('PL', status='FINISHED')
for match in matches[:5]:
    home = match['homeTeam']['name']
    away = match['awayTeam']['name']
    home_score = match['score']['fullTime']['home']
    away_score = match['score']['fullTime']['away']
    print(f"{home} {home_score} - {away_score} {away}")

# Check API usage
stats = client.get_request_stats()
print(f"Requests: {stats['requests_this_minute']}/{stats['rate_limit']}")
```

## 🐛 Troubleshooting

### ModuleNotFoundError: No module named 'apps'

Make sure you're running commands from the `backend` directory:
```bash
cd backend
python manage.py ...
```

### django.core.exceptions.ImproperlyConfigured: Error loading psycopg2

Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

### Rate Limit Exceeded

Wait 1 minute for the rate limit to reset. The API allows 10 requests per minute on the free tier.

## 📚 Resources

- [Football-Data.org Documentation](https://www.football-data.org/documentation/api)
- [API Registration](https://www.football-data.org/client/register)
- [Available Competitions](https://www.football-data.org/coverage)
