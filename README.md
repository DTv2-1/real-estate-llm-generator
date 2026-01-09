# Real Estate LLM System - Kelly's Costa Rica Properties

Complete Django-based Real Estate chatbot system with RAG (Retrieval Augmented Generation) for Kelly Phillipps' Costa Rica properties.

## 📁 Project Structure

```
/
├── backend/              # Django REST API
│   ├── apps/            # Django applications
│   ├── config/          # Settings & configuration
│   └── core/            # Core utilities (LLM, scraping, RAG)
├── frontend/            # React SPA with TypeScript
│   ├── src/             # React components
│   └── server.js        # Express server
├── deployment/          # Docker & deployment configs
│   ├── docker-compose.yml
│   ├── docker-compose.production.yml
│   └── nginx/
├── tools/               # Utility scripts
│   └── scripts/
├── documentation/       # Docs, evaluation & architecture
│   ├── docs/
│   ├── evaluation/
│   └── guardrails/
├── testing/             # Test suites & responses
│   └── tests/
├── .do/                 # DigitalOcean App Platform config
└── other/               # Static files & legacy code
```

## 🎯 System Overview

This system provides two main components:

### 1. **Data Collection Tool**
- Web interface for extracting property data from URLs or text
- Automatic scraping using Scrapfly (Cloudflare bypass) or Playwright
- LLM-powered extraction (GPT-4o-mini)
- Structured data validation and storage

### 2. **RAG-Powered Chatbot**
- Role-based responses (Buyer, Tourist, Vendor, Staff, Admin)
- Hybrid vector + keyword search
- Semantic caching for cost optimization
- Multi-tenant architecture
- LLM routing (GPT-4o-mini for simple, Claude 3.5 Sonnet for complex queries)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  React SPA (Express server) + Chatbot UI                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Django REST API                         │
│  /api/chat/         - RAG chatbot                       │
│  /api/properties/   - Property CRUD                     │
│  /api/conversations/- Chat history                      │
│  /api/documents/    - Document storage                  │
│  /api/ingest/       - Property ingestion                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌───────────────┬──────────────────┬─────────────────────┐
│  Core Modules │                  │                     │
│               │                  │                     │
│  Scraping     │   LLM Services   │   RAG Pipeline     │
│  (Playwright) │   (OpenAI)       │   (LangChain)      │
│               │                  │                     │
└───────────────┴──────────────────┴─────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│  - PostgreSQL + pgvector (vectors & metadata)           │
│  - Redis (caching & Celery broker)                      │
└─────────────────────────────────────────────────────────┘
```
```

## 📋 Prerequisites

- **Python 3.11+**
- **PostgreSQL 15+** with pgvector extension
- **Redis** for caching
- **Docker & Docker Compose** (recommended)
- **API Keys:**
  - OpenAI API key
  - Anthropic API key

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
cd real_estate_llm
chmod +x scripts/setup.sh
## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
./tools/scripts/setup.sh
```

This script will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Install Playwright browsers
- ✅ Start Docker containers (PostgreSQL + Redis)
- ✅ Run database migrations
- ✅ Create .env file

### Option 2: Manual Setup

1. **Create virtual environment:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Start Docker services:**
```bash
cd ../deployment
docker-compose up -d postgres redis
```

4. **Configure environment:**
```bash
cd ..
cp .env.example .env
# Edit .env with your API keys
```

5. **Run migrations:**
```bash
cd backend
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev  # Development
npm run build && npm start  # Production
```

## 🔑 Environment Configuration

Edit `.env` file with your credentials:

```bash
# Critical Settings
SECRET_KEY=your-django-secret-key-here
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Database (if using Docker, these are defaults)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/real_estate_llm
REDIS_URL=redis://localhost:6379/0

# Optional: Supabase (alternative to self-hosted PostgreSQL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
```

## 🎮 Running the System

### Start Development Server

```bash
python manage.py runserver
```

Server runs at: `http://localhost:8000`

### Start Celery Worker (for async tasks)

```bash
celery -A config worker --loglevel=info
```

### Access Points

- **API Root:** http://localhost:8000/api/v1/
- **Admin Panel:** http://localhost:8000/admin/
- **Data Collector:** http://localhost:8000/static/data_collector/index.html
- **API Docs:** (Coming soon - DRF Spectacular)

## 📚 API Documentation

### Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication:

