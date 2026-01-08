# 🚀 Quick Start Guide - Kelly Properties Chatbot

## Current Status ✅

The chatbot infrastructure is **ready** and waiting for property data!

### What's Been Implemented:

1. ✅ **Database Configuration** - PostgreSQL with pgvector
2. ✅ **Migrations** - All schema updates applied
3. ✅ **RAG Pipeline** - Hybrid search with semantic caching
4. ✅ **Chat API** - REST endpoint with conversation tracking
5. ✅ **Frontend** - Beautiful chat interface (`web/chat.html`)
6. ✅ **Management Commands** - Tools for embeddings & documents
7. ✅ **Testing Scripts** - Automated verification

### What You Need to Do:

⚠️ **Add Real Property Data** (10-20 properties recommended)

---

## 📝 Step-by-Step Instructions

### Option 1: Automated Setup (Recommended)

Run the setup script which will guide you through everything:

```bash
./scripts/setup_chatbot.sh
```

This script will:
- ✅ Check database connection
- ✅ Verify pgvector extension  
- ✅ Run migrations
- ✅ Check for properties (prompt you to add them if needed)
- ✅ Generate embeddings automatically
- ✅ Create RAG documents
- ✅ Run system tests
- ✅ Show you next steps

### Option 2: Manual Setup

If you prefer step-by-step control:

#### 1. Add Properties (Choose One)

**A. Use Data Collector (Best for real data)**
```bash
# Start server
python manage.py runserver

# Open in browser
open http://localhost:8000/static/data_collector/index.html

# Add 10-20 properties from:
# - encuentra24.com
# - coldwellbankercostarica.com
# - crrealestate.com
```

**B. Create Test Data**
```bash
python scripts/create_test_data.py
```

#### 2. Generate Embeddings
```bash
python manage.py generate_embeddings --properties
```

#### 3. Create RAG Documents
```bash
python manage.py create_property_documents
```

#### 4. Test the System
```bash
python scripts/test_chatbot.py
```

#### 5. Start the Server
```bash
python manage.py runserver
```

#### 6. Start the Frontend and Open the Chatbot
```bash
# In a new terminal
cd data-collector-frontend
npm run dev

# Open in browser:
# http://localhost:5173
# Then click on "Chatbot IA"
```

---

## 🧪 Testing Queries

Once the chatbot is running, try these:

```
1. "¿Qué propiedades tienes disponibles?"
2. "¿Propiedades en Tamarindo?"
3. "Casas con 3 cuartos bajo $300,000"
4. "¿Propiedades con piscina?"
5. "¿Cuál es la propiedad más cara?"
```

---

## 🔧 Troubleshooting

### No Properties Found
```bash
# Check database
python manage.py shell -c "
from apps.properties.models import Property
print(f'Properties: {Property.objects.count()}')
"

# Add test data
python scripts/create_test_data.py
```

### No Embeddings
```bash
# Check API key
echo $OPENAI_API_KEY

# Generate embeddings
python manage.py generate_embeddings --properties
```

### CORS Errors
```bash
# Check .env has:
# CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Migration Issues
```bash
# Reset migrations (only if needed)
python manage.py migrate documents --fake
python manage.py migrate
```

---

## 📊 Checking System Health

```bash
# Quick health check
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.properties.models import Property
from apps.documents.models import Document
from apps.tenants.models import Tenant

print(f'✓ Tenants: {Tenant.objects.count()}')
print(f'✓ Properties: {Property.objects.filter(is_active=True).count()}')
print(f'✓ With Embeddings: {Property.objects.filter(embedding__isnull=False).count()}')
print(f'✓ Documents: {Document.objects.filter(is_active=True).count()}')
print(f'✓ Property Docs: {Document.objects.filter(content_type=\"property\").count()}')
"
```

---

## 📚 Documentation

- **Full Implementation Plan**: [`docs/PLAN_CHATBOT_LOCAL.md`](PLAN_CHATBOT_LOCAL.md)
- **API Documentation**: [`docs/CHATBOT_README.md`](CHATBOT_README.md)
- **RAG Pipeline**: [`core/llm/rag.py`](../core/llm/rag.py)
- **Chat Views**: [`apps/chat/views.py`](../apps/chat/views.py)

---

## 🎯 Next Steps After Testing

1. **Add More Properties** - Aim for 50+ for better results
2. **Enable Authentication** - Uncomment `permission_classes` in `apps/chat/views.py`
3. **Deploy to Production** - Push to GitHub, DigitalOcean auto-deploys
4. **Monitor Performance** - Check Django logs for query latency
5. **Tune RAG Settings** - Adjust `VECTOR_SEARCH_TOP_K` in settings if needed

---

## ✅ Ready to Deploy?

Once local testing is successful:

```bash
# Commit your changes
git add .
git commit -m "feat: chatbot ready for production"
git push origin main

# DigitalOcean App Platform will auto-deploy
# Update frontend API URL to production endpoint
```

---

**Questions?** Check the full documentation in [`PLAN_CHATBOT_LOCAL.md`](PLAN_CHATBOT_LOCAL.md)
