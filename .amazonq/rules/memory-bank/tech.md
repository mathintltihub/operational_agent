# Technology Stack

## Programming Languages

### Python 3.9+
- **Backend Language**: All backend code written in Python
- **Version Requirement**: Python 3.9 or higher
- **Usage**: FastAPI application, services, business logic, AI integration

### JavaScript (ES6+)
- **Frontend Language**: Vanilla JavaScript for frontend logic
- **Usage**: API calls, DOM manipulation, event handling, UI updates

### HTML5 & CSS3
- **Frontend Markup**: Semantic HTML5
- **Styling**: Modern CSS3 with flexbox/grid layouts

## Backend Technologies

### Web Framework
- **FastAPI 0.115.0+**: Modern, fast Python web framework
  - Automatic API documentation (Swagger UI)
  - Built-in request/response validation
  - Async support
  - Type hints integration

### Server
- **Uvicorn 0.30.0+**: ASGI server for FastAPI
  - High-performance async server
  - Hot reload in development

### Data Validation
- **Pydantic 2.9.0+**: Data validation using Python type hints
  - Request/response schema validation
  - Automatic JSON serialization
  - Type safety
- **Pydantic Settings 2.6.0+**: Settings management from environment variables

### AI/ML Stack
- **LangChain Core 0.3.0+**: LLM application framework
  - Structured output parsing
  - Prompt management
  - Chain composition
- **LangChain Google GenAI 1.0.0+**: Google Gemini integration
  - Alternative to OpenAI
  - Structured output support

### HTTP Clients
- **HTTPX 0.27.0+**: Modern async HTTP client
  - Used for API calls
  - Async/sync support
- **Requests 2.32.0+**: Traditional HTTP library
  - Synchronous HTTP requests
  - Simple API

### Configuration
- **Python-dotenv 1.0.0+**: Environment variable management
  - Load .env files
  - Configuration management

## Frontend Technologies

### Core
- **Vanilla JavaScript**: No frameworks, pure JS
- **Fetch API**: For HTTP requests to backend
- **DOM API**: Direct DOM manipulation

### Development Tools
- **Live-server 1.2.2**: Development server with hot reload
  - Auto-refresh on file changes
  - Serves static files
- **Concurrently 9.2.1**: Run multiple commands simultaneously
  - Run backend + frontend together

## Data Storage

### File-Based Storage
- **JSON Files**: Local data persistence
  - `backend/data/logs.json`: Analysis logs
  - Simple, human-readable format
  - No database setup required

## Development Tools

### Package Management
- **pip**: Python package manager
  - requirements.txt for dependencies
  - Virtual environment support
- **npm**: Node.js package manager
  - package.json for dev scripts
  - Dev dependencies only

### Version Control
- **Git**: Source control
  - .gitignore configured for Python/Node.js

## API Integration

### LLM Providers
- **OpenAI API**: Primary AI provider (optional)
  - GPT models for ticket analysis
  - Requires API key
- **Google Gemini API**: Alternative AI provider (optional)
  - Gemini models via LangChain
  - Requires API key
- **Ollama**: Local LLM option (future)
  - Run models locally
  - No API key needed

### Fallback Mode
- **Mock Mode**: Keyword-based analysis
  - No external dependencies
  - Works offline
  - Deterministic results

## Build & Run Commands

### Python Backend
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend
python backend/main.py
# or
cd backend && python main.py
```

### Frontend
```bash
# Install Node.js dev dependencies
npm install

# Run frontend only
npm run frontend

# Run backend only
npm run backend

# Run both concurrently
npm run dev
```

### Manual Frontend
```bash
# Python HTTP server
python -m http.server 8080 --directory frontend

# Or just open in browser
open frontend/index.html
```

## Testing

### Test Framework
- **Python unittest**: Built-in testing framework
  - Located in tests/test_api.py
  - API endpoint validation

### Manual Testing
- **Sample Tickets**: 12 pre-configured test cases
- **Health Endpoint**: Quick validation of backend status
- **Logs Endpoint**: Verify data persistence

## Configuration Files

### Python
- **requirements.txt**: Python dependencies with version constraints
- **.env**: Environment variables (API keys)
- **.env.example**: Template for environment setup

### Node.js
- **package.json**: Dev scripts and dependencies
- **package-lock.json**: Dependency lock file

### Git
- **.gitignore**: Excludes venv/, node_modules/, .env, data/logs.json

## Environment Variables

### Required (Optional)
- `OPENAI_API_KEY`: OpenAI API key for AI analysis
- `GOOGLE_API_KEY`: Google Gemini API key for AI analysis

### Behavior
- If no API key: Runs in mock mode
- If API key present: Uses AI analysis

## Port Configuration

### Backend
- **Default**: 127.0.0.1:8000
- **Configurable**: Can be changed in main.py

### Frontend
- **Development**: localhost:5173 (via live-server)
- **Manual**: Any port via Python HTTP server or direct file open

## CORS Configuration
- **Enabled**: For frontend-backend communication
- **Origins**: Configured in main.py for local development
