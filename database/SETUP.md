# sPre - Supabase Setup Guide

Complete guide to setting up the Supabase database for sPre platform.

## 📋 Prerequisites

- Supabase account (https://supabase.com)
- Supabase CLI installed
- Git and basic SQL knowledge

## 🚀 Quick Start

### 1. Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Choose organization and enter project details:
   - **Name**: sPre
   - **Database Password**: (generate strong password and save it)
   - **Region**: Choose closest to your users
4. Wait for project to be created (~2 minutes)

### 2. Install Supabase CLI

```bash
# macOS
brew install supabase/tap/supabase

# Windows (with Scoop)
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# Linux
brew install supabase/tap/supabase

# NPM (all platforms)
npm install -g supabase
```

Verify installation:
```bash
supabase --version
```

### 3. Login to Supabase CLI

```bash
supabase login
```

This will open your browser for authentication.

### 4. Link Your Project

```bash
# Navigate to your project root
cd /path/to/sPre

# Link to your Supabase project
supabase link --project-ref YOUR_PROJECT_REF

# You can find YOUR_PROJECT_REF in your Supabase project URL:
# https://supabase.com/dashboard/project/YOUR_PROJECT_REF
```

### 5. Apply Database Schema

```bash
# Apply the initial schema migration
supabase db push
```

This will:
- Create all tables
- Set up Row Level Security policies
- Create necessary indexes
- Add triggers and functions

### 6. Seed Development Data (Optional)

```bash
# Load sample data for development
supabase db reset --seed
```

## 🗄️ Database Structure

Your database now includes:

### Core Tables
- ✅ `profiles` - User profiles
- ✅ `user_preferences` - User settings
- ✅ `sports` - Sport types
- ✅ `leagues` - Competitions
- ✅ `teams` - Sport teams  
- ✅ `matches` - Match fixtures
- ✅ `predictions` - User predictions
- ✅ `team_statistics` - Team stats
- ✅ `match_analytics` - ML predictions
- ✅ `data_sources` - External APIs
- ✅ `sync_logs` - Sync history

### Helper Views
- ✅ `v_upcoming_matches` - Upcoming fixtures
- ✅ `v_match_results` - Past results
- ✅ `v_team_standings` - League tables

## 🔐 Get Your API Keys

### 1. Get Project URL

In your Supabase dashboard, go to **Settings > API**

Copy your:
- **Project URL**: `https://xxxxx.supabase.co`
- **Anon (public) key**: `eyJhbG...`
- **Service role key**: `eyJhbG...` (keep this secret!)

### 2. Update Backend .env

Add to `backend/.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here

# Database URL
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

### 3. Update Frontend .env.local

Add to `frontend/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

## 🔧 Local Development with Supabase

### Start Local Supabase

```bash
# Start local Supabase (includes PostgreSQL, Auth, Storage, etc.)
supabase start
```

This gives you:
- **API URL**: http://localhost:54321
- **DB URL**: postgresql://postgres:postgres@localhost:54322/postgres
- **Studio URL**: http://localhost:54323
- **Inbucket URL**: http://localhost:54324 (email testing)

### Stop Local Supabase

```bash
supabase stop
```

### Reset Local Database

```bash
# Reset and apply all migrations + seed data
supabase db reset
```

## 📊 Database Migrations

### Create New Migration

```bash
# Create empty migration
supabase migration new migration_name

# Or generate from schema changes in Studio
supabase db diff -f migration_name
```

### Apply Migrations

```bash
# Apply all pending migrations locally
supabase migration up

# Apply to remote (production)
supabase db push
```

### Pull Remote Schema

```bash
# Pull schema from production
supabase db pull
```

## 🔒 Row Level Security (RLS)

All tables have RLS enabled. Key policies:

### User Data
- ✅ Users can only read/write their own profiles
- ✅ Users can only see their own predictions
- ✅ User preferences are private

### Public Data  
- ✅ Sports, leagues, teams are public (read-only)
- ✅ Matches are public (read-only)
- ✅ Match analytics are public (read-only)
- ✅ Team statistics are public (read-only)

### Admin Data
- ✅ Data sources require service role
- ✅ Sync logs require service role

## 🧪 Testing Your Setup

### 1. Check Tables

```bash
# List all tables
supabase db list

# Or open Studio
supabase studio
```

### 2. Test Auth Integration

Create a test user in Supabase Dashboard:
1. Go to **Authentication > Users**
2. Click "Add User"
3. Verify user profile is auto-created

### 3. Test API Connection

```bash
# Test from your backend
cd backend
python manage.py shell

>>> from supabase import create_client
>>> supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
>>> response = supabase.table('sports').select('*').execute()
>>> print(response.data)
```

## 📚 Useful Commands

```bash
# Check Supabase status
supabase status

# View logs
supabase logs

# Open Studio (web interface)
supabase studio

# Generate TypeScript types
supabase gen types typescript --local > types/database.types.ts

# Backup database
supabase db dump > backup.sql

# Restore database  
psql [CONNECTION_STRING] < backup.sql
```

## 🐛 Troubleshooting

### Migration Errors

```bash
# Check migration status
supabase migration list

# Repair migrations
supabase migration repair
```

### Connection Issues

1. Check if local Supabase is running: `supabase status`
2. Verify project is linked: `supabase link --check`
3. Check credentials in `.env` files

### RLS Issues

If queries fail with permission errors:
1. Check RLS policies in Studio
2. Verify user authentication
3. Test with service role key (bypasses RLS)

## 📖 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## 🎯 Next Steps

1. ✅ Database setup complete
2. ➡️ Configure Django to use Supabase
3. ➡️ Set up Next.js frontend with Supabase client
4. ➡️ Implement authentication flow
5. ➡️ Build API endpoints

---

**Need help?** Check the [main README](../README.md) or open an issue on GitHub.
