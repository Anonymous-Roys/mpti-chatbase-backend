import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.available = False
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        self.initialize_analyzers()
    
    def initialize_analyzers(self):
        """Initialize sentiment analysis with error handling"""
        try:
            from transformers import pipeline
            
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            self.available = True
            logger.info("✅ Sentiment analyzer initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Sentiment analysis dependencies not available: {e}")
            self.available = False
        except Exception as e:
            logger.error(f"Sentiment analyzer initialization failed: {e}")
            self.available = False
    
    def is_available(self):
        return self.available
    
    def analyze(self, text):
        """Analyze sentiment and emotions"""
        if not self.available:
            return self.get_basic_sentiment(text)
        
        try:
            # Basic sentiment
            sentiment_result = self.sentiment_pipeline(text[:512])[0]
            
            # Emotion analysis
            emotion_results = self.emotion_pipeline(text[:512])[0]
            top_emotion = max(emotion_results, key=lambda x: x['score'])
            
            return {
                "sentiment": sentiment_result['label'],
                "sentiment_score": sentiment_result['score'],
                "emotion": top_emotion['label'],
                "emotion_score": top_emotion['score'],
                "urgency": self.detect_urgency(text)
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self.get_basic_sentiment(text)
    
    def get_basic_sentiment(self, text):
        """Basic sentiment analysis without ML models"""
        text_lower = text.lower()
        
        positive_words = ['great', 'good', 'excellent', 'amazing', 'wonderful', 'happy', 'thanks', 'thank you']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'angry', 'frustrated', 'disappointed']
        urgent_words = ['urgent', 'emergency', 'asap', 'immediately', 'now', 'help']
        
        sentiment = 'NEUTRAL'
        emotion = 'neutral'
        urgency = 'low'
        
        # Check for positive/negative words
        for word in positive_words:
            if word in text_lower:
                sentiment = 'POSITIVE'
                emotion = 'joy'
                break
        
        for word in negative_words:
            if word in text_lower:
                sentiment = 'NEGATIVE'
                emotion = 'anger'
                break
        
        # Check for urgency
        for word in urgent_words:
            if word in text_lower:
                urgency = 'high'
                break
        
        return {
            'sentiment': sentiment,
            'sentiment_score': 0.8,
            'emotion': emotion,
            'emotion_score': 0.7,
            'urgency': urgency
        }
    
    def detect_urgency(self, text):
        """Detect urgency level in message"""
        urgent_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'now', 'help']
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in urgent_keywords):
            return "high"
        elif '?' in text and len(text) < 100:
            return "medium"
        else:
            return "low"