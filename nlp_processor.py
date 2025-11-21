import re
import logging
from collections import Counter
import json

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        self.synonyms = {
            'program': ['course', 'curriculum', 'study', 'training', 'education'],
            'apply': ['enroll', 'register', 'join', 'signup', 'admission'],
            'cost': ['fee', 'price', 'tuition', 'payment', 'expense'],
            'requirement': ['prerequisite', 'qualification', 'criteria', 'condition'],
            'contact': ['reach', 'call', 'email', 'phone', 'communicate'],
            'schedule': ['time', 'duration', 'when', 'timing', 'calendar']
        }
        
        self.entities = {
            'programs': ['tact', 'mechanical', 'electrical', 'welding', 'instrumentation', 'engineering'],
            'locations': ['ghana', 'accra', 'kumasi', 'campus'],
            'time_periods': ['semester', 'year', 'month', 'week', 'morning', 'evening']
        }
    
    def extract_entities(self, text):
        """Extract named entities from text"""
        text_lower = text.lower()
        found_entities = {}
        
        for entity_type, entity_list in self.entities.items():
            matches = [entity for entity in entity_list if entity in text_lower]
            if matches:
                found_entities[entity_type] = matches
        
        return found_entities
    
    def extract_keywords(self, text, max_keywords=5):
        """Extract important keywords from text"""
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove stop words
        keywords = [word for word in words if word not in self.stop_words]
        
        # Count frequency
        word_freq = Counter(keywords)
        
        # Return top keywords
        return [word for word, _ in word_freq.most_common(max_keywords)]
    
    def expand_synonyms(self, text):
        """Expand text with synonyms for better matching"""
        text_lower = text.lower()
        expanded_terms = set()
        
        for base_word, synonym_list in self.synonyms.items():
            if base_word in text_lower:
                expanded_terms.update(synonym_list)
            for synonym in synonym_list:
                if synonym in text_lower:
                    expanded_terms.add(base_word)
                    expanded_terms.update(synonym_list)
        
        return list(expanded_terms)
    
    def detect_question_type(self, text):
        """Detect the type of question being asked"""
        text_lower = text.lower().strip()
        
        question_patterns = {
            'what': r'\bwhat\b',
            'how': r'\bhow\b',
            'when': r'\bwhen\b',
            'where': r'\bwhere\b',
            'why': r'\bwhy\b',
            'who': r'\bwho\b',
            'which': r'\bwhich\b',
            'can': r'\bcan\s+i\b|\bcan\s+you\b',
            'is': r'\bis\s+there\b|\bis\s+it\b',
            'do': r'\bdo\s+you\b|\bdo\s+i\b'
        }
        
        for q_type, pattern in question_patterns.items():
            if re.search(pattern, text_lower):
                return q_type
        
        return 'statement' if not text_lower.endswith('?') else 'general_question'
    
    def extract_intent_signals(self, text):
        """Extract signals that indicate user intent"""
        text_lower = text.lower()
        signals = {}
        
        # Urgency signals
        urgency_words = ['urgent', 'asap', 'immediately', 'now', 'quickly', 'soon']
        signals['urgency'] = any(word in text_lower for word in urgency_words)
        
        # Comparison signals
        comparison_words = ['compare', 'difference', 'better', 'best', 'versus', 'vs', 'or']
        signals['comparison'] = any(word in text_lower for word in comparison_words)
        
        # Decision signals
        decision_words = ['decide', 'choose', 'select', 'pick', 'recommend', 'suggest']
        signals['seeking_advice'] = any(word in text_lower for word in decision_words)
        
        # Information depth
        depth_words = ['detail', 'more', 'explain', 'elaborate', 'specific', 'exactly']
        signals['wants_details'] = any(word in text_lower for word in depth_words)
        
        return signals
    
    def sentiment_analysis(self, text):
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'happy', 'excited']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'disappointed', 'frustrated', 'angry']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def process_message(self, text):
        """Comprehensive NLP processing of user message"""
        return {
            'entities': self.extract_entities(text),
            'keywords': self.extract_keywords(text),
            'synonyms': self.expand_synonyms(text),
            'question_type': self.detect_question_type(text),
            'intent_signals': self.extract_intent_signals(text),
            'sentiment': self.sentiment_analysis(text),
            'length': len(text.split()),
            'has_question': '?' in text
        }

class SemanticMatcher:
    def __init__(self):
        self.concept_clusters = {
            'education': ['learn', 'study', 'education', 'training', 'course', 'program', 'curriculum', 'academic'],
            'application': ['apply', 'enroll', 'register', 'admission', 'join', 'signup', 'form'],
            'financial': ['cost', 'fee', 'price', 'tuition', 'payment', 'scholarship', 'financial', 'money'],
            'technical': ['engineering', 'technology', 'technical', 'mechanical', 'electrical', 'welding'],
            'time': ['when', 'schedule', 'time', 'duration', 'start', 'end', 'semester', 'year'],
            'location': ['where', 'location', 'address', 'campus', 'ghana', 'accra']
        }
    
    def find_semantic_similarity(self, text, target_concepts):
        """Find semantic similarity between text and target concepts"""
        text_lower = text.lower()
        similarity_scores = {}
        
        for concept, keywords in self.concept_clusters.items():
            if concept in target_concepts:
                matches = sum(1 for keyword in keywords if keyword in text_lower)
                similarity_scores[concept] = matches / len(keywords) if keywords else 0
        
        return similarity_scores
    
    def enhance_intent_with_semantics(self, text, base_intent, confidence):
        """Enhance intent prediction using semantic analysis"""
        # Define semantic mappings for intents
        intent_concepts = {
            'programs': ['education', 'technical'],
            'application': ['application', 'financial'],
            'fees': ['financial'],
            'requirements': ['education', 'application'],
            'schedule': ['time'],
            'contact': ['location']
        }
        
        if base_intent in intent_concepts:
            target_concepts = intent_concepts[base_intent]
            similarities = self.find_semantic_similarity(text, target_concepts)
            
            # Boost confidence if semantic similarity is high
            semantic_boost = sum(similarities.values()) * 0.1
            enhanced_confidence = min(confidence + semantic_boost, 1.0)
            
            return base_intent, enhanced_confidence
        
        return base_intent, confidence