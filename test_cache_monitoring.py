#!/usr/bin/env python3
"""
Test caching and monitoring components
"""

def test_cache_manager():
    from cache_manager import CacheManager
    
    print("Testing Cache Manager:")
    
    # Test memory cache
    cache = CacheManager('memory', ttl=2)
    
    # Test set/get
    cache.set('test_key', {'data': 'test_value'})
    result = cache.get('test_key')
    print(f"  Memory cache set/get: {'PASS' if result and result['data'] == 'test_value' else 'FAIL'}")
    
    # Test TTL
    import time
    time.sleep(3)
    expired_result = cache.get('test_key')
    print(f"  Memory cache TTL: {'PASS' if expired_result is None else 'FAIL'}")
    
    # Test Redis fallback (when Redis not available)
    redis_cache = CacheManager('redis')
    print(f"  Redis fallback: {'PASS' if redis_cache.cache_type == 'memory' else 'FAIL'}")

def test_metrics_collector():
    from monitoring import MetricsCollector
    
    print("\nTesting Metrics Collector:")
    
    metrics = MetricsCollector()
    
    # Test request recording
    metrics.record_request('/chat', 0.5, 200)
    metrics.record_request('/chat', 1.0, 500)
    
    # Test cache recording
    metrics.record_cache_hit('hit')
    metrics.record_cache_hit('miss')
    
    # Test scrape recording
    metrics.record_scrape(5, True)
    
    stats = metrics.get_stats()
    
    print(f"  Total requests: {'PASS' if stats['total_requests'] == 2 else 'FAIL'}")
    print(f"  Error rate: {'PASS' if stats['error_rate'] == 0.5 else 'FAIL'}")
    print(f"  Cache hit rate: {'PASS' if stats['cache_hit_rate'] == 0.5 else 'FAIL'}")
    print(f"  Scrape success: {'PASS' if stats['scrape_success_rate'] == 1.0 else 'FAIL'}")

def test_structured_logger():
    from monitoring import StructuredLogger
    
    print("\nTesting Structured Logger:")
    
    logger = StructuredLogger('test')
    
    # Test different log types
    logger.log_request('POST', '/chat', 200, 0.5, '127.0.0.1')
    logger.log_cache_operation('GET', 'test_key', True)
    logger.log_scrape_operation(3, True)
    logger.log_error('test_component', 'Test error', {'context': 'test'})
    
    print("  Structured logging: PASS (check logs above)")

def test_monitor_decorator():
    from monitoring import monitor_endpoint, metrics
    
    print("\nTesting Monitor Decorator:")
    
    @monitor_endpoint('test_endpoint')
    def test_function():
        return "success", 200
    
    # Reset metrics
    metrics.counters.clear()
    
    # Call monitored function
    result = test_function()
    
    print(f"  Function result: {'PASS' if result[0] == 'success' else 'FAIL'}")
    print(f"  Metrics recorded: {'PASS' if metrics.counters['test_endpoint_requests'] == 1 else 'FAIL'}")

if __name__ == "__main__":
    print("Testing Cache and Monitoring Components")
    print("=" * 45)
    
    test_cache_manager()
    test_metrics_collector()
    test_structured_logger()
    test_monitor_decorator()
    
    print("\n" + "=" * 45)
    print("Cache and Monitoring Tests Complete!")
    print("\nFeatures added:")
    print("  • Memory cache with TTL")
    print("  • Redis cache with fallback")
    print("  • Request/response metrics")
    print("  • Cache hit/miss tracking")
    print("  • Structured logging")
    print("  • Endpoint monitoring")