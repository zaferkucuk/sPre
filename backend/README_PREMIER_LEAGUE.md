# 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League Integration - README

## 🎉 Status: MVP Complete!

The Premier League fixtures integration is **fully operational** and ready to use.

---

## ⚡ Quick Start

### 1️⃣ Setup Database
```bash
cd backend
python manage.py migrate
```

### 2️⃣ Fetch Fixtures
```bash
python manage.py fetch_premier_league_fixtures
```

### 3️⃣ Start Server
```bash
python manage.py runserver
```

### 4️⃣ Test Endpoints
```bash
# Get fixtures
curl http://localhost:8000/api/matches/premier-league/fixtures/?limit=10

# Get teams
curl http://localhost:8000/api/matches/premier-league/teams/

# Get stats
curl http://localhost:8000/api/matches/premier-league/stats/
```

### 5️⃣ Run Tests
```bash
python test_premier_league.py
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [**Quick Start Guide**](PREMIER_LEAGUE_QUICKSTART.md) | Step-by-step setup instructions |
| [**Implementation Summary**](IMPLEMENTATION_SUMMARY.md) | Technical architecture & details |
| [**Changelog**](CHANGELOG_PREMIER_LEAGUE.md) | Version history & changes |

---

## 🎯 What's Included

### ✅ Features
- ✨ Fetch Premier League fixtures from API-Football
- ✨ REST API endpoints for fixtures, teams, and statistics
- ✨ Advanced filtering (status, date range, upcoming)
- ✨ Team search functionality
- ✨ Automatic data updates
- ✨ Comprehensive error handling

### 📁 Files Created
```
backend/
├── apps/matches/
│   ├── management/commands/
│   │   └── fetch_premier_league_fixtures.py  # Fetch command
│   ├── views_premier_league.py                # API views
│   └── urls.py                                 # Updated routes
├── PREMIER_LEAGUE_QUICKSTART.md               # User guide
├── IMPLEMENTATION_SUMMARY.md                   # Tech docs
├── CHANGELOG_PREMIER_LEAGUE.md                # Change log
├── test_premier_league.py                      # Test suite
└── README_PREMIER_LEAGUE.md                    # This file
```

---

## 🚀 API Endpoints

### 1. Get Fixtures
```bash
GET /api/matches/premier-league/fixtures/

Parameters:
  - status: scheduled, live, finished
  - limit: 1-200 (default: 50)
  - date_from: YYYY-MM-DD
  - date_to: YYYY-MM-DD
  - upcoming: true/false

Example:
curl "http://localhost:8000/api/matches/premier-league/fixtures/?upcoming=true&limit=10"
```

### 2. Get Teams
```bash
GET /api/matches/premier-league/teams/

Parameters:
  - search: team name

Example:
curl "http://localhost:8000/api/matches/premier-league/teams/?search=Manchester"
```

### 3. Get Statistics
```bash
GET /api/matches/premier-league/stats/

Example:
curl "http://localhost:8000/api/matches/premier-league/stats/"
```

---

## 📊 Example Response

**Fixtures:**
```json
{
  "success": true,
  "count": 10,
  "league": {
    "name": "Premier League",
    "country": "England"
  },
  "data": [
    {
      "id": 1,
      "home_team": {
        "name": "Manchester United",
        "code": "MUN"
      },
      "away_team": {
        "name": "Liverpool",
        "code": "LIV"
      },
      "match_date": "2024-10-25T15:00:00Z",
      "venue": "Old Trafford",
      "status": "scheduled"
    }
  ]
}
```

---

## 🧪 Testing

Run the complete test suite:
```bash
python test_premier_league.py
```

**Test Coverage:**
- ✅ Fixtures list
- ✅ Filtered queries
- ✅ Status filtering
- ✅ Teams list
- ✅ Team search
- ✅ Statistics
- ✅ Error handling

---

## 🔄 Keeping Data Updated

### Manual Update
```bash
python manage.py fetch_premier_league_fixtures
```

### Automated Update (Cron)
```bash
# Add to crontab (daily at 6 AM)
0 6 * * * cd /path/to/sPre/backend && python manage.py fetch_premier_league_fixtures
```

---

## 🐛 Troubleshooting

### Problem: "Premier League not found"
**Solution:** Run the fetch command first:
```bash
python manage.py fetch_premier_league_fixtures
```

### Problem: "No fixtures found"
**Possible causes:**
- API rate limit (100/day on free tier)
- Invalid date range
- No scheduled matches

**Check API status:**
```bash
python manage.py shell
>>> from apps.datasources.fetchers.football_api_fetcher import FootballAPIFetcher
>>> fetcher = FootballAPIFetcher()
>>> leagues = fetcher.fetch_leagues(sport_id=1)
>>> print(f"API working: {len(leagues)} leagues found")
```

---

## 🎯 Next Steps

### Phase 2: Enhanced Backend
- [ ] Match statistics
- [ ] Player data
- [ ] Live score updates
- [ ] Historical analysis

### Phase 3: Frontend
- [ ] Next.js fixture display
- [ ] Match detail pages
- [ ] Team profiles
- [ ] Interactive filters

### Phase 4: Predictions
- [ ] ML-based predictions
- [ ] Form analysis
- [ ] Head-to-head stats

---

## 📖 Additional Resources

- **API-Football Docs:** https://www.api-football.com/documentation-v3
- **Django REST Docs:** https://www.django-rest-framework.org/
- **Project Repo:** https://github.com/zaferkucuk/sPre

---

## 💡 Tips

1. ✅ Run fetch command daily for fresh data
2. ✅ Monitor API quota (100 requests/day)
3. ✅ Use caching to minimize API calls
4. ✅ Check logs for debugging
5. ✅ Start with small date ranges

---

## ✨ Success Checklist

- [x] API key configured
- [x] Database migrated
- [x] Fixtures fetched
- [x] Endpoints tested
- [x] Documentation read
- [ ] Frontend integration
- [ ] Production deployment

---

## 🎊 Congratulations!

Your Premier League fixtures integration is **ready to use**! 🚀

**What you can do now:**
1. ✅ Fetch live fixture data
2. ✅ Query via REST API
3. ✅ Filter and search
4. ✅ Build frontend
5. ✅ Add predictions

---

## 📞 Support

Need help? Check:
1. [Quick Start Guide](PREMIER_LEAGUE_QUICKSTART.md)
2. [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
3. [Changelog](CHANGELOG_PREMIER_LEAGUE.md)
4. Backend logs: `backend/logs/`

---

**Version:** 1.0.0 MVP  
**Status:** ✅ Production Ready  
**Last Updated:** October 23, 2024
