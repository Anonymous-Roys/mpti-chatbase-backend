from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# Handle optional dependencies gracefully
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    print("Warning: python-dotenv not available - using environment variables only")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mpti_chatbot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Store conversations
conversations = {}

class MPTIWebsiteScraper:
    def __init__(self):
        self.base_url = "https://www.mptigh.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MPTI-Chatbot/1.0 (Educational Purpose)'
        })
        self.visited_urls = set()
    
    def scrape_website_content(self):
        """Scrape MPTI website for content"""
        try:
            logger.info("Starting MPTI website scraping...")
            
            core_pages = {
                'home': '',
                'about': 'about',
                'courses': 'courses',
                'programs': 'programs',
                'admissions': 'admissions',
                'contact': 'contact',
                'tact-program': 'tact-program',
                'mechanical-engineering': 'mechanicalengineering',
                'electrical-engineering': 'electricalengineering',
                'welding-fabrication': 'weldingandfabrication',
                'instrumentation': 'instrumentation',
                'equipment-training': 'equipmenttraining'
            }
            
            website_content = {}
            
            for page_name, page_path in core_pages.items():
                url = urljoin(self.base_url, page_path)
                content = self.scrape_page(url)
                if content:
                    website_content[page_name] = content
                    logger.info(f"Scraped {page_name}: {len(content)} chars")
                time.sleep(1)  # Be respectful
            
            logger.info(f"Successfully scraped {len(website_content)} pages")
            return website_content
            
        except Exception as e:
            logger.error(f"Website scraping failed: {e}")
            return {}
    
    def scrape_page(self, url):
        """Scrape a single page"""
        try:
            if url in self.visited_urls:
                return None
            
            self.visited_urls.add(url)
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()
            
            # Get page title
            title = soup.find('title')
            page_title = title.get_text().strip() if title else "MPTI Page"
            
            # Extract main content
            content_selectors = ['main', '.content', '#content', 'article', '.entry-content']
            main_content = ""
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    main_content = ' '.join([elem.get_text().strip() for elem in elements])
                    if len(main_content) > 200:
                        break
            
            # Fallback to body
            if not main_content or len(main_content) < 100:
                body = soup.find('body')
                if body:
                    main_content = body.get_text()
            
            # Clean up text
            lines = (line.strip() for line in main_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_content = ' '.join(chunk for chunk in chunks if chunk and len(chunk) > 2)
            
            # Build full content
            full_content = f"Page: {page_title}\n\n{clean_content}"
            
            return full_content[:3000] if len(clean_content) > 50 else None
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None

class SimpleKnowledgeBase:
    def __init__(self):
        self.documents = {}
        self.scraper = MPTIWebsiteScraper()
        self.available = True
        self.load_website_content()
        logger.info("Knowledge base initialized")
    
    def load_website_content(self):
        """Load website content on startup"""
        try:
            website_content = self.scraper.scrape_website_content()
            
            loaded_count = 0
            for page_name, content in website_content.items():
                if content and len(content.strip()) > 100:
                    doc_id = f"website_{page_name}"
                    self.documents[doc_id] = content
                    loaded_count += 1
            
            logger.info(f"Loaded {loaded_count} pages from MPTI website")
            
            # Add fallback MPTI info
            if loaded_count == 0:
                self.add_fallback_info()
                
        except Exception as e:
            logger.error(f"Failed to load website content: {e}")
            self.add_fallback_info()
    
    def add_fallback_info(self):
        """Add basic MPTI information as fallback"""
        fallback_info = {
            'mpti_basic': '''MPTI Technical Institute (https://www.mptigh.com/) is a leading technical education institution in Ghana.

Programs & Courses:
• Technical and vocational training programs
• Engineering and technology courses
• Professional certification programs
• Skills development training
• TACT Program - Technical Advancement and Certification Training

Admissions:
• Applications accepted throughout the year
• Various entry requirements depending on program
• Financial aid and scholarship opportunities available

Contact Information:
• Website: https://www.mptigh.com/
• Visit the official website for current contact details

For the most current information about programs, fees, admissions, and facilities, please visit https://www.mptigh.com/'''
        }
        
        for doc_id, content in fallback_info.items():
            self.documents[f"fallback_{doc_id}"] = content
        
        logger.info("Added fallback MPTI information")
    
    def is_available(self):
        return self.available
    
    def search(self, query, n_results=3):
        """Simple search in documents"""
        query_lower = query.lower()
        results = []
        scores = []
        
        for doc_id, content in self.documents.items():
            content_lower = content.lower()
            score = 0
            
            # Simple scoring
            if query_lower in content_lower:
                score += 10
            
            # Word matching
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2:
                    score += content_lower.count(word) * 2
            
            if score > 0:
                results.append(content)
                scores.append(1.0 / (score + 1))
        
        # Sort by best matches
        if results:
            sorted_pairs = sorted(zip(scores, results))
            sorted_results = [result for _, result in sorted_pairs]
            sorted_scores = [score for score, _ in sorted_pairs]
            
            logger.info(f"Found {len(sorted_results)} matches for: '{query}'")
            
            return {
                'documents': [sorted_results[:n_results]],
                'distances': [sorted_scores[:n_results]]
            }
        else:
            logger.info(f"No matches found for: '{query}'")
            return {'documents': [], 'distances': []}

class OllamaAI:
    def __init__(self):
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:1b')
        self.available = self.test_ollama()
        logger.info(f"Ollama AI initialized - Available: {self.available}")
    
    def test_ollama(self):
        """Test if Ollama is running"""
        try:
            response = requests.get(f'{self.ollama_base_url}/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def is_available(self):
        return self.available
    
    def generate_response(self, user_message, context="", history=[]):
        """Generate response using Ollama"""
        if self.available:
            return self.call_ollama_api(user_message, context, history)
        else:
            return self.get_rule_based_response(user_message)
    
    def call_ollama_api(self, user_message, context, history):
        """Call Ollama API"""
        try:
            system_prompt = f"""You are MPTI Assistant for MPTI Technical Institute (https://www.mptigh.com/). 
Provide helpful information about MPTI programs, admissions, and facilities.

{context if context else 'Visit https://www.mptigh.com/ for details.'}"""
            
            prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
            
            response = requests.post(
                f'{self.ollama_base_url}/api/generate',
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.7, 'num_predict': 300}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', '').strip()
                logger.info(f"Ollama response received: {len(ai_response)} characters")
                return ai_response
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self.get_rule_based_response(user_message)
                
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return self.get_rule_based_response(user_message)
    
    def get_rule_based_response(self, user_message):
        """Rule-based fallback responses"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return """Hello! Welcome to MPTI Technical Institute!

I'm your MPTI Assistant. I can help with:
• Programs and Courses
• Admissions Process  
• TACT Program information
• Contact Information

Visit https://www.mptigh.com/ for detailed information.

How can I help you today?"""
        
        if any(word in message_lower for word in ['tact', 'program']):
            return """The TACT (Technical Advancement and Certification Training) program is MPTI's flagship professional development initiative. It provides advanced technical training, industry certifications, and skills enhancement for working professionals.

For detailed information about the TACT program, visit: https://www.mptigh.com/tact-program"""
        
        if any(word in message_lower for word in ['course', 'program', 'study']):
            return """MPTI Technical Institute offers various technical and vocational programs:

• Technical Education Programs
• Engineering & Technology Courses
• Professional Certification Programs
• Skills Development Training

Visit https://www.mptigh.com/ for detailed program information."""
        
        return """Thank you for your interest in MPTI Technical Institute!

For information about our programs, admissions, and facilities, please visit:
https://www.mptigh.com/

How can I assist you with your MPTI inquiries?"""

# Initialize components
try:
    knowledge_base = SimpleKnowledgeBase()
    logger.info("Knowledge base initialized")
except Exception as e:
    logger.error(f"Knowledge base failed: {e}")
    knowledge_base = None

try:
    ai_handler = OllamaAI()
    logger.info("AI handler initialized")
except Exception as e:
    logger.error(f"AI handler failed: {e}")
    ai_handler = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-webscraper',
        'components': {
            'ai_models': ai_handler.is_available() if ai_handler else False,
            'knowledge_base': knowledge_base.is_available() if knowledge_base else False,
            'ollama_configured': True
        }
    })

