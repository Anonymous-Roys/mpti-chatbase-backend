import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging
import threading
import time
from datetime import datetime
import urllib3

# Disable SSL warnings for aggressive scraping
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, base_url, timeout=8):
        self.base_url = base_url
        self.timeout = max(timeout, 30)  # Minimum 30 seconds for aggressive scraping
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MPTI-Chatbot/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'close'  # Prevent connection reuse issues
        })
        self.last_scrape = None
        self.lock = threading.Lock()
    
    def scrape_pages(self, pages):
        """Scrape multiple pages"""
        content = {}
        for name, path in pages.items():
            url = urljoin(self.base_url, path)
            page_content = self.scrape_page(url)
            if page_content:
                content[name] = page_content
                logger.info(f"Scraped {name}: {len(page_content)} chars")
        return content
    
    def scrape_page(self, url, max_retries=5):
        """Scrape single page with retry logic"""
        for attempt in range(max_retries + 1):
            try:
                # Use shorter timeout with explicit connect and read timeouts
                response = self.session.get(
                    url, 
                    timeout=(10, self.timeout),  # (connect_timeout, read_timeout)
                    allow_redirects=True,
                    stream=False,
                    verify=False  # Ignore SSL issues
                )
                response.raise_for_status()
                
                # Check content length to avoid huge responses
                if len(response.content) > 500000:  # 500KB limit
                    logger.warning(f"Large response from {url}, truncating")
                    content = response.content[:500000]
                else:
                    content = response.content
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(["script", "style", "nav", "header", "footer"]):
                    element.decompose()
                
                # Extract content
                title = soup.find('title')
                title_text = title.get_text().strip() if title else "Page"
                
                # Get main content
                main_content = ""
                for selector in ['main', '.content', '#content', 'article']:
                    elements = soup.select(selector)
                    if elements:
                        main_content = ' '.join([elem.get_text().strip() for elem in elements])
                        break
                
                if not main_content:
                    body = soup.find('body')
                    main_content = body.get_text() if body else ""
                
                # Clean content
                lines = (line.strip() for line in main_content.splitlines())
                clean_content = ' '.join(line for line in lines if line and len(line) > 2)
                
                return f"{title_text}\n\n{clean_content[:1800]}"
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries:
                    wait_time = min((attempt + 1) * 3, 15)  # Progressive backoff, max 15s
                    logger.warning(f"Timeout/connection error for {url}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Failed to scrape {url} after {max_retries + 1} attempts: {e}")
                    # Try one last time with different approach
                    return self._emergency_scrape(url)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logger.info(f"Page not found (404): {url} - skipping")
                    return None
                elif attempt < max_retries:
                    logger.warning(f"HTTP error for {url}: {e}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"Failed to scrape {url}: {e}")
                    return self._emergency_scrape(url)
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Error scraping {url}: {e}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"Failed to scrape {url}: {e}")
                    return self._emergency_scrape(url)
        
        return None
    
    def _emergency_scrape(self, url):
        """Last resort scraping with minimal requirements"""
        try:
            # Try with requests without session
            response = requests.get(
                url, 
                timeout=60,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                verify=False,
                allow_redirects=True
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                clean_text = ' '.join(text.split())[:1000]
                logger.info(f"Emergency scrape successful for {url}")
                return f"Emergency Scraped Content\n\n{clean_text}"
        except:
            pass
        return None

class LinkExtractor:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def extract_external_links(self, soup):
        """Extract external links from soup"""
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