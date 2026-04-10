# Operations Agent

IT Operations Ticket Triage System - Local MVP

## Overview

Operations Agent is a local-first MVP for an AI-based IT Operations platform. It automates ticket triage, issue classification, priority detection, team assignment, and troubleshooting suggestions for IT support teams.

## Features

- **Ticket Analysis**: Analyzes support tickets using AI (LangChain + OpenAI)
- **Issue Classification**: Categorizes tickets into server, network, database, application, or access/request
- **Priority Detection**: Identifies critical, high, medium, or low priority
- **Team Routing**: Recommends the appropriate team for ticket assignment
- **Troubleshooting Steps**: Suggests practical, safe troubleshooting steps
- **Local Logging**: Saves all request/response pairs locally in JSON format
- **Mock Mode**: Works without API key using keyword-based analysis

## Architecture

```
operations_agent/
├── frontend/
│   ├── index.html     # Main UI
│   ├── style.css     # Styles
│   └── app.js        # Frontend logic
├── backend/
│   ├── main.py       # FastAPI application
│   ├── schemas.py   # Pydantic models
│   ├── services/
│   │   ├── analyzer.py    # LangChain ticket analyzer
│   │   ├── logger.py     # JSON logging service
│   │   └── sample_data.py # Sample tickets
│   ├── prompts/
│   │   └── operations_agent_prompt.txt # System prompt
│   └── data/
│       └── logs.json # Analysis logs
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.9+
- For AI analysis: OpenAI API key (optional - mock mode available)

## Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-api-key-here
```

**Note**: Without an API key, the app runs in mock mode with keyword-based analysis.

### 4. Start the Backend

```bash
cd backend
python main.py
```

The API will be available at `http://127.0.0.1:8000`

### 5. Start the Frontend

Open `frontend/index.html` in your browser, or use a simple HTTP server:

```bash
# Python 3
python -m http.server 8080 --directory frontend
```

Then visit `http://localhost:8080`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/analyze-ticket` | POST | Analyze a ticket |
| `/sample-tickets` | GET | Get sample tickets |
| `/logs` | GET | Get analysis logs |
| `/logs/{ticket_id}` | GET | Get specific log |
| `/logs` | DELETE | Clear logs |

## Usage

1. Open the frontend in your browser
2. Enter a ticket title and description
3. Click "Analyze Ticket"
4. View the classification results

Or click on a sample ticket to auto-fill the form.

## Sample Tickets

| ID | Title | Expected Issue | Expected Priority |
|----|-------|----------------|-------------------|
| 001 | Unable to connect to database from application | database | high |
| 002 | VPN users cannot access internal portal | network | high |
| 003 | Production application returns HTTP 500 | application | critical |
| 004 | Need access to production server | access/request | medium |
| 005 | Linux server CPU usage is 98 percent | server | high |
| 006 | Email password reset request | access/request | low |
| 007 | Network latency to US-East region | network | medium |
| 008 | Database replication lag | database | medium |
| 009 | Application crash on startup | application | high |
| 010 | Request for admin access to analytics platform | access/request | low |
| 011 | Web server unreachable | server | critical |
| 012 | Strange login attempts detected | network | high |

## Running Tests

```bash
# Basic API validation
python -c "
import requests
import json

BASE = 'http://127.0.0.1:8000'

# Test health
r = requests.get(f'{BASE}/health')
print('Health:', r.json())

# Test sample tickets
r = requests.get(f'{BASE}/sample-tickets')
print('Sample tickets:', len(r.json()))

# Test analyze ticket
r = requests.post(f'{BASE}/analyze-ticket', json={
    'title': 'Cannot connect to database',
    'description': 'Application timeout when connecting to DB'
})
print('Analysis result:', json.dumps(r.json(), indent=2))
"
```

## Configuration

### Mock Mode
If no `OPENAI_API_KEY` is set, the app uses keyword-based analysis:
- Good for demos and testing
- Uses keyword matching to determine issue type
- Always returns a result

### Live Mode
With a valid OpenAI API key:
- Uses GPT-4 with LangChain
- More accurate classification
- Better reasoning and troubleshooting steps

## Next Improvements

- Add more LLM provider options (Anthropic, local models)
- Implement ticket history and trending
- Add team workload balancing
- Add custom routing rules
- Add notification integrations (Slack, email)
- Add dashboard with analytics
- Implement ticket status tracking
- Add user authentication