@app.route('/chat/ai', methods=['POST'])
def chat_ai():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Initialize conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        history = conversations[conversation_id]
        
        # Search knowledge base
        kb_results = knowledge_base.search(user_message, n_results=3) if knowledge_base else {'documents': [], 'distances': []}
        context = ""
        sources_used = 0
        
        if kb_results['documents'] and kb_results['documents'][0]:
            context_parts = []
            for i, doc in enumerate(kb_results['documents'][0][:2]):
                max_length = 800 if i == 0 else 400
                context_parts.append(doc[:max_length])
            
            context = "\n\n--- MPTI Information ---\n".join(context_parts)
            sources_used = len(kb_results['documents'][0])
            logger.info(f"Found {sources_used} relevant sources")
        
        # Generate response
        start_time = datetime.now()
        
        if ai_handler and ai_handler.is_available():
            bot_reply = ai_handler.generate_response(user_message, context, history)
            source = 'ollama_ai'
        else:
            bot_reply = ai_handler.get_rule_based_response(user_message) if ai_handler else "Please visit https://www.mptigh.com/ for information."
            source = 'rule_based'
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Add to history
        history.append({
            'role': 'user',
            'message': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        history.append({
            'role': 'assistant',
            'message': bot_reply,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep history manageable
        if len(history) > 10:
            conversations[conversation_id] = history[-10:]
        
        logger.info(f"Chat completed - Source: {source} | Sources: {sources_used} | Time: {response_time:.2f}s")
        
        return jsonify({
            'reply': bot_reply,
            'conversation_id': conversation_id,
            'source': source,
            'response_time': response_time,
            'sources_used': sources_used
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'reply': 'I apologize, but I encountered an error. Please try again.',
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info("MPTI Chatbase - Webscraper + Ollama")
    logger.info(f"Server: {host}:{port}")
    logger.info(f"AI Engine: {'Ollama Available' if ai_handler and ai_handler.is_available() else 'Rule-Based Only'}")
    logger.info(f"Knowledge Base: {len(knowledge_base.documents) if knowledge_base else 0} documents loaded")
    logger.info("Ready to provide MPTI assistance!")
    
    app.run(host=host, port=port, debug=debug)