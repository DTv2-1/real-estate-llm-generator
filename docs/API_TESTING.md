# API Testing Guide

This guide provides examples for testing all API endpoints using curl.

## Authentication

First, obtain a JWT token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_buyer",
    "password": "testpass123"
  }'
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Save the access token:
```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## Property Endpoints

### List Properties

```bash
curl http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Bearer $TOKEN"
```

### Search Properties

```bash
# Search by location
curl "http://localhost:8000/api/v1/properties/?location=Tamarindo" \
  -H "Authorization: Bearer $TOKEN"

# Filter by price range
curl "http://localhost:8000/api/v1/properties/?min_price=200000&max_price=500000" \
  -H "Authorization: Bearer $TOKEN"

# Filter by bedrooms
curl "http://localhost:8000/api/v1/properties/?bedrooms=3" \
  -H "Authorization: Bearer $TOKEN"

# Filter by property type
curl "http://localhost:8000/api/v1/properties/?property_type=villa" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Property Detail

```bash
curl http://localhost:8000/api/v1/properties/{property_id}/ \
  -H "Authorization: Bearer $TOKEN"
```

### Property Statistics

```bash
curl http://localhost:8000/api/v1/properties/stats/ \
  -H "Authorization: Bearer $TOKEN"
```

## Ingestion Endpoints

### Ingest from URL

```bash
curl -X POST http://localhost:8000/api/v1/ingest/url/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://encuentra24.com/costa-rica-es/bienes-raices-venta-casa-guanacaste-tamarindo/12345"
  }'
```

### Ingest from Text

```bash
curl -X POST http://localhost:8000/api/v1/ingest/text/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Luxury villa in Tamarindo. 3 bedrooms, 2.5 bathrooms. Ocean view. $450,000.",
    "source_url": "manual-entry"
  }'
```

### Batch Ingestion

```bash
curl -X POST http://localhost:8000/api/v1/ingest/batch/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://encuentra24.com/costa-rica-es/listing1",
      "https://encuentra24.com/costa-rica-es/listing2"
    ]
  }'
```

### Async Batch Ingestion

```bash
curl -X POST http://localhost:8000/api/v1/ingest/batch/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://encuentra24.com/costa-rica-es/listing1",
      "https://encuentra24.com/costa-rica-es/listing2"
    ],
    "async": true
  }'
```

## Chat Endpoints

### Send Chat Message

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about beachfront properties in Tamarindo under $500k"
  }'
```

Response:
```json
{
  "conversation_id": "uuid-here",
  "message": "User message text",
  "response": "AI response text",
  "sources": [
    {
      "content_type": "property",
      "title": "Villa Mar",
      "relevance_score": 0.89
    }
  ],
  "model_used": "gpt-4o-mini",
  "tokens": 450,
  "cost_usd": "0.0023"
}
```

### Continue Conversation

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "uuid-from-previous-response",
    "message": "What about financing options?"
  }'
```

### List Conversations

```bash
curl http://localhost:8000/api/v1/conversations/ \
  -H "Authorization: Bearer $TOKEN"
```

### Get Conversation Details

```bash
curl http://localhost:8000/api/v1/conversations/{conversation_id}/ \
  -H "Authorization: Bearer $TOKEN"
```

## Document Endpoints

### List Documents

```bash
curl http://localhost:8000/api/v1/documents/ \
  -H "Authorization: Bearer $TOKEN"
```

### Filter Documents by Type

```bash
curl "http://localhost:8000/api/v1/documents/?content_type=market" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Document Detail

```bash
curl http://localhost:8000/api/v1/documents/{document_id}/ \
  -H "Authorization: Bearer $TOKEN"
```

## User Endpoints

### Get Current User Profile

```bash
curl http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer $TOKEN"
```

### Update User Preferences

```bash
curl -X PATCH http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "max_budget": 600000,
      "preferred_locations": ["Tamarindo", "Manuel Antonio"],
      "property_types": ["villa", "house"]
    }
  }'
```

## Role-Based Testing

### As Buyer (sees prices)

```bash
# Login as buyer
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_buyer",
    "password": "testpass123"
  }'

# Chat - should get investment advice
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are good investment properties?"
  }'
```

### As Tourist (no prices, activities focus)

```bash
# Login as tourist
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sarah_tourist",
    "password": "testpass123"
  }'

# Chat - should get activity recommendations
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are fun things to do in Tamarindo?"
  }'
```

### As Staff (full access)

```bash
# Login as staff
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mike_staff",
    "password": "testpass123"
  }'

# List all properties
curl http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Bearer $TOKEN"

# Create property manually
curl -X POST http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_name": "Test Villa",
    "price_usd": "350000",
    "bedrooms": 3,
    "bathrooms": "2",
    "property_type": "villa",
    "location": "Tamarindo",
    "user_roles": ["buyer", "staff", "admin"]
  }'
```

## Error Handling Examples

### Invalid Token

```bash
curl http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Bearer invalid_token"
```

Response (401):
```json
{
  "error": true,
  "status_code": 401,
  "message": "Given token not valid for any token type"
}
```

### Missing Required Field

```bash
curl -X POST http://localhost:8000/api/v1/ingest/url/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response (400):
```json
{
  "error": true,
  "status_code": 400,
  "errors": {
    "url": ["This field is required."]
  }
}
```

### Permission Denied

```bash
# Tourist trying to see prices
curl "http://localhost:8000/api/v1/properties/{property_id}/" \
  -H "Authorization: Bearer $TOURIST_TOKEN"
```

Response: Property data without price fields

## Health Check

```bash
curl http://localhost:8000/health/
```

Response:
```json
{
  "status": "healthy",
  "database": "ok",
  "redis": "ok"
}
```

## Testing Tips

1. **Use jq for JSON formatting**:
   ```bash
   curl http://localhost:8000/api/v1/properties/ \
     -H "Authorization: Bearer $TOKEN" | jq
   ```

2. **Save responses to files**:
   ```bash
   curl http://localhost:8000/api/v1/properties/ \
     -H "Authorization: Bearer $TOKEN" \
     -o properties.json
   ```

3. **Verbose output for debugging**:
   ```bash
   curl -v http://localhost:8000/api/v1/properties/ \
     -H "Authorization: Bearer $TOKEN"
   ```

4. **Time the request**:
   ```bash
   time curl http://localhost:8000/api/v1/properties/ \
     -H "Authorization: Bearer $TOKEN"
   ```
