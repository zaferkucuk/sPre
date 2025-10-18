-- sPre Database Schema Migration
-- This migration creates all necessary tables and relationships for the sPre platform
-- Run this migration after linking your Supabase project

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- USER PROFILES TABLE
-- Extends auth.users with additional profile information
-- =====================================================

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    phone_number TEXT,
    bio TEXT,
    avatar TEXT,
    notification_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Public profiles are viewable by everyone"
    ON public.profiles FOR SELECT
    USING (TRUE);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- =====================================================
-- USER PREFERENCES TABLE
-- Stores user-specific preferences and settings
-- =====================================================

CREATE TABLE IF NOT EXISTS public.user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    favorite_sports JSONB DEFAULT '[]'::JSONB,
    default_currency TEXT DEFAULT 'USD',
    timezone TEXT DEFAULT 'UTC',
    language TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own preferences"
    ON public.user_preferences FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferences"
    ON public.user_preferences FOR UPDATE
    USING (auth.uid() = user_id);

-- =====================================================
-- SPORTS TABLE
-- Defines different types of sports
-- =====================================================

CREATE TABLE IF NOT EXISTS public.sports (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS (public read access)
ALTER TABLE public.sports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Sports are viewable by everyone"
    ON public.sports FOR SELECT
    USING (TRUE);

-- =====================================================
-- LEAGUES TABLE
-- Represents sports leagues and competitions
-- =====================================================

CREATE TABLE IF NOT EXISTS public.leagues (
    id BIGSERIAL PRIMARY KEY,
    sport_id BIGINT REFERENCES public.sports(id) ON DELETE CASCADE NOT NULL,
    external_id TEXT,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    season TEXT NOT NULL,
    logo TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(sport_id, external_id)
);

-- Create indexes
CREATE INDEX idx_leagues_sport_country ON public.leagues(sport_id, country);
CREATE INDEX idx_leagues_external_id ON public.leagues(external_id);

-- Enable RLS
ALTER TABLE public.leagues ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Leagues are viewable by everyone"
    ON public.leagues FOR SELECT
    USING (TRUE);

-- =====================================================
-- TEAMS TABLE
-- Represents sports teams
-- =====================================================

CREATE TABLE IF NOT EXISTS public.teams (
    id BIGSERIAL PRIMARY KEY,
    sport_id BIGINT REFERENCES public.sports(id) ON DELETE CASCADE NOT NULL,
    external_id TEXT,
    name TEXT NOT NULL,
    code TEXT,
    country TEXT NOT NULL,
    logo TEXT,
    founded INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(sport_id, external_id)
);

-- Create indexes
CREATE INDEX idx_teams_sport_country ON public.teams(sport_id, country);
CREATE INDEX idx_teams_external_id ON public.teams(external_id);

-- Enable RLS
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Teams are viewable by everyone"
    ON public.teams FOR SELECT
    USING (TRUE);

-- =====================================================
-- MATCHES TABLE
-- Stores match information
-- =====================================================

CREATE TYPE match_status AS ENUM ('SCHEDULED', 'LIVE', 'FINISHED', 'POSTPONED', 'CANCELLED');

CREATE TABLE IF NOT EXISTS public.matches (
    id BIGSERIAL PRIMARY KEY,
    league_id BIGINT REFERENCES public.leagues(id) ON DELETE CASCADE NOT NULL,
    external_id TEXT UNIQUE,
    home_team_id BIGINT REFERENCES public.teams(id) ON DELETE CASCADE NOT NULL,
    away_team_id BIGINT REFERENCES public.teams(id) ON DELETE CASCADE NOT NULL,
    match_date TIMESTAMPTZ NOT NULL,
    status match_status DEFAULT 'SCHEDULED',
    home_score INTEGER CHECK (home_score >= 0),
    away_score INTEGER CHECK (away_score >= 0),
    venue TEXT,
    referee TEXT,
    statistics JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_matches_league_date ON public.matches(league_id, match_date);
CREATE INDEX idx_matches_status_date ON public.matches(status, match_date);
CREATE INDEX idx_matches_external_id ON public.matches(external_id);

-- Enable RLS
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Matches are viewable by everyone"
    ON public.matches FOR SELECT
    USING (TRUE);

-- =====================================================
-- PREDICTIONS TABLE
-- Stores user and ML predictions for matches
-- =====================================================

CREATE TYPE prediction_type AS ENUM ('USER', 'ML_MODEL', 'STATISTICAL');

CREATE TABLE IF NOT EXISTS public.predictions (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES public.matches(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    prediction_type prediction_type DEFAULT 'USER',
    predicted_home_score INTEGER NOT NULL CHECK (predicted_home_score >= 0),
    predicted_away_score INTEGER NOT NULL CHECK (predicted_away_score >= 0),
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    reasoning TEXT,
    is_correct BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(match_id, user_id, prediction_type)
);

-- Create indexes
CREATE INDEX idx_predictions_match_user ON public.predictions(match_id, user_id);
CREATE INDEX idx_predictions_type_created ON public.predictions(prediction_type, created_at);

-- Enable RLS
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own predictions"
    ON public.predictions FOR SELECT
    USING (auth.uid() = user_id OR prediction_type != 'USER');

CREATE POLICY "Users can create their own predictions"
    ON public.predictions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own predictions"
    ON public.predictions FOR UPDATE
    USING (auth.uid() = user_id);

-- =====================================================
-- TEAM STATISTICS TABLE
-- Aggregated team performance statistics
-- =====================================================

CREATE TABLE IF NOT EXISTS public.team_statistics (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT REFERENCES public.teams(id) ON DELETE CASCADE NOT NULL,
    season TEXT NOT NULL,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    clean_sheets INTEGER DEFAULT 0,
    form JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(team_id, season)
);

-- Create index
CREATE INDEX idx_team_stats_team_season ON public.team_statistics(team_id, season);

-- Enable RLS
ALTER TABLE public.team_statistics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Team statistics are viewable by everyone"
    ON public.team_statistics FOR SELECT
    USING (TRUE);

-- =====================================================
-- MATCH ANALYTICS TABLE
-- ML-based match analysis and predictions
-- =====================================================

CREATE TABLE IF NOT EXISTS public.match_analytics (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES public.matches(id) ON DELETE CASCADE UNIQUE NOT NULL,
    home_win_probability FLOAT DEFAULT 0.0,
    draw_probability FLOAT DEFAULT 0.0,
    away_win_probability FLOAT DEFAULT 0.0,
    expected_goals_home FLOAT DEFAULT 0.0,
    expected_goals_away FLOAT DEFAULT 0.0,
    confidence_score FLOAT DEFAULT 0.0,
    factors JSONB DEFAULT '{}'::JSONB,
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.match_analytics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Match analytics are viewable by everyone"
    ON public.match_analytics FOR SELECT
    USING (TRUE);

-- =====================================================
-- DATA SOURCES TABLE
-- External API configurations
-- =====================================================

CREATE TYPE source_type AS ENUM ('FOOTBALL_API', 'ODDS_API', 'SPORTS_DATA', 'CUSTOM');

CREATE TABLE IF NOT EXISTS public.data_sources (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    source_type source_type NOT NULL,
    api_url TEXT NOT NULL,
    api_key_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 60,
    last_sync TIMESTAMPTZ,
    config JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS (admin only)
ALTER TABLE public.data_sources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Only admins can view data sources"
    ON public.data_sources FOR SELECT
    USING (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- SYNC LOGS TABLE
-- Tracks data synchronization operations
-- =====================================================

CREATE TYPE sync_status AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED');

CREATE TABLE IF NOT EXISTS public.sync_logs (
    id BIGSERIAL PRIMARY KEY,
    data_source_id BIGINT REFERENCES public.data_sources(id) ON DELETE CASCADE NOT NULL,
    status sync_status DEFAULT 'PENDING',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message TEXT,
    details JSONB DEFAULT '{}'::JSONB
);

-- Create indexes
CREATE INDEX idx_sync_logs_source_status ON public.sync_logs(data_source_id, status);
CREATE INDEX idx_sync_logs_started ON public.sync_logs(started_at);

-- Enable RLS (admin only)
ALTER TABLE public.sync_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Only admins can view sync logs"
    ON public.sync_logs FOR SELECT
    USING (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sports_updated_at BEFORE UPDATE ON public.sports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leagues_updated_at BEFORE UPDATE ON public.leagues
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON public.teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matches_updated_at BEFORE UPDATE ON public.matches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_predictions_updated_at BEFORE UPDATE ON public.predictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_team_statistics_updated_at BEFORE UPDATE ON public.team_statistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_match_analytics_updated_at BEFORE UPDATE ON public.match_analytics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_sources_updated_at BEFORE UPDATE ON public.data_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create user preferences on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, username, first_name, last_name)
    VALUES (
        NEW.id,
        NEW.raw_user_meta_data->>'username',
        NEW.raw_user_meta_data->>'first_name',
        NEW.raw_user_meta_data->>'last_name'
    );
    
    INSERT INTO public.user_preferences (user_id)
    VALUES (NEW.id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- SAMPLE DATA (for development)
-- =====================================================

-- Insert sample sports
INSERT INTO public.sports (name, slug, description) VALUES
    ('Football', 'football', 'Association Football / Soccer'),
    ('Basketball', 'basketball', 'Professional Basketball'),
    ('Tennis', 'tennis', 'Professional Tennis')
ON CONFLICT (name) DO NOTHING;

COMMENT ON TABLE public.profiles IS 'User profiles extending auth.users';
COMMENT ON TABLE public.matches IS 'Sports matches and fixtures';
COMMENT ON TABLE public.predictions IS 'User and ML predictions for matches';
COMMENT ON TABLE public.team_statistics IS 'Aggregated team performance metrics';
COMMENT ON TABLE public.match_analytics IS 'ML-based match analysis';
