import json
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_type='memory', ttl=3600):
        self.cache_type = cache_type
        self.ttl = ttl
        self.cache = {}
        self.redis_client = None
        
        if cache_type == 'redis':
            self._init_redis()
    
    def _init_redis(self):
        try:
            import redis
            self.redis_client = redis.Redis(
                host='localhost', port=6379, db=0, 
                decode_responses=True, socket_timeout=5
            )
            self.redis_client.ping()
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis unavailable, using memory cache: {e}")
            self.cache_type = 'memory'
    
    def get(self, key):
        try:
            if self.cache_type == 'redis' and self.redis_client:
                data = self.redis_client.get(key)
                return json.loads(data) if data else None
            else:
                # Memory cache with TTL
                if key in self.cache:
                    data, timestamp = self.cache[key]
                    if time.time() - timestamp < self.ttl:
                        return data
                    else:
                        del self.cache[key]
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key, value):
        try:
            if self.cache_type == 'redis' and self.redis_client:
                self.redis_client.setex(key, self.ttl, json.dumps(value))
            else:
                self.cache[key] = (value, time.time())
                # Simple cleanup
                if len(self.cache) > 1000:
                    self._cleanup_memory_cache()
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key):
        try:
            if self.cache_type == 'redis' and self.redis_client:
                self.redis_client.delete(key)
            else:
                self.cache.pop(key, None)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def _cleanup_memory_cache(self):
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]