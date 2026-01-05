#!/bin/bash
# =============================================================================
# PRODUCTION DEPLOYMENT SCRIPT
# Deploy to Digital Ocean or any VPS
# =============================================================================

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    exit 1
fi

# Pull latest code (if using git)
if [ -d .git ]; then
    echo -e "${YELLOW}📥 Pulling latest code...${NC}"
    git pull
fi

# Stop running containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.production.yml down

# Build images
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker-compose -f docker-compose.production.yml build --no-cache

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Wait for database
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
sleep 10

# Run migrations
echo -e "${YELLOW}📦 Running database migrations...${NC}"
docker-compose -f docker-compose.production.yml exec -T web python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}📁 Collecting static files...${NC}"
docker-compose -f docker-compose.production.yml exec -T web python manage.py collectstatic --noinput

# Create superuser if needed
echo -e "${YELLOW}👤 Checking for superuser...${NC}"
docker-compose -f docker-compose.production.yml exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("Creating superuser from environment variables...")
    import os
    User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
    )
    print("Superuser created!")
else:
    print("Superuser already exists.")
EOF

# Show running containers
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Running containers:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo -e "${GREEN}🎉 Application is running!${NC}"
echo "Access the application at: http://localhost"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose -f docker-compose.production.yml logs -f"
echo "  Stop services:    docker-compose -f docker-compose.production.yml down"
echo "  Restart services: docker-compose -f docker-compose.production.yml restart"
echo "  Shell access:     docker-compose -f docker-compose.production.yml exec web bash"
