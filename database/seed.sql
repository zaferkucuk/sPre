-- Sample seed data for development and testing
-- This file is automatically run when you execute: supabase db reset

-- =====================================================
-- SEED SPORTS DATA
-- =====================================================

-- Sports are already seeded in the main migration
-- But we can add more details here

UPDATE public.sports SET description = 'The world''s most popular sport' WHERE slug = 'football';
UPDATE public.sports SET description = 'Fast-paced team sport' WHERE slug = 'basketball';
UPDATE public.sports SET description = 'Individual or doubles racket sport' WHERE slug = 'tennis';

-- =====================================================
-- SEED LEAGUES
-- =====================================================

-- Football Leagues
INSERT INTO public.leagues (sport_id, name, country, season, external_id) VALUES
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Premier League', 'England', '2024-2025', 'EPL_2024'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'La Liga', 'Spain', '2024-2025', 'LALIGA_2024'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Bundesliga', 'Germany', '2024-2025', 'BUN_2024'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Serie A', 'Italy', '2024-2025', 'SERIA_2024'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Ligue 1', 'France', '2024-2025', 'LIGUE1_2024')
ON CONFLICT (sport_id, external_id) DO NOTHING;

-- Basketball Leagues
INSERT INTO public.leagues (sport_id, name, country, season, external_id) VALUES
    ((SELECT id FROM public.sports WHERE slug = 'basketball'), 'NBA', 'USA', '2024-2025', 'NBA_2024'),
    ((SELECT id FROM public.sports WHERE slug = 'basketball'), 'EuroLeague', 'Europe', '2024-2025', 'EUROLEAGUE_2024')
ON CONFLICT (sport_id, external_id) DO NOTHING;

-- =====================================================
-- SEED TEAMS
-- =====================================================

-- Premier League Teams
INSERT INTO public.teams (sport_id, name, code, country, founded, external_id) VALUES
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Manchester United', 'MUN', 'England', 1878, 'MUN'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Liverpool FC', 'LIV', 'England', 1892, 'LIV'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Chelsea FC', 'CHE', 'England', 1905, 'CHE'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Arsenal FC', 'ARS', 'England', 1886, 'ARS'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Manchester City', 'MCI', 'England', 1880, 'MCI'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Tottenham Hotspur', 'TOT', 'England', 1882, 'TOT')
ON CONFLICT (sport_id, external_id) DO NOTHING;

-- La Liga Teams
INSERT INTO public.teams (sport_id, name, code, country, founded, external_id) VALUES
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'FC Barcelona', 'BAR', 'Spain', 1899, 'BAR'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Real Madrid', 'RMA', 'Spain', 1902, 'RMA'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Atletico Madrid', 'ATM', 'Spain', 1903, 'ATM'),
    ((SELECT id FROM public.sports WHERE slug = 'football'), 'Sevilla FC', 'SEV', 'Spain', 1890, 'SEV')
ON CONFLICT (sport_id, external_id) DO NOTHING;

-- =====================================================
-- SEED MATCHES
-- =====================================================

-- Upcoming Premier League Matches
INSERT INTO public.matches (league_id, home_team_id, away_team_id, match_date, status, external_id) VALUES
    (
        (SELECT id FROM public.leagues WHERE external_id = 'EPL_2024'),
        (SELECT id FROM public.teams WHERE external_id = 'MUN'),
        (SELECT id FROM public.teams WHERE external_id = 'LIV'),
        NOW() + INTERVAL '3 days',
        'SCHEDULED',
        'EPL_MUN_LIV_001'
    ),
    (
        (SELECT id FROM public.leagues WHERE external_id = 'EPL_2024'),
        (SELECT id FROM public.teams WHERE external_id = 'CHE'),
        (SELECT id FROM public.teams WHERE external_id = 'ARS'),
        NOW() + INTERVAL '5 days',
        'SCHEDULED',
        'EPL_CHE_ARS_001'
    ),
    (
        (SELECT id FROM public.leagues WHERE external_id = 'EPL_2024'),
        (SELECT id FROM public.teams WHERE external_id = 'MCI'),
        (SELECT id FROM public.teams WHERE external_id = 'TOT'),
        NOW() + INTERVAL '7 days',
        'SCHEDULED',
        'EPL_MCI_TOT_001'
    )
ON CONFLICT (external_id) DO NOTHING;

-- Finished La Liga Matches
INSERT INTO public.matches (league_id, home_team_id, away_team_id, match_date, status, home_score, away_score, external_id) VALUES
    (
        (SELECT id FROM public.leagues WHERE external_id = 'LALIGA_2024'),
        (SELECT id FROM public.teams WHERE external_id = 'RMA'),
        (SELECT id FROM public.teams WHERE external_id = 'BAR'),
        NOW() - INTERVAL '2 days',
        'FINISHED',
        2,
        1,
        'LALIGA_RMA_BAR_001'
    ),
    (
        (SELECT id FROM public.leagues WHERE external_id = 'LALIGA_2024'),
        (SELECT id FROM public.teams WHERE external_id = 'ATM'),
        (SELECT id FROM public.teams WHERE external_id = 'SEV'),
        NOW() - INTERVAL '5 days',
        'FINISHED',
        3,
        0,
        'LALIGA_ATM_SEV_001'
    )
ON CONFLICT (external_id) DO NOTHING;

-- =====================================================
-- SEED TEAM STATISTICS
-- =====================================================

