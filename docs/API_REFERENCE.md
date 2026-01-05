# Real Estate LLM API - Complete Endpoint Reference

Base URL: `http://localhost:8000/api/v1`

---

## Authentication

### Get JWT Token
```http
POST /auth/token/
Content-Type: application/json

{
  "username": "john_buyer",
  "password": "testpass123"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token
```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Users

### Get Current User
```http
GET /users/me/
Authorization: Bearer {access_token}
```

### Update User Profile
```http
PATCH /users/me/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "preferences": {
    "max_budget": 500000,
    "preferred_locations": ["Tamarindo", "Manuel Antonio"],
    "property_types": ["villa", "house"]
  }
}
```

### List Users (Staff/Admin only)
```http
GET /users/
Authorization: Bearer {access_token}
```

---

## Properties

### List Properties
```http
GET /properties/
Authorization: Bearer {access_token}

Query Parameters:
  - location: string (filter by location)
  - min_price: number
  - max_price: number
  - bedrooms: number
  - bathrooms: number
  - property_type: villa|house|condo|apartment|land|commercial
  - status: available|sold|rented
  - ordering: price_usd|-price_usd|bedrooms|-bedrooms
  - page: number
  - page_size: number (default: 10)
```

**Example:**
```http
GET /properties/?location=Tamarindo&min_price=200000&max_price=500000&bedrooms=3
```

### Get Property Detail
```http
GET /properties/{property_id}/
Authorization: Bearer {access_token}
```

**Response includes:**
- Property details
- Images
- Amenities
- Extraction confidence
- Available to user's role

### Property Statistics
```http
GET /properties/stats/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "total_properties": 45,
  "average_price": 385000,
  "price_range": {
    "min": 150000,
    "max": 950000
  },
  "by_type": {
    "villa": 12,
    "house": 18,
    "condo": 15
  },
  "by_location": {
    "Tamarindo": 15,
    "Manuel Antonio": 10,
    "San José": 8
  }
}
```

### Verify Property Extraction
```http
POST /properties/{property_id}/verify/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "verified": true,
  "corrections": {
    "price_usd": 475000,
    "bedrooms": 4
  }
}
```

---

## Ingestion

### Ingest from URL
```http
POST /ingest/url/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "url": "https://encuentra24.com/costa-rica-es/property-listing"
}
```

**Response:**
```json
{
  "status": "success",
  "property_id": "uuid-here",
  "property_name": "Villa Mar",
  "extraction_confidence": 0.89,
  "data": {
    "property_name": "Villa Mar",
    "price_usd": "450000.00",
    "bedrooms": 3,
    "bathrooms": "2.50",
    "location": "Tamarindo",
    "property_type": "villa"
  }
}
```

### Ingest from Text
```http
POST /ingest/text/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "text": "Luxury villa in Tamarindo. 3 bedrooms, 2.5 bathrooms. Ocean view. $450,000.",
  "source_url": "manual-entry"
}
```

### Batch Ingestion
```http
POST /ingest/batch/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "urls": [
    "https://encuentra24.com/listing1",
    "https://encuentra24.com/listing2"
  ],
  "async": false
}
```

**Async mode (returns immediately, processes in background):**
```json
{
  "urls": [...],
  "async": true
}
```

**Response (sync):**
```json
{
  "results": [
    {
      "url": "...",
      "status": "success",
      "property_id": "uuid"
    },
    {
      "url": "...",
      "status": "failed",
      "error": "Scraping failed"
    }
  ],
  "successful": 1,
  "failed": 1
}
```

**Response (async):**
```json
{
  "status": "queued",
  "task_ids": ["task-id-1", "task-id-2"],
  "message": "2 URLs queued for processing"
}
```

---

## Chat

### Send Message
```http
POST /chat/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "message": "Tell me about beachfront properties in Tamarindo under $500k"
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "message": "Tell me about beachfront properties in Tamarindo under $500k",
  "response": "I found several beachfront properties in Tamarindo within your budget...",
  "sources": [
    {
      "content_type": "property",
      "title": "Villa Mar - Luxury Beachfront",
      "relevance_score": 0.89
    },
    {
      "content_type": "market",
      "title": "Tamarindo Market Analysis",
      "relevance_score": 0.76
    }
  ],
  "model_used": "gpt-4o-mini",
  "tokens": 450,
  "cost_usd": "0.0023"
}
```

