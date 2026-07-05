from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=10, window=60):
        self.max_requests = max_requests
        self.window = window
        self.storage = defaultdict(list)
    
    def allow_request(self, client_ip, max_requests=None, window=None):
        """Check if request is allowed"""
        max_req = max_requests or self.max_requests
        win = window or self.window
        now = datetime.now()
        
        self.storage[client_ip] = [
            req_time for req_time in self.storage[client_ip]
            if now - req_time < timedelta(seconds=win)
        ]
        
        if len(self.storage[client_ip]) >= max_req:
            return False
        
        self.storage[client_ip].append(now)
        return True