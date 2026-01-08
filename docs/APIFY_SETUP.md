# Apify Actor Setup - Correct Architecture

## How It Works (The Right Way!)

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Apify Actor (Cloud)                                 │
│ - Playwright scraping with Cloudflare bypass               │
│ - Residential proxies (Costa Rica)                          │
│ - Advanced stealth techniques                               │
│ - Stores raw HTML in Key-Value Store                        │
│ - Pushes metadata to Dataset                                │
└─────────────────────────────────────────────────────────────┘
                          ↓ Dataset ready
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Django Backend (DigitalOcean)                       │
│ - Fetches dataset from Apify API                            │
│ - Gets HTML from Key-Value Store                            │
│ - Calls OpenAI API for extraction                           │
│ - Saves to PostgreSQL with confidence scores                │
└─────────────────────────────────────────────────────────────┘
```

## Why This Architecture?

**Apify Actor:**
- ✅ Only scrapes HTML (simple, focused)
- ✅ Uses residential proxies to bypass Cloudflare
- ✅ Stores raw HTML for later processing
- ✅ No expensive OpenAI calls in Actor (cost control)

**Django Backend:**
- ✅ Full control over OpenAI prompts and logic
- ✅ Can retry extractions without re-scraping
- ✅ Easier to debug and iterate
- ✅ Can process old HTML when prompts improve

## Files Updated

### Apify Actor (Simplified)
- `apify_actor/main.py` - Removed OpenAI/webhook code, kept all stealth features
- `apify_actor/.actor/input_schema.json` - Removed OpenAI fields
- `apify_actor/requirements.txt` - Removed openai/httpx dependencies

### Django Backend (New Sync View)
- `apps/ingestion/views_apify_sync.py` - NEW: Fetch from Apify + OpenAI extraction
- `apps/ingestion/urls.py` - Added `/ingestion/apify/sync/` endpoint
- `requirements.txt` - Added `apify-client==1.7.1`

## Quick Start

### 1. Deploy Apify Actor

```bash
cd apify_actor

# Install CLI (if not already installed)
npm install -g apify-cli
apify login

# Deploy to Apify
apify push
```

### 2. Run Actor in Apify Console

```json
{
  "start_urls": [
    {"url": "https://www.coldwellbankercostarica.com/property/search"},
    {"url": "https://www.encuentra24.com/costa-rica-en/real-estate-for-sale"}
  ],
  "use_residential_proxies": true,
  "proxy_country": "CR",
  "max_listings": 50
}
```

The Actor will:
1. Scrape HTML with Playwright
2. Store HTML in Key-Value Store
3. Push metadata to Dataset

### 3. Configure Django Settings

Add to your `.env` or Django settings:

```bash
# OpenAI API Key (Kelly's key)
OPENAI_API_KEY=sk-proj-exbbWndl_N4ksZjvXxryxKw6tJJk-...

# Apify API Token (from https://console.apify.com/account/integrations)
APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxx
```

### 4. Sync Data to Django

After Actor finishes, call Django endpoint:

```bash
curl -X POST https://goldfish-app-3hc23.ondigitalocean.app/ingestion/apify/sync/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "abc123xyz",
    "actor_run_id": "run456"
  }'
```

Django will:
1. Fetch dataset from Apify
2. Get HTML from Key-Value Store
3. Call OpenAI to extract data
4. Save to PostgreSQL

## Cost Breakdown (Updated)

### Apify Starter Plan ($39/month)

**For 1000 listings/month:**

| Component | Amount | Cost |
|-----------|--------|------|
| Compute (scraping only) | ~15 CU | $4.50 |
| Residential proxies | 0.3 GB | $2.40 |
| **Subtotal Apify** | | **$6.90** |

### OpenAI API (Separate)

| Component | Amount | Cost |
|-----------|--------|------|
| gpt-4o-mini extraction | 1000 calls | ~$5 |
| Input tokens | ~2M tokens | ~$0.30 |
| Output tokens | ~300K tokens | ~$0.90 |
| **Subtotal OpenAI** | | **~$6.20** |

**Total Monthly: ~$13.10** (within your $39 Apify plan + OpenAI credits)

## Deployment Steps

### Step 1: Deploy Django Changes

```bash
cd /Users/1di/kp-real-estate-llm-prototype

# Commit new sync view
git add apps/ingestion/views_apify_sync.py
git add apps/ingestion/urls.py
git add requirements.txt
git commit -m "Add Apify sync endpoint with OpenAI extraction in Django"
git push origin main
```

DigitalOcean will auto-deploy.

### Step 2: Add Environment Variables to DigitalOcean

In your DigitalOcean App Platform:

1. Go to Settings → Environment Variables
2. Add:
   - `OPENAI_API_KEY` = Kelly's key
   - `APIFY_TOKEN` = Your Apify API token (from console.apify.com)

### Step 3: Deploy Apify Actor

```bash
cd apify_actor
apify push
```

### Step 4: Test Complete Flow

1. **Run Actor in Apify Console** with 1 test URL:

```json
{
  "start_urls": [
    {"url": "https://www.coldwellbankercostarica.com/property/1234"}
  ],
  "use_residential_proxies": false,
  "max_listings": 1
}
```

2. **Wait for Actor to finish**, note the dataset ID (e.g., `abc123xyz`)

3. **Call Django sync endpoint**:

```bash
curl -X POST https://goldfish-app-3hc23.ondigitalocean.app/ingestion/apify/sync/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "dataset_id": "abc123xyz"
  }'
