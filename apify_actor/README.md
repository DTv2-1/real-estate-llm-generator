# Costa Rica Real Estate Scraper Actor

Apify Actor for scraping real estate listings from Costa Rica websites with advanced Cloudflare bypass and LLM data extraction.

## Features

- **Intelligent Proxy Routing**: Automatically uses residential proxies for Cloudflare-protected sites
- **Advanced Stealth Techniques**: Navigator mocking, hardware fingerprinting, human behavior simulation
- **LLM Data Extraction**: Uses OpenAI to extract and normalize property data
- **Dual Storage**: Raw HTML in Key-Value Store + structured data in Dataset
- **Provenance Tracking**: Links extracted data back to raw sources

## Supported Websites

- Coldwell Banker Costa Rica
- Encuentra24 Costa Rica (with Cloudflare bypass)
- Any real estate website in Costa Rica

## Input Configuration

### Start URLs (Required)
List of URLs to scrape. Each URL should point to a property listing page or search results.

Example:
```json
{
  "start_urls": [
    { "url": "https://www.coldwellbankercostarica.com/property/search" },
    { "url": "https://www.encuentra24.com/costa-rica-en/real-estate-for-sale" }
  ]
}
```

### Use Residential Proxies (Default: true)
Enable residential proxies for bypassing Cloudflare protection. Required for encuentra24.com.

### Proxy Country (Default: CR)
Two-letter country code for proxy geolocation. Options: CR, US, MX, PA

### Max Listings (Default: 100)
Maximum number of listings to scrape. Set to 0 for unlimited.

### Use LLM Extraction (Default: true)
Extract and normalize data using OpenAI LLM for consistent structured output.

### OpenAI API Key (Optional)
Your OpenAI API key. If not provided, will use the platform secret configured in Actor settings.

## Output

### Dataset
Structured property data with the following fields:

```json
{
  "url": "https://...",
  "title": "Beautiful Beach House",
  "extracted_data": {
    "price": 250000,
    "currency": "USD",
    "beds": 3,
    "baths": 2,
    "size_m2": 150,
    "location": "Tamarindo, Guanacaste",
    "property_type": "house",
    "status": "sale"
  },
  "confidence": {
    "price": 0.98,
    "location": 0.95
  },
  "evidence": {
    "price": "Price: $250,000",
    "location": "Located in Tamarindo..."
  },
  "scraped_at": "2026-01-07T12:00:00Z",
  "raw_html_key": "raw_12345"
}
```

### Key-Value Store
Raw HTML content for each scraped page, stored with keys like `raw_12345`.

## Cost Estimation

### Compute Units
- Basic listing: ~0.01 CU
- With Cloudflare bypass: ~0.03 CU
- Total for 100 listings: ~2-3 CU

### Residential Proxies
- Encuentra24 requires residential proxies
- Cost: $8/GB
- Average: ~0.5 MB per listing
- Total for 100 listings: ~$0.40

### Total Monthly Cost (1000 listings)
- Compute: ~$9 (30 CU × $0.30)
- Proxies: ~$4 (0.5 GB × $8)
- **Total: ~$13/month** (with Starter plan credit)

## Local Development

1. Install dependencies:
```bash
cd apify_actor
pip install -r requirements.txt
playwright install chromium
```

2. Set environment variables:
```bash
export APIFY_TOKEN="your_token"
export OPENAI_API_KEY="your_key"
```

3. Run locally:
```bash
apify run
```

## Deployment

1. Install Apify CLI:
```bash
npm install -g apify-cli
apify login
```

2. Deploy Actor:
```bash
cd apify_actor
apify push
```

3. Configure secrets in Apify Console:
- Go to Settings → Environment Variables
- Add `OPENAI_API_KEY` as secret

## Integration with Existing System

To sync data back to your Django/PostgreSQL backend:

```python
from apify_client import ApifyClient

client = ApifyClient('your_token')

# Run the Actor
run = client.actor('your-username/real-estate-scraper').call(
    run_input={
        'start_urls': [{'url': 'https://...'}],
        'use_residential_proxies': True
    }
)

# Get dataset items
dataset = client.dataset(run['defaultDatasetId'])
for item in dataset.iterate_items():
    # Save to your PostgreSQL database
    save_to_django_db(item)
```

## Troubleshooting

### Cloudflare Blocking
If Cloudflare still blocks requests:
- Ensure `use_residential_proxies` is enabled
- Try different proxy countries
- Increase random delays in code

### LLM Extraction Fails
- Check OpenAI API key is valid
- Verify you have API credits
- HTML content may be too complex

### Rate Limiting
- Add delays between requests
- Reduce `max_listings`
- Use scheduling to spread scraping over time

## Support

For issues or questions:
- GitHub: https://github.com/your-repo
- Email: your-email@example.com
