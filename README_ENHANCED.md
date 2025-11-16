# MPTI Chatbase AI - Enhanced Website Integration

## 🎯 Overview

This enhanced version of the MPTI Chatbase AI system provides comprehensive website scraping and intelligent responses about MPTI Technical Institute. The system automatically discovers and scrapes all relevant pages from https://www.mptigh.com/ to provide accurate, up-to-date information.

## 🚀 Key Features

### Enhanced Web Scraping
- **Comprehensive Page Discovery**: Automatically finds and scrapes all relevant MPTI website pages
- **Intelligent Content Extraction**: Advanced parsing to extract meaningful content from various page layouts
- **Structured Data Processing**: Extracts lists, tables, and other structured information
- **Real-time Content Refresh**: Manual and automatic website content updates

### Improved AI Responses
- **MPTI-Focused Context**: AI responses specifically tailored for MPTI information
- **Multi-Source Knowledge**: Combines multiple website pages for comprehensive answers
- **Enhanced Rule-Based Fallback**: Detailed MPTI information even without OpenAI
- **Intelligent Search Matching**: Advanced relevance scoring for better context selection

### WordPress Integration
- **Public Access Enabled**: Allows public users to access MPTI information
- **Enhanced Analytics**: Detailed conversation tracking and performance metrics
- **Health Monitoring**: Real-time backend status checking
- **Content Management**: Admin tools for refreshing website content

## 📁 File Structure

```
python-backend/
├── app.py                    # Main Flask application with enhanced scraping
├── website_scraper.py        # Dedicated scraper (if using separate file)
├── knowledge_base.py         # Enhanced knowledge management
├── test_scraper.py          # Comprehensive test suite
├── start_mpti_backend.bat   # Windows launcher script
├── requirements.txt         # Updated dependencies
├── .env                     # Environment variables (create this)
└── documents/               # Additional documents directory
```

## 🛠️ Installation & Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the python-backend directory:

```env
# OpenAI Configuration (optional but recommended)
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=False

# MPTI Website Configuration
MPTI_WEBSITE_URL=https://www.mptigh.com/
SCRAPING_ENABLED=True
```

### 3. Quick Start (Windows)

Simply double-click `start_mpti_backend.bat` or run:

```cmd
start_mpti_backend.bat
```

### 4. Manual Start

```bash
python app.py
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_scraper.py
```

This will test:
- Backend health check
- Comprehensive website scraping
- Knowledge base statistics
- Chat functionality with various MPTI queries

## 🌐 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health and status |
| `/chat/ai` | POST | Main chat with AI enhancement |
| `/chat/simple` | POST | Simple rule-based chat |

### Knowledge Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/knowledge/refresh` | POST | Refresh website content |
| `/knowledge/stats` | GET | Knowledge base statistics |
| `/scrape/comprehensive` | POST | Trigger full website scraping |

### Example Usage

```javascript
// Chat with MPTI Assistant
fetch('http://localhost:5000/chat/ai', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "What courses does MPTI offer?",
        conversation_id: "user_123",
        use_ai: true
    })
})
.then(response => response.json())
.then(data => {
    console.log('Reply:', data.reply);
    console.log('Sources used:', data.sources_used);
    console.log('Response time:', data.response_time);
});
```

## 🔧 WordPress Plugin Integration

### Enhanced Features

1. **Public Access**: The chatbot is now accessible to all website visitors
2. **Real-time Health Monitoring**: Admin dashboard shows backend status
3. **Content Refresh**: Admins can manually refresh MPTI website content
4. **Enhanced Analytics**: Detailed conversation tracking and performance metrics

### Admin Functions

- **Settings**: Configure backend URL and AI settings
- **Knowledge Base**: Manage and refresh website content
- **Analytics**: View conversation statistics and popular questions
- **Health Check**: Monitor backend connectivity and performance

## 📊 Monitoring & Analytics

### Health Check Response
```json
{
    "status": "healthy",
    "version": "2.1.0-comprehensive-scraping",
    "mpti_integration": {
        "website_url": "https://www.mptigh.com/",
        "scraping_enabled": true,
        "comprehensive_mode": true
    },
    "components": {
        "ai_models": true,
        "knowledge_base": true,
        "website_content_loaded": 15,
        "total_documents": 18
    }
}
```

### Knowledge Base Statistics
```json
{
    "total_documents": 18,
    "website_documents": 15,
    "fallback_documents": 3,
    "document_details": {
        "website": [
            {
                "id": "website_home",
                "length": 2847,
                "preview": "Page: MPTI Technical Institute..."
            }
        ]
    }
}
```

## 🎯 MPTI-Specific Features

### Comprehensive Content Coverage
- **Homepage**: Main MPTI information and overview
- **About/About Us**: Institution history and mission
- **Courses/Programs**: Academic offerings and curriculum
- **Admissions**: Application process and requirements
- **Contact**: Location, phone, email information
- **Facilities**: Campus and equipment information
- **News/Events**: Latest updates and announcements
- **Staff/Faculty**: Personnel information
- **Student Life**: Campus experience details

### Intelligent Response System
- **Context-Aware**: Uses multiple website sources for comprehensive answers
- **MPTI-Focused**: Responses specifically tailored for MPTI inquiries
- **Fallback Information**: Provides helpful MPTI details even when scraping fails
- **Website References**: Always directs users to official website for current information

## 🔍 Troubleshooting

### Common Issues

1. **Backend Not Starting**
   - Check Python installation: `python --version`
   - Verify dependencies: `pip install -r requirements.txt`
   - Check port availability: Ensure port 5000 is not in use

2. **Scraping Issues**
   - Verify internet connection
   - Check if MPTI website is accessible
   - Review scraping logs for specific errors

3. **WordPress Integration**
   - Ensure backend URL is correctly configured in WordPress admin
   - Check that backend is running and accessible
   - Verify REST API permissions

### Debug Mode

Enable debug mode by setting `DEBUG=True` in `.env` file for detailed logging.

## 📈 Performance Optimization

### Scraping Optimization
- **Respectful Delays**: 0.5-1 second delays between requests
- **Content Limits**: Reasonable limits on content length and page count
- **Error Handling**: Graceful handling of failed requests
- **Caching**: Intelligent caching of scraped content

### Response Optimization
- **Context Prioritization**: Best matches get more context space
- **Source Limiting**: Limits number of sources to prevent overwhelming AI
- **Response Caching**: Conversation history for context continuity

## 🔐 Security Considerations

- **Rate Limiting**: Respectful scraping with appropriate delays
- **Input Sanitization**: All user inputs are properly sanitized
- **Error Handling**: Secure error messages without sensitive information
- **API Key Protection**: Environment variables for sensitive configuration

## 🚀 Future Enhancements

- **Scheduled Scraping**: Automatic periodic content updates
- **Advanced Analytics**: More detailed conversation insights
- **Multi-language Support**: Support for local languages
- **Enhanced AI Models**: Integration with newer AI models
- **Mobile Optimization**: Better mobile chat experience

## 📞 Support

For technical support or questions about the MPTI Chatbase AI system:

1. Check the logs in `mpti_chatbot.log`
2. Run the test suite: `python test_scraper.py`
3. Verify backend health: `http://localhost:5000/health`
4. Review WordPress plugin settings and logs

---

**MPTI Chatbase AI - Providing comprehensive, accurate information about MPTI Technical Institute through intelligent web scraping and AI-powered responses.**