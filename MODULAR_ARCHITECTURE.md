# MPTI Chatbot - Modular Architecture

## 🏗️ Architecture Overview

The system has been refactored from a monolithic design to a modular architecture with clear separation of concerns.

## 📦 Components

### 1. **scraper.py** - Web Scraping
- `WebScraper`: Handles HTTP requests and HTML parsing
- `LinkExtractor`: Extracts external links from pages
- **Responsibility**: Data collection from websites
- **Dependencies**: requests, BeautifulSoup

### 2. **knowledge_manager.py** - Content Management
- `KnowledgeManager`: Manages content storage and updates
- **Responsibility**: Knowledge base operations and background updates
- **Dependencies**: scraper.py, threading

### 3. **intent_analyzer.py** - Intent Recognition
- `IntentAnalyzer`: Analyzes user messages for intent
- **Responsibility**: Understanding user queries
- **Dependencies**: None (pure logic)

### 4. **response_generator.py** - Response Creation
- `ResponseGenerator`: Generates responses and CTAs
- **Responsibility**: Creating user-facing content
- **Dependencies**: None (template-based)

### 5. **validators.py** - Input Validation
- `InputValidator`: Validates and sanitizes user input
- **Responsibility**: Security and data validation
- **Dependencies**: re (regex)

### 6. **rate_limiter.py** - Rate Limiting
- `RateLimiter`: Controls request frequency
- **Responsibility**: API protection and abuse prevention
- **Dependencies**: datetime, collections

### 7. **chatbot.py** - Main Orchestrator
- `Chatbot`: Coordinates all components
- **Responsibility**: Business logic orchestration
- **Dependencies**: All above components

### 8. **app.py** - Web Interface
- Flask application with minimal logic
- **Responsibility**: HTTP handling and routing
- **Dependencies**: chatbot.py, Flask

## ✅ Benefits Achieved

### **Separation of Concerns**
- Each component has a single, well-defined responsibility
- Changes to one component don't affect others
- Clear interfaces between components

### **Testability**
- Each component can be tested in isolation
- Mock dependencies easily for unit testing
- Test coverage can be measured per component

### **Maintainability**
- Easy to locate and fix bugs
- Simple to add new features
- Clear code organization

### **Reusability**
- Components can be reused in other projects
- Easy to swap implementations (e.g., different scrapers)
- Modular deployment options

## 🧪 Testing

Run individual component tests:
```bash
python test_components.py
```

Test specific components:
```python
from intent_analyzer import IntentAnalyzer
analyzer = IntentAnalyzer()
result = analyzer.analyze("Hello")  # Returns: 'greeting'
```

## 🔄 Component Interactions

```
User Request
     ↓
  app.py (Flask)
     ↓
  validators.py (Input validation)
     ↓
  rate_limiter.py (Rate limiting)
     ↓
  chatbot.py (Orchestration)
     ↓
  ┌─ intent_analyzer.py (Intent detection)
  ├─ knowledge_manager.py (Content search)
  └─ response_generator.py (Response creation)
     ↓
  JSON Response
```

## 🚀 Adding New Features

### Adding a New Intent:
1. Update `intent_analyzer.py` patterns
2. Add response template to `response_generator.py`
3. No changes needed elsewhere

### Adding a New Data Source:
1. Create new scraper in `scraper.py`
2. Update `knowledge_manager.py` to use it
3. No changes to other components

### Adding New Validation Rules:
1. Update `validators.py` only
2. All endpoints automatically use new rules

## 📊 Before vs After

| Aspect | Before (Monolithic) | After (Modular) |
|--------|-------------------|-----------------|
| **Testing** | Hard to test parts | Easy unit testing |
| **Debugging** | Complex debugging | Isolated debugging |
| **Changes** | Risky modifications | Safe, isolated changes |
| **Reusability** | Tightly coupled | Highly reusable |
| **Understanding** | Complex codebase | Clear, focused modules |

## 🛠️ Development Workflow

1. **Identify the component** responsible for the feature
2. **Modify only that component** 
3. **Test the component** in isolation
4. **Test integration** with other components
5. **Deploy** with confidence

The modular architecture makes the system more maintainable, testable, and scalable while reducing coupling between different concerns.