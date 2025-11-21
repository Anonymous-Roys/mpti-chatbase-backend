class IntentAnalyzer:
    def __init__(self):
        self.intent_patterns = {
            'history': ['how long', 'when founded', 'when established', 'history', 'existence', 'started', 'began'],
            'tact_program': ['tact', 'technical advancement'],
            'application': ['apply', 'admission', 'enroll', 'form'],
            'programs': ['program', 'course', 'study'],
            'contact': ['contact', 'phone', 'email'],
            'greeting': ['hello', 'hi', 'hey']
        }
    
    def analyze(self, message):
        """Analyze user intent from message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        return 'general'