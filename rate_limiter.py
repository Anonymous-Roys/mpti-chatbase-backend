from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
from flask import request, jsonify

class RateLimiter:
    def __init__(self, max_requests=10, window=60):
        self.max_requests = max_requests
        self.window = window
        self.storage = defaultdict(list)
    
    def is_allowed(self, client_ip):
        """Check if request is allowed"""
        now = datetime.now()
        
        # Clean old requests
        self.storage[client_ip] = [
            req_time for req_time in self.storage[client_ip]
            if now - req_time < timedelta(seconds=self.window)
        ]
        
        # Check limit
        if len(self.storage[client_ip]) >= self.max_requests:
            return False
        
        # Add current request
        self.storage[client_ip].append(now)
        return True
    
    def decorator(self, max_requests=None, window=None):
        """Rate limiting decorator"""
        max_req = max_requests or self.max_requests
        win = window or self.window
        
        def rate_limit_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                client_ip = request.remote_addr
                
                if not self.is_allowed(client_ip):
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                return f(*args, **kwargs)
            return wrapper
        return rate_limit_decorator