from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class IntelligentMPTIScraper:
    def __init__(self):
        self.base_url = "https://www.mptigh.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MPTI-Agent/2.0 (Educational AI Assistant)'
        })
        self.content_map = {}
        self.navigation_structure = {}
    
    def comprehensive_analysis(self):
        """Perform comprehensive website analysis"""
        logger.info("🔍 Starting comprehensive MPTI website analysis...")
        
        # Core pages with specific analysis
        pages_to_analyze = {
            'home': {'url': '', 'type': 'landing', 'priority': 'high'},
            'about': {'url': 'about', 'type': 'informational', 'priority': 'high'},
            'programs': {'url': 'programs', 'type': 'service', 'priority': 'high'},
            'courses': {'url': 'courses', 'type': 'service', 'priority': 'high'},
            'admissions': {'url': 'admissions', 'type': 'conversion', 'priority': 'high'},
            'tact-program': {'url': 'tact-program', 'type': 'service', 'priority': 'high'},
            'contact': {'url': 'contact', 'type': 'conversion', 'priority': 'medium'},
            'mechanical-engineering': {'url': 'mechanicalengineering', 'type': 'service', 'priority': 'medium'},
            'electrical-engineering': {'url': 'electricalengineering', 'type': 'service', 'priority': 'medium'},
            'welding-fabrication': {'url': 'weldingandfabrication', 'type': 'service', 'priority': 'medium'},
            'instrumentation': {'url': 'instrumentation', 'type': 'service', 'priority': 'medium'},
            'equipment-training': {'url': 'equipmenttraining', 'type': 'service', 'priority': 'medium'}
        }
        
        analyzed_content = {}
        
        for page_name, page_info in pages_to_analyze.items():
            url = urljoin(self.base_url, page_info['url'])
            analysis = self.analyze_page(url, page_info['type'], page_info['priority'])
            
            if analysis:
                analyzed_content[page_name] = analysis
                logger.info(f"✅ Analyzed {page_name}: {len(analysis['content'])} chars, {len(analysis['ctas'])} CTAs")
        
        # Build navigation structure
        self.build_navigation_map(analyzed_content)
        
        logger.info(f"🎯 Analysis complete: {len(analyzed_content)} pages analyzed")
        return analyzed_content
    
    def analyze_page(self, url, page_type, priority):
        """Analyze individual page with intelligent extraction"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove noise
            for element in soup(["script", "style", "nav", "header", "footer", ".sidebar"]):
                element.decompose()
            
            analysis = {
                'url': url,
                'type': page_type,
                'priority': priority,
                'title': self.extract_title(soup),
                'meta_description': self.extract_meta_description(soup),
                'content': self.extract_structured_content(soup),
                'key_points': self.extract_key_points(soup),
                'ctas': self.extract_ctas(soup, page_type),
                'contact_info': self.extract_contact_info(soup),
                'programs_mentioned': self.extract_programs(soup),
                'navigation_hints': self.extract_navigation_hints(soup)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze {url}: {e}")
            return None
    
    def extract_title(self, soup):
        """Extract page title"""
        title = soup.find('title')
        return title.get_text().strip() if title else "MPTI Page"
    
    def extract_meta_description(self, soup):
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '') if meta else ''
    
    def extract_structured_content(self, soup):
        """Extract main content with structure preservation"""
        content_parts = []
        
        # Priority content selectors
        selectors = ['main', '.content', '#content', 'article', '.entry-content', '.post-content']
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text().strip()
                    if len(text) > 100:
                        content_parts.append(text)
                break
        
        # Fallback to body
        if not content_parts:
            body = soup.find('body')
            if body:
                content_parts.append(body.get_text())
        
        # Clean and structure content
        full_content = ' '.join(content_parts)
        lines = (line.strip() for line in full_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_content = ' '.join(chunk for chunk in chunks if chunk and len(chunk) > 2)
        
        return clean_content[:4000]  # Increased limit for comprehensive analysis
    
    def extract_key_points(self, soup):
        """Extract key points and highlights"""
        key_points = []
        
        # Extract from headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        for heading in headings[:8]:
            text = heading.get_text().strip()
            if 5 < len(text) < 100:
                key_points.append(f"• {text}")
        
        # Extract from lists
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists[:3]:
            items = lst.find_all('li')
            for item in items[:5]:
                text = item.get_text().strip()
                if 10 < len(text) < 150:
                    key_points.append(f"• {text}")
        
        return key_points[:10]
    
    def extract_ctas(self, soup, page_type):
        """Extract Call-to-Action elements intelligently"""
        ctas = []
        
        # Find buttons and links
        cta_elements = soup.find_all(['a', 'button'], class_=re.compile(r'btn|button|cta|apply|contact|enroll', re.I))
        cta_elements.extend(soup.find_all(['a', 'button'], string=re.compile(r'apply|contact|enroll|learn more|get started|call|email', re.I)))
        
        for elem in cta_elements[:5]:
            text = elem.get_text().strip()
            href = elem.get('href', '')
            
            if text and len(text) < 50:
                cta_type = self.classify_cta(text, href, page_type)
                ctas.append({
                    'text': text,
                    'url': href,
                    'type': cta_type,
                    'priority': self.get_cta_priority(cta_type)
                })
        
        # Add intelligent CTAs based on page type
        ctas.extend(self.generate_intelligent_ctas(page_type))
        
        return ctas
    
    def classify_cta(self, text, href, page_type):
        """Classify CTA type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['apply', 'enroll', 'register']):
            return 'application'
        elif any(word in text_lower for word in ['contact', 'call', 'email']):
            return 'contact'
        elif any(word in text_lower for word in ['learn', 'more', 'details']):
            return 'information'
        elif any(word in text_lower for word in ['download', 'brochure']):
            return 'resource'
        else:
            return 'navigation'
    
    def get_cta_priority(self, cta_type):
        """Get CTA priority"""
        priority_map = {
            'application': 'high',
            'contact': 'high',
            'information': 'medium',
            'resource': 'medium',
            'navigation': 'low'
        }
        return priority_map.get(cta_type, 'low')
    
    def generate_intelligent_ctas(self, page_type):
        """Generate intelligent CTAs based on page type"""
        base_ctas = {
            'landing': [
                {'text': 'Explore Our Programs', 'url': '/programs', 'type': 'navigation', 'priority': 'high'},
                {'text': 'Apply Now', 'url': '/admissions', 'type': 'application', 'priority': 'high'}
            ],
            'service': [
                {'text': 'Apply for This Program', 'url': '/admissions', 'type': 'application', 'priority': 'high'},
                {'text': 'Contact Admissions', 'url': '/contact', 'type': 'contact', 'priority': 'medium'}
            ],
            'conversion': [
                {'text': 'Start Your Application', 'url': '/admissions', 'type': 'application', 'priority': 'high'},
                {'text': 'Schedule a Visit', 'url': '/contact', 'type': 'contact', 'priority': 'high'}
            ],
            'informational': [
                {'text': 'View Our Programs', 'url': '/programs', 'type': 'navigation', 'priority': 'medium'},
                {'text': 'Learn About TACT Program', 'url': '/tact-program', 'type': 'navigation', 'priority': 'medium'}
            ]
        }
        
        return base_ctas.get(page_type, [])
    
    def extract_contact_info(self, soup):
        """Extract contact information"""
        contact_info = {}
        
        text = soup.get_text()
        
        # Phone numbers
        phone_pattern = r'[\+]?[1-9]?[0-9]{3}-?[0-9]{3}-?[0-9]{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phones'] = phones[:3]
        
        # Email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['emails'] = emails[:3]
        
        return contact_info
    
    def extract_programs(self, soup):
        """Extract mentioned programs"""
        programs = []
        text = soup.get_text().lower()
        
        program_keywords = [
            'mechanical engineering', 'electrical engineering', 'welding', 'fabrication',
            'instrumentation', 'equipment training', 'tact program', 'certification',
            'technical education', 'vocational training'
        ]
        
        for program in program_keywords:
            if program in text:
                programs.append(program.title())
        
        return programs
    
    def extract_navigation_hints(self, soup):
        """Extract navigation hints for intelligent routing"""
        hints = []
        
        # Extract from navigation menus
        nav_elements = soup.find_all(['nav', '.menu', '.navigation'])
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links[:10]:
                text = link.get_text().strip()
                href = link.get('href', '')
                if text and href:
                    hints.append({'text': text, 'url': href})
        
        return hints
    
    def build_navigation_map(self, analyzed_content):
        """Build intelligent navigation map"""
        self.navigation_structure = {
            'main_sections': {
                'programs': {
                    'title': 'Academic Programs',
                    'pages': ['programs', 'courses', 'tact-program'],
                    'cta': 'Explore Programs'
                },
                'engineering': {
                    'title': 'Engineering Specializations',
                    'pages': ['mechanical-engineering', 'electrical-engineering', 'welding-fabrication'],
                    'cta': 'View Engineering Programs'
                },
                'admissions': {
                    'title': 'Join MPTI',
                    'pages': ['admissions', 'contact'],
                    'cta': 'Apply Now'
                },
                'about': {
                    'title': 'About MPTI',
                    'pages': ['about', 'home'],
                    'cta': 'Learn More'
                }
            },
            'quick_actions': [
                {'text': 'Apply Now', 'url': '/admissions', 'priority': 'high'},
                {'text': 'View Programs', 'url': '/programs', 'priority': 'high'},
                {'text': 'Contact Us', 'url': '/contact', 'priority': 'medium'},
                {'text': 'TACT Program', 'url': '/tact-program', 'priority': 'medium'}
            ]
        }

