-- ================================================================
-- Spain Teams Update Script for 2025-26 Season
-- ================================================================
-- This script corrects team assignments across Spanish leagues
-- Run date: October 19, 2025
-- ================================================================

BEGIN;

DO $$
DECLARE
    la_liga_id BIGINT;
    segunda_id BIGINT;
    football_sport_id BIGINT;
BEGIN
    -- Get sport ID for football
    SELECT id INTO football_sport_id FROM public.sports WHERE slug = 'football';
    
    -- Get league IDs
    SELECT id INTO la_liga_id FROM public.leagues WHERE external_api_id = '140' AND season = '2025-26';
    SELECT id INTO segunda_id FROM public.leagues WHERE external_api_id = '141' AND season = '2025-26';

    RAISE NOTICE 'League IDs - La Liga: %, Segunda: %', la_liga_id, segunda_id;

    -- ================================================================
    -- STEP 1: Clean up incorrect assignments
    -- ================================================================
    
    -- Remove teams that are in both La Liga and Segunda (duplicates)
    -- These teams should ONLY be in one league
    DELETE FROM public.team_leagues 
    WHERE season = '2025-26' 
      AND league_id = segunda_id
      AND team_id IN (
          SELECT id FROM public.teams 
          WHERE external_id IN (
              '723',  -- Alaves (in La Liga)
              '729',  -- Elche (promoted to La Liga)
              '534',  -- Levante (promoted to La Liga)
              '724',  -- Osasuna (in La Liga)
              '728',  -- Rayo Vallecano (in La Liga)
              '542',  -- Real Oviedo (promoted to La Liga)
              '727'   -- Villarreal (in La Liga)
          )
          AND country = 'Spain'
      );
    
    RAISE NOTICE 'Removed duplicate Segunda assignments';

    -- ================================================================
    -- STEP 2: Add relegated La Liga teams to Segunda
    -- ================================================================
    
    -- Valladolid
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Real Valladolid', 'VLL', 'Spain', 1928, '549', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name, is_active = TRUE, updated_at = NOW();
    
    -- Las Palmas
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Las Palmas', 'LPA', 'Spain', 1949, '543', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name, is_active = TRUE, updated_at = NOW();
    
    -- Leganés
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Leganés', 'LEG', 'Spain', 1928, '742', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name, is_active = TRUE, updated_at = NOW();

    RAISE NOTICE 'Added relegated La Liga teams';

    -- Remove from La Liga, add to Segunda
    DELETE FROM public.team_leagues 
    WHERE season = '2025-26' 
      AND league_id = la_liga_id
      AND team_id IN (
          SELECT id FROM public.teams 
          WHERE external_id IN ('549', '543', '742')
            AND country = 'Spain'
      );
    
    INSERT INTO public.team_leagues (team_id, league_id, season, is_current)
    SELECT t.id, segunda_id, '2025-26', TRUE
    FROM public.teams t
    WHERE t.external_id IN ('549', '543', '742')
      AND t.country = 'Spain'
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Moved relegated teams to Segunda';

    -- ================================================================
    -- STEP 3: Add promoted Primera Federación teams to Segunda
    -- ================================================================
    
    -- Ceuta
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Ceuta', 'CEU', 'Spain', 1956, '744', TRUE)
    ON CONFLICT (sport_id, external_id) DO NOTHING;
    
    -- Cultural Leonesa
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Cultural Leonesa', 'CUL', 'Spain', 1923, '739', TRUE)
    ON CONFLICT (sport_id, external_id) DO NOTHING;
    
    -- FC Andorra
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'FC Andorra', 'AND', 'Spain', 1942, '16582', TRUE)
    ON CONFLICT (sport_id, external_id) DO NOTHING;
    
    -- Real Sociedad B
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Real Sociedad B', 'RSB', 'Spain', 1951, '743', TRUE)
    ON CONFLICT (sport_id, external_id) DO NOTHING;

    RAISE NOTICE 'Added promoted Primera Federación teams';

    -- Add to Segunda
    INSERT INTO public.team_leagues (team_id, league_id, season, is_current)
    SELECT t.id, segunda_id, '2025-26', TRUE
    FROM public.teams t
    WHERE t.external_id IN ('744', '739', '16582', '743')
      AND t.country = 'Spain'
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Added promoted teams to Segunda';

    -- ================================================================
    -- STEP 4: Remove relegated Segunda teams
    -- ================================================================
    
    -- Remove Cartagena, Racing Ferrol, Tenerife, Eldense from Segunda
    DELETE FROM public.team_leagues 
    WHERE season = '2025-26' 
      AND league_id = segunda_id
      AND team_id IN (
          SELECT id FROM public.teams 
          WHERE external_id IN ('722', '737', '714', '736')  -- Cartagena, Ferrol, Tenerife, Eldense
            AND country = 'Spain'
      );
    
    RAISE NOTICE 'Removed relegated Segunda teams';

    -- ================================================================
    -- STEP 5: Ensure all staying Segunda teams are present
    -- ================================================================
    
    -- Cordoba
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Cordoba', 'COR', 'Spain', 1954, '732', TRUE)
    ON CONFLICT (sport_id, external_id) DO NOTHING;
    
    -- Granada
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Granada', 'GRA', 'Spain', 1931, '715', TRUE)
    ON CONFLICT (sport_id, external_id) DO NOTHING;
    
    -- Castellón
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Castellón', 'CAS', 'Spain', 1922, '741', TRUE)
    ON CONFLICT (sport_id, external_id) DO NOTHING;
    
    -- Racing Santander
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Racing Santander', 'RAC', 'Spain', 1913, '536', TRUE)
    ON CONFLICT (sport_id, external_id) DO NOTHING;

    RAISE NOTICE 'Added missing Segunda teams';

    -- Ensure all Segunda teams are in team_leagues
    INSERT INTO public.team_leagues (team_id, league_id, season, is_current)
    SELECT t.id, segunda_id, '2025-26', TRUE
    FROM public.teams t
    WHERE t.external_id IN (
        '718', -- Albacete
        '717', -- Almeria
        '721', -- Burgos
        '731', -- Cadiz
        '732', -- Cordoba
        '738', -- Deportivo
        '725', -- Eibar
        '715', -- Granada
        '730', -- Huesca
        '735', -- Malaga
        '720', -- Mirandes
        '536', -- Racing Santander
        '545', -- Real Zaragoza
        '726', -- Sporting Gijon
        '741'  -- Castellón
    )
    AND t.country = 'Spain'
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Ensured all Segunda teams present';

    -- ================================================================
    -- STEP 6: Verify La Liga has exactly 20 teams
    -- ================================================================
    
    -- Ensure promoted teams are in La Liga
    INSERT INTO public.team_leagues (team_id, league_id, season, is_current)
    SELECT t.id, la_liga_id, '2025-26', TRUE
    FROM public.teams t
    WHERE t.external_id IN ('534', '729', '542')  -- Levante, Elche, Real Oviedo
      AND t.country = 'Spain'
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Ensured promoted teams in La Liga';

    -- ================================================================
    -- STEP 7: Final verification
    -- ================================================================
    
    RAISE NOTICE '=== Final Team Counts ===';
    RAISE NOTICE 'La Liga: %', (
        SELECT COUNT(*) FROM public.team_leagues tl
        JOIN public.leagues l ON tl.league_id = l.id
        WHERE l.external_api_id = '140' AND tl.season = '2025-26'
    );
    
    RAISE NOTICE 'Segunda División: %', (
        SELECT COUNT(*) FROM public.team_leagues tl
        JOIN public.leagues l ON tl.league_id = l.id
        WHERE l.external_api_id = '141' AND tl.season = '2025-26'
    );

END $$;

COMMIT;

-- ================================================================
-- Summary Report
-- ================================================================
SELECT 
    l.name as league_name,
    l.tier,
    COUNT(tl.team_id) as team_count
FROM public.leagues l
LEFT JOIN public.team_leagues tl ON l.id = tl.league_id AND tl.season = '2025-26'
WHERE l.country = 'Spain' 
  AND l.season = '2025-26'
GROUP BY l.id, l.name, l.tier
ORDER BY l.tier;
