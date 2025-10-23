# 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League Fixtures - Quick Start Guide

## 📋 Overview

This guide will help you quickly set up and start fetching Premier League fixtures from API-Football.

---

## 🚀 Quick Start

### Step 1: Verify API Key

Check that your Football API key is configured in `.env`:

```bash
cd backend
cat .env | grep API_FOOTBALL_KEY
```

Expected output:
```
API_FOOTBALL_KEY=35fefc7e2a57cd2b9de7cfc330c0177b
FOOTBALL_API_KEY=35fefc7e2a57cd2b9de7cfc330c0177b
```

✅ **API Key is already configured!**

---

### Step 2: Run Database Migrations

```bash
cd backend
python manage.py migrate
```

This will create all necessary database tables.

---

### Step 3: Fetch Premier League Fixtures

Run the management command to fetch fixtures from API-Football:

```bash
# Fetch next 30 days of fixtures (default)
python manage.py fetch_premier_league_fixtures

# Fetch next 60 days of fixtures
python manage.py fetch_premier_league_fixtures --days 60

# Fetch specific date range
python manage.py fetch_premier_league_fixtures --from-date 2024-10-01 --to-date 2024-12-31
```

**Example Output:**
```
============================================================
  Fetching Premier League Fixtures
============================================================
Period: 2024-10-23 to 2024-11-22
Days: 30

Initializing API-Football fetcher...

Step 1: Setting up Premier League...
✓ League ready: Premier League

Step 2: Fetching fixtures from API...
✓ Fetched 38 fixtures

Step 3: Processing fixtures...
  Processing fixture 38/38...

============================================================
  Summary
============================================================
Period: 2024-10-23 to 2024-11-22
Total fixtures fetched: 38
✓ Created: 38
↻ Updated: 0
============================================================

✓ Successfully processed Premier League fixtures!
```

---

## 📡 API Endpoints

Once fixtures are fetched, you can access them via the following endpoints:

### 1. Get Fixtures List

```bash
# Get all Premier League fixtures
GET http://localhost:8000/api/matches/premier-league/fixtures/

# Get upcoming fixtures only
GET http://localhost:8000/api/matches/premier-league/fixtures/?upcoming=true

# Get scheduled fixtures
GET http://localhost:8000/api/matches/premier-league/fixtures/?status=scheduled

# Get fixtures for specific date range
GET http://localhost:8000/api/matches/premier-league/fixtures/?date_from=2024-10-25&date_to=2024-11-01

# Get limited number of fixtures
GET http://localhost:8000/api/matches/premier-league/fixtures/?limit=10
```

**Example Response:**
```json
{
  "success": true,
  "count": 10,
  "total_available": 38,
  "league": {
    "id": 1,
    "name": "Premier League",
    "country": "England",
    "logo_url": "https://...",
    "season": "2024"
  },
  "filters": {
    "status": null,
    "date_from": null,
    "date_to": null,
    "upcoming": false
  },
  "data": [
    {
      "id": 1,
      "external_id": "1234567",
      "home_team": {
        "id": 1,
        "name": "Manchester United",
        "code": "MUN",
        "logo_url": "https://..."
      },
      "away_team": {
        "id": 2,
        "name": "Liverpool",
        "code": "LIV",
        "logo_url": "https://..."
      },
      "match_date": "2024-10-25T15:00:00Z",
      "venue": "Old Trafford",
      "status": "scheduled",
      "home_score": null,
      "away_score": null,
      "round": "Matchweek 9"
    }
  ]
}
```

### 2. Get Teams List

```bash
# Get all Premier League teams
GET http://localhost:8000/api/matches/premier-league/teams/

# Search teams
GET http://localhost:8000/api/matches/premier-league/teams/?search=Manchester
```

### 3. Get Statistics

```bash
# Get Premier League statistics
GET http://localhost:8000/api/matches/premier-league/stats/
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "league": {
      "id": 1,
      "name": "Premier League",
      "country": "England",
      "season": "2024"
    },
    "statistics": {
      "total_teams": 20,
      "total_matches": 380,
      "scheduled_matches": 200,
      "finished_matches": 150,
      "live_matches": 0
    }
  }
}
```

---

## 🧪 Testing with cURL

### Test Fixtures Endpoint

```bash
# Get upcoming fixtures
curl -X GET "http://localhost:8000/api/matches/premier-league/fixtures/?upcoming=true&limit=5"

# Get scheduled fixtures
curl -X GET "http://localhost:8000/api/matches/premier-league/fixtures/?status=scheduled"
```

### Test Teams Endpoint

```bash
# Get all teams
curl -X GET "http://localhost:8000/api/matches/premier-league/teams/"

# Search for Manchester teams
curl -X GET "http://localhost:8000/api/matches/premier-league/teams/?search=Manchester"
```

### Test Statistics Endpoint

```bash
# Get statistics
curl -X GET "http://localhost:8000/api/matches/premier-league/stats/"
```

---

## 🔄 Updating Fixtures

To keep fixtures up-to-date, run the fetch command periodically:

```bash
# Update fixtures daily
python manage.py fetch_premier_league_fixtures
```

**Pro Tip:** You can set up a cron job to run this automatically:

```bash
# Add to crontab (runs daily at 6 AM)
0 6 * * * cd /path/to/sPre/backend && python manage.py fetch_premier_league_fixtures
```

---

## 🐛 Troubleshooting

### Issue: "Premier League not found"

**Solution:** Run the fetch command first:
```bash
python manage.py fetch_premier_league_fixtures
```

### Issue: "No fixtures found"

**Possible causes:**
1. API rate limit reached (100 requests/day on free tier)
2. Invalid API key
3. No fixtures in the specified date range

**Solution:**
- Check API key in `.env`
- Verify date range
- Check API-Football dashboard for rate limits

### Issue: API Errors

**Check API status:**
```bash
python manage.py shell
>>> from apps.datasources.fetchers.football_api_fetcher import FootballAPIFetcher
>>> fetcher = FootballAPIFetcher()
>>> # Test API connection
>>> leagues = fetcher.fetch_leagues(sport_id=1)
>>> print(f"Found {len(leagues)} leagues")
```

---

## 📊 Query Parameters Reference

### Fixtures Endpoint

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by match status | `?status=scheduled` |
| `limit` | integer | Max results (1-200) | `?limit=20` |
| `date_from` | string (YYYY-MM-DD) | Start date | `?date_from=2024-10-25` |
| `date_to` | string (YYYY-MM-DD) | End date | `?date_to=2024-11-01` |
| `upcoming` | boolean | Only upcoming matches | `?upcoming=true` |

### Valid Status Values

- `scheduled` - Match not started yet
- `live` - Match in progress
- `finished` - Match completed

---

## 📝 Next Steps

1. ✅ **Backend is ready** - API endpoints are working
2. 🔄 **Next: Frontend** - Create Next.js pages to display fixtures
3. 📈 **Next: Analytics** - Add match statistics and predictions

---

## 🆘 Need Help?

- Check API documentation: https://www.api-football.com/documentation-v3
- Review logs: `backend/logs/`
- Contact: [Your contact info]

---

**Happy Coding! ⚽️**