```

4. **Check Django logs** to see:
   - Fetching dataset from Apify
   - Getting HTML from Key-Value Store
   - OpenAI extraction
   - Saving to PostgreSQL

5. **Verify in PostgreSQL**:

```sql
SELECT title, price, location, metadata->>'confidence'
FROM properties
WHERE metadata->>'apify_dataset_id' = 'abc123xyz';
```

## Advantages of This Architecture

### vs Previous (OpenAI in Apify Actor)

**Better Cost Control:**
- No wasted OpenAI calls if Actor crashes
- Can retry extraction without re-scraping
- Can reprocess old HTML with improved prompts

**Easier Debugging:**
- Full Django logs for OpenAI calls
- Can test prompts locally
- Can inspect HTML before extraction

**More Flexible:**
- Change extraction logic without redeploying Actor
- Can use different LLMs (Anthropic, local models)
- Can add validation rules in Django

### Data Flow Comparison

**Old Way (Complex):**
```
Apify Actor → OpenAI → Webhook → Django
    ❌ Coupled: scraping + extraction + delivery
    ❌ Hard to debug: logs split across platforms
    ❌ Expensive retries: must re-scrape to re-extract
```

**New Way (Simple):**
```
Apify Actor → Dataset → Django → OpenAI → PostgreSQL
    ✅ Decoupled: scraping separate from extraction
    ✅ Easy to debug: all Django logs in one place
    ✅ Cheap retries: just refetch HTML from Apify
```

## Monitoring

### Apify Console
- Actor runs and status
- Dataset preview
- Proxy bandwidth usage
- Key-Value Store browser

### Django Logs
```bash
# View extraction logs
heroku logs --tail --source app | grep "OpenAI"

# Or in DigitalOcean
# App Platform → Logs → Filter: "extraction"
```

### PostgreSQL Analytics
```sql
-- Extraction success rate
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN metadata->>'extraction_status' = 'success' THEN 1 END) as successful,
    ROUND(100.0 * COUNT(CASE WHEN metadata->>'extraction_status' = 'success' THEN 1 END) / COUNT(*), 2) as success_rate
FROM properties;

-- Average confidence scores
SELECT 
    AVG((metadata->'confidence'->>'price')::float) as avg_price_confidence,
    AVG((metadata->'confidence'->>'location')::float) as avg_location_confidence
FROM properties
WHERE metadata->'confidence' IS NOT NULL;

-- Recent imports
SELECT 
    COUNT(*) as count,
    DATE(created_at) as import_date
FROM properties
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY import_date DESC;
```

## Automation Options

### Option A: Manual Trigger (Recommended for Start)

1. Run Apify Actor when needed
2. Call Django sync endpoint with dataset ID
3. Monitor via logs

### Option B: Scheduled Scraping

Create Apify Schedule:

```json
{
  "name": "Daily Real Estate Scraping",
  "cronExpression": "0 2 * * *",  // 2 AM daily
  "input": {
    "start_urls": [...],
    "use_residential_proxies": true,
    "max_listings": 100
  }
}
```

Then create Django management command:

```python
# apps/ingestion/management/commands/sync_latest_apify.py
from django.core.management.base import BaseCommand
from apify_client import ApifyClient
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        client = ApifyClient(settings.APIFY_TOKEN)
        
        # Get latest run
        actor = client.actor('YOUR_ACTOR_ID')
        runs = actor.runs().list(limit=1, status='SUCCEEDED')
        
        if runs.items:
            run = runs.items[0]
            dataset_id = run['defaultDatasetId']
            
            # Call sync view logic
            from apps.ingestion.views_apify_sync import sync_apify_dataset
            # ... process dataset
```

Schedule with cron:
```bash
0 3 * * * cd /app && python manage.py sync_latest_apify
```

### Option C: Webhook from Apify (Advanced)

Configure Apify webhook to call Django when Actor finishes:

**Apify Webhook Settings:**
- URL: `https://goldfish-app-3hc23.ondigitalocean.app/ingestion/apify/sync/`
- Events: `ACTOR.RUN.SUCCEEDED`
- Payload: Include dataset ID

## Troubleshooting

### Actor doesn't scrape (Cloudflare blocks)

✅ **Solution**: Enable residential proxies in Actor input

### Django can't fetch dataset

❌ **Error**: `APIFY_TOKEN not configured`
✅ **Solution**: Add `APIFY_TOKEN` to DigitalOcean env vars

### OpenAI extraction fails

❌ **Error**: `OpenAI API key not found`
✅ **Solution**: Add `OPENAI_API_KEY` to Django settings

