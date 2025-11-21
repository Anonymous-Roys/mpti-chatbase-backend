import time
import logging
from datetime import datetime
from collections import defaultdict, deque
from functools import wraps

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self, max_history=1000):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.response_times = deque(maxlen=max_history)
        self.error_counts = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_request(self, endpoint, response_time, status_code):
        self.counters['total_requests'] += 1
        self.counters[f'{endpoint}_requests'] += 1
        self.response_times.append(response_time)
        
        if status_code >= 400:
            self.error_counts[f'{endpoint}_errors'] += 1
            self.counters['total_errors'] += 1
    
    def record_cache_hit(self, cache_type='hit'):
        self.counters[f'cache_{cache_type}'] += 1
    
    def record_scrape(self, pages_scraped, success=True):
        self.counters['scrape_attempts'] += 1
        if success:
            self.counters['scrape_success'] += 1
            self.counters['pages_scraped'] += pages_scraped
    
    def get_stats(self):
        uptime = (datetime.now() - self.start_time).total_seconds()
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.counters['total_requests'],
            'total_errors': self.counters['total_errors'],
            'error_rate': self.counters['total_errors'] / max(self.counters['total_requests'], 1),
            'avg_response_time': round(avg_response_time, 3),
            'cache_hits': self.counters['cache_hit'],
            'cache_misses': self.counters['cache_miss'],
            'cache_hit_rate': self.counters['cache_hit'] / max(self.counters['cache_hit'] + self.counters['cache_miss'], 1),
            'scrape_success_rate': self.counters['scrape_success'] / max(self.counters['scrape_attempts'], 1),
            'pages_scraped': self.counters['pages_scraped']
        }

# Global metrics collector
metrics = MetricsCollector()

def monitor_endpoint(endpoint_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                response_time = time.time() - start_time
                
                # Extract status code from Flask response
                status_code = 200
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, tuple) and len(result) > 1:
                    status_code = result[1]
                
                metrics.record_request(endpoint_name, response_time, status_code)
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                metrics.record_request(endpoint_name, response_time, 500)
                raise
        return wrapper
    return decorator

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log_request(self, method, path, status_code, response_time, user_ip=None):
        self.logger.info(
            f"REQUEST {method} {path} - {status_code} - {response_time:.3f}s - IP:{user_ip}"
        )
    
    def log_cache_operation(self, operation, key, hit=None):
        status = f"HIT" if hit else "MISS" if hit is False else "SET"
        self.logger.info(f"CACHE {operation} {key} - {status}")
    
    def log_scrape_operation(self, pages_scraped, success, error=None):
        status = "SUCCESS" if success else f"FAILED: {error}"
        self.logger.info(f"SCRAPE {pages_scraped} pages - {status}")
    
    def log_error(self, component, error, context=None):
        context_str = f" - Context: {context}" if context else ""
        self.logger.error(f"ERROR {component} - {error}{context_str}")

# Global structured logger
structured_logger = StructuredLogger('mpti_chatbot')