"""
Apify Actor for Real Estate HTML Collection
Scrapes property listings with advanced Cloudflare bypass
LLM extraction happens in Django backend
"""

import asyncio
import os
from typing import Dict, List, Optional
from urllib.parse import urlparse
import random

from apify import Actor
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


# Domain classification for intelligent routing
CLOUDFLARE_PROTECTED_DOMAINS = ['encuentra24.com']
EXTERNAL_SERVICE_DOMAINS = []


# User agent pool for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
]


def needs_residential_proxy(url: str) -> bool:
    """Check if URL requires residential proxy for Cloudflare bypass"""
    domain = urlparse(url).netloc
    return any(protected in domain for protected in CLOUDFLARE_PROTECTED_DOMAINS)


async def scrape_with_playwright(url: str, proxy_url: Optional[str] = None) -> Dict:
    """
    Scrape URL using Playwright with advanced stealth techniques
    
    Args:
        url: Target URL
        proxy_url: Optional residential proxy URL for Cloudflare bypass
        
    Returns:
        Dictionary with HTML content and metadata
    """
    
    # Prepare browser args for stealth
    browser_args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--start-maximized',
        '--disable-infobars',
        '--disable-blink-features',
        '--hide-scrollbars',
        '--mute-audio'
    ]
    
    async with async_playwright() as p:
        # Configure proxy if needed
        proxy_config = None
        if proxy_url:
            Actor.log.info(f'Using residential proxy for {url}')
            proxy_config = {'server': proxy_url}
        
        # Launch browser
        browser = await p.chromium.launch(
            headless=True,
            args=browser_args
        )
        
        # Create context with proxy
        user_agent = random.choice(USER_AGENTS)
        context = await browser.new_context(
            proxy=proxy_config,
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        # Apply stealth techniques
        await context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Mock hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            
            // Mock device memory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            
            // Mock platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'MacIntel'
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override chrome property
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Hide automation in iframes
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    return window;
                }
            });
        """)
        
        page = await context.new_page()
        
        # Random initial delay
        await asyncio.sleep(random.uniform(2, 5))
        
        # Navigate to page
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # Wait for network to be idle
        await page.wait_for_load_state('networkidle', timeout=30000)
        
        # Simulate human behavior
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Scroll randomly
        for _ in range(random.randint(2, 5)):
            await page.evaluate(f'window.scrollBy(0, {random.randint(300, 800)})')
            await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Get page content
        html_content = await page.content()
        title = await page.title()
        
        await browser.close()
        
        return {
            'html': html_content,
            'title': title,
            'url': url,
            'status': 'success'
        }





async def main() -> None:
    """
    Main Actor coroutine
    Scrapes HTML only - LLM extraction happens in Django backend
    """
    async with Actor:
        # Get Actor input
        actor_input = await Actor.get_input() or {}
        
        start_urls = actor_input.get('start_urls', [])
        use_residential_proxies = actor_input.get('use_residential_proxies', True)
        max_listings = actor_input.get('max_listings', 100)
        
        if not start_urls:
            Actor.log.info('No start URLs provided, exiting')
            return
        
        Actor.log.info(f'Starting HTML scraping for {len(start_urls)} URLs')
        Actor.log.info(f'Residential proxies: {use_residential_proxies}')
        Actor.log.info(f'Max listings: {max_listings}')
        
        # Create proxy configuration for Cloudflare bypass
        proxy_cfg = None
        if use_residential_proxies:
            Actor.log.info('Configuring residential proxies (Costa Rica)')
            proxy_cfg = await Actor.create_proxy_configuration(
                groups=['RESIDENTIAL'],
                country_code='CR'
            )
        
        # Process each URL
        successful = 0
        failed = 0
        
        for url_entry in start_urls:
            if successful >= max_listings:
                Actor.log.info(f'Reached max listings limit: {max_listings}')
                break
                
            url = url_entry.get('url') if isinstance(url_entry, dict) else url_entry
            if not url:
                continue
            
            Actor.log.info(f'Processing {url}')
            
            try:
                # Determine if we need proxy
                proxy_url = None
                if proxy_cfg and needs_residential_proxy(url):
                    Actor.log.info(f'Using residential proxy for Cloudflare-protected: {url}')
                    proxy_url = await proxy_cfg.new_url()
                
                # Scrape page with Playwright
                scrape_result = await scrape_with_playwright(url, proxy_url)
                
                if scrape_result['status'] != 'success':
                    Actor.log.warning(f'Failed to scrape {url}')
                    failed += 1
                    continue
                
                # Store raw HTML in Key-Value Store
                raw_html_key = f'html_{successful + 1}'
                await Actor.set_value(
                    raw_html_key,
                    scrape_result['html'],
                    content_type='text/html'
                )
                Actor.log.info(f'Stored HTML as {raw_html_key} ({len(scrape_result["html"])} bytes)')
                
                # Push metadata to Dataset (Django will fetch HTML and extract)
                dataset_item = {
                    'url': url,
                    'title': scrape_result['title'],
                    'html_key': raw_html_key,
                    'html_size_bytes': len(scrape_result['html']),
                    'scraped_at': str(Actor.get_env().get('started_at')),
                    'actor_run_id': Actor.get_env().get('actor_run_id'),
                    'used_residential_proxy': proxy_url is not None
                }
                
                await Actor.push_data(dataset_item)
                
                Actor.log.info(f'Successfully scraped {url} (Total: {successful + 1}/{max_listings})')
                successful += 1
                
            except Exception as e:
                Actor.log.error(f'Error processing {url}: {e}')
                failed += 1
                await Actor.push_data({
                    'url': url,
                    'error': str(e),
                    'scraped_at': str(Actor.get_env().get('started_at'))
                })
                continue
        
        Actor.log.info(f'Scraping completed: {successful} successful, {failed} failed')


if __name__ == '__main__':
    asyncio.run(main())
