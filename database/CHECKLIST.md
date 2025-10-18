# 🚀 Supabase Setup Checklist

Quick checklist for setting up Supabase database.

## ✅ Pre-Setup Checklist

- [ ] Supabase account created (https://supabase.com)
- [ ] GitHub repo cloned locally
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed (for CLI)

---

## 📋 Step-by-Step Setup

### 1️⃣ Create Supabase Project

- [ ] Go to https://supabase.com/dashboard
- [ ] Click **New Project**
- [ ] Fill in details:
  - Name: `sPre`
  - Database Password: _________________ (SAVE THIS!)
  - Region: _________________ 
- [ ] Wait for project creation (~2 minutes)
- [ ] Note your **Project Reference**: _________________

### 2️⃣ Get API Keys

- [ ] Go to **Settings > API**
- [ ] Copy **Project URL**: `https://____________.supabase.co`
- [ ] Copy **anon public key**: `eyJhbG...`
- [ ] Copy **service_role key**: `eyJhbG...` (KEEP SECRET!)

### 3️⃣ Update Backend .env

- [ ] Open `backend/.env`
- [ ] Update these values:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
DATABASE_URL=postgresql://postgres:YOUR-DB-PASSWORD@db.your-project-ref.supabase.co:5432/postgres
```

### 4️⃣ Apply Database Schema

**Option A: SQL Editor (Recommended)** ⭐

- [ ] Go to **SQL Editor** in Supabase Dashboard
- [ ] Click **New query**
- [ ] Copy content from `database/migrations/20251018_initial_schema.sql`
- [ ] Paste and click **Run**
- [ ] Wait for success message
- [ ] Create another new query
- [ ] Copy content from `database/seed.sql`
- [ ] Paste and click **Run**

**Option B: Supabase CLI**

```bash
# Install CLI
npm install -g supabase

# Login
supabase login

# Link project
supabase link --project-ref YOUR-PROJECT-REF

# Copy migration files
mkdir -p supabase/migrations
cp database/migrations/20251018_initial_schema.sql supabase/migrations/
cp database/seed.sql supabase/seed.sql

# Apply migrations
supabase db push
supabase db reset --seed
```

### 5️⃣ Verify Tables Created

- [ ] Go to **Table Editor**
- [ ] Verify these tables exist:
  - [ ] profiles
  - [ ] user_preferences
  - [ ] sports (should have 3 rows)
  - [ ] leagues (should have 7 rows)
  - [ ] teams (should have 10 rows)
  - [ ] matches (should have 5 rows)
  - [ ] predictions
  - [ ] team_statistics
  - [ ] match_analytics
  - [ ] data_sources
  - [ ] sync_logs

### 6️⃣ Configure Authentication

- [ ] Go to **Authentication > Providers**
- [ ] Enable **Email** provider
- [ ] Set **Confirm email** to `Disabled` (for development)
- [ ] Go to **Authentication > URL Configuration**
- [ ] Set **Site URL**: `http://localhost:3000`
- [ ] Add to **Redirect URLs**: `http://localhost:3000/**`

### 7️⃣ Test Connection

```bash
cd backend

# Install dependencies
pip install -r requirements/dev.txt

# Test Supabase connection
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

### 8️⃣ Test Django Integration

```bash
# Run migrations (Django → Supabase)
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

- [ ] Visit http://localhost:8000/admin
- [ ] Login with superuser
- [ ] Verify you can see data

### 9️⃣ API Smoke Test

```bash
# Test API endpoints
curl http://localhost:8000/api/matches/sports/
curl http://localhost:8000/api/matches/leagues/
curl http://localhost:8000/api/matches/teams/
```

---

## 🎉 Setup Complete!

When all boxes are checked, your Supabase database is ready!

### What's Next?

1. **Frontend Setup**: Create Next.js app
2. **Connect Frontend to Supabase**: Install Supabase client
3. **Implement Auth UI**: Login/Register pages
4. **Build Features**: Match listing, predictions, analytics

---

## 🐛 Troubleshooting

### Can't connect to Supabase?
- [ ] Check SUPABASE_URL and SUPABASE_ANON_KEY in .env
- [ ] Verify project is active in Supabase dashboard
- [ ] Check internet connection

### Tables not created?
- [ ] Make sure you ran the SQL migration script
- [ ] Check for errors in SQL Editor
- [ ] Verify you're in the correct project

### Authentication not working?
- [ ] Enable Email provider in Auth settings
- [ ] Set correct redirect URLs
- [ ] Check API keys are correct

### Django migrations failing?
- [ ] Verify DATABASE_URL is correct
- [ ] Check database password
- [ ] Ensure migrations folder exists

---

## 📚 Useful SQL Queries

### Check all tables
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

### Count records
```sql
SELECT 
    'sports' as table_name, COUNT(*) as count FROM sports
UNION ALL
SELECT 'leagues', COUNT(*) FROM leagues
UNION ALL
SELECT 'teams', COUNT(*) FROM teams
UNION ALL
SELECT 'matches', COUNT(*) FROM matches;
```

### View upcoming matches
```sql
SELECT * FROM v_upcoming_matches;
```

### Check RLS policies
```sql
SELECT schemaname, tablename, policyname, cmd
FROM pg_policies 
WHERE schemaname = 'public';
```

---

**Need help?** Check `database/SETUP.md` for detailed guide.