❌ **Error**: `Failed to parse JSON`
✅ **Solution**: Check Django logs for raw OpenAI response, improve prompt

### Data not saving to PostgreSQL

✅ **Solution**: Check Django logs for errors, verify Property model fields match extracted data

## Next Steps

1. ✅ Deploy Apify Actor (done above)
2. ✅ Deploy Django sync endpoint (done above)
3. ⏳ Test with 1 URL to verify flow
4. ⏳ Run with 10 URLs to check quality
5. ⏳ Schedule daily runs
6. ⏳ Meeting with Data Collector person to train

## Questions?

- **How do I reprocess old HTML?** Call sync endpoint again with same dataset ID
- **Can I use different LLMs?** Yes, edit `views_apify_sync.py` to use Anthropic/etc
- **How do I improve extraction?** Update the prompt in `extract_with_openai()` function
- **What if Actor crashes?** Just run it again, HTML is stored in Dataset
- **How much does this cost?** ~$13/month for 1000 listings (see cost breakdown above)

## Updated Deployment Steps

### Step 1: Test Webhook Locally

```bash
# In your Django project
python manage.py runserver

# Test webhook with curl
curl -X POST http://localhost:8000/ingestion/webhooks/apify/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://test.com",
    "title": "Test Property",
    "extracted_data": {
      "price": 250000,
      "beds": 3,
      "location": "Tamarindo"
    }
  }'
```

### Step 2: Deploy Django Changes

```bash
cd /Users/1di/kp-real-estate-llm-prototype

# Commit webhook changes
git add apps/ingestion/views_apify_webhook.py apps/ingestion/urls.py
git commit -m "Add Apify webhook endpoint for cloud data ingestion"
git push origin main
```

DigitalOcean will auto-deploy.

### Step 3: Test Full Flow

1. Go to Apify Console
2. Run your Actor with this input:

```json
{
  "start_urls": [
    {"url": "https://www.coldwellbankercostarica.com/property/1234"}
  ],
  "use_residential_proxies": false,
  "use_llm_extraction": true,
  "backend_webhook_url": "https://goldfish-app-3hc23.ondigitalocean.app/ingestion/webhooks/apify/"
}
```

3. Check Actor logs to see:
   - Scraping success
   - OpenAI extraction
   - Webhook POST to Django

4. Check Django logs:
   - Webhook received
   - Property saved to database

### Step 4: Schedule Automatic Runs

In Apify Console:

1. Go to your Actor → Schedules
2. Create new schedule
3. Set cron: `0 */6 * * *` (every 6 hours)
4. Input:
```json
{
  "start_urls": [
    {"url": "https://www.encuentra24.com/costa-rica-en/real-estate-for-sale"},
    {"url": "https://www.coldwellbankercostarica.com/property/search"}
  ],
  "use_residential_proxies": true,
  "use_llm_extraction": true,
  "backend_webhook_url": "https://goldfish-app-3hc23.ondigitalocean.app/ingestion/webhooks/apify/",
  "max_listings": 50
}
```

## Monitoring

### Apify Console
- Real-time logs
- Resource usage
- Proxy bandwidth
- Dataset preview

### Django Logs
```bash
# View webhook activity
heroku logs --tail --app goldfish-app-3hc23
```

Or in DigitalOcean App Platform → Logs

### PostgreSQL
```sql
-- Check recent imports
SELECT 
    COUNT(*) as total,
    MAX(created_at) as last_import
FROM properties 
WHERE metadata->>'extraction_status' = 'success';

-- Check data quality
SELECT 
    AVG((metadata->'confidence'->>'price')::float) as avg_price_confidence,
    AVG((metadata->'confidence'->>'location')::float) as avg_location_confidence
FROM properties;
```

## Troubleshooting

### Webhook not receiving data

1. Check Actor logs for HTTP errors
2. Verify URL is correct (include trailing slash)
3. Test webhook manually with curl
4. Check Django ALLOWED_HOSTS includes your domain

### OpenAI extraction fails

1. Verify OPENAI_API_KEY is set in Apify
2. Check you have API credits
3. Try with smaller text samples
4. Review Actor logs for API errors

### Cloudflare still blocking

1. Enable residential proxies
2. Check proxy credits in Apify
3. Try different proxy country
4. Increase delays between requests

## Next Steps

1. **Deploy Django webhook** (git push)
2. **Deploy Apify Actor** (apify push)
3. **Test with 1 URL** to verify full flow
4. **Schedule runs** for automatic scraping
5. **Monitor costs** in Apify Console

## Advantages of This Setup

**vs Current DigitalOcean scraping:**
- No cloud IP blocking (residential proxies)
- No infrastructure management
- Serverless scaling
- Built-in monitoring

**vs Running OpenAI in Django:**
- Faster (parallel processing)
- Cheaper (Actor handles retries)
- Simpler (less Django code)
- More reliable (Actor error handling)

**Total simplification:**
- Remove Celery tasks
- Remove local scraping code
- Just receive clean data via webhook
