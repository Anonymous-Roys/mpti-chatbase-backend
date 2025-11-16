import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class MPTIWebsiteScraper:
    def __init__(self, base_url="https://www.mptigh.com/"):
        self.base_url = base_url
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MPTI-Chatbot-Scraper/1.0'
        })
    
    def scrape_website(self):
        """Scrape the MPTI website for content"""
        try:
            logger.info(f"Starting to scrape MPTI website: {self.base_url}")
            
            # Important pages to scrape
            important_pages = [
                '',  # Homepage
                'about',
                'courses',
                'programs',
                'admissions',
                'contact',
                'facilities',
                'news'
            ]
            
            all_content = {}
            
            for page in important_pages:
                url = urljoin(self.base_url, page)
                content = self.scrape_page(url)
                if content:
                    all_content[page or 'homepage'] = content
                time.sleep(1)  # Be respectful to the server
            
            logger.info(f"Scraped {len(all_content)} pages from MPTI website")
            return all_content
            
        except Exception as e:
            logger.error(f"Website scraping failed: {e}")
            return {}
    
    def scrape_page(self, url):
        """Scrape a single page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract important sections
            title = soup.find('title')
            page_title = title.get_text().strip() if title else url
            
            # Get main content (try to find main content areas)
            main_content = self.extract_main_content(soup)
            
            if main_content:
                text = f"Page: {page_title}\n\n{main_content}"
            else:
                text = f"Page: {page_title}\n\n{text}"
            
            logger.info(f"Scraped page: {url} ({len(text)} characters)")
            return text[:2000]  # Limit content length
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None
    
    def extract_main_content(self, soup):
        """Extract main content from common content areas"""
        content_selectors = [
            'main',
            '.content',
            '#content',
            '.main-content',
            '#main-content',
            '.entry-content',
            '.post-content',
            'article'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                text = ' '.join(element.get_text().strip() for element in elements)
                if len(text) > 100:  # Only return if we have substantial content
                    return text
        
        return None

# Add this endpoint to your app.py
@app.route('/scrape/website', methods=['POST'])
def scrape_website():
    """Scrape MPTI website and add to knowledge base"""
    try:
        data = request.get_json()
        website_url = data.get('url', 'https://www.mptigh.com/')
        
        scraper = MPTIWebsiteScraper(website_url)
        website_content = scraper.scrape_website()
        
        added_count = 0
        for page_name, content in website_content.items():
            if content and len(content) > 50:  # Only add substantial content
                knowledge_base.add_document([content], [{'type': 'website', 'page': page_name}])
                added_count += 1
        
        return jsonify({
            'message': f'Successfully scraped and added {added_count} pages from website',
            'pages_added': added_count,
            'scraped_pages': list(website_content.keys())
        })
        
    except Exception as e:
        logger.error(f"Website scraping endpoint error: {e}")
        return jsonify({'error': 'Website scraping failed'}), 500