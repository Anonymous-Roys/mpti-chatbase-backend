import asyncio
import logging
from datetime import datetime
from async_scraper import AsyncWebScraper
from cache_manager import CacheManager
from monitoring import metrics, structured_logger

logger = logging.getLogger(__name__)

class AsyncKnowledgeManager:
    def __init__(self, scraper, scrape_interval=3600, cache_type='memory'):
        self.scraper = scraper
        self.scrape_interval = scrape_interval
        self.knowledge = {}
        self.status = 'idle'
        self.cache = CacheManager(cache_type, ttl=scrape_interval)
        self.fallback_knowledge = self._get_fallback_knowledge()
        self._background_task = None
        self._initialize()
    
    def _get_fallback_knowledge(self):
        """Enhanced fallback knowledge when scraping fails"""
        return {
            'home': '''MPTI Technical Institute - Leading Technical Education in Ghana
            
MPTI Technical Institute is a premier institution offering technical and vocational education programs.
Programs: Technical Education, Engineering Technology, Professional Certifications, TACT Program
Website: https://www.mptigh.com/
Contact: Visit our website for current contact information and application details.''',
            
            'programs': '''MPTI Programs and Courses
            
Technical Education Programs:
- Engineering Technology
- Information Technology
- Business and Management
- Professional Certifications
- TACT (Technical Advancement and Certification Training)
            
For detailed program information, admission requirements, and applications, visit https://www.mptigh.com/''',
            
            'admissions': '''MPTI Admissions Information
            
Admission Requirements:
- Completed application form
- Academic transcripts
- Relevant certificates
            
Application Process:
1. Visit https://www.mptigh.com/ for current application forms
2. Submit required documents
3. Await admission decision
            
For specific admission requirements and deadlines, please visit our website or contact the admissions office.'''
        }
    
    def _initialize(self):
        """Initialize with fallback and start background updates"""
        # Try to load from cache first
        cached_knowledge = self.cache.get('knowledge_base')
        if cached_knowledge:
            self.knowledge = cached_knowledge
            metrics.record_cache_hit('hit')
            structured_logger.log_cache_operation('GET', 'knowledge_base', True)
            logger.info("Knowledge loaded from cache")
        else:
            self.knowledge = self.fallback_knowledge.copy()
            metrics.record_cache_hit('miss')
            structured_logger.log_cache_operation('GET', 'knowledge_base', False)
        
        # Start background task
        self._start_background_updates()
    
    def _start_background_updates(self):
        """Start background update task"""
        async def update_worker():
            while True:
                try:
                    await self.async_update_knowledge()
                    await asyncio.sleep(self.scrape_interval)
                except Exception as e:
                    logger.error(f"Background async update error: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error
        
        self._background_task = asyncio.create_task(update_worker())
        logger.info("Background async knowledge updates started")
    
    async def async_update_knowledge(self):
        """Update knowledge from scraper asynchronously"""
        try:
            self.status = 'updating'
            structured_logger.logger.info("ASYNC SCRAPING: Starting concurrent page scraping...")
            
            # Core pages that exist - scrape concurrently
            pages = {
                'home': '', 
                'about': 'about', 
                'programs': 'programs', 
                'courses': 'courses', 
                'admissions': 'admissions', 
                'contact': 'contact', 
                'tact-program': 'tact-program'
            }
            
            # Async scraping with concurrent execution
            scraped_content = await self.scraper.scrape_pages(pages)
            
            # If initial scraping fails, try individual pages
            if not scraped_content or len(scraped_content) < 2:
                logger.warning("Initial async scraping failed, trying individual pages...")
                individual_content = {}
                
                # Create individual tasks
                tasks = []
                for name, path in pages.items():
                    task = asyncio.create_task(self._scrape_individual_page(name, path))
                    tasks.append(task)
                
                # Wait for all individual tasks
                individual_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in individual_results:
                    if isinstance(result, tuple) and len(result) == 2:
                        name, content = result
                        if content:
                            individual_content[name] = content
                            logger.info(f"Successfully async scraped {name} individually")
                
                # Merge results
                if individual_content:
                    if scraped_content:
                        scraped_content.update(individual_content)
                    else:
                        scraped_content = individual_content
            
            # AGGRESSIVE: Accept ANY scraped content (even 1 page)
            if scraped_content and len(scraped_content) > 0:
                self.knowledge.update(scraped_content)
                self.cache.set('knowledge_base', self.knowledge)
                self.scraper.last_scrape = datetime.now()
                
                metrics.record_scrape(len(scraped_content), True)
                structured_logger.log_scrape_operation(len(scraped_content), True)
                logger.info(f"ASYNC SCRAPING SUCCESS: {len(scraped_content)} pages updated")
            else:
                metrics.record_scrape(0, False)
                structured_logger.log_scrape_operation(0, False, "All async scraping attempts failed")
                logger.error("ASYNC SCRAPING FAILED: All attempts exhausted")
                # Still ensure fallback knowledge exists
                if not self.knowledge:
                    self.knowledge = self.fallback_knowledge.copy()
                    logger.info("Loaded fallback knowledge as last resort")
            
            self.status = 'completed'
            
        except Exception as e:
            metrics.record_scrape(0, False)
            structured_logger.log_scrape_operation(0, False, str(e))
            structured_logger.log_error('async_knowledge_manager', str(e))
            logger.error(f"Async knowledge update failed: {e}")
            self.status = 'failed'
    
    async def _scrape_individual_page(self, name, path):
        """Scrape individual page asynchronously"""
        try:
            url = f"{self.scraper.base_url.rstrip('/')}/{path}" if path else self.scraper.base_url
            
            # Create a single-page scraping task
            pages = {name: path}
            result = await self.scraper.scrape_pages(pages)
            
            if result and name in result:
                return name, result[name]
            
            await asyncio.sleep(2)  # Brief delay between individual attempts
            return name, None
            
        except Exception as e:
            logger.warning(f"Failed individual async scrape of {name}: {e}")
            return name, None
    
    def get_knowledge(self):
        """Get current knowledge (sync method)"""
        return self.knowledge.copy()
    
    def search_content(self, query):
        """Search for relevant content with caching (sync method)"""
        cache_key = f"search:{hash(query.lower())}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            metrics.record_cache_hit('hit')
            structured_logger.log_cache_operation('GET', cache_key, True)
            return cached_result
        
        metrics.record_cache_hit('miss')
        structured_logger.log_cache_operation('GET', cache_key, False)
        
        # Search in knowledge
        query_lower = query.lower()
        relevant = []
        
        for section, content in self.knowledge.items():
            content_lower = content.lower()
            score = 0
            
            words = query_lower.split()
            for word in words:
                if len(word) > 3 and word in content_lower:
                    score += content_lower.count(word)
            
            if score > 0:
                relevant.append((section, content, score))
        
        relevant.sort(key=lambda x: x[2], reverse=True)
        result = [content for _, content, _ in relevant[:2]]
        
        # Cache the result
        self.cache.set(cache_key, result)
        structured_logger.log_cache_operation('SET', cache_key)
        
        return result
    
    async def force_refresh(self):
        """Force immediate async refresh"""
        await self.async_update_knowledge()
    
    def cleanup(self):
        """Cleanup background tasks"""
        if self._background_task:
            self._background_task.cancel()
            logger.info("Async background task cancelled")