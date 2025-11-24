#!/bin/bash

# MPTI Chatbot Backend Deployment Script
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e

ENVIRONMENT=${1:-development}
echo "🚀 Deploying MPTI Chatbot Backend to $ENVIRONMENT..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Run tests if they exist
if [ -f "test_complete_system.py" ]; then
    print_status "Running tests..."
    python test_complete_system.py
fi

# Set environment variables based on deployment environment
if [ "$ENVIRONMENT" = "production" ]; then
    export DEBUG=False
    export PORT=10000
    export RATE_LIMIT_REQUESTS=50
    export SCRAPE_INTERVAL=7200
    print_status "Production environment configured"
elif [ "$ENVIRONMENT" = "staging" ]; then
    export DEBUG=True
    export PORT=10001
    export RATE_LIMIT_REQUESTS=20
    export SCRAPE_INTERVAL=3600
    print_status "Staging environment configured"
else
    export DEBUG=True
    export PORT=10000
    export RATE_LIMIT_REQUESTS=10
    export SCRAPE_INTERVAL=1800
    print_status "Development environment configured"
fi

# Check if gunicorn is available for production
if [ "$ENVIRONMENT" = "production" ] && command -v gunicorn &> /dev/null; then
    print_status "Starting with Gunicorn (Production)..."
    gunicorn --config gunicorn.conf.py app:app
elif [ "$ENVIRONMENT" = "production" ]; then
    print_warning "Gunicorn not found, installing..."
    pip install gunicorn
    print_status "Starting with Gunicorn (Production)..."
    gunicorn --config gunicorn.conf.py app:app
else
    print_status "Starting with Flask development server..."
    python app.py
fi