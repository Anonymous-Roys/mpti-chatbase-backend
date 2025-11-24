# MPTI Chatbot Backend - Hosting Guide

## 🚀 Hosting Options

### 1. **Render.com (Recommended - Free Tier Available)**

#### Setup:
1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create new Web Service
4. Use these settings:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT app:app
```

**Environment Variables:**
```
PORT=10000
MPTI_BASE_URL=https://www.mptigh.com/
DEBUG=False
CACHE_TYPE=memory
SCRAPE_TIMEOUT=10
MAX_MESSAGE_LENGTH=500
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW=60
SCRAPE_INTERVAL=3600
```

### 2. **Railway.app (Simple Deploy)**

#### Setup:
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Deploy: `railway up`

**railway.json:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT app:app",
    "healthcheckPath": "/health"
  }
}
```

### 3. **Heroku (Popular Choice)**

#### Setup:
1. Install Heroku CLI
2. Create app: `heroku create mpti-chatbot`
3. Deploy: `git push heroku main`

**Procfile:**
```
web: gunicorn --bind 0.0.0.0:$PORT app:app
```

### 4. **DigitalOcean App Platform**

#### Setup:
1. Create DigitalOcean account
2. Create new App
3. Connect repository
4. Configure:

**App Spec:**
```yaml
name: mpti-chatbot
services:
- name: web
  source_dir: /
  github:
    repo: your-username/your-repo
    branch: main
  run_command: gunicorn --bind 0.0.0.0:$PORT app:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  health_check:
    http_path: /health
  envs:
  - key: PORT
    value: "8080"
  - key: DEBUG
    value: "False"
```

### 5. **VPS/Cloud Server (Advanced)**

#### Requirements:
- **CPU**: 1 vCPU minimum (2 vCPU recommended)
- **RAM**: 512MB minimum (1GB recommended)
- **Storage**: 10GB minimum
- **OS**: Ubuntu 20.04+ or CentOS 8+

#### Setup Script:
```bash
#!/bin/bash
# Install Python and dependencies
sudo apt update
sudo apt install -y python3 python3-pip nginx supervisor

# Clone repository
git clone https://github.com/your-username/mpti-chatbot.git
cd mpti-chatbot/python-backend

# Install dependencies
pip3 install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/mpti-chatbot.service > /dev/null <<EOF
[Unit]
Description=MPTI Chatbot Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/mpti-chatbot/python-backend
Environment=PATH=/usr/bin/python3
ExecStart=/usr/local/bin/gunicorn --bind 0.0.0.0:10000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable mpti-chatbot
sudo systemctl start mpti-chatbot
```

## 📋 Resource Requirements

### **Minimum Requirements:**
- **CPU**: 1 vCPU
- **RAM**: 512MB
- **Storage**: 5GB
- **Bandwidth**: 10GB/month

### **Recommended Requirements:**
- **CPU**: 2 vCPU
- **RAM**: 1GB
- **Storage**: 20GB
- **Bandwidth**: 50GB/month

### **High Traffic Requirements:**
- **CPU**: 4 vCPU
- **RAM**: 2GB
- **Storage**: 50GB
- **Bandwidth**: 200GB/month

## 🔧 Production Configuration

### **Environment Variables (.env):**
```env
# Server Configuration
PORT=10000
HOST=0.0.0.0
DEBUG=False

# MPTI Configuration
MPTI_BASE_URL=https://www.mptigh.com/
SCRAPE_TIMEOUT=15
SCRAPE_INTERVAL=7200
MAX_MESSAGE_LENGTH=1000

# Performance
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=60
CACHE_TYPE=memory

# Monitoring
LOG_LEVEL=INFO
STRUCTURED_LOGGING=True
```

### **Gunicorn Configuration (gunicorn.conf.py):**
```python
bind = "0.0.0.0:10000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

## 🔒 Security Configuration

### **Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:10000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:10000/health;
        access_log off;
    }
}
```

### **SSL Certificate (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring & Logging

### **Health Check Endpoint:**
- URL: `https://your-domain.com/health`
- Expected Response: `{"status": "healthy"}`

### **Metrics Endpoint:**
- URL: `https://your-domain.com/metrics`
- Provides: Response times, request counts, error rates

### **Log Monitoring:**
```bash
# View logs
sudo journalctl -u mpti-chatbot -f

# Log rotation
sudo logrotate /etc/logrotate.d/mpti-chatbot
```

## 🚀 Deployment Commands

### **Quick Deploy Script:**
```bash
#!/bin/bash
echo "🚀 Deploying MPTI Chatbot Backend..."

# Pull latest code
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Restart service
sudo systemctl restart mpti-chatbot

# Check status
sudo systemctl status mpti-chatbot

echo "✅ Deployment complete!"
```

### **Docker Deployment:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  mpti-chatbot:
    build: .
    ports:
      - "10000:10000"
    environment:
      - PORT=10000
      - DEBUG=False
      - MPTI_BASE_URL=https://www.mptigh.com/
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "https://mpti-chatbase-backend.onrender.com/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 💰 Cost Estimates

### **Free Tier Options:**
- **Render.com**: Free (750 hours/month)
- **Railway.app**: $5/month (512MB RAM)
- **Heroku**: $7/month (512MB RAM)

### **Paid Options:**
- **DigitalOcean**: $6/month (1GB RAM)
- **AWS EC2**: $8-15/month (t3.micro)
- **Google Cloud**: $10-20/month (e2-micro)

## 🔧 WordPress Integration

### **Update WordPress Settings:**
1. Go to **MPTI Chatbase → Settings**
2. Update Backend URL to your hosted URL
3. Test connection
4. Save settings

### **CORS Configuration:**
Your backend already includes CORS support. For production, update:
```python
from flask_cors import CORS

# Allow specific origins in production
CORS(app, origins=['https://your-wordpress-site.com'])
```

## 🆘 Troubleshooting

### **Common Issues:**
1. **Port conflicts**: Change PORT environment variable
2. **Memory issues**: Upgrade to higher RAM plan
3. **Timeout errors**: Increase SCRAPE_TIMEOUT
4. **Rate limiting**: Adjust RATE_LIMIT_REQUESTS

### **Debug Commands:**
```bash
# Check service status
sudo systemctl status mpti-chatbot

# View logs
sudo journalctl -u mpti-chatbot -n 50

# Test endpoint
curl -X POST https://your-domain.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## 📈 Scaling

### **Horizontal Scaling:**
- Use load balancer (nginx, HAProxy)
- Deploy multiple instances
- Implement Redis for shared caching

### **Vertical Scaling:**
- Increase CPU/RAM
- Optimize worker processes
- Enable caching layers

---

**Choose the hosting option that best fits your budget and technical requirements. Render.com is recommended for beginners, while VPS offers more control for advanced users.**