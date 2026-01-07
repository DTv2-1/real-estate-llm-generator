#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Real Estate LLM System - Development Setup          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Python 3.11+ is installed
echo -e "${BLUE}[1/8]${NC} Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo -e "${GREEN}✓${NC} Python $python_version found"
else
    echo -e "${RED}✗${NC} Python 3.11+ required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo -e "\n${BLUE}[2/8]${NC} Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\n${BLUE}[3/8]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Install dependencies
echo -e "\n${BLUE}[4/8]${NC} Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Install Playwright browsers
echo -e "\n${BLUE}[5/8]${NC} Installing Playwright browsers..."
playwright install chromium
echo -e "${GREEN}✓${NC} Playwright browsers installed"

# Create .env file if it doesn't exist
echo -e "\n${BLUE}[6/8]${NC} Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file from .env.example"
    echo -e "${RED}⚠${NC}  Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - SECRET_KEY (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Check if Docker is running
echo -e "\n${BLUE}[7/8]${NC} Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker is running"
    
    # Start Docker services
    echo -e "\n${BLUE}Starting Docker services...${NC}"
    docker-compose up -d postgres redis
    
    # Wait for PostgreSQL to be ready
    echo -e "Waiting for PostgreSQL to be ready..."
    sleep 5
    
    echo -e "${GREEN}✓${NC} Database and Redis are running"
else
    echo -e "${RED}✗${NC} Docker is not running. Please start Docker Desktop"
    echo -e "   You can also use local PostgreSQL and Redis installations"
fi

# Run migrations
echo -e "\n${BLUE}[8/8]${NC} Running database migrations..."
python manage.py makemigrations
python manage.py migrate
echo -e "${GREEN}✓${NC} Database migrations completed"

# Create test data
echo -e "\n${BLUE}Creating test data...${NC}"
python manage.py shell < scripts/create_test_data.py
echo -e "${GREEN}✓${NC} Test data created"

# Generate embeddings
echo -e "\n${BLUE}Generating embeddings...${NC}"
python manage.py generate_embeddings
echo -e "${GREEN}✓${NC} Embeddings generated"

# Create superuser prompt
echo -e "\n${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}Test Users Created:${NC}"
echo "  • Buyer: john_buyer / testpass123"
echo "  • Tourist: sarah_tourist / testpass123"
echo "  • Staff: mike_staff / testpass123"

echo -e "\n${BLUE}URLs:${NC}"
echo "  • API: http://localhost:8000/"
echo "  • Admin: http://localhost:8000/admin/"
echo "  • Data Collector: http://localhost:8000/static/data_collector/index.html"
echo "  • Health Check: http://localhost:8000/health/"

echo -e "\n${BLUE}Documentation:${NC}"
echo "  • README.md - Complete system documentation"
echo "  • QUICKSTART.md - Quick start guide"
echo "  • API_TESTING.md - API endpoint testing examples"

echo -e "\n${BLUE}Quick Test:${NC}"
echo "  curl -X POST http://localhost:8000/auth/token/ \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\": \"john_buyer\", \"password\": \"testpass123\"}'"

echo -e "\n${BLUE}Start Services:${NC}"
echo "  1. Development server: python manage.py runserver"
echo "  2. Celery worker: celery -A config worker --loglevel=info"
echo "  Or use Docker: docker-compose up -d"

echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
