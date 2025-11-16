import os
from datetime import timedelta

class Config:
    """Configuration settings for the Flask application"""
    
    # Basic settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'mpti-chatbase-secret-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # AI Settings - DeepSeek Configuration
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    AI_MODEL = os.getenv('AI_MODEL', 'deepseek-chat')
    
    # Legacy OpenAI support (fallback)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Knowledge Base Settings
    CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    # Sentiment Analysis
    SENTIMENT_MODEL = os.getenv('SENTIMENT_MODEL', 'distilbert-base-uncased-finetuned-sst-2-english')
    EMOTION_MODEL = os.getenv('EMOTION_MODEL', 'j-hartmann/emotion-english-distilroberta-base')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')