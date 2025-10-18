# 📡 External Data Sources Integration

Complete documentation for external data integration system.

## 🎯 Overview

The datasources module provides a comprehensive system for fetching, normalizing, and synchronizing sports data from external APIs to the Supabase database.

### Key Features

- ✅ **Multiple Data Sources** - Extensible fetcher architecture
- ✅ **Rate Limiting** - Automatic API rate limit compliance
- ✅ **Caching** - Smart caching to minimize API calls
- ✅ **Data Normalization** - Transform external data to database schema
- ✅ **Error Handling** - Robust error handling with retries
- ✅ **Sync Tracking** - Complete audit trail of sync operations
- ✅ **CLI Commands** - Easy management commands
- ✅ **API Endpoints** - RESTful sync triggers

## 📁 Architecture

```
apps/datasources/
├── fetchers/                  # Data fetchers
│   ├── base_fetcher.py       # Abstract base class
│   └── football_api_fetcher.py  # Football API implementation
├── normalizers/               # Data normalizers
│   ├── base_normalizer.py    # Abstract base class
│   └── football_normalizer.py   # Football data normalizer
├── management/commands/       # Django commands
│   └── sync_data.py          # Sync command
├── sync_service.py           # Main sync service
├── views.py                  # API endpoints
└── urls.py                   # URL routing
```

## 🔧 Components

### 1. Base Fetcher

Abstract base class providing:
- HTTP request handling
- Rate limiting
- Caching
- Error handling
- Retry logic

```python
from apps.datasources.fetchers import BaseFetcher

class MyFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            name="MyAPI",
            base_url="https://api.example.com",
            rate_limit_calls=100,
            rate_limit_period=60
        )
```

### 2. Football API Fetcher

Implementation for API-Football (RapidAPI):
- Fetch leagues and competitions
- Fetch teams and squads
- Fetch fixtures (matches)
- Fetch match statistics

```python
from apps.datasources.fetchers import FootballAPIFetcher

fetcher = FootballAPIFetcher(api_key="your-key")
leagues = fetcher.fetch_leagues(sport_id=1)
teams = fetcher.fetch_teams(league_id=39)  # Premier League
matches = fetcher.fetch_matches(league_id=39)
```

### 3. Data Normalizers

Transform external API data to database schema:

```python
from apps.datasources.normalizers import FootballNormalizer

normalizer = FootballNormalizer()

# Normalize league data
normalized_league = normalizer.normalize_league(raw_api_data)

# Normalize team data
normalized_team = normalizer.normalize_team(raw_api_data, league_id=1)

# Normalize match data
normalized_match = normalizer.normalize_match(
    raw_api_data,
    league_id=1,
    home_team_id=1,
    away_team_id=2
)
```

### 4. Sync Service

Coordinates the entire synchronization process:

```python
from apps.datasources.sync_service import DataSyncService

sync_service = DataSyncService()

# Sync leagues
result = sync_service.sync_leagues(sport_id=1)

# Sync teams
result = sync_service.sync_teams(league_external_id="39")

# Sync matches
result = sync_service.sync_matches(
    league_external_id="39",
    days_ahead=30
)

# Full sync (teams + matches)
results = sync_service.full_sync(league_external_id="39")

# Cleanup
sync_service.cleanup()
```

## 🖥️ Management Commands

### Sync Data Command

```bash
# Sync all leagues
python manage.py sync_data --type leagues

# Sync teams for Premier League (ID: 39)
python manage.py sync_data --type teams --league 39

# Sync matches for next 7 days
python manage.py sync_data --type matches --league 39 --days 7

# Full sync (teams + matches)
python manage.py sync_data --type full --league 39
```

### Command Options

- `--type` : Type of sync (leagues, teams, matches, full)
- `--league` : League external ID
- `--sport` : Sport ID (default: 1)
- `--days` : Number of days ahead for matches (default: 30)

## 🌐 API Endpoints

### Sync Leagues

```bash
POST /api/datasources/sync/leagues/
Authorization: Bearer {admin_token}

{
  "sport_id": 1
}
```

### Sync Teams

```bash
POST /api/datasources/sync/teams/
Authorization: Bearer {admin_token}

{
  "league_external_id": "39",
  "sport_id": 1
}
```

### Sync Matches

```bash
POST /api/datasources/sync/matches/
Authorization: Bearer {admin_token}

{
  "league_external_id": "39",
  "days_ahead": 30,
  "sport_id": 1
}
```

### Full Sync

```bash
POST /api/datasources/sync/full/
Authorization: Bearer {admin_token}

{
  "league_external_id": "39"
}
```

### Get Sync Status

```bash
GET /api/datasources/sync/status/
Authorization: Bearer {token}

# Optional query parameter
?data_type=matches
```

## 🔑 Configuration

### Environment Variables

```bash
# Football API Key (API-Football from RapidAPI)
FOOTBALL_API_KEY=your-api-key-here

# Optional: Other API keys
ODDS_API_KEY=your-odds-api-key
```

