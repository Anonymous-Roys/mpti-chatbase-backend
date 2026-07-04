from quart import Quart, request, jsonify
from quart_cors import cors
import os
import logging
import asyncio
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import async components
from async_chatbot import AsyncChatbot
from validators import InputValidator
from rate_limiter import RateLimiter
from monitoring import monitor_endpoint, metrics, structured_logger

# Configuration from environment
class Config:
    BASE_URL = os.getenv('MPTI_BASE_URL', 'https://www.mptigh.com/')
    SCRAPE_TIMEOUT = int(os.getenv('SCRAPE_TIMEOUT', '10'))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '500'))
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '10'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '3600'))
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'memory')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Quart(__name__)
app = cors(app)

# Initialize components
validator = InputValidator(Config.MAX_MESSAGE_LENGTH)
rate_limiter = RateLimiter(Config.RATE_LIMIT_REQUESTS, Config.RATE_LIMIT_WINDOW)

# Initialize async chatbot
chatbot = None

@app.before_serving
async def startup():
    """Initialize async chatbot on startup with fallback"""
    global chatbot
    max_retries = 3
    for attempt in range(max_retries):
        try:
            chatbot = AsyncChatbot(
                Config.BASE_URL, 
                Config.SCRAPE_TIMEOUT, 
                Config.SCRAPE_INTERVAL,
                Config.CACHE_TYPE
            )
            structured_logger.logger.info("Async modular chatbot with caching initialized successfully")
            logger.info("🚀 Async MPTI Chatbot - Ready!")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Chatbot init attempt {attempt + 1} failed: {e}, retrying...")
                await asyncio.sleep(2)
            else:
                structured_logger.log_error('async_app_init', str(e))
                logger.error(f"Failed to initialize async chatbot after {max_retries} attempts: {e}")
                # Continue without chatbot - will use fallback responses

@app.after_serving
async def cleanup():
    """Cleanup async resources on shutdown"""
    if chatbot:
        chatbot.cleanup()
        logger.info("Async chatbot resources cleaned up")

@app.route('/health', methods=['GET'])
@monitor_endpoint('health')
async def health_check():
    if not chatbot:
        return jsonify({
            'status': 'unhealthy',
            'error': 'Async chatbot not initialized',
            'timestamp': datetime.now().isoformat()
        }), 503
    
    status = chatbot.get_status()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        **status
    })

@app.route('/', methods=['GET', 'HEAD'])
async def root():
    """Root endpoint used by PaaS health checks"""
    return await health_check()

@app.route('/chat', methods=['POST'])
@monitor_endpoint('chat')
async def chat():
    """Main async chat endpoint with concurrent processing"""
    if not chatbot:
        return jsonify({
            'error': 'Service temporarily unavailable',
            'reply': 'Please visit https://www.mptigh.com/ for information.'
        }), 503
    
    try:
        # Rate limiting check (sync)
        client_ip = request.remote_addr
        if not rate_limiter.allow_request(client_ip):
            return jsonify({
                'error': 'Rate limit exceeded',
                'reply': 'Please wait before sending another message.'
            }), 429
        
        data = await request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        message = data.get('message', '')
        session_id = data.get('session_id')
        
        # Validate input
        validated_message, error = validator.validate(message)
        if error:
            return jsonify({'error': error}), 400
        
        start_time = datetime.now()
        
        # Process message asynchronously with concurrent operations
        result = await chatbot.async_process_message(validated_message, session_id)
        
        response_time = (datetime.now() - start_time).total_seconds()
        result['response_time'] = response_time
        
        structured_logger.log_request('POST', '/chat', 200, response_time, client_ip)
        
        return jsonify(result)
        
    except Exception as e:
        structured_logger.log_error('async_chat_endpoint', str(e), {'message': message[:50] if 'message' in locals() else 'unknown'})
        return jsonify({
            'reply': 'Service temporarily unavailable. Please visit https://www.mptigh.com/ for information.',
            'error': 'Internal server error'
        }), 500

@app.route('/refresh', methods=['POST'])
@monitor_endpoint('refresh')
async def refresh_knowledge():
    """Manually trigger async knowledge refresh"""
    if not chatbot:
        return jsonify({'error': 'Service unavailable'}), 503
    
    try:
        # Rate limiting for refresh endpoint
        client_ip = request.remote_addr
        if not rate_limiter.allow_request(client_ip, max_requests=2, window=300):
            return jsonify({'error': 'Refresh rate limit exceeded'}), 429
        
        # Trigger async refresh in background
        asyncio.create_task(chatbot.async_refresh_knowledge())
        
        status = chatbot.get_status()
        structured_logger.log_request('POST', '/refresh', 200, 0, client_ip)
        return jsonify({
            'message': 'Async knowledge refresh triggered',
            **status
        })
    except Exception as e:
        structured_logger.log_error('async_refresh_endpoint', str(e))
        return jsonify({'error': 'Async refresh failed'}), 500

@app.route('/metrics', methods=['GET'])
@monitor_endpoint('metrics')
async def get_metrics():
    """Get system metrics"""
    stats = metrics.get_stats()
    if chatbot:
        conversation_stats = chatbot.get_conversation_stats()
        stats.update(conversation_stats)
    return jsonify(stats)

@app.route('/save-model', methods=['POST'])
@monitor_endpoint('save_model')
async def save_model():
    """Save ML model weights"""
    if not chatbot:
        return jsonify({'error': 'Service unavailable'}), 503
    
    try:
        # Rate limiting for model saving
        client_ip = request.remote_addr
        if not rate_limiter.allow_request(client_ip, max_requests=1, window=300):
            return jsonify({'error': 'Model save rate limit exceeded'}), 429
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, chatbot.save_ml_model)
        
        return jsonify({'message': 'ML model saved successfully'})
    except Exception as e:
        structured_logger.log_error('async_save_model', str(e))
        return jsonify({'error': 'Failed to save model'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info("🚀 MPTI Async Chatbot - Production Ready")
    logger.info(f"💾 Cache: {Config.CACHE_TYPE}")
    logger.info(f"⚡ Async scraping: Active (every {Config.SCRAPE_INTERVAL}s)")
    logger.info(f"🛡️ Rate limiting: {Config.RATE_LIMIT_REQUESTS} req/{Config.RATE_LIMIT_WINDOW}s")
    logger.info(f"📈 Metrics endpoint: /metrics")
    logger.info(f"🌐 Server: 0.0.0.0:{port}")
    logger.info("✅ Production deployment with async processing!")
    
    # Use hypercorn for production
    try:
        import hypercorn.asyncio
        from hypercorn import Config as HyperConfig
        
        config = HyperConfig()
        config.bind = [f"0.0.0.0:{port}"]
        config.workers = 2
        config.access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s"'
        
        asyncio.run(hypercorn.asyncio.serve(app, config))
    except ImportError:
        # Fallback to quart dev server
        app.run(host='0.0.0.0', port=port, debug=debug)