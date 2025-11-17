from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class MPTIScraper:
    def __init__(self):
        self.base_url = "https://www.mptigh.com/"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'MPTI-Chatbot/1.0'})
    
    def scrape_content(self):
        """Scrape MPTI website content"""
        pages = {
            'home': '', 'about': 'about', 'programs': 'programs', 'courses': 'courses',
            'admissions': 'admissions', 'contact': 'contact', 'tact-program': 'tact-program'
        }
        
        content = {}
        for name, path in pages.items():
            url = urljoin(self.base_url, path)
            page_content = self.scrape_page(url)
            if page_content:
                content[name] = page_content
                logger.info(f"Scraped {name}: {len(page_content)} chars")
        
        return content
    
    def scrape_page(self, url):
        """Scrape individual page with external links"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract external links before removing elements
            external_links = self.extract_external_links(soup)
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()
            
            # Extract content
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "MPTI"
            
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
            
            # Add external links info
            links_text = ""
            if external_links:
                links_text = "\n\nExternal Links:\n" + "\n".join([f"• {link['text']}: {link['url']}" for link in external_links])
            
            return f"{title_text}\n\n{clean_content[:1800]}{links_text}"
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None
    
    def extract_external_links(self, soup):
        """Extract external links like Microsoft Forms, applications, etc."""
        external_links = []
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Check for external domains
            external_domains = [
                'forms.microsoft.com', 'forms.office.com', 'docs.google.com',
                'typeform.com', 'surveymonkey.com', 'jotform.com',
                'application', 'apply', 'register', 'enroll'
            ]
            
            # Check if it's an external link or application form
            if href and text and len(text) > 3:
                is_external = any(domain in href.lower() for domain in external_domains)
                is_application = any(word in text.lower() for word in ['apply', 'application', 'register', 'enroll', 'form', 'submit'])
                
                if is_external or is_application:
                    # Clean up the link text
                    clean_text = re.sub(r'\s+', ' ', text).strip()
                    if len(clean_text) < 100:  # Reasonable link text length
                        external_links.append({
                            'text': clean_text,
                            'url': href if href.startswith('http') else urljoin(self.base_url, href),
                            'type': 'form' if 'form' in href.lower() else 'application'
                        })
        
        return external_links[:5]  # Limit to 5 most relevant links

class IntelligentChatbot:
    def __init__(self):
        self.scraper = MPTIScraper()
        self.knowledge = {}
        self.external_links = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        """Load MPTI knowledge"""
        logger.info("Loading MPTI knowledge...")
        scraped_content = self.scraper.scrape_content()
        
        # Add scraped content and extract external links
        self.knowledge.update(scraped_content)
        self.extract_all_external_links()
        
        # Only add TACT details if not found in scraped content
        if not any('tact' in content.lower() for content in scraped_content.values()):
            self.knowledge['tact_details'] = """TACT Program - Technical Advancement and Certification Training

The TACT program is MPTI's professional development initiative for advanced technical training.