### API-Football Setup

1. Sign up at https://www.api-football.com/
2. Subscribe to a plan (Free tier: 100 requests/day)
3. Get your API key from RapidAPI
4. Add to `.env` file

### League IDs

Common league IDs for API-Football:

| League | ID |
|--------|-----|
| Premier League | 39 |
| La Liga | 140 |
| Bundesliga | 78 |
| Serie A | 135 |
| Ligue 1 | 61 |
| Champions League | 2 |
| Europa League | 3 |

## 📊 Data Flow

```
External API (API-Football)
         ↓
    Fetcher (with rate limiting & caching)
         ↓
    Normalizer (transform to our schema)
         ↓
    Sync Service (CRUD operations)
         ↓
    Supabase Database
         ↓
    Sync Logs (audit trail)
```

## 🛡️ Error Handling

### Rate Limiting

Automatic rate limit enforcement:

```python
# Configured per fetcher
rate_limit_calls = 100  # Max calls
rate_limit_period = 86400  # Per 24 hours

# Raises RateLimitExceededError when exceeded
```

### Retry Logic

Automatic retries for transient failures:

```python
@retry_on_failure(max_attempts=3, delay=2.0)
def _make_request(self, endpoint, params):
    # Will retry up to 3 times with 2 second delay
    pass
```

### Error Responses

```json
{
  "success": false,
  "created": 0,
  "updated": 5,
  "errors": 2,
  "error_messages": [
    "Error processing team: Invalid data format",
    "Error processing league: Connection timeout"
  ]
}
```

## 📈 Performance

### Caching Strategy

- **Leagues**: 24 hours
- **Teams**: 24 hours
- **Matches**: 1 hour
- **Match Details**: 30 minutes

### Rate Limiting

- Football API Free Tier: 100 requests/day
- Cached requests don't count toward limit
- Smart batching reduces API calls

## 🧪 Testing

### Unit Tests

```bash
# Test fetchers
python manage.py test apps.datasources.tests.FetcherTests

# Test normalizers
python manage.py test apps.datasources.tests.NormalizerTests

# Test sync service
python manage.py test apps.datasources.tests.SyncServiceTests
```

### Manual Testing

```python
# Test fetcher
from apps.datasources.fetchers import FootballAPIFetcher

fetcher = FootballAPIFetcher()
leagues = fetcher.fetch_leagues(sport_id=1)
print(f"Found {len(leagues)} leagues")

# Test normalizer
from apps.datasources.normalizers import FootballNormalizer

normalizer = FootballNormalizer()
normalized = normalizer.normalize_league(leagues[0])
print(normalized)

# Test sync
from apps.datasources.sync_service import DataSyncService

sync = DataSyncService()
result = sync.sync_leagues()
print(result)
```

## 📝 Best Practices

### 1. Check Rate Limits

Always monitor your API usage:

```python
# Check sync status
result = sync_service.get_sync_status(data_type='matches')
print(f"Last sync: {result[0]['synced_at']}")
```

### 2. Use Caching

Leverage caching to minimize API calls:

```python
# Cache is automatic, but you can force refresh
cache.delete(f"FootballAPI:leagues:1")
```

### 3. Handle Errors Gracefully

```python
try:
    result = sync_service.sync_teams(league_external_id="39")
    if not result['success']:
        logger.warning(f"Sync completed with {result['errors']} errors")
except Exception as e:
    logger.error(f"Sync failed: {str(e)}")
```

### 4. Schedule Regular Syncs

Use Celery or cron for scheduled syncs:

```bash
# Crontab example
0 */6 * * * cd /path/to/project && python manage.py sync_data --type matches --league 39
```

## 🔮 Future Enhancements

- [ ] Additional data sources (Odds API, Stats API)
- [ ] Real-time data updates via webhooks
- [ ] Advanced conflict resolution
- [ ] Data quality monitoring
- [ ] Automated sync scheduling
- [ ] Performance analytics dashboard

## 🐛 Troubleshooting

### Rate Limit Exceeded

```
Error: Rate limit exceeded for FootballAPI
```

**Solution**: Wait for rate limit to reset or upgrade API plan

### Connection Timeout

```
Error: Request to FootballAPI timed out after 30s
```

**Solution**: Check internet connection or increase timeout

### Invalid API Key

```
Error: HTTP error from FootballAPI: 401 Unauthorized
```

**Solution**: Verify FOOTBALL_API_KEY in .env file

### Data Not Syncing

1. Check sync logs: `GET /api/datasources/sync/status/`
2. Review error messages in response
3. Check database constraints
4. Verify league/team IDs exist

## 📚 Additional Resources

- [API-Football Documentation](https://www.api-football.com/documentation-v3)
- [Supabase Documentation](https://supabase.com/docs)
- [Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)

---

**Last Updated**: October 18, 2025
