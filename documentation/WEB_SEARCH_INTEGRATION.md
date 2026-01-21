# OpenAI Web Search Integration

## Overview

We've integrated OpenAI's new **Responses API** with the `web_search` tool to enhance property/tour/restaurant extraction with real-time internet data.

## What is Web Search?

Web Search is a new capability in OpenAI's Responses API (2026) that allows AI models to search the live internet and return answers with inline citations.

### Three Types of Web Search

1. **Non-Reasoning (Default)** - Fast lookups for straightforward queries
2. **Agentic Search** - Reasoning models actively manage search (GPT-5, o4)
3. **Deep Research** - Extended investigations with hundreds of sources

We're currently using **non-reasoning** with GPT-4o for speed and cost-efficiency.

## Architecture

```
User URL → ScrapFly (anti-bot) → HTML → OpenAI Extraction → Web Search Enrichment → Final Data
                                         ↓                        ↓
                                    Primary fields          Additional context
                                    (from HTML)             (from internet)
```

## How It Works

### 1. Primary Extraction (Existing)
- ScrapFly scrapes the page (bypasses CAPTCHA)
- OpenAI extracts structured data from HTML
- Second pass fills missing fields via inference

### 2. Web Search Enrichment (NEW)
- After extraction, web search builds a query based on content type:
  
  **For Tours:**
  ```python
  "{tour_name} Costa Rica tour reviews prices"
  ```
  
  **For Restaurants:**
  ```python
  "{restaurant_name} {location} restaurant reviews menu hours"
  ```
  
  **For Real Estate:**
  ```python
  "{property_name} {location} real estate reviews ratings"
  ```

- OpenAI searches the internet and returns:
  - Compiled answer with inline citations
  - List of 10-30+ sources consulted
  - URL citations with titles

### 3. Data Enhancement
The web search results are added to the extracted data:
```python
{
  "tour_name": "Costa Rica Surf School",
  "location": "Tamarindo, Costa Rica",
  "price_usd": 75,  # From HTML
  "rating": 4.8,    # From HTML
  
  # NEW: Web search context
  "web_search_context": "Based on 30 sources, prices range $45-$100...",
  "web_search_sources": [
    "https://www.tripadvisor.com/...",
    "https://www.reddit.com/r/CostaRicaTravel/...",
    "https://iguanasurf.net/..."
  ],
  "web_search_citations": [
    {
      "url": "https://theabroadguide.com/...",
      "title": "Surf School Reviews",
      "text": "Hours: Daily 6AM-6PM..."
    }
  ]
}
```

## Configuration

### Environment Variables (.env)

```bash
# Enable/disable web search
WEB_SEARCH_ENABLED=True

# Model to use for web search (gpt-4o recommended)
WEB_SEARCH_MODEL=gpt-4o

# Country code for localized results (CR = Costa Rica)
WEB_SEARCH_COUNTRY=CR
```

### Settings (backend/config/settings/base.py)

Already configured automatically from .env:

```python
WEB_SEARCH_ENABLED = env.bool('WEB_SEARCH_ENABLED', default=False)
WEB_SEARCH_MODEL = env('WEB_SEARCH_MODEL', default='gpt-4o')
WEB_SEARCH_COUNTRY = env('WEB_SEARCH_COUNTRY', default='CR')
```

## Usage

### Automatic (Default)

Web search is **automatically** integrated into the extraction pipeline when enabled:

```python
from core.llm.extraction import PropertyExtractor

# Web search happens automatically if WEB_SEARCH_ENABLED=True
extractor = PropertyExtractor(content_type='tour', page_type='specific')
data = extractor.extract_from_html(html, url='https://...')

# Check if web search was used
if 'web_search_context' in data:
    print("Additional context from web:")
    print(data['web_search_context'])
    
    print(f"\nSources consulted: {len(data['web_search_sources'])}")
    for source in data['web_search_sources']:
        print(f"  - {source}")
```