INSERT INTO public.team_statistics (team_id, season, matches_played, wins, draws, losses, goals_scored, goals_conceded, clean_sheets, form)
SELECT 
    id,
    '2024-2025',
    10,
    FLOOR(RANDOM() * 7 + 3)::INTEGER,
    FLOOR(RANDOM() * 3)::INTEGER,
    FLOOR(RANDOM() * 3)::INTEGER,
    FLOOR(RANDOM() * 15 + 10)::INTEGER,
    FLOOR(RANDOM() * 10 + 5)::INTEGER,
    FLOOR(RANDOM() * 4)::INTEGER,
    '["W", "D", "W", "L", "W"]'::JSONB
FROM public.teams
WHERE external_id IN ('MUN', 'LIV', 'CHE', 'ARS', 'MCI', 'TOT', 'RMA', 'BAR', 'ATM', 'SEV')
ON CONFLICT (team_id, season) DO NOTHING;

-- =====================================================
-- SEED MATCH ANALYTICS
-- =====================================================

INSERT INTO public.match_analytics (match_id, home_win_probability, draw_probability, away_win_probability, expected_goals_home, expected_goals_away, confidence_score, model_version)
SELECT 
    id,
    ROUND((RANDOM() * 60 + 20)::NUMERIC, 2),
    ROUND((RANDOM() * 30 + 10)::NUMERIC, 2),
    ROUND((RANDOM() * 60 + 20)::NUMERIC, 2),
    ROUND((RANDOM() * 2 + 1)::NUMERIC, 2),
    ROUND((RANDOM() * 2 + 1)::NUMERIC, 2),
    ROUND((RANDOM() * 30 + 60)::NUMERIC, 2),
    'v1.0.0'
FROM public.matches
WHERE status = 'SCHEDULED'
ON CONFLICT (match_id) DO NOTHING;

-- =====================================================
-- SEED DATA SOURCES
-- =====================================================

INSERT INTO public.data_sources (name, source_type, api_url, api_key_name, rate_limit, config) VALUES
    ('API-Football', 'FOOTBALL_API', 'https://api-football-v1.p.rapidapi.com/v3', 'FOOTBALL_API_KEY', 100, '{"version": "v3", "provider": "RapidAPI"}'::JSONB),
    ('The Odds API', 'ODDS_API', 'https://api.the-odds-api.com/v4', 'ODDS_API_KEY', 500, '{"version": "v4"}'::JSONB)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- HELPFUL VIEWS FOR DEVELOPMENT
-- =====================================================

-- View for upcoming matches with team names
CREATE OR REPLACE VIEW public.v_upcoming_matches AS
SELECT 
    m.id,
    m.match_date,
    l.name AS league_name,
    ht.name AS home_team,
    ht.code AS home_team_code,
    at.name AS away_team,
    at.code AS away_team_code,
    m.venue,
    m.status
FROM public.matches m
JOIN public.leagues l ON m.league_id = l.id
JOIN public.teams ht ON m.home_team_id = ht.id
JOIN public.teams at ON m.away_team_id = at.id
WHERE m.status = 'SCHEDULED'
ORDER BY m.match_date ASC;

-- View for match results
CREATE OR REPLACE VIEW public.v_match_results AS
SELECT 
    m.id,
    m.match_date,
    l.name AS league_name,
    ht.name AS home_team,
    m.home_score,
    at.name AS away_team,
    m.away_score,
    m.status
FROM public.matches m
JOIN public.leagues l ON m.league_id = l.id
JOIN public.teams ht ON m.home_team_id = ht.id
JOIN public.teams at ON m.away_team_id = at.id
WHERE m.status = 'FINISHED'
ORDER BY m.match_date DESC;

-- View for team standings (based on statistics)
CREATE OR REPLACE VIEW public.v_team_standings AS
SELECT 
    t.name AS team_name,
    t.code AS team_code,
    l.name AS league_name,
    ts.season,
    ts.matches_played,
    ts.wins,
    ts.draws,
    ts.losses,
    (ts.wins * 3 + ts.draws) AS points,
    ts.goals_scored,
    ts.goals_conceded,
    (ts.goals_scored - ts.goals_conceded) AS goal_difference,
    ts.clean_sheets,
    ROUND((ts.wins::DECIMAL / NULLIF(ts.matches_played, 0) * 100), 2) AS win_percentage
FROM public.team_statistics ts
JOIN public.teams t ON ts.team_id = t.id
JOIN public.sports s ON t.sport_id = s.id
LEFT JOIN public.leagues l ON l.sport_id = s.id AND l.season = ts.season
ORDER BY points DESC, goal_difference DESC, goals_scored DESC;

-- =====================================================
-- END OF SEED DATA
-- =====================================================

-- Log seed completion
DO $$
BEGIN
    RAISE NOTICE '✅ Seed data loaded successfully!';
    RAISE NOTICE '📊 Database contains:';
    RAISE NOTICE '   - % sports', (SELECT COUNT(*) FROM public.sports);
    RAISE NOTICE '   - % leagues', (SELECT COUNT(*) FROM public.leagues);
    RAISE NOTICE '   - % teams', (SELECT COUNT(*) FROM public.teams);
    RAISE NOTICE '   - % matches', (SELECT COUNT(*) FROM public.matches);
    RAISE NOTICE '   - % team statistics', (SELECT COUNT(*) FROM public.team_statistics);
END $$;
