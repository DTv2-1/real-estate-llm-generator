# Quick Start Guide

Get the Real Estate LLM system running in 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- OpenAI API key
- Anthropic API key (optional, for complex queries)

## Steps

### 1. Clone & Setup Environment

```bash
cd /Users/1di/kp-real-estate-llm-prototype/real_estate_llm

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Required variables:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # optional
SECRET_KEY=your-secret-key-here
```

### 2. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Start Docker containers (PostgreSQL with pgvector, Redis)
- Install Python dependencies
- Run migrations
- Create test data

### 3. Verify Installation

```bash
# Check containers are running
docker-compose ps

# Should show:
# - postgres (healthy)
# - redis (healthy)
# - web (healthy)
# - celery (healthy)

# Access Django shell
docker-compose exec web python manage.py shell
```

### 4. Test the API

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_buyer",
    "password": "testpass123"
  }'

# Save the access token
export TOKEN="your-access-token-here"

# List properties
curl http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Bearer $TOKEN"

# Chat with the bot
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about properties in Tamarindo"
  }'
```

### 5. Access Data Collector UI

Open in browser: http://localhost:8000/static/data_collector/

Use this interface to:
- Extract property data from URLs
- Manually enter property information
- View extraction confidence scores

## Test Accounts

The setup script creates these test users:

| Username       | Password     | Role    | Can See Prices | Use Case                    |
|----------------|--------------|---------|----------------|-----------------------------|
| john_buyer     | testpass123  | buyer   | ✓              | Investment/purchase queries |
| sarah_tourist  | testpass123  | tourist | ✗              | Activities/dining queries   |
| mike_staff     | testpass123  | staff   | ✓              | Property management         |

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Generate embeddings
docker-compose exec web python manage.py generate_embeddings

# Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web pytest

# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d real_estate_llm
```

## Next Steps

1. **Import Real Data**: Use the ingestion API to import properties from Encuentra24 or RE.CR
2. **Add Documents**: Create documents with market info, legal guides, activity recommendations
3. **Generate Embeddings**: Run `python manage.py generate_embeddings` to enable semantic search
4. **Customize Prompts**: Edit `core/llm/prompts.py` to adjust bot behavior
5. **Configure Caching**: Adjust semantic cache thresholds in `config/settings/base.py`

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker-compose logs

# Reset everything
docker-compose down -v
docker-compose up -d --build
```

### PostgreSQL connection error
```bash
# Check PostgreSQL is healthy
docker-compose exec postgres pg_isready

# Check pgvector extension
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

### Playwright browser issues
```bash
# Install Playwright browsers
docker-compose exec web playwright install chromium
```

### Redis connection error
```bash
# Check Redis
docker-compose exec redis redis-cli ping
```

### API returns 500 errors
```bash
# Check logs for details
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate
```

## Development Tips

1. **Auto-reload**: Django auto-reloads on code changes (no restart needed)
2. **Debug Mode**: Set `DEBUG=True` in .env for detailed errors
3. **Log Level**: Set `LOG_LEVEL=DEBUG` for verbose logging
4. **Test Data**: Run `python manage.py shell < scripts/create_test_data.py` to reset test data
5. **API Documentation**: See `API_TESTING.md` for complete endpoint examples

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up SSL/HTTPS
- [ ] Configure static file serving (WhiteNoise or S3)
- [ ] Set up error monitoring (Sentry)
- [ ] Configure backup strategy for PostgreSQL
- [ ] Set up monitoring (CloudWatch, Datadog, etc.)
- [ ] Review and adjust rate limiting
- [ ] Configure CORS for your frontend domain
- [ ] Set up CI/CD pipeline
- [ ] Load test the API

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Review README.md for detailed documentation
3. Check API_TESTING.md for endpoint examples
4. Verify environment variables in .env
