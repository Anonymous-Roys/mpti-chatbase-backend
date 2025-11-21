import time
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, max_history=10, session_timeout=1800):
        self.conversations = defaultdict(lambda: {
            'messages': deque(maxlen=max_history),
            'context': {},
            'last_activity': datetime.now()
        })
        self.session_timeout = session_timeout
    
    def add_message(self, session_id, message, intent, response):
        """Add message to conversation history"""
        self._cleanup_expired_sessions()
        
        conversation = self.conversations[session_id]
        conversation['messages'].append({
            'timestamp': datetime.now(),
            'user_message': message,
            'intent': intent,
            'response': response[:200] + '...' if len(response) > 200 else response
        })
        conversation['last_activity'] = datetime.now()
        
        # Update context based on intent
        self._update_context(session_id, intent, message)
    
    def get_context(self, session_id):
        """Get conversation context"""
        self._cleanup_expired_sessions()
        return self.conversations[session_id]['context']
    
    def get_recent_intents(self, session_id, count=3):
        """Get recent intents for context"""
        conversation = self.conversations[session_id]
        recent_messages = list(conversation['messages'])[-count:]
        return [msg['intent'] for msg in recent_messages]
    
    def _update_context(self, session_id, intent, message):
        """Update conversation context"""
        context = self.conversations[session_id]['context']
        
        # Track user interests
        if intent not in context:
            context[intent] = 0
        context[intent] += 1
        
        # Track specific topics
        message_lower = message.lower()
        if 'tact' in message_lower:
            context['interested_in_tact'] = True
        if any(word in message_lower for word in ['apply', 'application']):
            context['considering_application'] = True
        if any(word in message_lower for word in ['program', 'course']):
            context['exploring_programs'] = True
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        cutoff = datetime.now() - timedelta(seconds=self.session_timeout)
        expired_sessions = [
            session_id for session_id, data in self.conversations.items()
            if data['last_activity'] < cutoff
        ]
        for session_id in expired_sessions:
            del self.conversations[session_id]
    
    def get_personalized_suggestions(self, session_id):
        """Get personalized suggestions based on context"""
        context = self.get_context(session_id)
        suggestions = []
        
        if context.get('interested_in_tact'):
            suggestions.append("Learn more about TACT program requirements")
        if context.get('considering_application'):
            suggestions.append("View application deadlines and requirements")
        if context.get('exploring_programs'):
            suggestions.append("Compare different program options")
        
        # Based on frequent intents
        top_intent = max(context.items(), key=lambda x: x[1] if isinstance(x[1], int) else 0, default=(None, 0))[0]
        if top_intent == 'programs' and len(suggestions) < 2:
            suggestions.append("Explore engineering specializations")
        
        return suggestions[:3]