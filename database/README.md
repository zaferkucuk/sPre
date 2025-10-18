# Supabase Database Schema

Database schema and migrations for sPre (Sport Prediction) platform.

## 📁 Structure

```
database/
├── migrations/           # SQL migration files
├── seed.sql             # Sample data for development
└── README.md           # This file
```

## 🗄️ Database Schema Overview

### Core Tables

**Users & Authentication**
- `auth.users` - Managed by Supabase Auth
- `public.profiles` - User profiles and preferences
  
**Sports Data**
- `public.sports` - Sport types (Football, Basketball, etc.)
- `public.leagues` - Competitions and leagues
- `public.teams` - Sport teams
- `public.matches` - Match data
- `public.predictions` - User and ML predictions

**Analytics**
- `public.team_statistics` - Team performance metrics
- `public.match_analytics` - Match analysis and ML predictions

**Data Sources**
- `public.data_sources` - External API configurations
- `public.sync_logs` - Data synchronization history

## 🚀 Setup Instructions

### 1. Install Supabase CLI

```bash
# macOS
brew install supabase/tap/supabase

# Windows
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# NPM
npm install -g supabase
```

### 2. Initialize Local Development

```bash
# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Start local Supabase
supabase start
```

### 3. Apply Migrations

```bash
# Apply all migrations
supabase db reset

# Or apply specific migration
supabase migration up
```

### 4. Seed Database (Optional)

```bash
# Reset with seed data
supabase db reset
```

## 📝 Creating New Migrations

```bash
# Create new migration
supabase migration new migration_name

# Generate from schema diff
supabase db diff -f migration_name
```

## 🔗 Database Connection

Local Supabase connection details:
- **Host**: localhost
- **Port**: 54322
- **Database**: postgres
- **User**: postgres
- **Password**: postgres

API URL: `http://localhost:54321`

## 🔐 Row Level Security (RLS)

All tables have RLS enabled. Policies are defined in migrations to ensure:
- Users can only see their own data
- Team/league data is public
- Match data respects user permissions
- Predictions are user-scoped

## 📚 Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Database Migrations Guide](https://supabase.com/docs/guides/deployment/database-migrations)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