```bash
# Login
POST /api/v1/auth/login/
{
  "username": "your_username",
  "password": "your_password"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use token in subsequent requests
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Core Endpoints

#### 1. **Property Ingestion**

**Ingest from URL:**
```bash
POST /api/v1/ingest/url/
{
  "url": "https://encuentra24.com/costa-rica/property/123"
}

Response:
{
  "status": "success",
  "property_id": "uuid",
  "extraction_confidence": 0.87,
  "property": { ... }
}
```

**Ingest from Text:**
```bash
POST /api/v1/ingest/text/
{
  "text": "Beautiful 3-bedroom villa in Tamarindo, $450,000..."
}
```

**Batch Ingestion:**
```bash
POST /api/v1/ingest/batch/
{
  "urls": [
    "https://encuentra24.com/property/1",
    "https://re.cr/property/2"
  ],
  "async": true
}
```

#### 2. **Chat with RAG**

```bash
POST /api/v1/chat/
{
  "message": "What's the ROI for properties in Tamarindo?",
  "conversation_id": "optional-uuid"
}

Response:
{
  "conversation_id": "uuid",
  "response": "Based on current market data...",
  "sources": [
    {
      "document_id": "uuid",
      "excerpt": "...",
      "relevance_score": 0.89,
      "updated_at": "2024-01-15"
    }
  ],
  "model": "gpt-4o-mini",
  "latency_ms": 1523,
  "cached": false,
  "tokens_used": 1834
}
```

#### 3. **Property Management**

```bash
# List properties
GET /api/v1/properties/?status=available&min_price=300000&max_price=500000

# Get property details
GET /api/v1/properties/{id}/

# Verify property
PATCH /api/v1/properties/{id}/verify/
{
  "verified": true
}

# Get property stats
GET /api/v1/properties/stats/
```

#### 4. **Conversation Management**

```bash
# List conversations
GET /api/v1/chat/conversations/

# Get conversation with messages
GET /api/v1/chat/conversations/{id}/

# Archive conversation
DELETE /api/v1/chat/conversations/{id}/
```

## 👥 User Roles & Permissions

### Role-Based Access Control

Each user has a role that determines what information they can access:

| Role     | Can View Prices | Can View Financial | Can View Personal Data | Typical Use Case |
|----------|----------------|-------------------|----------------------|------------------|
| **Buyer**    | ✅ Yes | ✅ Yes | ❌ No | Investors, property buyers |
| **Tourist**  | ❌ No  | ❌ No  | ❌ No | Guests, vacation renters |
| **Vendor**   | ❌ No  | Limited | ❌ No | Service providers |
| **Staff**    | ✅ Yes | Limited | ✅ Yes | Property managers |
| **Admin**    | ✅ Yes | ✅ Yes | ✅ Yes | System administrators |

### Creating Users

```python
# Via Django shell
python manage.py shell

from apps.tenants.models import Tenant
from apps.users.models import CustomUser

# Get tenant
tenant = Tenant.objects.first()

# Create buyer user
buyer = CustomUser.objects.create_user(
    username='john_investor',
    email='john@example.com',
    password='secure_password',
    tenant=tenant,
    role='buyer',
    first_name='John',
    last_name='Investor'
)

# Create tourist user
tourist = CustomUser.objects.create_user(
    username='sarah_guest',
    email='sarah@example.com',
    password='secure_password',
    tenant=tenant,
    role='tourist'
)
```

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# Specific app
pytest apps/properties/tests/

# With coverage
pytest --cov=apps --cov-report=html
```

### Manual Testing

```bash
# Test property extraction
python manage.py shell
>>> from core.llm.extraction import extract_property_data
>>> data = extract_property_data('<html>...</html>')
>>> print(data)

# Test RAG pipeline
>>> from core.llm.rag import RAGPipeline
>>> rag = RAGPipeline(tenant_id='uuid', user_role='buyer')
>>> result = rag.query("What properties are available in Tamarindo?")
>>> print(result['response'])
```

## 📊 Database Schema

### Key Models

**Tenant** - Multi-tenancy support
- id, name, slug, domain
- subscription_tier, max_properties, max_users

**CustomUser** - Users with role-based access
- id, username, email, tenant
- role (buyer/tourist/vendor/staff/admin)
- preferences, language, timezone

**Property** - Real estate listings
- id, tenant, property_name, price_usd
- bedrooms, bathrooms, square_meters
- location, latitude, longitude
- embedding (vector), search_vector (full-text)
- extraction_confidence, field_confidence

**Document** - RAG knowledge base
- id, tenant, content
- embedding (vector)
- user_roles (array), content_type
- times_retrieved, avg_relevance_score

