# 🤖 Kelly Properties RAG Chatbot

An intelligent chatbot for Costa Rica real estate properties using RAG (Retrieval-Augmented Generation).

## 🎯 Features

- **Semantic Search**: Find properties using natural language queries
- **Multi-Model Support**: GPT-4o-mini for simple queries, Claude 3.5 Sonnet for complex ones
- **Real-Time Data**: Connected to live property database
- **Source Attribution**: Shows which properties were used to generate responses
- **Conversation History**: Maintains context across multiple queries
- **Beautiful UI**: Modern, responsive chat interface

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- OpenAI API key

### Setup (5 minutes)

1. **Clone and install dependencies**:
```bash
cd /Users/1di/kp-real-estate-llm-prototype
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
# Edit .env file with your credentials
cp .env.example .env  # if needed
nano .env
```

Required settings:
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENAI_API_KEY=sk-proj-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

3. **Run setup script**:
```bash
chmod +x scripts/setup_chatbot.sh
./scripts/setup_chatbot.sh
```

This will:
- ✅ Check database connection
- ✅ Run migrations
- ✅ Verify pgvector extension
- ✅ Generate embeddings for properties
- ✅ Create RAG documents
- ✅ Run system tests

4. **Start the server**:
```bash
python manage.py runserver
```

5. **Start the frontend and open the chatbot**:
```bash
# In a new terminal
cd data-collector-frontend
npm run dev

# Open browser: http://localhost:5173
# Click on "Chatbot IA"
```

## 📝 Adding Properties

### Option 1: Data Collector (Recommended)

1. Open: http://localhost:8000/static/data_collector/index.html
2. Paste property URLs from:
   - https://www.encuentra24.com/costa-rica-en/bienes-raices-venta
   - https://www.coldwellbankercostarica.com/property/search
   - https://crrealestate.com/property-search/
3. Click "Extract & Save"

### Option 2: Manual Test Data

```bash
python scripts/create_test_data.py
```

After adding properties, regenerate embeddings:
```bash
python manage.py generate_embeddings --properties
python manage.py create_property_documents
```

## 🧪 Testing

### Run Test Suite

```bash
python scripts/test_chatbot.py
```

This tests:
- Database connectivity
- Embedding generation
- RAG search functionality
- Response quality

### Manual Testing

Try these queries in the chatbot:

1. **Location Search**: "¿Propiedades en Tamarindo?"
2. **Filtered Search**: "Casas con 3 cuartos bajo $300K"
3. **Amenity Search**: "¿Propiedades con piscina?"
4. **Comparison**: "¿Cuál es la propiedad más cara?"
5. **Follow-up**: "¿Tiene fotos?" (after asking about a specific property)

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │ HTTP POST
       ▼
┌─────────────────────────────┐
│   Django Chat API           │
│   (apps/chat/views.py)      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   RAG Pipeline              │
│   (core/llm/rag.py)         │
│                             │
│  1. Hybrid Search           │
│     • Vector (pgvector)     │
│     • Keyword (postgres)    │
│                             │
│  2. Semantic Cache          │
│     • Redis                 │
│                             │
│  3. LLM Router              │
│     • GPT-4o-mini (simple)  │
│     • Claude 3.5 (complex)  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   PostgreSQL + pgvector     │
│                             │
│  • Properties (embeddings)  │
│  • Documents (RAG search)   │
│  • Conversations            │
└─────────────────────────────┘
```

## 📊 Database Schema

### Properties
- Vector embeddings (1536 dimensions)
- Full property details
- Source URLs and metadata

### Documents
- Content for RAG search
- Links to properties
- Role-based access control

### Conversations
- Message history
- Token usage tracking
- Cost tracking

## 🔧 Management Commands

```bash
# Generate embeddings for properties
python manage.py generate_embeddings --properties

# Create RAG documents from properties
python manage.py create_property_documents

# Create test data
python scripts/create_test_data.py

# Test the system
python scripts/test_chatbot.py
```

## 🌐 API Endpoints

### Chat
```
POST /api/v1/chat/
Content-Type: application/json

{
  "message": "¿Propiedades en Tamarindo?",
  "conversation_id": "uuid" (optional)
}
```

Response:
```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "response": "Encontré 3 propiedades...",
  "sources": [
    {
      "document_id": "uuid",
      "content_type": "property",
      "relevance_score": 0.89,
      "metadata": {
        "property_name": "Villa Mar",
        "price_usd": 450000,
        "location": "Tamarindo"
      }
    }
  ],
  "model": "gpt-4o-mini",
  "latency_ms": 1234,
  "cached": false
}
```

### List Conversations
```
GET /api/v1/chat/conversations/
Authorization: Bearer <token>
```

### Get Conversation
```
GET /api/v1/chat/conversations/{id}/
Authorization: Bearer <token>
```

## 🔐 Authentication

For testing, authentication is disabled. To enable:

1. Uncomment in `apps/chat/views.py`:
```python
permission_classes = [IsAuthenticated]
```

2. Get auth token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

3. Use token in requests:
```javascript
headers: {
  'Authorization': 'Bearer <token>'
}
```

## 📈 Performance

- **Query Latency**: 1-3 seconds (first query), <1s (cached)
- **Embedding Cost**: ~$0.02 per 100 properties
- **Query Cost**: ~$0.001 per query (GPT-4o-mini)
- **Cache Hit Rate**: 70-80% with semantic caching

## 🚢 Deployment

### Local Testing → DigitalOcean

1. **Database**: Already on DigitalOcean with pgvector ✅
2. **Properties**: Stored in cloud DB ✅
3. **Embeddings**: Generated once, persistent ✅

To deploy backend:
```bash
git push origin main
# DigitalOcean App Platform auto-deploys
```

Update frontend API URL:
```javascript
// web/chat.html
const API_URL = 'https://your-app.ondigitalocean.app/api/v1/chat/';
```

## 🐛 Troubleshooting

### "No documents found"
```bash
# Check if documents exist
python manage.py shell -c "from apps.documents.models import Document; print(Document.objects.count())"

# Recreate documents
python manage.py create_property_documents --force
```

### "Responses are generic"
- Check relevance scores (should be > 0.7)
- Verify embeddings are generated
- Ensure `content_for_search` has rich information

### "CORS error"
- Check `CORS_ALLOWED_ORIGINS` in `.env`
- Ensure `corsheaders` middleware is enabled

### "Database connection failed"
- Verify `DATABASE_URL` in `.env`
- Test connection: `psql $DATABASE_URL`
- For DigitalOcean, ensure SSL mode: `?sslmode=require`

## 📚 Documentation

- [Full Implementation Plan](docs/PLAN_CHATBOT_LOCAL.md)
- [RAG Pipeline Details](core/llm/rag.py)
- [Property Model](apps/properties/models.py)
- [Chat API](apps/chat/views.py)

## 🤝 Contributing

1. Create test properties
2. Try edge case queries
3. Report issues with query examples
4. Suggest improvements

## 📄 License

Proprietary - Kelly Properties

---

**Need Help?** Check [PLAN_CHATBOT_LOCAL.md](docs/PLAN_CHATBOT_LOCAL.md) for detailed setup guide.
