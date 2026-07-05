import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging
import time
from datetime import datetime
import ssl

logger = logging.getLogger(__name__)

class AsyncWebScraper:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.last_scrape = None
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
        
    async def scrape_pages(self, pages):
        """Scrape multiple pages concurrently"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10)
        timeout = aiohttp.ClientTimeout(total=self.timeout, connect=5)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'MPTI-Chatbot/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
        ) as session:
            tasks = []
            for name, path in pages.items():
                url = urljoin(self.base_url, path)
                task = asyncio.create_task(self._scrape_page_with_semaphore(session, name, url))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            content = {}
            for result in results:
                if isinstance(result, tuple) and len(result) == 2:
                    name, page_content = result
                    if page_content:
                        content[name] = page_content
                        logger.info(f"Async scraped {name}: {len(page_content)} chars")
                elif isinstance(result, Exception):
                    logger.error(f"Scraping task failed: {result}")
            
            return content
    
    async def _scrape_page_with_semaphore(self, session, name, url):
        """Scrape single page with semaphore control"""
        async with self.semaphore:
            return await self._scrape_page(session, name, url)
    
    async def _scrape_page(self, session, name, url, max_retries=3):
        """Scrape single page with async retry logic"""
        for attempt in range(max_retries + 1):
            try:
                async with session.get(url) as response:
                    if response.status == 404:
                        logger.info(f"Page not found (404): {url} - skipping")
                        return name, None
                    
                    response.raise_for_status()
                    
                    # Read and decode full response as text
                    html = await response.text(encoding='utf-8', errors='replace')
                    if len(html) > 1000000:  # 1MB text limit - safe to truncate text at word boundary
                        logger.warning(f"Large response from {url}, truncating")
                        html = html[:1000000]
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(["script", "style", "nav", "header", "footer", "noscript"]):
                        element.decompose()
                    
                    # Extract content
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else "Page"
                    
                    # Get main content - try multiple selectors
                    main_content = ""
                    for selector in ['main', '[role="main"]', '.entry-content', '.post-content', '.page-content', '.content', '#content', '#main', 'article', '.site-content']:
                        elements = soup.select(selector)
                        if elements:
                            main_content = ' '.join([elem.get_text(separator=' ', strip=True) for elem in elements])
                            if len(main_content) > 100:  # Only accept if meaningful content found
                                break
                    
                    if not main_content or len(main_content) < 100:
                        body = soup.find('body')
                        main_content = body.get_text(separator=' ', strip=True) if body else ""
                    
                    # Clean content
                    lines = (line.strip() for line in main_content.splitlines())
                    clean_content = ' '.join(line for line in lines if line and len(line) > 2)
                    clean_content = re.sub(r' {2,}', ' ', clean_content).strip()
                    
                    return name, f"{title_text}\n\n{clean_content[:3000]}"
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Async timeout/error for {url}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries + 1})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Failed to async scrape {url} after {max_retries + 1} attempts: {e}")
                    return name, None
            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {e}")
                return name, None
        
        return name, None

class AsyncLinkExtractor:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def extract_external_links(self, soup):
        """Extract external links from soup (sync method)"""
        external_links = []
        links = soup.find_all('a', href=True)
        
        external_domains = [
            'forms.microsoft.com', 'forms.office.com', 'docs.google.com',
            'typeform.com', 'surveymonkey.com', 'jotform.com'
        ]
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            if href and text and len(text) > 3:
                is_external = any(domain in href.lower() for domain in external_domains)
                is_application = any(word in text.lower() for word in ['apply', 'application', 'register', 'enroll', 'form'])
                
                if is_external or is_application:
                    clean_text = re.sub(r'\s+', ' ', text).strip()
                    if len(clean_text) < 100:
                        external_links.append({
                            'text': clean_text,
                            'url': href if href.startswith('http') else urljoin(self.base_url, href),
                            'type': 'form' if 'form' in href.lower() else 'application'
                        })
        
        return external_links[:5]