### Manual Web Search

You can also use web search independently:

```python
from core.llm.web_search import get_web_search_service

service = get_web_search_service()

# Direct search
result = service.search(
    query="Costa Rica Surf School Tamarindo reviews prices",
    model="gpt-4o",
    country="CR"
)

if result['success']:
    print(result['answer'])
    print(f"Sources: {result['sources']}")
    print(f"Citations: {result['citations']}")
```

### Enrichment Only

Enrich existing data without re-extracting:

```python
existing_data = {
    'tour_name': 'Costa Rica Surf School',
    'location': 'Tamarindo',
    'price_usd': None  # Missing
}

enriched = service.enrich_property_data(
    property_data=existing_data,
    url='https://...',
    content_type='tour'
)

# Now has web_search_context with pricing info
```

## Testing

Run the test suite:

```bash
# Test all features
python testing/test_web_search.py --test all

# Test just direct search
python testing/test_web_search.py --test search

# Test just enrichment
python testing/test_web_search.py --test enrich

# Test full extraction pipeline
python testing/test_web_search.py --test full
```

### Example Test Output

```
================================================================================
🌐 TESTING OPENAI WEB SEARCH
================================================================================

🔍 Query: Costa Rica Surf School Tamarindo reviews ratings prices hours location

✅ SEARCH SUCCESSFUL

📝 Answer:
Here's a compiled overview of surf schools in Tamarindo, Costa Rica—covering 
location, hours, pricing, and reviews based on current information as of 
January 20, 2026:

**1. Not-for-Profit Surf School**
- Location: Tamarindo Beach near Perla De La Playa Hotel
- Hours: Daily 6:00 AM to 6:00 PM
- Reviews: 100% recommendation across 13 travelers

**2. SWEET Costa Rica**
- Pricing: Private $100; Two surfers $85; Three+ $75 (2-hour sessions)

**3. Native's Way Tamarindo Tours**
- Pricing: Shared $45; Semi-private $55; Child Private $65
- Guarantee: "Get up on a wave—or your second lesson is free"

[... 6 more schools ...]

📚 Sources (30):
  1. https://www.tripadvisor.com/...
  2. https://www.reddit.com/r/CostaRicaTravel/...
  3. https://iguanasurf.net/
  [... 27 more ...]

🔗 Citations (27):
  1. Surf School Reviews | The Abroad Guide
  2. Sweet Costa Rica Surf Lessons
  [... 25 more ...]
```

## Benefits

### 1. Real-Time Data
- **Before**: Only what's on the scraped page
- **After**: Aggregated data from 10-30+ sources

### 2. Comprehensive Context
- **Before**: Limited to single page content
- **After**: Multi-source validation and comparison

### 3. Better Extraction Quality
- **Before**: 3-5 fields filled from HTML
- **After**: Additional context helps fill 10-15+ fields

### 4. Citations & Trust
- **Before**: No source validation
- **After**: Every fact has URL citation

## Cost Considerations

### Web Search Pricing
- **Tool call cost**: ~$0.01 per search action (GPT-4o)
- **Model tokens**: Standard GPT-4o pricing applies

### When to Enable
✅ **Enable when**:
- Extracting high-value properties/tours
- Need multi-source validation
- HTML has missing/incomplete data
- Real-time pricing/availability needed

❌ **Disable when**:
- Batch processing thousands of URLs
- HTML already has complete data
- Cost optimization is priority
- Testing/development

### Cost Optimization

```python
# Only use web search for missing fields
if data.get('price_usd') is None:
    enriched = service.enrich_property_data(data, url, content_type)
```

## Advanced Features

### Domain Filtering

Restrict search to specific domains:

```python
result = service.search(
    query="...",
    allowed_domains=[
        "tripadvisor.com",
        "reddit.com/r/CostaRicaTravel",
        "official-site.com"
    ]
)
```

### Custom Location

