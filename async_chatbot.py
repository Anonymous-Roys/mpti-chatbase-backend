import asyncio
import uuid
import logging
from async_scraper import AsyncWebScraper
from async_knowledge_manager import AsyncKnowledgeManager
from intent_analyzer import IntentAnalyzer
from ml_intent_analyzer import MLIntentAnalyzer
from response_generator import ResponseGenerator
from advanced_response_generator import AdvancedResponseGenerator
from conversation_manager import ConversationManager
from nlp_processor import NLPProcessor, SemanticMatcher

logger = logging.getLogger(__name__)

class AsyncChatbot:
    def __init__(self, base_url, scrape_timeout=10, scrape_interval=3600, cache_type='memory'):
        self.scraper = AsyncWebScraper(base_url, scrape_timeout)
        self.knowledge_manager = AsyncKnowledgeManager(self.scraper, scrape_interval, cache_type)
        self.intent_analyzer = IntentAnalyzer()
        self.ml_intent_analyzer = MLIntentAnalyzer()
        self.response_generator = ResponseGenerator()
        self.advanced_response_generator = AdvancedResponseGenerator()
        self.conversation_manager = ConversationManager()
        self.nlp_processor = NLPProcessor()
        self.semantic_matcher = SemanticMatcher()
        
        # Async processing pools
        self.intent_semaphore = asyncio.Semaphore(10)  # Limit concurrent intent analysis
        self.response_semaphore = asyncio.Semaphore(5)  # Limit concurrent response generation
        
        logger.info(f"Async chatbot initialized with {cache_type} cache, concurrent processing")
    
    async def async_process_message(self, message, session_id=None):
        """Process user message asynchronously with concurrent operations"""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Start concurrent operations
            async with self.intent_semaphore:
                # Concurrent context and NLP processing
                context_task = asyncio.create_task(self._get_conversation_context(session_id))
                nlp_task = asyncio.create_task(self._process_nlp(message))
                content_task = asyncio.create_task(self._search_content(message))
                
                # Wait for all concurrent operations
                context, nlp_analysis, relevant_content = await asyncio.gather(
                    context_task, nlp_task, content_task
                )
            
            # Analyze intent with ML and context
            intent = await self._analyze_intent(message, context, nlp_analysis)
            confidence = self.ml_intent_analyzer.get_confidence(message, intent)
            
            # Generate response concurrently
            async with self.response_semaphore:
                response_task = asyncio.create_task(self._generate_response(
                    intent, nlp_analysis, relevant_content, context
                ))
                suggestions_task = asyncio.create_task(self._get_suggestions(session_id))
                followups_task = asyncio.create_task(self._generate_followups(intent, nlp_analysis))
                
                response, suggestions, follow_ups = await asyncio.gather(
                    response_task, suggestions_task, followups_task
                )
            
            # Get CTAs (sync operation)
            ctas = self.response_generator.get_ctas(intent)
            
            # Store conversation (async)
            await self._store_conversation(session_id, message, intent, response)
            
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
                'source': 'async_advanced_nlp_chatbot'
            }
            
        except Exception as e:
            logger.error(f"Async message processing error: {e}")
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
                'source': 'async_error_fallback'
            }
    
    async def _get_conversation_context(self, session_id):
        """Get conversation context asynchronously"""
        # Run sync method in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        context = await loop.run_in_executor(None, self.conversation_manager.get_context, session_id)
        recent_intents = await loop.run_in_executor(None, self.conversation_manager.get_recent_intents, session_id)
        context['recent_intents'] = recent_intents
        return context
    
    async def _process_nlp(self, message):
        """Process NLP asynchronously"""
        loop = asyncio.get_event_loop()
        nlp_analysis = await loop.run_in_executor(None, self.nlp_processor.process_message, message)
        nlp_analysis['original_message'] = message
        return nlp_analysis
    
    async def _search_content(self, message):
        """Search content asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.knowledge_manager.search_content, message)
    
    async def _analyze_intent(self, message, context, nlp_analysis):
        """Analyze intent asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Try ML intent analyzer first
        intent = await loop.run_in_executor(None, self.ml_intent_analyzer.analyze, message, context)
        confidence = await loop.run_in_executor(None, self.ml_intent_analyzer.get_confidence, message, intent)
        
        # Enhance with semantic analysis
        intent, confidence = await loop.run_in_executor(
            None, self.semantic_matcher.enhance_intent_with_semantics, message, intent, confidence
        )
        
        # Fallback to rule-based if low confidence
        if confidence < 0.5:
            intent = await loop.run_in_executor(None, self.intent_analyzer.analyze, message)
            logger.info(f"Used fallback intent analyzer for: {message[:50]}")
        
        return intent
    
    async def _generate_response(self, intent, nlp_analysis, relevant_content, context):
        """Generate response asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.advanced_response_generator.generate_contextual_response,
            intent, nlp_analysis, relevant_content, context
        )
    
    async def _get_suggestions(self, session_id):
        """Get personalized suggestions asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.conversation_manager.get_personalized_suggestions, session_id)
    
    async def _generate_followups(self, intent, nlp_analysis):
        """Generate follow-up questions asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.advanced_response_generator.generate_follow_up_questions,
            intent, nlp_analysis
        )
    
    async def _store_conversation(self, session_id, message, intent, response):
        """Store conversation asynchronously"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.conversation_manager.add_message,
            session_id, message, intent, response
        )
    
    def get_status(self):
        """Get chatbot status (sync method)"""
        return {
            'knowledge_sections': len(self.knowledge_manager.knowledge),
            'scraping_status': self.knowledge_manager.status,
            'last_scrape': self.scraper.last_scrape.isoformat() if self.scraper.last_scrape else None,
            'async_enabled': True
        }
    
    async def async_refresh_knowledge(self):
        """Manually trigger async knowledge refresh"""
        await self.knowledge_manager.force_refresh()
    
    def save_ml_model(self):
        """Save ML model weights (sync method)"""
        self.ml_intent_analyzer.save_weights()
    
    def get_conversation_stats(self):
        """Get conversation statistics (sync method)"""
        return {
            'active_sessions': len(self.conversation_manager.conversations),
            'total_conversations': sum(len(conv['messages']) for conv in self.conversation_manager.conversations.values())
        }
    
    def cleanup(self):
        """Cleanup async resources"""
        self.knowledge_manager.cleanup()
        logger.info("Async chatbot resources cleaned up")