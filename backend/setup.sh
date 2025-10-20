#!/bin/bash

# ============================================================
# sPre Initial Setup Script
# ============================================================
# This script performs the initial setup for sPre application:
# 1. Creates database tables (migrations)
# 2. Creates cache table
# 3. Creates 2025-2026 season
# 4. Tests API connection
# 5. Loads Premier League data
# ============================================================

echo "============================================================"
echo "🚀 sPre Initial Setup"
echo "============================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the backend directory${NC}"
    echo "   cd backend && bash setup.sh"
    exit 1
fi

echo -e "${BLUE}📋 Step 1/6: Checking environment...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# Check if API key is configured
API_KEY=$(grep "API_FOOTBALL_KEY=" .env | cut -d '=' -f2)
if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-rapidapi-key-here" ]; then
    echo -e "${RED}❌ API_FOOTBALL_KEY not configured in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment configured${NC}"
echo ""

echo -e "${BLUE}📋 Step 2/6: Running migrations...${NC}"
python manage.py makemigrations
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ makemigrations failed${NC}"
    exit 1
fi

python manage.py migrate
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ migrate failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Database migrations completed${NC}"
echo ""

echo -e "${BLUE}📋 Step 3/6: Creating cache table...${NC}"
python manage.py createcachetable
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Cache table creation failed (may already exist)${NC}"
fi

echo -e "${GREEN}✅ Cache table ready${NC}"
echo ""

echo -e "${BLUE}📋 Step 4/6: Creating 2025-2026 season...${NC}"
python manage.py shell << EOF
from apps.matches.models import Season
from datetime import date

# Check if season already exists
if Season.objects.filter(name='2025-2026').exists():
    print('Season 2025-2026 already exists')
    season = Season.objects.get(name='2025-2026')
    season.is_current = True
    season.save()
    print('✅ Updated 2025-2026 as current season')
else:
    season = Season.objects.create(
        name='2025-2026',
        year=2025,
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 31),
        is_current=True
    )
    print('✅ Created season: 2025-2026')

EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Season creation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Season 2025-2026 created${NC}"
echo ""

echo -e "${BLUE}📋 Step 5/6: Testing API connection...${NC}"
python manage.py test_api_connection
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ API connection test failed${NC}"
    echo -e "${YELLOW}   Please check your API_FOOTBALL_KEY in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API connection successful${NC}"
echo ""

echo -e "${BLUE}📋 Step 6/6: Loading Premier League data...${NC}"
echo -e "${YELLOW}⚠️  This will use ~2 API requests${NC}"
echo ""

read -p "Load Premier League data now? (yes/no): " CONFIRM

if [ "$CONFIRM" = "yes" ]; then
    python manage.py load_initial_data --league "Premier League"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Premier League data loaded successfully!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Data loading failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⏭️  Skipping data load${NC}"
    echo -e "${BLUE}   Run manually: python manage.py load_initial_data --league \"Premier League\"${NC}"
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo "============================================================"
echo ""
echo "📊 Next steps:"
echo "   1. Load more leagues:"
echo "      python manage.py load_initial_data --league \"La Liga\""
echo ""
echo "   2. Setup daily sync (cron):"
echo "      0 3 * * * cd $(pwd) && python manage.py daily_sync_data"
echo ""
echo "   3. Start development server:"
echo "      python manage.py runserver"
echo ""
echo "============================================================"
