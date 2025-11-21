import re

class InputValidator:
    def __init__(self, max_length=500):
        self.max_length = max_length
    
    def validate(self, message):
        """Validate and sanitize user input"""
        if not message or not isinstance(message, str):
            return None, "Message is required"
        
        message = message.strip()
        if len(message) == 0:
            return None, "Message cannot be empty"
        
        if len(message) > self.max_length:
            return None, f"Message too long (max {self.max_length} characters)"
        
        # Basic sanitization
        message = re.sub(r'[<>"\'\\]', '', message)
        return message, None