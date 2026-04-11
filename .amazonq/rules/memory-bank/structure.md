# Project Structure

## Directory Organization

```
operational_agent/
├── backend/                    # Python FastAPI backend
│   ├── data/                  # Local data storage
│   │   └── logs.json         # Analysis logs (request/response pairs)
│   ├── prompts/              # AI prompt templates
│   │   └── operations_agent_prompt.txt  # System prompt for ticket analysis
│   ├── services/             # Business logic services
│   │   ├── __init__.py
│   │   ├── analyzer.py       # LangChain ticket analyzer (core AI logic)
│   │   ├── identity_skill.py # Identity/access management utilities
│   │   ├── logger.py         # JSON logging service
│   │   ├── ollama_client.py  # Ollama LLM client integration
│   │   └── sample_data.py    # Sample ticket data for testing
│   ├── __init__.py
│   ├── main.py               # FastAPI application entry point
│   ├── schemas.py            # Pydantic models for validation
│   └── utils_network.py      # Network utility functions
├── frontend/                  # HTML/CSS/JS frontend
│   ├── app.js                # Frontend logic and API calls
│   ├── index.html            # Main UI
│   └── style.css             # Styles
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_api.py           # API endpoint tests
├── .env                       # Environment variables (not in git)
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── package.json              # Node.js scripts for dev workflow
├── package-lock.json         # Node.js dependency lock
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

## Core Components

### Backend Architecture

#### 1. API Layer (main.py)
- **FastAPI Application**: RESTful API server with CORS support
- **Endpoints**:
  - `GET /health` - Health check with version info
  - `POST /analyze-ticket` - Main ticket analysis endpoint
  - `GET /sample-tickets` - Retrieve sample tickets
  - `GET /logs` - Get all analysis logs
  - `GET /logs/{ticket_id}` - Get specific log entry
  - `DELETE /logs` - Clear all logs
- **Port**: Runs on 127.0.0.1:8000
- **CORS**: Configured for frontend access

#### 2. Service Layer (services/)
- **analyzer.py**: Core ticket analysis logic
  - LangChain integration with OpenAI/Google Gemini
  - Structured output parsing
  - Mock mode fallback with keyword matching
  - Confidence scoring and reasoning
  
- **logger.py**: Persistent logging service
  - JSON-based storage in data/logs.json
  - CRUD operations for log entries
  - Thread-safe file operations
  
- **sample_data.py**: Test data provider
  - 12 pre-configured sample tickets
  - Expected classifications for validation
  
- **identity_skill.py**: Identity/access utilities
  - Helper functions for access-related tickets
  
- **ollama_client.py**: Local LLM integration
  - Alternative to OpenAI for local inference

#### 3. Data Layer (schemas.py)
- **TicketRequest**: Input validation (title, description)
- **TicketResponse**: Structured analysis output (issue_type, priority, team, steps, etc.)
- **SampleTicket**: Sample ticket structure
- **LogEntry**: Log storage format
- **HealthResponse**: Health check format

### Frontend Architecture

#### 1. UI Layer (index.html)
- Single-page application
- Form for ticket input (title + description)
- Results display area
- Sample tickets sidebar
- Logs viewer

#### 2. Logic Layer (app.js)
- API communication with backend
- Form handling and validation
- Dynamic UI updates
- Sample ticket loading
- Log display and management

#### 3. Presentation Layer (style.css)
- Responsive design
- Clean, professional styling
- Color-coded priority indicators
- Card-based layout

## Architectural Patterns

### 1. Layered Architecture
- **Presentation Layer**: HTML/CSS/JS frontend
- **API Layer**: FastAPI REST endpoints
- **Service Layer**: Business logic (analyzer, logger)
- **Data Layer**: JSON file storage

### 2. Service-Oriented Design
- Each service has a single responsibility
- Services are loosely coupled
- Easy to swap implementations (e.g., OpenAI → Ollama)

### 3. Schema-First API Design
- Pydantic models define contracts
- Automatic validation and serialization
- Type safety throughout the stack

### 4. Fallback Pattern
- Primary: OpenAI/Gemini API analysis
- Fallback: Mock mode with keyword matching
- Graceful degradation without API key

### 5. Local-First Data
- All data stored locally in JSON
- No external database required
- Simple file-based persistence

## Component Relationships

```
Frontend (app.js)
    ↓ HTTP POST
API Layer (main.py)
    ↓ validates with
Schemas (schemas.py)
    ↓ calls
Analyzer Service (analyzer.py)
    ↓ uses
LangChain + OpenAI/Gemini
    ↓ returns structured
TicketResponse
    ↓ logged by
Logger Service (logger.py)
    ↓ persists to
data/logs.json
```

## Configuration Management

### Environment Variables (.env)
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `GOOGLE_API_KEY`: Google Gemini API key (optional)
- Falls back to mock mode if not set

### Package Management
- **Python**: requirements.txt with pinned versions
- **Node.js**: package.json for dev scripts (concurrently, live-server)

## Development Workflow

### Scripts (package.json)
- `npm run dev`: Run backend + frontend concurrently
- `npm run frontend`: Start frontend only (port 5173)
- `npm run backend`: Start backend only (port 8000)

### Manual Workflow
1. Activate virtual environment
2. Run `python backend/main.py` for backend
3. Open `frontend/index.html` or use live-server for frontend
