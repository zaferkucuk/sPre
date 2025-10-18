# 📚 sPre API Guide

Comprehensive guide for using the sPre Backend API with Supabase integration.

## 🚀 Quick Start

### Base URL

```
Development: http://localhost:8000/api/matches/
Production: https://your-domain.com/api/matches/
```

### Authentication

Most endpoints require JWT authentication:

```bash
# Get access token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl http://localhost:8000/api/matches/predictions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🏆 Sports Endpoints

### List All Sports

Get all available sports.

**Endpoint:** `GET /api/matches/sports/`

**Authentication:** Not required

**Query Parameters:**
- `active_only` (boolean, default: true) - Filter by active status

**Example Request:**

```bash
curl http://localhost:8000/api/matches/sports/
```

**Example Response:**

```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": 1,
      "name": "Football",
      "slug": "football",
      "description": "Association football / Soccer",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Sport Details

**Endpoint:** `GET /api/matches/sports/{id}/`

**Authentication:** Not required

## 🏆 Leagues Endpoints

### List Leagues

**Endpoint:** `GET /api/matches/leagues/`

**Query Parameters:**
- `sport_id` (integer) - Filter by sport ID
- `active_only` (boolean, default: true)

### Get League Details

**Endpoint:** `GET /api/matches/leagues/{id}/`

## 👥 Teams Endpoints

### List Teams

**Endpoint:** `GET /api/matches/teams/`

**Query Parameters:**
- `league_id` (integer) - Filter by league
- `search` (string) - Search teams by name

### Get Team Details

**Endpoint:** `GET /api/matches/teams/{id}/`

### Get Team Matches

**Endpoint:** `GET /api/matches/teams/{id}/matches/`

**Query Parameters:**
- `status` (string) - `scheduled`, `live`, `finished`
- `limit` (integer, default: 20)

## ⚽ Matches Endpoints

### List Upcoming Matches

**Endpoint:** `GET /api/matches/matches/`

**Query Parameters:**
- `sport_id` (integer)
- `league_id` (integer)
- `limit` (integer, default: 50)

**Example Request:**

```bash
curl http://localhost:8000/api/matches/matches/?sport_id=1&limit=20
```

**Example Response:**

```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": 1,
      "home_team": {
        "id": 1,
        "name": "Manchester United",
        "logo_url": "https://example.com/logo.png"
      },
      "away_team": {
        "id": 2,
        "name": "Liverpool",
        "logo_url": "https://example.com/logo.png"
      },
      "league": {
        "id": 1,
        "name": "Premier League"
      },
      "match_date": "2024-10-25T15:00:00Z",
      "venue": "Old Trafford",
      "status": "scheduled"
    }
  ]
}
```

### Get Match Details

**Endpoint:** `GET /api/matches/matches/{id}/`

**Example Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "home_team": {
      "id": 1,
      "name": "Manchester United",
      "code": "MUN",
      "logo_url": "https://example.com/logo.png",
      "league": {
        "id": 1,
        "name": "Premier League"
      }
    },
    "away_team": {
      "id": 2,
      "name": "Liverpool",
      "code": "LIV"
    },
    "league": {
      "id": 1,
      "name": "Premier League",
      "country": "England"
    },
    "match_date": "2024-10-25T15:00:00Z",
    "venue": "Old Trafford",
    "status": "scheduled",
    "home_score": null,
    "away_score": null,
    "external_id": "ext-12345"
  }
}
```

## 🎯 Predictions Endpoints

### Create Prediction

**Endpoint:** `POST /api/matches/predictions/create/`

**Authentication:** Required

**Request Body:**

```json
{
  "match_id": 1,
  "predicted_winner": "home",
  "confidence_score": 0.85,
  "notes": "Strong home form, key away players injured"
}
```

**Field Validation:**
- `predicted_winner`: Must be `"home"`, `"away"`, or `"draw"`
- `confidence_score`: Must be between 0 and 1
- `notes`: Optional

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/matches/predictions/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": 1,
    "predicted_winner": "home",
    "confidence_score": 0.85,
    "notes": "Strong home form"
  }'
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "id": 123,
    "user_id": "user-456",
    "match_id": 1,
    "predicted_winner": "home",
    "confidence_score": 0.85,
    "notes": "Strong home form",
    "created_at": "2024-10-18T12:00:00Z"
  }
}
```

### List User Predictions

**Endpoint:** `GET /api/matches/predictions/`

**Authentication:** Required

**Query Parameters:**
- `match_id` (integer) - Filter by specific match

**Example Request:**

```bash
curl http://localhost:8000/api/matches/predictions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Example Response:**

```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "id": 123,
      "match": {
        "id": 1,
        "home_team": {"name": "Manchester United"},
        "away_team": {"name": "Liverpool"},
        "match_date": "2024-10-25T15:00:00Z"
      },
      "predicted_winner": "home",
      "confidence_score": 0.85,
      "notes": "Strong home form",
      "created_at": "2024-10-18T12:00:00Z"
    }
  ]
}
```

## 🏥 Health Check

### Check Service Health

**Endpoint:** `GET /api/matches/health/`

**Authentication:** Not required

**Example Request:**

```bash
curl http://localhost:8000/api/matches/health/
```

**Example Response (Healthy):**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "supabase",
    "timestamp": "2024-10-18T12:00:00Z"
  }
}
```

