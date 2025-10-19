-- ================================================================
-- England Teams Update Script for 2025-26 Season
-- ================================================================
-- This script corrects team assignments across English leagues
-- Run date: October 19, 2025
-- ================================================================

BEGIN;

-- Get league IDs
DO $$
DECLARE
    premier_league_id BIGINT;
    championship_id BIGINT;
    league_one_id BIGINT;
    football_sport_id BIGINT;
BEGIN
    -- Get sport ID for football
    SELECT id INTO football_sport_id FROM public.sports WHERE slug = 'football';
    
    -- Get league IDs
    SELECT id INTO premier_league_id FROM public.leagues WHERE external_api_id = '39' AND season = '2025-26';
    SELECT id INTO championship_id FROM public.leagues WHERE external_api_id = '40' AND season = '2025-26';
    SELECT id INTO league_one_id FROM public.leagues WHERE external_api_id = '41' AND season = '2025-26';

    RAISE NOTICE 'League IDs - Premier: %, Championship: %, League One: %', 
        premier_league_id, championship_id, league_one_id;

    -- ================================================================
    -- STEP 1: Remove incorrect league assignments for 2025-26
    -- ================================================================
    
    -- Remove Burnley, Leeds, Sunderland from Championship (they're in Premier League)
    DELETE FROM public.team_leagues 
    WHERE season = '2025-26' 
      AND league_id = championship_id
      AND team_id IN (
          SELECT id FROM public.teams 
          WHERE external_id IN ('44', '53', '56') -- Burnley, Leeds, Sunderland
            AND country = 'England'
      );
    
    RAISE NOTICE 'Removed incorrect Championship assignments';

    -- ================================================================
    -- STEP 2: Add missing Premier League relegated teams to Championship
    -- ================================================================
    
    -- Leicester City (external_id: 1003 or needs to be added)
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Leicester City', 'LEI', 'England', 1884, '46', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name, 
        code = EXCLUDED.code,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Ipswich Town
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Ipswich Town', 'IPS', 'England', 1878, '57', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name, 
        code = EXCLUDED.code,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Southampton
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Southampton', 'SOU', 'England', 1885, '41', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name, 
        code = EXCLUDED.code,
        is_active = TRUE,
        updated_at = NOW();

    RAISE NOTICE 'Added/Updated relegated Premier League teams';

    -- ================================================================
    -- STEP 3: Add Championship teams to team_leagues
    -- ================================================================
    
    -- Add Leicester, Ipswich, Southampton to Championship
    INSERT INTO public.team_leagues (team_id, league_id, season, is_current)
    SELECT t.id, championship_id, '2025-26', TRUE
    FROM public.teams t
    WHERE t.external_id IN ('46', '57', '41')  -- Leicester, Ipswich, Southampton
      AND t.country = 'England'
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Added relegated teams to Championship';

    -- ================================================================
    -- STEP 4: Add promoted League One teams
    -- ================================================================
    
    -- Birmingham City
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Birmingham City', 'BIR', 'England', 1875, '1354', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        code = EXCLUDED.code,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Wrexham
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Wrexham', 'WRE', 'England', 1864, '1363', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        code = EXCLUDED.code,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Charlton Athletic
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Charlton Athletic', 'CHA', 'England', 1905, '1344', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        code = EXCLUDED.code,
        is_active = TRUE,
        updated_at = NOW();

    RAISE NOTICE 'Added/Updated promoted League One teams';

    -- Add Birmingham, Wrexham, Charlton to Championship
    INSERT INTO public.team_leagues (team_id, league_id, season, is_current)
    SELECT t.id, championship_id, '2025-26', TRUE
    FROM public.teams t
    WHERE t.external_id IN ('1354', '1363', '1344')  -- Birmingham, Wrexham, Charlton
      AND t.country = 'England'
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Added promoted teams to Championship';

    -- ================================================================
    -- STEP 5: Move Luton and Plymouth from Championship to League One
    -- ================================================================
    
    -- Remove from Championship
    DELETE FROM public.team_leagues 
    WHERE season = '2025-26' 
      AND league_id = championship_id
      AND team_id IN (
          SELECT id FROM public.teams 
          WHERE external_id IN ('1353', '69')  -- Luton, Plymouth
            AND country = 'England'
      );
    
    -- Add to League One
    INSERT INTO public.team_leagues (team_id, league_id, season, is_current)
    SELECT t.id, league_one_id, '2025-26', TRUE
    FROM public.teams t
    WHERE t.external_id IN ('1353', '69')  -- Luton, Plymouth
      AND t.country = 'England'
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Moved Luton and Plymouth to League One';

    -- ================================================================
    -- STEP 6: Add more League One teams
    -- ================================================================
    
    -- Huddersfield Town
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Huddersfield Town', 'HUD', 'England', 1908, '1347', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Bolton Wanderers
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Bolton Wanderers', 'BOL', 'England', 1874, '1334', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Blackpool
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Blackpool', 'BLA', 'England', 1887, '1337', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Wigan Athletic
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Wigan Athletic', 'WIG', 'England', 1932, '1342', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Burton Albion
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Burton Albion', 'BUR', 'England', 1950, '1355', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Barnsley
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Barnsley', 'BAR', 'England', 1887, '1348', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Reading
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Reading', 'REA', 'England', 1871, '1345', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Rotherham United
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Rotherham United', 'ROT', 'England', 1925, '1349', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Peterborough United
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Peterborough United', 'PET', 'England', 1934, '1350', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Northampton Town
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Northampton Town', 'NOR', 'England', 1897, '1351', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Leyton Orient
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Leyton Orient', 'LEY', 'England', 1881, '1346', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Lincoln City
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Lincoln City', 'LIN', 'England', 1884, '1356', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Exeter City
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Exeter City', 'EXE', 'England', 1904, '1358', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- AFC Wimbledon
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'AFC Wimbledon', 'WIM', 'England', 2002, '1360', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Bradford City
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Bradford City', 'BRA', 'England', 1903, '1338', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Mansfield Town
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Mansfield Town', 'MAN', 'England', 1897, '1368', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Stockport County
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Stockport County', 'STO', 'England', 1883, '1339', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Wycombe Wanderers
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Wycombe Wanderers', 'WYC', 'England', 1887, '1343', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();
    
    -- Port Vale
    INSERT INTO public.teams (sport_id, name, code, country, founded, external_id, is_active)
    VALUES (football_sport_id, 'Port Vale', 'POR', 'England', 1876, '1340', TRUE)
    ON CONFLICT (sport_id, external_id) DO UPDATE 
    SET name = EXCLUDED.name,
        is_active = TRUE,
        updated_at = NOW();

    RAISE NOTICE 'Added/Updated League One teams';

    -- Add League One teams to team_leagues
    INSERT INTO public.team_leagues (team_id, league_id, season, is_current)
    SELECT t.id, league_one_id, '2025-26', TRUE
    FROM public.teams t
    WHERE t.external_id IN (
        '1353', '69',      -- Luton, Plymouth (already added above)
        '1347', '1334', '1337', '1342', '1355', '1348', '1345', '1349',
        '1350', '1351', '1346', '1356', '1358', '1360', '1338', '1368',
        '1339', '1343', '1340'
    )
    AND t.country = 'England'
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Added League One teams to team_leagues';

    -- ================================================================
    -- STEP 7: Final verification
    -- ================================================================
    
    RAISE NOTICE '=== Final Team Counts ===';
    RAISE NOTICE 'Premier League: %', (
        SELECT COUNT(*) FROM public.team_leagues tl
        JOIN public.leagues l ON tl.league_id = l.id
        WHERE l.external_api_id = '39' AND tl.season = '2025-26'
    );
    
    RAISE NOTICE 'Championship: %', (
        SELECT COUNT(*) FROM public.team_leagues tl
        JOIN public.leagues l ON tl.league_id = l.id
        WHERE l.external_api_id = '40' AND tl.season = '2025-26'
    );
    
    RAISE NOTICE 'League One: %', (
        SELECT COUNT(*) FROM public.team_leagues tl
        JOIN public.leagues l ON tl.league_id = l.id
        WHERE l.external_api_id = '41' AND tl.season = '2025-26'
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
WHERE l.country = 'England' 
  AND l.season = '2025-26'
GROUP BY l.id, l.name, l.tier
ORDER BY l.tier;
