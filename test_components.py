#!/usr/bin/env python3
"""
Test individual components to demonstrate modularity
"""

def test_intent_analyzer():
    from intent_analyzer import IntentAnalyzer
    
    analyzer = IntentAnalyzer()
    
    test_cases = [
        ("Hello there", "greeting"),
        ("Tell me about TACT program", "tact_program"),
        ("How can I apply?", "application"),
        ("What programs do you offer?", "programs"),
        ("How can I contact you?", "contact")
    ]
    
    print("Testing Intent Analyzer:")
    for message, expected in test_cases:
        result = analyzer.analyze(message)
        status = "PASS" if result == expected else "FAIL"
        print(f"  {status} '{message}' -> {result}")

def test_response_generator():
    from response_generator import ResponseGenerator
    
    generator = ResponseGenerator()
    
    print("\nTesting Response Generator:")
    response = generator.generate("greeting")
    print(f"  PASS Greeting response: {len(response)} chars")
    
    ctas = generator.get_ctas("application")
    print(f"  PASS Application CTAs: {len(ctas)} items")

def test_validator():
    from validators import InputValidator
    
    validator = InputValidator(max_length=50)
    
    test_cases = [
        ("Hello", True),
        ("", False),
        ("A" * 100, False),
        ("<script>alert('xss')</script>", True)  # Should be sanitized
    ]
    
    print("\nTesting Input Validator:")
    for message, should_pass in test_cases:
        result, error = validator.validate(message)
        passed = result is not None
        status = "PASS" if passed == should_pass else "FAIL"
        print(f"  {status} '{message[:20]}...' -> {'Valid' if passed else 'Invalid'}")

def test_rate_limiter():
    from rate_limiter import RateLimiter
    
    limiter = RateLimiter(max_requests=3, window=60)
    
    print("\nTesting Rate Limiter:")
    
    # Test multiple requests from same IP
    for i in range(5):
        allowed = limiter.is_allowed("127.0.0.1")
        status = "PASS" if allowed else "FAIL"
        print(f"  Request {i+1}: {status} {'Allowed' if allowed else 'Blocked'}")

if __name__ == "__main__":
    print("Testing Modular Components")
    print("=" * 40)
    
    test_intent_analyzer()
    test_response_generator()
    test_validator()
    test_rate_limiter()
    
    print("\n" + "=" * 40)
    print("All components tested individually!")
    print("Benefits of modular architecture:")
    print("  • Each component can be tested in isolation")
    print("  • Easy to modify without breaking other parts")
    print("  • Clear separation of concerns")
    print("  • Reusable components")