**Example Response (Unhealthy):**

```json
{
  "success": false,
  "data": {
    "status": "unhealthy",
    "service": "supabase",
    "timestamp": "2024-10-18T12:00:00Z"
  }
}
```

## 🚨 Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### Common Error Examples

**404 Not Found:**

```json
{
  "success": false,
  "error": "Sport with id 999 not found"
}
```

**400 Bad Request:**

```json
{
  "success": false,
  "error": "Missing required field: match_id"
}
```

**401 Unauthorized:**

```json
{
  "success": false,
  "error": "Authentication credentials were not provided"
}
```

**500 Internal Server Error:**

```json
{
  "success": false,
  "error": "Failed to fetch sports"
}
```

## 📝 Usage Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/api/matches"

# Get all sports
response = requests.get(f"{BASE_URL}/sports/")
sports = response.json()["data"]

# Get upcoming matches for a sport
response = requests.get(
    f"{BASE_URL}/matches/",
    params={"sport_id": 1, "limit": 10}
)
matches = response.json()["data"]

# Create a prediction (requires auth)
headers = {"Authorization": f"Bearer {access_token}"}
data = {
    "match_id": 1,
    "predicted_winner": "home",
    "confidence_score": 0.85
}
response = requests.post(
    f"{BASE_URL}/predictions/create/",
    json=data,
    headers=headers
)
prediction = response.json()["data"]
```

### JavaScript/TypeScript Example

```typescript
const BASE_URL = 'http://localhost:8000/api/matches';

// Get all sports
const getSports = async () => {
  const response = await fetch(`${BASE_URL}/sports/`);
  const result = await response.json();
  return result.data;
};

// Get upcoming matches
const getMatches = async (sportId: number, limit: number = 10) => {
  const response = await fetch(
    `${BASE_URL}/matches/?sport_id=${sportId}&limit=${limit}`
  );
  const result = await response.json();
  return result.data;
};

// Create prediction
const createPrediction = async (
  matchId: number,
  predictedWinner: 'home' | 'away' | 'draw',
  confidenceScore: number,
  token: string
) => {
  const response = await fetch(`${BASE_URL}/predictions/create/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      match_id: matchId,
      predicted_winner: predictedWinner,
      confidence_score: confidenceScore
    })
  });
  
  const result = await response.json();
  
  if (!result.success) {
    throw new Error(result.error);
  }
  
  return result.data;
};
```

### cURL Examples

```bash
# Get sports
curl http://localhost:8000/api/matches/sports/

# Search teams
curl "http://localhost:8000/api/matches/teams/?search=Manchester"

# Get upcoming matches for Premier League
curl "http://localhost:8000/api/matches/matches/?league_id=1&limit=20"

# Create prediction (with auth)
curl -X POST http://localhost:8000/api/matches/predictions/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": 1,
    "predicted_winner": "home",
    "confidence_score": 0.85
  }'

# Get user predictions
curl http://localhost:8000/api/matches/predictions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔒 Rate Limiting

API rate limits (to be implemented):

- Public endpoints: 100 requests/minute
- Authenticated endpoints: 200 requests/minute
- Prediction creation: 10 requests/minute

## 📊 Pagination

Currently, endpoints use simple limit parameters. Future pagination will include:

```json
{
  "success": true,
  "count": 100,
  "next": "http://localhost:8000/api/matches/matches/?page=2",
  "previous": null,
  "data": []
}
```

## 🌐 CORS Configuration

The API supports CORS for the following origins:
- `http://localhost:3000` (Next.js development)
- `http://127.0.0.1:3000`
- Your production domain

## 📚 Additional Resources

- [Backend README](./backend/README.md)
- [Database Setup Guide](./database/SETUP.md)
- [Core Services Documentation](./backend/apps/core/README.md)
- [Supabase Documentation](https://supabase.com/docs)

## 🐛 Troubleshooting

### Common Issues

**Connection Errors:**
```json
{"success": false, "error": "Failed to fetch sports"}
```

**Solution:** Check Supabase configuration in `.env` file

**Authentication Errors:**
```json
{"success": false, "error": "Authentication credentials were not provided"}
```

**Solution:** Ensure you're including the Bearer token in headers

**Not Found Errors:**
```json
{"success": false, "error": "Match with id 999 not found"}
```

**Solution:** Verify the resource ID exists in the database

## 💡 Best Practices

1. **Always check `success` field** in responses
2. **Handle errors gracefully** with try-catch blocks
3. **Cache static data** (sports, leagues) on the client
4. **Use appropriate HTTP methods** (GET for reading, POST for creating)
5. **Include auth tokens** for protected endpoints
6. **Validate input** before sending requests
7. **Log errors** for debugging

## 🔄 API Versioning

Current version: `v1` (implicit in URL structure)

Future versions will use explicit versioning:
```
http://localhost:8000/api/v2/matches/
```