For more information: https://www.mptigh.com/tact-program"""
        
        logger.info(f"Knowledge loaded: {len(self.knowledge)} sections")
    
    def extract_all_external_links(self):
        """Extract external links from all content"""
        for section, content in self.knowledge.items():
            if "External Links:" in content:
                links_section = content.split("External Links:")[1]
                links = []
                for line in links_section.split("\n"):
                    if line.strip().startswith("•"):
                        parts = line.strip()[2:].split(": ", 1)
                        if len(parts) == 2:
                            links.append({"text": parts[0], "url": parts[1]})
                if links:
                    self.external_links[section] = links
        
        logger.info(f"External links found: {sum(len(links) for links in self.external_links.values())}")
    
    def analyze_intent(self, message):
        """Analyze user intent"""
        message_lower = message.lower()
        
        # Check history first (more specific)
        if any(phrase in message_lower for phrase in ['how long', 'when founded', 'when established', 'history', 'existence', 'started', 'began', 'company being', 'been in existence', 'how old']):
            return 'history'
        elif any(word in message_lower for word in ['tact', 'technical advancement']):
            return 'tact_program'
        elif any(word in message_lower for word in ['apply', 'admission', 'enroll', 'form']):
            return 'application'
        elif any(word in message_lower for word in ['program', 'course', 'study']):
            return 'programs'
        elif any(word in message_lower for word in ['contact', 'phone', 'email']):
            return 'contact'
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return 'greeting'
        else:
            return 'general'
    
    def find_relevant_content(self, message):
        """Find relevant content"""
        message_lower = message.lower()
        relevant = []
        
        for section, content in self.knowledge.items():
            content_lower = content.lower()
            score = 0
            
            # Check for keyword matches
            words = message_lower.split()
            for word in words:
                if len(word) > 3 and word in content_lower:
                    score += content_lower.count(word)
            
            if score > 0:
                relevant.append((section, content, score))
        
        # Sort by relevance score
        relevant.sort(key=lambda x: x[2], reverse=True)
        return [content for _, content, _ in relevant[:2]]
    
    def get_external_links_for_intent(self, intent):
        """Get external links relevant to user intent"""
        relevant_links = []
        
        # Get links from relevant sections
        intent_sections = {
            'tact_program': ['tact-program', 'tact_details'],
            'application': ['admissions', 'tact-program'],
            'programs': ['programs', 'courses'],
            'contact': ['contact']
        }
        
        sections = intent_sections.get(intent, [])
        for section in sections:
            if section in self.external_links:
                relevant_links.extend(self.external_links[section])
        
        return relevant_links[:3]  # Limit to 3 most relevant
    
    def generate_response(self, message):
        """Generate intelligent response with external links"""
        intent = self.analyze_intent(message)
        relevant_content = self.find_relevant_content(message)
        external_links = self.get_external_links_for_intent(intent)
        
        # Build response based on intent
        if intent == 'greeting':
            response = """👋 Hello! Welcome to MPTI Technical Institute!

I'm your MPTI Assistant. I can help you with:
• 🎓 Programs and Courses
• 📝 TACT Program Information
• 🏫 Admissions Process
• 📞 Contact Information

What would you like to know about MPTI?"""
        
        elif intent == 'tact_program':
            # Use scraped TACT content first
            if relevant_content:
                response = f"""🚀 **TACT Program Information**

{relevant_content[0][:500]}...

**Learn More:** https://www.mptigh.com/tact-program
**Apply:** https://www.mptigh.com/admissions"""
            else:
                response = """🚀 **TACT Program**

Technical Advancement and Certification Training program for professional development.

**Learn More:** https://www.mptigh.com/tact-program
**Apply:** https://www.mptigh.com/admissions"""
        
        elif intent == 'application':
            response = """📝 **Ready to Join MPTI Technical Institute?**

**Application Process:**
• Applications accepted year-round
• Various entry requirements by program
• Financial aid available
• Scholarship opportunities"""
            
            # Add external application links
            if external_links:
                response += "\n\n**📋 Direct Application Links:**"
                for link in external_links:
                    response += f"\n🔗 **{link['text']}**: {link['url']}"
            
            response += """

**Next Steps:**
🎯 **Start Application:** https://www.mptigh.com/admissions
📞 **Contact Admissions:** https://www.mptigh.com/contact
📋 **View Programs:** https://www.mptigh.com/programs

**Need help choosing a program?** Ask me about our TACT program or other technical courses!"""
        
        elif intent == 'programs':
            response = """🎓 **MPTI Technical Institute Programs**

**Our Offerings:**
• Technical Education Programs
• Engineering & Technology Courses
• Professional Certification Programs
• TACT Program (Technical Advancement)
• Skills Development Training

**Popular Programs:**
• Mechanical Engineering Technology
• Electrical Engineering Technology
• Welding and Fabrication
• Instrumentation and Control

**Explore More:**
📋 **All Programs:** https://www.mptigh.com/programs
🚀 **TACT Program:** https://www.mptigh.com/tact-program
📝 **Apply:** https://www.mptigh.com/admissions"""
        
        elif intent == 'contact':
            response = """📞 **Get in Touch with MPTI**

**Contact Information:**
🌐 **Website:** https://www.mptigh.com/
📧 **Contact Page:** https://www.mptigh.com/contact

**Quick Actions:**
• 📝 **Apply Now:** https://www.mptigh.com/admissions
• 🎓 **View Programs:** https://www.mptigh.com/programs
• 🏫 **About MPTI:** https://www.mptigh.com/about

**Need specific information?** Ask me about our programs, admissions, or the TACT program!"""
        
        elif intent == 'history':
            # Use scraped content first
            if relevant_content:
                response = f"""🏛️ **MPTI Technical Institute History**

{relevant_content[0][:600]}...

**Learn More:**
🏫 **About MPTI:** https://www.mptigh.com/about
🎓 **Programs:** https://www.mptigh.com/programs"""
            else:
                response = """🏛️ **MPTI Technical Institute History**

MPTI Technical Institute has been serving the technical education community, establishing itself as a leading institution in technical and engineering education.

**Learn More About Our Journey:**
🏫 **About MPTI:** https://www.mptigh.com/about
🎓 **Programs:** https://www.mptigh.com/programs"""
        
        else:
            # Always use scraped content when available
            if relevant_content:
                response = f"""**MPTI Information**

{relevant_content[0][:500]}...

**Learn More:**
🎓 **Programs:** https://www.mptigh.com/programs
🚀 **TACT Program:** https://www.mptigh.com/tact-program
📝 **Apply:** https://www.mptigh.com/admissions"""
            else:
                response = """🏫 **Welcome to MPTI Technical Institute!**

I'm here to help with MPTI information.

**Quick Links:**
• **Programs:** https://www.mptigh.com/programs
• **TACT Program:** https://www.mptigh.com/tact-program
• **Apply:** https://www.mptigh.com/admissions

What would you like to know?"""
        
        return response
    
    def get_cta_suggestions(self, intent):
        """Get contextual call-to-action suggestions with external links"""
        cta_map = {
            'tact_program': [
                {'text': 'Learn More About TACT', 'url': 'https://www.mptigh.com/tact-program'},
                {'text': 'Apply for TACT Program', 'url': 'https://www.mptigh.com/admissions'}
            ],
            'application': [
                {'text': 'Start Application', 'url': 'https://www.mptigh.com/admissions'},
                {'text': 'Contact Admissions', 'url': 'https://www.mptigh.com/contact'}
            ],
            'programs': [
                {'text': 'View All Programs', 'url': 'https://www.mptigh.com/programs'},
                {'text': 'Apply Now', 'url': 'https://www.mptigh.com/admissions'}
            ],
            'contact': [
                {'text': 'Contact Us', 'url': 'https://www.mptigh.com/contact'},
                {'text': 'Visit Campus', 'url': 'https://www.mptigh.com/about'}
            ],
            'history': [
                {'text': 'Learn About MPTI', 'url': 'https://www.mptigh.com/about'},
                {'text': 'View Programs', 'url': 'https://www.mptigh.com/programs'}
            ]
        }
        
        base_ctas = cta_map.get(intent, [
            {'text': 'Explore Programs', 'url': 'https://www.mptigh.com/programs'},
            {'text': 'Apply Now', 'url': 'https://www.mptigh.com/admissions'}
        ])
        
        # Add external links as CTAs
        external_links = self.get_external_links_for_intent(intent)
        for link in external_links:
            base_ctas.append({
                'text': f"📋 {link['text']}",
                'url': link['url'],
                'type': 'external'
            })
        
        return base_ctas

