from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import threading

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import modular components
from chatbot import Chatbot
from validators import InputValidator
from rate_limiter import RateLimiter
from monitoring import monitor_endpoint, metrics, structured_logger

# Configuration from environment
class Config:
    BASE_URL = os.getenv('MPTI_BASE_URL', 'https://www.mptigh.com/')
    SCRAPE_TIMEOUT = int(os.getenv('SCRAPE_TIMEOUT', '60'))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '500'))
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '10'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '3600'))
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'memory')  # 'redis' or 'memory'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize components
validator = InputValidator(Config.MAX_MESSAGE_LENGTH)
rate_limiter = RateLimiter(Config.RATE_LIMIT_REQUESTS, Config.RATE_LIMIT_WINDOW)

# Initialize chatbot with error handling
try:
    chatbot = Chatbot(
        Config.BASE_URL, 
        Config.SCRAPE_TIMEOUT, 
        Config.SCRAPE_INTERVAL,
        Config.CACHE_TYPE
    )
    structured_logger.logger.info("Modular chatbot with caching initialized successfully")
except Exception as e:
    structured_logger.log_error('app_init', str(e))
    logger.error(f"Failed to initialize chatbot: {e}")
    chatbot = None

@app.route('/health', methods=['GET'])
@monitor_endpoint('health')
def health_check():
    if not chatbot:
        return jsonify({
            'status': 'unhealthy',
            'error': 'Chatbot not initialized',
            'timestamp': datetime.now().isoformat()
        }), 503
    
    status = chatbot.get_status()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        **status
    })


@app.route('/', methods=['GET', 'HEAD'])
def root():
    """Root endpoint used by PaaS health checks. Returns same payload as /health."""
    return health_check()

@app.route('/chat', methods=['POST'])
@monitor_endpoint('chat')
@rate_limiter.decorator()
def chat():
    """Main chat endpoint with monitoring"""
    if not chatbot:
        return jsonify({
            'error': 'Service temporarily unavailable',
            'reply': 'Please visit https://www.mptigh.com/ for information.'
        }), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        message = data.get('message', '')
        session_id = data.get('session_id')  # Optional session ID
        
        # Validate input
        validated_message, error = validator.validate(message)
        if error:
            return jsonify({'error': error}), 400
        
        start_time = datetime.now()
        
        # Process message with conversation context
        result = chatbot.process_message(validated_message, session_id)
        
        response_time = (datetime.now() - start_time).total_seconds()
        result['response_time'] = response_time
        
        structured_logger.log_request('POST', '/chat', 200, response_time, request.remote_addr)
        
        return jsonify(result)
        
    except Exception as e:
        structured_logger.log_error('chat_endpoint', str(e), {'message': message[:50]})
        return jsonify({
            'reply': 'Service temporarily unavailable. Please visit https://www.mptigh.com/ for information.',
            'error': 'Internal server error'
        }), 500

@app.route('/refresh', methods=['POST'])
@monitor_endpoint('refresh')
@rate_limiter.decorator(max_requests=2, window=300)
def refresh_knowledge():
    """Manually trigger knowledge refresh"""
    if not chatbot:
        return jsonify({'error': 'Service unavailable'}), 503
    
    try:
        threading.Thread(target=chatbot.refresh_knowledge, daemon=True).start()
        
        status = chatbot.get_status()
        structured_logger.log_request('POST', '/refresh', 200, 0, request.remote_addr)
        return jsonify({
            'message': 'Knowledge refresh triggered',
            **status
        })
    except Exception as e:
        structured_logger.log_error('refresh_endpoint', str(e))
        return jsonify({'error': 'Refresh failed'}), 500

@app.route('/metrics', methods=['GET'])
@monitor_endpoint('metrics')
def get_metrics():
    """Get system metrics"""
    stats = metrics.get_stats()
    if chatbot:
        conversation_stats = chatbot.get_conversation_stats()
        stats.update(conversation_stats)
    return jsonify(stats)

@app.route('/save-model', methods=['POST'])
@monitor_endpoint('save_model')
@rate_limiter.decorator(max_requests=1, window=300)
def save_model():
    """Save ML model weights"""
    if not chatbot:
        return jsonify({'error': 'Service unavailable'}), 503
    
    try:
        chatbot.save_ml_model()
        return jsonify({'message': 'ML model saved successfully'})
    except Exception as e:
        structured_logger.log_error('save_model', str(e))
        return jsonify({'error': 'Failed to save model'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info("🚀 MPTI Chatbot - Cached & Monitored")
    if chatbot:
        status = chatbot.get_status()
        logger.info(f"📊 Knowledge: {status['knowledge_sections']} sections loaded")
        logger.info(f"💾 Cache: {Config.CACHE_TYPE}")
        logger.info(f"⚡ Background scraping: Active (every {Config.SCRAPE_INTERVAL}s)")
    else:
        logger.error("❌ Chatbot initialization failed")
    
    logger.info(f"🛡️ Rate limiting: {Config.RATE_LIMIT_REQUESTS} req/{Config.RATE_LIMIT_WINDOW}s")
    logger.info(f"📈 Metrics endpoint: /metrics")
    logger.info(f"🌐 Server: 0.0.0.0:{port}")
    logger.info("✅ Ready with caching, monitoring, and structured logging!")
    
    app.run(host='0.0.0.0', port=port, debug=debug)