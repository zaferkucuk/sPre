# Core Application

Core utilities, services, and helpers used across the entire sPre application.

## 📁 Structure

```
apps/core/
├── __init__.py
├── apps.py                 # App configuration
├── exceptions.py           # Custom exception classes
├── decorators.py           # Utility decorators
├── tests.py               # Unit tests
├── services/
│   ├── __init__.py
│   ├── supabase_client.py # Supabase client wrapper
│   └── supabase_service.py # Business logic layer
└── README.md              # This file
```

## 🔧 Services

### SupabaseClient

Low-level Supabase client wrapper with connection pooling and error handling.

**Features:**
- Singleton pattern for connection reuse
- Thread-safe operations
- Comprehensive error handling
- Health checks
- Transaction-like context managers

**Usage:**

```python
from apps.core.services import get_supabase_client

# Get client instance
client = get_supabase_client()

# Query data
response = client.table('sports').select('*').execute()

# Call RPC function
result = client.rpc('get_match_stats', {'match_id': 123})

# Health check
if client.health_check():
    print("Connection is healthy")
```

### SupabaseService

High-level business logic service for common operations.

**Features:**
- Clean, business-focused methods
- Automatic error handling
- Logging and monitoring
- Data validation

**Usage:**

```python
from apps.core.services import SupabaseService

service = SupabaseService()

# Get all sports
sports = service.get_all_sports()

# Get upcoming matches
matches = service.get_upcoming_matches(sport_id=1, limit=10)

# Create a prediction
prediction = service.create_prediction(
    user_id='user-123',
    match_id=1,
    predicted_winner='home',
    confidence_score=0.85
)

# Search teams
teams = service.search_teams('Manchester')
```

## 🚨 Exceptions

Custom exception hierarchy for better error handling.

### Base Exceptions

- `BaseAppException` - Base class for all custom exceptions
- `SupabaseException` - Base for Supabase-related errors
- `DataSourceException` - Base for data source errors
- `ValidationException` - Base for validation errors
- `AuthenticationException` - Base for auth errors
- `PredictionException` - Base for prediction errors

### Specific Exceptions

**Supabase:**
- `SupabaseConnectionError` - Connection failures
- `SupabaseConfigurationError` - Configuration issues
- `SupabaseQueryError` - Query execution failures
- `ResourceNotFoundError` - Resource not found

**Data Sources:**
- `DataFetchError` - External API fetch failures
- `DataParsingError` - Data parsing failures
- `RateLimitExceededError` - API rate limit exceeded

**Validation:**
- `InvalidInputError` - Invalid user input
- `DuplicateResourceError` - Duplicate resource creation

**Authentication:**
- `InvalidCredentialsError` - Invalid credentials
- `UnauthorizedError` - Unauthorized access
- `TokenExpiredError` - Expired auth token

**Predictions:**
- `ModelNotFoundError` - Prediction model not found
- `InsufficientDataError` - Insufficient data for prediction
- `PredictionFailedError` - Prediction calculation failed

**Usage:**

```python
from apps.core.exceptions import ResourceNotFoundError, InvalidInputError

# Raise exceptions
if not user:
    raise ResourceNotFoundError("User not found")

if confidence < 0 or confidence > 1:
    raise InvalidInputError("Confidence must be between 0 and 1")

# Catch exceptions
try:
    sport = service.get_sport_by_id(999)
except ResourceNotFoundError as e:
    logger.error(f"Sport not found: {e}")
```

## 🎨 Decorators

Reusable decorators for common patterns.

### Available Decorators

#### `@handle_supabase_errors`

Handles Supabase operation errors and converts them to application exceptions.

```python
from apps.core.decorators import handle_supabase_errors

@handle_supabase_errors
def get_user(user_id):
    return client.table('users').select('*').eq('id', user_id).execute()
```

#### `@handle_external_api_errors`

Handles external API call errors.

```python
from apps.core.decorators import handle_external_api_errors

@handle_external_api_errors
def fetch_match_data(match_id):
    return requests.get(f'https://api.example.com/matches/{match_id}').json()
```

#### `@log_execution_time`

Logs function execution time for performance monitoring.

```python
from apps.core.decorators import log_execution_time

@log_execution_time
def complex_calculation():
    # Time-consuming operation
    pass
```

#### `@retry_on_failure`

Retries function on failure with configurable attempts and delay.

```python
from apps.core.decorators import retry_on_failure

@retry_on_failure(max_attempts=3, delay=2.0)
def fetch_data():
    return requests.get('https://api.example.com/data').json()
```

#### `@cache_result`

Caches function results with TTL.

```python
from apps.core.decorators import cache_result

@cache_result(ttl_seconds=600)
def get_sports():
    return client.table('sports').select('*').execute()
```

#### `@validate_input`

Validates function inputs.

```python
from apps.core.decorators import validate_input

@validate_input(
    user_id=lambda x: isinstance(x, int) and x > 0,
    email=lambda x: '@' in x
)
def create_user(user_id, email):
    pass
```

#### `@require_auth`

Requires authentication (placeholder for customization).

```python
from apps.core.decorators import require_auth

@require_auth
def get_user_profile(user_id):
    return client.table('profiles').select('*').eq('id', user_id).execute()
```

## 🧪 Testing

Run tests:

```bash
# All tests
python manage.py test apps.core

# Specific test class
python manage.py test apps.core.tests.SupabaseClientTests

# With coverage
pytest apps/core/tests.py --cov=apps.core
```

## 📝 Best Practices

### Error Handling

1. Always use custom exceptions instead of generic `Exception`
2. Log errors with context for debugging
3. Use decorators for consistent error handling
4. Provide meaningful error messages

```python
# Good
try:
    sport = service.get_sport_by_id(sport_id)
except ResourceNotFoundError as e:
    logger.error(f"Sport {sport_id} not found: {e}")
    return Response({'error': 'Sport not found'}, status=404)

# Bad
try:
    sport = service.get_sport_by_id(sport_id)
except Exception:
    return Response({'error': 'Error'}, status=500)
```

### Service Usage

1. Always use `SupabaseService` for business logic
2. Use `SupabaseClient` only for custom queries
3. Don't access database directly from views

```python
# Good
service = SupabaseService()
sports = service.get_all_sports()

# Bad
client = get_supabase_client()
sports = client.table('sports').select('*').execute().data
```

### Logging

1. Use appropriate log levels
2. Include context in log messages
3. Use structured logging when possible

```python
import logging

logger = logging.getLogger(__name__)

# Debug level for detailed info
logger.debug(f"Fetching sport with id {sport_id}")

# Info level for normal operations
logger.info(f"Retrieved {len(sports)} sports")

# Warning for recoverable issues
logger.warning(f"Sport {sport_id} is inactive")

# Error for failures
logger.error(f"Failed to fetch sport {sport_id}: {str(e)}")
```

## 🔐 Configuration

Required environment variables:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Logging
LOG_LEVEL=INFO
```

## 📚 Additional Resources

- [Supabase Python Documentation](https://supabase.com/docs/reference/python/introduction)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
