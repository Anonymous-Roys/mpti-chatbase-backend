import os
import requests
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = os.getenv('GROQ_BASE_URL')
        self.model = os.getenv('AI_MODEL')
        
    def generate_response(self, message, context="", intent="general"):
        """Generate AI response using Groq API"""
        
        # Build context-aware prompt
        prompt = f"""You are MPTI Technical Institute's helpful AI assistant. Answer questions about our programs, admissions, and services.

MPTI Context: {context[:500] if context else "Mac Partners Training Institute offers technical education and engineering programs in Ghana."}

User Question: {message}
Detected Intent: {intent}

Provide a helpful, accurate, and conversational response. Be specific about MPTI programs when possible."""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return self._fallback_response(intent)
                
        except Exception as e:
            logger.error(f"AI service error: {e}")
            return self._fallback_response(intent)
    
    def _fallback_response(self, intent):
        """Fallback responses when AI fails"""
        fallbacks = {
            'programs': "MPTI offers technical education programs including engineering technology, welding, and professional certifications. Visit https://www.mptigh.com/programs for details.",
            'application': "To apply to MPTI, visit our admissions page at https://www.mptigh.com/admissions or contact our admissions team.",
            'contact': "Contact MPTI at https://www.mptigh.com/contact for more information.",
            'general': "Thank you for your interest in MPTI Technical Institute. Visit https://www.mptigh.com/ for more information."
        }
        return fallbacks.get(intent, fallbacks['general'])