class LightweightAIModel:
    def __init__(self):
        self.ai_provider = os.getenv('AI_PROVIDER', 'groq')
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.groq_model = os.getenv('AI_MODEL', 'llama3-8b-8192')
        self.available = bool(self.groq_key)
        
    def generate_response(self, user_message, context=""):
        if not self.available:
            return None
            
        try:
            system_prompt = f"""You are MPTI Assistant for MPTI Technical Institute (https://www.mptigh.com/). 
Provide helpful, accurate information about MPTI programs, admissions, and services.

MPTI Content: {context[:2000]}

Respond professionally with specific MPTI information."""
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f'Bearer {self.groq_key}', 'Content-Type': 'application/json'},
                json={
                    'model': self.groq_model,
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_message}
                    ],
                    'max_tokens': 500,
                    'temperature': 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
                
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            
        return None

class IntelligentAgent:
    def __init__(self):
        self.scraper = IntelligentMPTIScraper()
        self.ai_model = LightweightAIModel()
        self.base_url = "https://www.mptigh.com/"
        self.knowledge_base = {}
        self.conversation_context = {}
        self.load_intelligence()
    
    def load_intelligence(self):
        """Load comprehensive website intelligence"""
        logger.info("🧠 Loading MPTI intelligence...")
        self.knowledge_base = self.scraper.comprehensive_analysis()
        logger.info(f"🎯 Intelligence loaded: {len(self.knowledge_base)} pages analyzed")
    
    def generate_intelligent_response(self, user_message, conversation_id='default'):
        """Generate intelligent, agentic response with navigation and CTAs"""
        
        # Analyze user intent
        intent = self.analyze_user_intent(user_message)
        
        # Find relevant content
        relevant_content = self.find_relevant_content(user_message, intent)
        
        # Generate contextual response
        response = self.build_contextual_response(user_message, intent, relevant_content)
        
        # Add intelligent navigation and CTAs
        response = self.add_intelligent_navigation(response, intent, relevant_content)
        
        # Update conversation context
        self.update_conversation_context(conversation_id, user_message, response, intent)
        
        return response
    
    def analyze_user_intent(self, message):
        """Analyze user intent from message"""
        message_lower = message.lower()
        
        intents = {
            'application': ['apply', 'enroll', 'register', 'admission', 'join'],
            'program_inquiry': ['program', 'course', 'study', 'degree', 'certificate'],
            'tact_program': ['tact', 'technical advancement', 'certification training'],
            'engineering': ['mechanical', 'electrical', 'welding', 'fabrication', 'instrumentation'],
            'contact': ['contact', 'phone', 'email', 'address', 'location', 'visit'],
            'general_info': ['about', 'information', 'tell me', 'what is', 'how'],
            'navigation': ['where', 'how to find', 'navigate', 'go to']
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intents.append(intent)
        
        return detected_intents[0] if detected_intents else 'general_info'
    
    def find_relevant_content(self, message, intent):
        """Find most relevant content based on message and intent"""
        relevant_pages = []
        
        # Intent-based page mapping
        intent_pages = {
            'application': ['admissions', 'contact'],
            'program_inquiry': ['programs', 'courses'],
            'tact_program': ['tact-program'],
            'engineering': ['mechanical-engineering', 'electrical-engineering', 'welding-fabrication'],
            'contact': ['contact'],
            'general_info': ['about', 'home'],
            'navigation': ['home']
        }
        
        # Get pages for intent
        target_pages = intent_pages.get(intent, ['home'])
        
        # Search content for relevance
        for page_name in target_pages:
            if page_name in self.knowledge_base:
                relevant_pages.append(self.knowledge_base[page_name])
        
        # Add keyword-based search
        message_words = message.lower().split()
        for page_name, page_data in self.knowledge_base.items():
            content_lower = page_data['content'].lower()
            relevance_score = sum(1 for word in message_words if word in content_lower and len(word) > 3)
            
            if relevance_score > 0 and page_data not in relevant_pages:
                relevant_pages.append(page_data)
        
        return relevant_pages[:3]  # Top 3 most relevant
    
    def build_contextual_response(self, message, intent, relevant_content):
        """Build intelligent contextual response using AI"""
        
        # Build context from relevant content
        context_parts = []
        for content in relevant_content[:2]:
            context_parts.append(f"Page: {content['title']}\nContent: {content['content'][:800]}")
        
        context = "\n\n".join(context_parts)
        
        # Try AI response first
        if self.ai_model.available and context:
            ai_response = self.ai_model.generate_response(message, context)
            if ai_response:
                return ai_response
        
        # Fallback to rule-based if AI fails
        if not relevant_content:
            return self.get_fallback_response(intent)
        
        # Build response based on intent and content
        response_parts = []
        
        # Intent-specific greeting
        greetings = {
            'application': "Great! I'd be happy to help you with applying to MPTI Technical Institute. 🎓",
            'program_inquiry': "Excellent question about our programs! Let me share the details. 📚",
            'tact_program': "The TACT Program is one of our flagship offerings! 🚀",
            'engineering': "Our engineering programs are highly regarded! ⚙️",
            'contact': "I'll help you get in touch with MPTI! 📞",
            'general_info': "I'm happy to share information about MPTI Technical Institute! 🏫",
            'navigation': "Let me guide you to the right information! 🧭"
        }
        
        response_parts.append(greetings.get(intent, "Thank you for your interest in MPTI! 👋"))
        
        # Add relevant content
        for i, content in enumerate(relevant_content[:2]):
            if i == 0:
                # Primary content - more detailed
                response_parts.append(f"\n\n**{content['title']}**")
                
                # Add key points
                if content['key_points']:
                    response_parts.append("\nKey highlights:")
                    for point in content['key_points'][:4]:
                        response_parts.append(point)
                
                # Add specific content excerpt
                content_excerpt = content['content'][:500] + "..." if len(content['content']) > 500 else content['content']
                response_parts.append(f"\n{content_excerpt}")
            
            else:
                # Secondary content - brief mention
                response_parts.append(f"\n\n**Related: {content['title']}**")
                if content['key_points']:
                    response_parts.append(f"• {content['key_points'][0]}")
        
        return '\n'.join(response_parts)
    
    def add_intelligent_navigation(self, response, intent, relevant_content):
        """Add intelligent navigation and CTAs"""
        
        navigation_parts = []
        
        # Add relevant CTAs
        ctas_added = []
        for content in relevant_content:
            for cta in content.get('ctas', []):
                if cta['priority'] in ['high', 'medium'] and cta not in ctas_added:
                    navigation_parts.append(f"🔗 **{cta['text']}** - {self.base_url.rstrip('/')}{cta['url']}")
                    ctas_added.append(cta)
                    if len(ctas_added) >= 3:
                        break
        
        # Add intent-specific navigation
        intent_navigation = {
            'application': [
                "🎯 **Ready to Apply?** Visit our admissions page: https://www.mptigh.com/admissions",
                "📞 **Need Help?** Contact our admissions team: https://www.mptigh.com/contact"
            ],
            'program_inquiry': [
                "📋 **Explore All Programs:** https://www.mptigh.com/programs",
                "🎓 **Learn About TACT Program:** https://www.mptigh.com/tact-program"
            ],
            'tact_program': [
                "🚀 **TACT Program Details:** https://www.mptigh.com/tact-program",
                "📝 **Apply for TACT:** https://www.mptigh.com/admissions"
            ],
            'engineering': [
                "⚙️ **Engineering Programs:** https://www.mptigh.com/programs",
                "🔧 **Mechanical Engineering:** https://www.mptigh.com/mechanicalengineering"
            ],
            'contact': [
                "📞 **Contact Information:** https://www.mptigh.com/contact",
                "🏫 **Visit Our Campus:** https://www.mptigh.com/about"
            ]
        }
        
        if intent in intent_navigation:
            navigation_parts.extend(intent_navigation[intent][:2])
        
        # Add general navigation
        navigation_parts.extend([
            "\n**🧭 Quick Navigation:**",
            "• **Programs & Courses:** https://www.mptigh.com/programs",
            "• **Admissions:** https://www.mptigh.com/admissions", 
            "• **Contact Us:** https://www.mptigh.com/contact",
            "• **About MPTI:** https://www.mptigh.com/about"
        ])
        
        if navigation_parts:
            response += "\n\n" + '\n'.join(navigation_parts)
        
        # Add helpful footer
        response += "\n\n💡 **Need more specific information?** Just ask me about any MPTI program, admission requirements, or how to get started!"
        
        return response
    
    def get_fallback_response(self, intent):
        """Fallback response when no content found"""
        fallback_responses = {
            'tact_program': """🚀 **TACT Program - Technical Advancement and Certification Training**

The TACT Program is MPTI's premier professional development initiative designed for working professionals and career advancement.

**🎯 Program Overview:**
• Advanced technical training for industry professionals
• Flexible scheduling for working adults
• Industry-recognized certifications
• Hands-on practical experience
• Career advancement opportunities

**📚 Specialization Areas:**
• Advanced Welding Techniques & Certification
• Instrumentation Calibration & Control Systems
• Mechanical Systems Maintenance & Repair
• Electrical Safety Protocols & Power Systems
• Equipment Operation & Maintenance
• Process Control & Automation

**✅ Program Benefits:**
• Industry-standard certifications
• Enhanced job prospects
• Salary advancement potential
• Networking with industry professionals
• Continuous professional development

**🎓 Who Should Apply:**
• Working professionals seeking advancement
• Technical workers wanting certifications
• Career changers entering technical fields
• Recent graduates seeking specialization

🚀 **TACT Program Details:** https://www.mptigh.com/tact-program
📝 **Apply Now:** https://www.mptigh.com/admissions
📞 **Program Inquiry:** https://www.mptigh.com/contact

💡 **Ready to advance your technical career? The TACT Program is your pathway to professional excellence!**""",
            
            'application': """🎓 **Ready to Join MPTI Technical Institute?**

I'd love to help you with your application! While I gather the specific details you need, here's how you can get started:

🔗 **Apply Now:** https://www.mptigh.com/admissions
📞 **Contact Admissions:** https://www.mptigh.com/contact
📋 **View Programs:** https://www.mptigh.com/programs

What specific program are you interested in applying for?""",
            
            'program_inquiry': """📚 **MPTI Technical Institute Programs**

We offer comprehensive technical and vocational training programs:

• **Engineering & Technology Courses**
• **Professional Certification Programs** 
• **TACT Program** - Technical Advancement and Certification Training
• **Skills Development Training**

🔗 **Explore All Programs:** https://www.mptigh.com/programs
🎯 **TACT Program Details:** https://www.mptigh.com/tact-program

Which area of study interests you most?""",
            
            'default': """👋 **Welcome to MPTI Technical Institute!**

I'm your intelligent MPTI assistant, here to help you navigate our programs and services.

🎯 **Popular Destinations:**
• **Programs & Courses:** https://www.mptigh.com/programs
• **TACT Program:** https://www.mptigh.com/tact-program  
• **Admissions:** https://www.mptigh.com/admissions
• **Contact Us:** https://www.mptigh.com/contact

How can I assist you with your MPTI journey today?"""
        }
        
        return fallback_responses.get(intent, fallback_responses['default'])
    
    def update_conversation_context(self, conversation_id, user_message, response, intent):
        """Update conversation context for better follow-ups"""
        if conversation_id not in self.conversation_context:
            self.conversation_context[conversation_id] = []
        
        self.conversation_context[conversation_id].append({
            'user_message': user_message,
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 5 interactions
        if len(self.conversation_context[conversation_id]) > 5:
            self.conversation_context[conversation_id] = self.conversation_context[conversation_id][-5:]

# Initialize the intelligent agent
intelligent_agent = IntelligentAgent()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-intelligent-agent',
        'intelligence': {
            'pages_analyzed': len(intelligent_agent.knowledge_base),
            'navigation_structure': bool(intelligent_agent.scraper.navigation_structure),
            'agent_ready': True
        }
    })

@app.route('/chat', methods=['POST'])
def intelligent_chat():
    """Intelligent agentic chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        start_time = datetime.now()
        
        # Generate intelligent response
        response = intelligent_agent.generate_intelligent_response(user_message, conversation_id)
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"🤖 Intelligent response generated in {response_time:.2f}s")
        
        return jsonify({
            'reply': response,
            'conversation_id': conversation_id,
            'source': 'intelligent_agent',
            'response_time': response_time,
            'intelligence_level': 'high',
            'features': ['content_analysis', 'intent_detection', 'smart_navigation', 'contextual_ctas']
        })
        
    except Exception as e:
        logger.error(f"Intelligent chat error: {str(e)}")
        return jsonify({
            'reply': 'I apologize, but I encountered an error. Please try again or visit https://www.mptigh.com/ directly.',
            'error': 'Internal server error'
        }), 500

@app.route('/refresh-intelligence', methods=['POST'])
def refresh_intelligence():
    """Refresh the intelligent agent's knowledge"""
    try:
        intelligent_agent.load_intelligence()
        return jsonify({
            'message': 'Intelligence refreshed successfully',
            'pages_analyzed': len(intelligent_agent.knowledge_base),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Intelligence refresh error: {e}")
        return jsonify({'error': 'Failed to refresh intelligence'}), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info("🚀 MPTI Intelligent Agent - Advanced Agentic Chatbot")
    logger.info(f"🌐 Server: {host}:{port}")
    logger.info(f"🧠 Intelligence: {len(intelligent_agent.knowledge_base)} pages analyzed")
    logger.info("🎯 Features: Intent Analysis, Smart Navigation, Contextual CTAs, Agentic Responses")
    logger.info("✅ Ready to provide intelligent MPTI assistance!")
    
    app.run(host=host, port=port, debug=debug)