**Conversation** - Chat sessions
- id, tenant, user, user_role
- title, total_tokens, total_cost_usd

**Message** - Chat messages
- id, conversation, role, content
- tokens_input, tokens_output, model_used
- retrieved_documents, latency_ms

## 🎨 System Prompts

Each user role has a customized system prompt that defines boundaries and behavior:

- **Buyer:** Focuses on ROI, investment analysis, legal requirements
- **Tourist:** Focuses on activities, restaurants, safety (NO prices)
- **Vendor:** Focuses on demand insights, pricing benchmarks (NO personal data)
- **Staff:** Focuses on SOPs, procedures, vendor contacts
- **Admin:** Full access to all information

See `core/llm/prompts.py` for complete prompts.

## 🚢 Deployment

### AWS Lambda (Recommended for elastic scaling)

```bash
# Install Mangum for ASGI/Lambda compatibility
pip install mangum

# Deploy using AWS SAM or Serverless Framework
# See deployment docs for detailed instructions
```

### AWS ECS Fargate

```bash
# Build Docker image
docker build -t real-estate-llm .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-registry
docker tag real-estate-llm:latest your-registry/real-estate-llm:latest
docker push your-registry/real-estate-llm:latest

# Deploy to ECS (use Terraform or CloudFormation)
```

### Environment Variables for Production

```bash
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@rds-endpoint/dbname
REDIS_URL=redis://elasticache-endpoint:6379/0
SECRET_KEY=production-secret-key
SENTRY_DSN=your-sentry-dsn
```

## 📈 Performance Optimization

### Semantic Caching

- **Saves 30-40%** on LLM API costs
- Caches similar queries with cosine similarity > 0.95
- Configurable TTL based on content type

### Database Indexing

Critical indexes for performance:
- HNSW indexes on vector columns
- GiN indexes for full-text search
- B-tree indexes on frequently queried fields

### Query Optimization

```python
# Use select_related and prefetch_related
properties = Property.objects.filter(
    tenant=tenant
).select_related('tenant', 'verified_by').prefetch_related('images')

# Limit retrieved documents
top_docs = hybrid_search(query, k=5)  # Only top 5
```

## 🔧 Troubleshooting

### Common Issues

**1. PostgreSQL Connection Error**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres
```

**2. pgvector Extension Missing**
```sql
-- Connect to database and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

**3. OpenAI API Rate Limits**
```python
# Implement exponential backoff in settings
OPENAI_MAX_RETRIES = 3
OPENAI_RETRY_DELAY = 2  # seconds
```

**4. Playwright Browser Not Found**
```bash
playwright install chromium
playwright install-deps chromium
```

## 📝 Development Roadmap

### Phase 1: MVP (Weeks 1-4) ✅
- [x] Core models and database schema
- [x] Property ingestion from URLs
- [x] Basic RAG pipeline
- [x] User authentication
- [x] Data collector frontend

### Phase 2: Enhancement (Weeks 5-8)
- [ ] PDF property document processing
- [ ] Advanced property search filters
- [ ] Email notifications
- [ ] Bulk property import
- [ ] Analytics dashboard

### Phase 3: Scale (Weeks 9-12)
- [ ] Multi-language support (Spanish)
- [ ] Property image optimization
- [ ] Advanced analytics
- [ ] Mobile app API
- [ ] Third-party integrations

### Phase 4: Production (Weeks 13-16)
- [ ] Full AWS deployment
- [ ] Load testing and optimization
- [ ] Security audit
- [ ] Documentation finalization
- [ ] Training materials

## 🤝 Contributing

This is a private client project. For questions or issues:

**Contact:** Developer Team
**Client:** Kelly Phillipps
**Timeline:** 14-16 weeks
**Status:** Development Phase

## 📄 License

Proprietary - All rights reserved to Kelly Phillipps Real Estate

---

## 🎓 Quick Reference

### Daily Development Commands

```bash
# Start everything
docker-compose up -d && python manage.py runserver

# Stop everything
docker-compose down

# View logs
docker-compose logs -f postgres
docker-compose logs -f redis

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Create test data
python manage.py shell < scripts/create_test_data.py

# Run specific tests
pytest apps/properties/tests/test_extraction.py -v
```

### Useful Django Commands

```bash
# Create app
python manage.py startapp app_name

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell_plus  # if django-extensions installed
```

---

**Built with ❤️ for Costa Rica Real Estate**