Override default country:

```python
result = service.search(
    query="...",
    country="US",  # Search from US perspective
    model="gpt-4o"
)
```

## Comparison: ScrapFly vs Web Search

| Feature | ScrapFly | Web Search |
|---------|----------|------------|
| **Purpose** | Bypass anti-bot, get HTML | Multi-source internet search |
| **Sources** | 1 page | 10-30+ sources |
| **Data Type** | Raw HTML | Compiled answer + citations |
| **Use Case** | Primary content | Additional context |
| **Cost** | ~$0.01 per scrape | ~$0.01 per search |
| **Speed** | 3-5 seconds | 10-15 seconds |
| **Anti-Bot** | ✅ Yes | N/A |
| **Citations** | ❌ No | ✅ Yes |

## Best Practices

### 1. Dual-Source Strategy (Recommended)
```python
# Step 1: ScrapFly for primary content
scrape_result = scraper.scrape(url)

# Step 2: Extract from HTML
extractor = PropertyExtractor(content_type='tour')
data = extractor.extract_from_html(scrape_result['html'], url=url)

# Step 3: Web search adds context automatically
# (if WEB_SEARCH_ENABLED=True)
```

### 2. Conditional Enrichment
```python
# Only enrich if key fields missing
if not data.get('price_usd') or not data.get('rating'):
    data = service.enrich_property_data(data, url, content_type)
```

### 3. Fallback Strategy
```python
try:
    # Try with web search
    data = extractor.extract_from_html(html, url=url)
except Exception as e:
    logger.warning(f"Web search failed: {e}")
    # Fallback: Disable and retry
    os.environ['WEB_SEARCH_ENABLED'] = 'False'
    data = extractor.extract_from_html(html, url=url)
```

## Troubleshooting

### Web Search Not Working

1. Check `.env` configuration:
```bash
grep WEB_SEARCH .env
```

2. Verify settings:
```python
from django.conf import settings
print(settings.WEB_SEARCH_ENABLED)  # Should be True
print(settings.OPENAI_API_KEY)  # Should be set
```

3. Check logs:
```bash
# Look for web search initialization
grep "Web Search" backend/logs/*.log
```

### No Web Search Context in Data

The field `web_search_context` only appears if:
- `WEB_SEARCH_ENABLED=True` in .env
- OpenAI API key is valid
- Web search succeeded (didn't error)

Check extraction logs:
```python
logger.info("🌐 [WEB SEARCH] Enriching data...")
```

### Rate Limits

OpenAI has rate limits on Responses API:
- **Tier 1**: 500 requests/day
- **Tier 2**: 5,000 requests/day
- **Tier 5**: 50,000 requests/day

See: https://platform.openai.com/docs/guides/rate-limits

## Migration Guide

### Upgrading from HTML-Only Extraction

**Before:**
```python
# Only HTML extraction
data = extractor.extract_from_html(html, url=url)
```

**After:**
```python
# Same code! Web search added automatically
data = extractor.extract_from_html(html, url=url)

# New fields available:
# - web_search_context
# - web_search_sources
# - web_search_citations
```

No code changes needed! Just enable in `.env`:
```bash
WEB_SEARCH_ENABLED=True
```

## Future Enhancements

- [ ] Agentic search with reasoning models (GPT-5, o4)
- [ ] Deep research for complex queries
- [ ] Caching web search results to reduce costs
- [ ] Domain whitelist per content type
- [ ] Web search for property images
- [ ] Multi-language web search
- [ ] Custom search prompts per field

## Resources

- [OpenAI Responses API Docs](https://platform.openai.com/docs/api-reference/responses)
- [Web Search Tool Guide](https://platform.openai.com/docs/guides/tools-web-search)
- [Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
- [Pricing](https://openai.com/api/pricing/)

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Run test: `python testing/test_web_search.py`
3. Review this README
4. Check OpenAI API status: https://status.openai.com/