# Initialize chatbot
chatbot = IntelligentChatbot()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'knowledge_sections': len(chatbot.knowledge),
        'external_links': sum(len(links) for links in chatbot.external_links.values())
    })


@app.route('/', methods=['GET', 'HEAD'])
def root():
    """Root endpoint used by PaaS health checks. Returns same payload as /health."""
    return health_check()

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with external links support"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        start_time = datetime.now()
        
        # Generate response
        response = chatbot.generate_response(message)
        intent = chatbot.analyze_intent(message)
        ctas = chatbot.get_cta_suggestions(intent)
        external_links = chatbot.get_external_links_for_intent(intent)
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Chat response generated - Intent: {intent}, External Links: {len(external_links)}, Time: {response_time:.2f}s")
        
        return jsonify({
            'reply': response,
            'intent': intent,
            'ctas': ctas,
            'external_links': external_links,
            'response_time': response_time,
            'source': 'enhanced_mpti_bot'
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'reply': 'I apologize for the error. Please visit https://www.mptigh.com/ for information.',
            'error': 'Internal server error'
        }), 500

@app.route('/refresh', methods=['POST'])
def refresh_knowledge():
    """Refresh chatbot knowledge"""
    try:
        chatbot.load_knowledge()
        return jsonify({
            'message': 'Knowledge refreshed successfully',
            'sections': len(chatbot.knowledge),
            'external_links': sum(len(links) for links in chatbot.external_links.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    logger.info("🚀 Enhanced MPTI Chatbot with External Links")
    logger.info(f"📊 Knowledge: {len(chatbot.knowledge)} sections loaded")
    logger.info(f"🔗 External Links: {sum(len(links) for links in chatbot.external_links.values())} found")
    logger.info(f"🌐 Server: {host}:{port}")
    logger.info("✅ Ready to assist with MPTI inquiries and navigate to external forms!")
    
    app.run(host=host, port=port, debug=True)