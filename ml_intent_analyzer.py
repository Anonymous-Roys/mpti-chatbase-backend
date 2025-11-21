import re
import logging
from collections import Counter
import pickle
import os

logger = logging.getLogger(__name__)

class MLIntentAnalyzer:
    def __init__(self):
        self.intent_patterns = {
            'history': ['how long', 'when founded', 'established', 'history', 'existence', 'started', 'began', 'old', 'years'],
            'tact_program': ['tact', 'technical advancement', 'certification training', 'professional development'],
            'application': ['apply', 'admission', 'enroll', 'form', 'register', 'join', 'signup'],
            'programs': ['program', 'course', 'study', 'degree', 'curriculum', 'major', 'specialization'],
            'contact': ['contact', 'phone', 'email', 'address', 'location', 'reach', 'call'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings'],
            'fees': ['fee', 'cost', 'price', 'tuition', 'payment', 'scholarship', 'financial'],
            'requirements': ['requirement', 'prerequisite', 'qualification', 'criteria', 'eligibility'],
            'schedule': ['schedule', 'time', 'duration', 'when', 'start', 'semester', 'class']
        }
        
        # Simple feature weights (can be trained)
        self.feature_weights = {}
        self.conversation_context = {}
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize or load feature weights"""
        weights_file = 'intent_weights.pkl'
        if os.path.exists(weights_file):
            try:
                with open(weights_file, 'rb') as f:
                    self.feature_weights = pickle.load(f)
                logger.info("Loaded trained intent weights")
            except Exception as e:
                logger.warning(f"Failed to load weights: {e}")
                self._create_default_weights()
        else:
            self._create_default_weights()
    
    def _create_default_weights(self):
        """Create default feature weights"""
        for intent, patterns in self.intent_patterns.items():
            self.feature_weights[intent] = {}
            for pattern in patterns:
                self.feature_weights[intent][pattern] = 1.0
    
    def analyze(self, message, conversation_context=None):
        """Analyze intent with ML-enhanced scoring"""
        message_lower = message.lower()
        intent_scores = {}
        
        # Calculate base scores
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in message_lower:
                    weight = self.feature_weights.get(intent, {}).get(pattern, 1.0)
                    score += weight
                    
                    # Boost score for exact matches
                    if pattern == message_lower.strip():
                        score += 2.0
            
            intent_scores[intent] = score
        
        # Apply conversation context
        if conversation_context:
            intent_scores = self._apply_context_boost(intent_scores, conversation_context)
        
        # Apply semantic similarity (simple version)
        intent_scores = self._apply_semantic_boost(intent_scores, message_lower)
        
        # Get best intent
        if not intent_scores or max(intent_scores.values()) == 0:
            return 'general'
        
        best_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
        
        # Update learning (simple frequency-based)
        self._update_weights(best_intent, message_lower)
        
        return best_intent
    
    def _apply_context_boost(self, intent_scores, context):
        """Boost scores based on conversation context"""
        recent_intents = context.get('recent_intents', [])
        
        # Boost related intents
        intent_relationships = {
            'programs': ['requirements', 'fees', 'schedule'],
            'tact_program': ['application', 'requirements', 'fees'],
            'application': ['requirements', 'fees', 'programs'],
            'requirements': ['programs', 'application']
        }
        
        for recent_intent in recent_intents[-2:]:  # Last 2 intents
            if recent_intent in intent_relationships:
                for related_intent in intent_relationships[recent_intent]:
                    if related_intent in intent_scores:
                        intent_scores[related_intent] += 0.5
        
        return intent_scores
    
    def _apply_semantic_boost(self, intent_scores, message):
        """Apply simple semantic similarity boost"""
        # Educational context words
        edu_words = ['learn', 'education', 'training', 'skill', 'knowledge']
        if any(word in message for word in edu_words):
            intent_scores['programs'] += 0.3
            intent_scores['tact_program'] += 0.3
        
        # Question words
        question_words = ['what', 'how', 'when', 'where', 'why', 'which']
        if any(word in message for word in question_words):
            if 'cost' in message or 'much' in message:
                intent_scores['fees'] += 0.5
            if 'time' in message or 'long' in message:
                intent_scores['schedule'] += 0.5
        
        return intent_scores
    
    def _update_weights(self, intent, message):
        """Simple learning: increase weights for successful patterns"""
        if intent not in self.feature_weights:
            self.feature_weights[intent] = {}
        
        for pattern in self.intent_patterns.get(intent, []):
            if pattern in message:
                current_weight = self.feature_weights[intent].get(pattern, 1.0)
                self.feature_weights[intent][pattern] = min(current_weight + 0.1, 3.0)
    
    def save_weights(self):
        """Save learned weights"""
        try:
            with open('intent_weights.pkl', 'wb') as f:
                pickle.dump(self.feature_weights, f)
            logger.info("Saved intent weights")
        except Exception as e:
            logger.error(f"Failed to save weights: {e}")
    
    def get_confidence(self, message, predicted_intent):
        """Get confidence score for prediction"""
        message_lower = message.lower()
        patterns = self.intent_patterns.get(predicted_intent, [])
        
        matches = sum(1 for pattern in patterns if pattern in message_lower)
        base_confidence = min(matches / max(len(patterns), 1), 1.0)
        
        # Boost confidence for exact matches
        if any(pattern == message_lower.strip() for pattern in patterns):
            base_confidence = min(base_confidence + 0.3, 1.0)
        
        # Boost for multiple pattern matches
        if matches > 1:
            base_confidence = min(base_confidence + 0.2, 1.0)
            
        return max(base_confidence, 0.1)  # Minimum confidence