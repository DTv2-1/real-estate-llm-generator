# 🌐 Residential Proxy Setup Guide

## Why Residential Proxies?

Cloudflare and other anti-bot systems detect **datacenter IPs** (AWS, DigitalOcean, Azure) and block them. Residential proxies use **real ISP IPs** from homes, making them appear as legitimate users.

## Multi-Site Strategy

Our scraper automatically detects which sites need residential proxies:

```python
# Automatically uses proxy for these domains:
CLOUDFLARE_PROTECTED_DOMAINS = [
    'encuentra24.com',  # ✅ Uses proxy
]

# Regular Playwright for other sites:
're.cr',  # ❌ No proxy needed (faster & cheaper)
```

## Recommended Providers (Budget-Friendly to Premium)

### 🥉 **Budget Options ($10-50/month)**

#### 1. **ProxyEmpire** - Best for testing
- **Price**: ~$3/GB (pay-as-you-go)
- **Trial**: No free trial, but cheap to test
- **Format**: `http://username:password@residential.proxyempire.io:9002`
- **Link**: https://proxyempire.io/

#### 2. **Smartproxy** - Good starter
- **Price**: $12.5/GB or $50/month (8GB)
- **Trial**: 14-day money-back guarantee
- **Format**: `http://username:password@gate.smartproxy.com:7000`
- **Link**: https://smartproxy.com/

#### 3. **ProxyScrape** - Cheapest option
- **Price**: $10/month (5GB residential)
- **Trial**: 3-day money-back
- **Format**: `http://username:password@residential.proxyscrape.com:6060`
- **Link**: https://proxyscrape.com/

### 🥈 **Mid-Range Options ($100-300/month)**

#### 4. **Oxylabs** - Reliable and fast
- **Price**: ~$15/GB (min ~$300/month for Business)
- **Trial**: 7-day free trial
- **Format**: `http://username:password@pr.oxylabs.io:7777`
- **Link**: https://oxylabs.io/

#### 5. **IPRoyal** - Good balance
- **Price**: $7/GB (cheaper than most)
- **Trial**: No, but refund available
- **Format**: `http://username:password@geo.iproyal.com:12321`
- **Link**: https://iproyal.com/

### 🥇 **Premium Options ($300-1000/month)**

#### 6. **Bright Data (formerly Luminati)** - Industry standard
- **Price**: ~$12.75/GB (min ~$500/month)
- **Trial**: 7-day free trial with $5 credit
- **Format**: `http://username:password@brd.superproxy.io:22225`
- **Features**: Best success rate, CAPTCHA solver included
- **Link**: https://brightdata.com/

#### 7. **NetNut** - Premium quality
- **Price**: ~$20/GB (starts at $300/month)
- **Trial**: Contact for trial
- **Format**: Custom based on plan
- **Link**: https://netnut.io/

## Setup Instructions

### 1. Choose a Provider

Start with **Smartproxy** or **ProxyEmpire** for testing (cheapest with trials).

### 2. Get Your Credentials

After signing up, you'll receive:
- Username
- Password
- Proxy server address
- Port

### 3. Configure in DigitalOcean

#### Option A: Via DigitalOcean Dashboard

1. Go to your app → Settings → Environment Variables
2. Add new variable:
   ```
   Key: RESIDENTIAL_PROXY_URL
   Value: http://username:password@proxy-server.com:port
   ```
3. Mark as **SECRET** (encrypted)
4. Save and redeploy

#### Option B: Via `.do/app.yaml`

```yaml
envs:
  - key: RESIDENTIAL_PROXY_URL
    type: SECRET
    value: EV[1:encrypt_your_proxy_url_here]
```

### 4. Local Testing

Create/update `.env` file:
```bash
RESIDENTIAL_PROXY_URL=http://username:password@proxy-server.com:port
```

### 5. Test It

```bash
# The scraper will log:
# 🔧 Scraper initialized - Residential proxy: ✅ Configured
# 🛡️ Cloudflare-protected site detected: encuentra24.com - Using residential proxy
# 🌐 Using residential proxy for: https://encuentra24.com/...
```

## Cost Estimation

For scraping **~100 property listings per day**:

| Provider | Monthly Cost | Notes |
|----------|-------------|-------|
| ProxyEmpire | $10-30 | Pay per GB, good for testing |
| Smartproxy | $50 (8GB) | Best value for startups |
| Oxylabs | $300+ | Enterprise-grade |
| Bright Data | $500+ | Best success rate |

**Recommendation**: Start with **Smartproxy $50/month plan** (8GB). If that's not enough, upgrade to Bright Data.

## Adding More Protected Sites

When you encounter Cloudflare on new sites, just add them to the list:

```python
# In core/scraping/scraper.py
CLOUDFLARE_PROTECTED_DOMAINS = [
    'encuentra24.com',
    'newsite.com',      # Add here
    'another-site.cr',  # Add here
]
```

## Troubleshooting

### Proxy Not Working?

1. **Check format**: Must be `http://user:pass@host:port`
2. **Test with curl**:
   ```bash
   curl -x "http://user:pass@host:port" https://encuentra24.com
   ```
3. **Check logs**: Look for "Using residential proxy" message

### Still Getting Blocked?

Try in this order:
1. Add more random delays (increase `random.uniform(5, 10)`)
2. Rotate proxies more frequently (contact provider for rotation settings)
3. Switch to a premium provider (Bright Data)

### Too Expensive?

Options:
1. Only scrape Cloudflare sites 1-2 times per day (cache results)
2. Use **ScraperAPI** ($50/month) - handles proxies for you
3. Hybrid: External API for Encuentra24, direct for other sites

## Alternative: ScraperAPI

If proxies are too complex, use **ScraperAPI**:

```python
# Simple API call instead of Playwright
url = f"https://api.scraperapi.com/?api_key=YOUR_KEY&url={target_url}"
response = httpx.get(url)
```

- **Price**: $50/month (100K requests)
- **Pros**: Handles everything (proxies, CAPTCHA, etc.)
- **Cons**: More expensive per request
- **Link**: https://scraperapi.com

## Support

If you need help choosing or configuring a provider, check:
- Provider comparison: https://scrapeops.io/proxy-providers/comparison/
- Community: r/webscraping on Reddit
