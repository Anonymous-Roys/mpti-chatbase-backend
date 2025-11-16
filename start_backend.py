#!/usr/bin/env python3
"""
MPTI Chatbase Backend Launcher
Automatically detects and starts the appropriate Python backend
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask-cors', 'requests', 'beautifulsoup4']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required packages are installed")
    return True

def setup_environment():
    """Setup environment variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("📝 Creating .env file with default settings...")
        with open('.env', 'w') as f:
            f.write("""# MPTI Chatbase Backend Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=True

# AI Provider Configuration
AI_PROVIDER=groq
AI_MODEL=llama3-8b-8192

# Groq API Configuration (Get free key from console.groq.com)
# IMPORTANT: Do NOT commit your API key. Set `GROQ_API_KEY` in your environment
# or create a local `.env` file with the key and keep it out of git.
GROQ_API_KEY=
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama3-8b-8192

# Ollama Configuration (for local AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# Database Configuration
DATABASE_URL=sqlite:///mpti_chatbot.db
""")
        print("✅ Created .env file with default configuration")
    else:
        print("✅ Found existing .env file")

def get_available_backends():
    """Get list of available backend applications"""
    backends = {}
    
    if Path('enhanced_chatbot.py').exists():
        backends['enhanced'] = {
            'file': 'enhanced_chatbot.py',
            'name': 'Enhanced Chatbot',
            'description': 'External Links & Forms Integration',
            'endpoints': ['/chat', '/health', '/refresh']
        }
    
    if Path('intelligent_agent.py').exists():
        backends['intelligent'] = {
            'file': 'intelligent_agent.py',
            'name': 'Intelligent Agent',
            'description': 'Advanced Website Analysis & CTAs',
            'endpoints': ['/chat', '/health', '/refresh-intelligence']
        }
    
    return backends

def start_backend(backend_type='main', port=5000):
    """Start the specified backend"""
    backends = get_available_backends()
    
    if not backends:
        print("❌ No backend applications found!")
        return False
    
    if backend_type not in backends:
        print(f"❌ Backend '{backend_type}' not found!")
        print(f"Available backends: {', '.join(backends.keys())}")
        return False
    
    backend = backends[backend_type]
    
    print(f"🚀 Starting {backend['name']} ({backend['description']})...")
    print(f"📁 File: {backend['file']}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"🔗 Endpoints: {', '.join(backend['endpoints'])}")
    print("=" * 60)
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['HOST'] = '0.0.0.0'
        
        # Start the backend
        subprocess.run([sys.executable, backend['file']], env=env)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='MPTI Chatbase Backend Launcher')
    parser.add_argument('--backend', '-b', 
                       choices=['enhanced', 'intelligent'], 
                       default='enhanced',
                       help='Backend type to start (default: enhanced)')
    parser.add_argument('--port', '-p', 
                       type=int, 
                       default=5000,
                       help='Port to run on (default: 5000)')
    parser.add_argument('--list', '-l', 
                       action='store_true',
                       help='List available backends')
    
    args = parser.parse_args()
    
    print("🤖 MPTI Chatbase Backend Launcher")
    print("=" * 40)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    if args.list:
        backends = get_available_backends()
        if backends:
            print("Available backends:")
            for key, backend in backends.items():
                print(f"  {key}: {backend['name']} - {backend['description']}")
        else:
            print("No backend applications found!")
        return
    
    # Check requirements
    if not check_requirements():
        return
    
    # Setup environment
    setup_environment()
    
    # Start backend
    start_backend(args.backend, args.port)

if __name__ == '__main__':
    main()