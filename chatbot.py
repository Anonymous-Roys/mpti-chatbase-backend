from scraper import WebScraper
from knowledge_manager import KnowledgeManager
from intent_analyzer import IntentAnalyzer
from ml_intent_analyzer import MLIntentAnalyzer
from response_generator import ResponseGenerator
from advanced_response_generator import AdvancedResponseGenerator
from conversation_manager import ConversationManager
from nlp_processor import NLPProcessor, SemanticMatcher
import logging
import uuid

logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, base_url, scrape_timeout=10, scrape_interval=3600, cache_type='memory'):
        self.scraper = WebScraper(base_url, scrape_timeout)
        self.knowledge_manager = KnowledgeManager(self.scraper, scrape_interval, cache_type)
        self.intent_analyzer = IntentAnalyzer()  # Fallback
        self.ml_intent_analyzer = MLIntentAnalyzer()  # Primary
        self.response_generator = ResponseGenerator()  # Basic
        self.advanced_response_generator = AdvancedResponseGenerator()  # NLP-enhanced
        self.conversation_manager = ConversationManager()
        self.nlp_processor = NLPProcessor()
        self.semantic_matcher = SemanticMatcher()
        logger.info(f"Chatbot initialized with {cache_type} cache, ML intent analysis, and advanced NLP")
    
    def process_message(self, message, session_id=None):
        """Process user message with conversation context"""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Get conversation context
            context = self.conversation_manager.get_context(session_id)
            context['recent_intents'] = self.conversation_manager.get_recent_intents(session_id)
            
            # Advanced NLP processing
            nlp_analysis = self.nlp_processor.process_message(message)
            nlp_analysis['original_message'] = message  # Store original for AI
            
            # Analyze intent with ML and context
            intent = self.ml_intent_analyzer.analyze(message, context)
            confidence = self.ml_intent_analyzer.get_confidence(message, intent)
            
            # Enhance with semantic analysis
            intent, confidence = self.semantic_matcher.enhance_intent_with_semantics(message, intent, confidence)
            
            # Fallback to rule-based if low confidence
            if confidence < 0.5:
                intent = self.intent_analyzer.analyze(message)
                confidence = 0.8  # Boost confidence for rule-based
                logger.info(f"Used fallback intent analyzer for: {message[:50]}")
            
            # Find relevant content
            relevant_content = self.knowledge_manager.search_content(message)
            
            # Generate advanced NLP-aware response
            response = self.advanced_response_generator.generate_contextual_response(
                intent, nlp_analysis, relevant_content, context
            )
            
            # Add personalized suggestions
            suggestions = self.conversation_manager.get_personalized_suggestions(session_id)
            if suggestions:
                response += "\n\n**Based on our conversation, you might also be interested in:**\n"
                for suggestion in suggestions:
                    response += f"• {suggestion}\n"
            
            # Add intelligent follow-up questions
            follow_ups = self.advanced_response_generator.generate_follow_up_questions(intent, nlp_analysis)
            if follow_ups:
                response += "\n\n**I can also help with:**\n"
                for question in follow_ups:
                    response += f"• {question}\n"
            
            # Get CTAs
            ctas = self.response_generator.get_ctas(intent)
            
            # Store conversation
            self.conversation_manager.add_message(session_id, message, intent, response)
            
            return {
                'reply': response,
                'intent': intent,
                'confidence': round(confidence, 2),
                'ctas': ctas,
                'external_links': [],
                'session_id': session_id,
                'suggestions': suggestions,
                'nlp_analysis': {
                    'entities': nlp_analysis.get('entities', {}),
                    'keywords': nlp_analysis.get('keywords', []),
                    'question_type': nlp_analysis.get('question_type'),
                    'sentiment': nlp_analysis.get('sentiment'),
                    'intent_signals': nlp_analysis.get('intent_signals', {})
                },
                'follow_up_questions': follow_ups,
                'source': 'advanced_nlp_chatbot'
            }
            
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            return {
                'reply': 'I encountered an issue. Please visit https://www.mptigh.com/ for information.',
                'intent': 'error',
                'confidence': 0.0,
                'ctas': [],
                'external_links': [],
                'session_id': session_id or str(uuid.uuid4()),
                'suggestions': [],
                'nlp_analysis': {},
                'follow_up_questions': [],
                'source': 'error_fallback'
            }
    
    def get_status(self):
        """Get chatbot status"""
        return {
            'knowledge_sections': len(self.knowledge_manager.knowledge),
            'scraping_status': self.knowledge_manager.status,
            'last_scrape': self.scraper.last_scrape.isoformat() if self.scraper.last_scrape else None
        }
    
    def refresh_knowledge(self):
        """Manually trigger knowledge refresh"""
        self.knowledge_manager.update_knowledge()
    
    def save_ml_model(self):
        """Save ML model weights"""
        self.ml_intent_analyzer.save_weights()
    
    def get_conversation_stats(self):
        """Get conversation statistics"""
        return {
            'active_sessions': len(self.conversation_manager.conversations),
            'total_conversations': sum(len(conv['messages']) for conv in self.conversation_manager.conversations.values())
        }