### Continue Conversation
```http
POST /chat/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "conversation_id": "uuid-from-previous-response",
  "message": "What about financing options for foreigners?"
}
```

### List Conversations
```http
GET /conversations/
Authorization: Bearer {access_token}

Query Parameters:
  - page: number
  - page_size: number
```

**Response:**
```json
{
  "count": 15,
  "next": "/conversations/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:35:00Z",
      "message_count": 5,
      "total_tokens": 2450,
      "total_cost_usd": "0.0125"
    }
  ]
}
```

### Get Conversation Detail
```http
GET /conversations/{conversation_id}/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "created_at": "2024-01-15T10:30:00Z",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Tell me about properties in Tamarindo",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "I can help you with that...",
      "created_at": "2024-01-15T10:30:15Z",
      "model_used": "gpt-4o-mini",
      "tokens_input": 150,
      "tokens_output": 300,
      "sources": [...]
    }
  ],
  "total_tokens": 450,
  "total_cost_usd": "0.0023"
}
```

---

## Documents

### List Documents
```http
GET /documents/
Authorization: Bearer {access_token}

Query Parameters:
  - content_type: property|market|legal|finance|neighborhood|restaurant|activity|transportation|schools|healthcare|shopping|events|culture|investment|process
  - page: number
  - page_size: number
```

**Example:**
```http
GET /documents/?content_type=market
```

### Get Document Detail
```http
GET /documents/{document_id}/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "content": "Tamarindo is one of Costa Rica's most popular...",
  "content_type": "market",
  "content_type_display": "Market Analysis",
  "source_reference": "Market Report Q1 2024",
  "freshness_date": "2024-01-01",
  "is_fresh": true,
  "times_retrieved": 45,
  "avg_relevance_score": "0.82",
  "user_roles": ["buyer", "staff", "admin"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Tenants (Admin only)

### List Tenants
```http
GET /tenants/
Authorization: Bearer {access_token}
```

### Get Tenant Detail
```http
GET /tenants/{tenant_id}/
Authorization: Bearer {access_token}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": true,
  "status_code": 400,
  "message": "Error description",
  "errors": {
    "field_name": ["Error detail"]
  }
}
```

### Common Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created
- `204 No Content` - Resource deleted
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource doesn't exist
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## Rate Limiting

Default limits:
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Staff/Admin: 5000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1674567890
```

---

## Pagination

List endpoints support pagination:

**Request:**
```http
GET /properties/?page=2&page_size=20
```

**Response:**
```json
{
  "count": 45,
  "next": "/properties/?page=3",
  "previous": "/properties/?page=1",
  "results": [...]
}
```

---

## Filtering & Ordering

### Filtering
```http
GET /properties/?location=Tamarindo&min_price=200000
GET /documents/?content_type=market
GET /conversations/?created_after=2024-01-01
```

### Ordering
```http
GET /properties/?ordering=price_usd        # ascending
GET /properties/?ordering=-price_usd       # descending
GET /properties/?ordering=created_at,-price_usd  # multiple fields
```

---

## Role-Based Access

### User Roles and Permissions

| Endpoint          | Buyer | Tourist | Vendor | Staff | Admin |
|-------------------|-------|---------|--------|-------|-------|
| Properties (list) | ✓     | ✗       | ✗      | ✓     | ✓     |
| Property prices   | ✓     | ✗       | ✗      | ✓     | ✓     |
| Chat (general)    | ✓     | ✓       | ✓      | ✓     | ✓     |
| Chat (investment) | ✓     | ✗       | ✗      | ✓     | ✓     |
| Ingestion         | ✗     | ✗       | ✗      | ✓     | ✓     |
| Documents         | ✓     | ✓       | ✓      | ✓     | ✓     |
| Users             | ✗     | ✗       | ✗      | ✓     | ✓     |
| Tenants           | ✗     | ✗       | ✗      | ✗     | ✓     |

---

## Webhooks (Coming Soon)

Future support for webhooks on:
- Property created
- Property updated
- Chat message sent
- Ingestion completed

---

## API Versioning

Current version: `v1`

Access previous versions:
- `http://localhost:8000/api/v1/...` (current)

Breaking changes will increment the major version number.

---

## Support

For API issues:
1. Check error response message
2. Review API_TESTING.md for examples
3. Check logs: `docker-compose logs -f web`
4. Verify authentication token validity
