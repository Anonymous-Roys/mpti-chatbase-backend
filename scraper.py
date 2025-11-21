import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'MPTI-Chatbot/1.0'})
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
    
    def scrape_page(self, url):
        """Scrape single page"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
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