#!/bin/bash
# Setup script for Kelly Properties Chatbot with Real Data
# This script implements the plan from docs/PLAN_CHATBOT_LOCAL.md

set -e  # Exit on error

echo "🚀 Kelly Properties Chatbot Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_section() {
    echo ""
    echo -e "${BLUE}$1${NC}"
    echo "----------------------------------------"
}

# Check if .env exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    echo "Please create .env file with database credentials."
    exit 1
fi

# Load .env
export $(cat .env | grep -v '^#' | xargs)

# PHASE 1: Database Setup
print_section "PHASE 1: Database Setup"

print_info "Checking database connection..."
if python manage.py check --database default; then
    print_success "Database connection OK"
else
    print_error "Database connection failed"
    print_info "Please check your DATABASE_URL in .env"
    exit 1
fi

print_info "Running migrations..."
if python manage.py migrate; then
    print_success "Migrations completed"
else
    print_error "Migrations failed"
    exit 1
fi

print_info "Checking pgvector extension..."
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('CREATE EXTENSION IF NOT EXISTS vector;')
print('pgvector extension OK')
"
print_success "pgvector extension installed"

# Check if superuser exists
print_info "Checking for superuser..."
USER_EXISTS=$(python manage.py shell -c "
from apps.users.models import CustomUser
print(CustomUser.objects.filter(is_superuser=True).exists())
" | tail -n 1)

if [ "$USER_EXISTS" == "False" ]; then
    print_warning "No superuser found"
    echo ""
    echo "Create a superuser to access Django admin:"
    python manage.py createsuperuser
else
    print_success "Superuser exists"
fi

# PHASE 2: Check for Properties
print_section "PHASE 2: Property Data"

PROPERTY_COUNT=$(python manage.py shell -c "
from apps.properties.models import Property
print(Property.objects.filter(is_active=True).count())
" | tail -n 1)

print_info "Active properties in database: $PROPERTY_COUNT"

if [ "$PROPERTY_COUNT" -eq 0 ]; then
    print_warning "No properties found in database"
    echo ""
    echo "You have two options:"
    echo "1. Use Data Collector (recommended):"
    echo "   - Start server: python manage.py runserver"
    echo "   - Open: http://localhost:8000/static/data_collector/index.html"
    echo "   - Add 10-20 real properties from Costa Rica"
    echo ""
    echo "2. Create test data:"
    echo "   - Run: python scripts/create_test_data.py"
    echo ""
    read -p "Do you want to create test data now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Creating test data..."
        python scripts/create_test_data.py
        print_success "Test data created"
    else
        print_warning "Skipping test data creation"
        print_info "Please add properties manually before continuing"
        echo "After adding properties, run this script again."
        exit 0
    fi
else
    print_success "Found $PROPERTY_COUNT properties"
fi

# PHASE 3: Generate Embeddings
print_section "PHASE 3: Generate Embeddings"

EMBEDDED_COUNT=$(python manage.py shell -c "
from apps.properties.models import Property
print(Property.objects.filter(is_active=True, embedding__isnull=False).count())
" | tail -n 1)

print_info "Properties with embeddings: $EMBEDDED_COUNT/$PROPERTY_COUNT"

if [ "$EMBEDDED_COUNT" -lt "$PROPERTY_COUNT" ]; then
    print_warning "Some properties don't have embeddings"
    
    # Check API key
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "your-api-key-here" ]; then
        print_error "OPENAI_API_KEY not configured in .env"
        echo "Please add a valid OpenAI API key to generate embeddings"
        exit 1
    fi
    
    print_info "Generating embeddings..."
    if python manage.py generate_embeddings --properties; then
        print_success "Embeddings generated"
    else
        print_error "Failed to generate embeddings"
        exit 1
    fi
else
    print_success "All properties have embeddings"
fi

# PHASE 4: Create Property Documents
print_section "PHASE 4: Create Property Documents for RAG"

DOC_COUNT=$(python manage.py shell -c "
from apps.documents.models import Document
print(Document.objects.filter(content_type='property', is_active=True).count())
" | tail -n 1)

print_info "Property documents: $DOC_COUNT"

if [ "$DOC_COUNT" -lt "$PROPERTY_COUNT" ]; then
    print_warning "Creating property documents for RAG..."
    if python manage.py create_property_documents; then
        print_success "Property documents created"
    else
        print_error "Failed to create property documents"
        exit 1
    fi
else
    print_success "Property documents exist"
fi

# PHASE 5: Test RAG System
print_section "PHASE 5: Test RAG System"

print_info "Running RAG tests..."
if python scripts/test_chatbot.py; then
    print_success "RAG system tests passed"
else
    print_warning "Some RAG tests failed (see above)"
fi

# Final Summary
print_section "✅ Setup Complete!"

echo ""
echo "Your chatbot is ready! 🎉"
echo ""
echo "📊 Summary:"
echo "   • Properties: $PROPERTY_COUNT"
echo "   • Embeddings: $EMBEDDED_COUNT"
echo "   • Documents: $DOC_COUNT"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Start the Django server:"
echo "   python manage.py runserver"
echo ""
echo "2. Start the frontend:"
echo "   cd data-collector-frontend"
echo "   npm run dev"
echo ""
echo "3. Open the chatbot:"
echo "   Visit: http://localhost:5173"
echo "   Click on 'Chatbot IA'"
echo ""
echo "3. Try some queries:"
echo "   • '¿Propiedades en Tamarindo?'"
echo "   • 'Casas con 3 cuartos bajo \$300K'"
echo "   • '¿Propiedades con piscina?'"
echo ""
echo "4. Access Django Admin (optional):"
echo "   http://localhost:8000/admin"
echo ""
echo "📝 To add more properties:"
echo "   http://localhost:8000/static/data_collector/index.html"
echo ""
print_success "Happy chatting! 🏡"
echo ""
