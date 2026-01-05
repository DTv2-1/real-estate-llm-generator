# Development Commands Cheatsheet

Quick reference for common development tasks.

## 🚀 Starting Services

```bash
# Start all Docker services
docker-compose up -d

# Start only database and Redis
docker-compose up -d postgres redis

# Start Django development server
python manage.py runserver

# Start Celery worker
celery -A config worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A config beat --loglevel=info
```

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop web
```

## 📊 Database Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations status
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name migration_name

# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Or directly via Docker
docker-compose exec postgres psql -U postgres -d real_estate_llm
```

## 👥 User Management

```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword username

# Create test data
python manage.py shell < scripts/create_test_data.py
```

## 🔍 Data Management

```bash
# Generate embeddings for all properties and documents
python manage.py generate_embeddings

# Generate embeddings for properties only
python manage.py generate_embeddings --properties

# Generate embeddings for documents only
python manage.py generate_embeddings --documents

# Filter by tenant
python manage.py generate_embeddings --tenant kelly-properties
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_extraction.py

# Run with coverage
pytest --cov=apps --cov=core

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_extraction.py::TestPropertyExtractor::test_extract_from_html_success
```

## 📝 Logging and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f celery

# View last 100 lines
docker-compose logs --tail=100 web

# Django logs location
tail -f logs/django.log
```

## 🔧 Cache Management

```bash
# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Check Redis keys
docker-compose exec redis redis-cli KEYS '*'

# Monitor Redis
docker-compose exec redis redis-cli MONITOR
```

## 📦 Dependencies

```bash
# Install new package
pip install package-name
pip freeze > requirements.txt

# Update all packages
pip install --upgrade -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## 🔄 Code Quality

```bash
# Format with black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy apps/ core/
```

## 🌐 API Testing

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_buyer", "password": "testpass123"}'

# Save token
export TOKEN="your-token-here"

# Test endpoint
curl http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Bearer $TOKEN"

# Or use the test script
./scripts/test_system.sh
```

## 🐛 Debugging

```bash
# Enter Django container shell
docker-compose exec web bash

# Enter PostgreSQL container
docker-compose exec postgres bash

# Check PostgreSQL connection
docker-compose exec postgres pg_isready

# Check pgvector extension
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_extension WHERE extname='vector';"

# Python shell with Django context
python manage.py shell_plus

# Interactive debugging (add to code)
import pdb; pdb.set_trace()
```

## 📊 Performance

```bash
# Check database size
docker-compose exec postgres psql -U postgres -c "\l+"

# Check table sizes
docker-compose exec postgres psql -U postgres -d real_estate_llm -c "\dt+"

# Vacuum database
docker-compose exec postgres psql -U postgres -d real_estate_llm -c "VACUUM ANALYZE;"

# Check slow queries
docker-compose exec postgres psql -U postgres -d real_estate_llm -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 🚀 Deployment

```bash
# Collect static files
python manage.py collectstatic --noinput

# Check for deployment issues
python manage.py check --deploy

# Create deployment package
tar -czf deployment.tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='venv' \
  --exclude='.git' \
  .
```

## 🔑 Environment Variables

```bash
# Generate new SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Check environment variables
printenv | grep -E 'OPENAI|ANTHROPIC|DATABASE|REDIS'
```

## 📈 Monitoring

```bash
# Check Celery workers
celery -A config inspect active

# Check Celery stats
celery -A config inspect stats

# Purge Celery queue
celery -A config purge

# Check Docker stats
docker stats

# Check disk usage
docker system df
```

## 🔄 Reset Everything

```bash
# CAUTION: This deletes all data

# Stop all services
docker-compose down -v

# Remove all containers and volumes
docker-compose rm -f -s -v

# Rebuild
docker-compose up -d --build

# Re-run migrations
python manage.py migrate

# Create test data
python manage.py shell < scripts/create_test_data.py

# Generate embeddings
python manage.py generate_embeddings
```

## 💡 Tips

- Use `ipython` for better interactive shell: `pip install ipython`
- Use `django-extensions` for enhanced management commands: `pip install django-extensions`
- Add `shell_plus` to your workflow: `python manage.py shell_plus --ipython`
- Use `django-debug-toolbar` in development
- Enable SQL logging in development settings
- Use `pgAdmin` or `DBeaver` for database GUI

## 📚 Common Workflows

### Add a new property manually
```bash
python manage.py shell
>>> from apps.properties.models import Property
>>> from apps.tenants.models import Tenant
>>> tenant = Tenant.objects.first()
>>> Property.objects.create(
...     tenant=tenant,
...     property_name="Test Villa",
...     price_usd=350000,
...     bedrooms=3,
...     bathrooms=2,
...     property_type='villa',
...     location='Tamarindo',
...     user_roles=['buyer', 'staff', 'admin']
... )
```

### Add a new document
```bash
python manage.py shell
>>> from apps.documents.models import Document
>>> from apps.tenants.models import Tenant
>>> from datetime import date
>>> tenant = Tenant.objects.first()
>>> Document.objects.create(
...     tenant=tenant,
...     content="Market insight text here...",
...     content_type='market',
...     user_roles=['buyer', 'staff', 'admin'],
...     freshness_date=date.today()
... )
```

### Check embedding status
```bash
python manage.py shell
>>> from apps.properties.models import Property
>>> from apps.documents.models import Document
>>> print(f"Properties with embeddings: {Property.objects.filter(embedding__isnull=False).count()}")
>>> print(f"Properties without embeddings: {Property.objects.filter(embedding__isnull=True).count()}")
>>> print(f"Documents with embeddings: {Document.objects.filter(embedding__isnull=False).count()}")
>>> print(f"Documents without embeddings: {Document.objects.filter(embedding__isnull=True).count()}")
```
