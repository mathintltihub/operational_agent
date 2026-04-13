# Operations Agent

Operations Agent is a local-first IT operations triage assistant with a FastAPI backend, a lightweight chat frontend, deterministic skill-based analysis, and optional Ollama-powered enrichment.

It is designed for support-style workflows such as incident intake, priority estimation, team routing, and troubleshooting guidance without requiring any cloud dependency.

## What It Does

- accepts free-form IT issue descriptions through API or chat UI
- classifies the issue type
- estimates priority
- recommends the owning team
- summarizes impacted area
- suggests next troubleshooting steps
- logs analysis results locally

When Ollama is available, the backend uses a local model to improve analysis. When it is not available, the app continues working with rule-based logic.

## Tech Stack

- Backend: FastAPI
- Frontend: static HTML, CSS, and vanilla JavaScript
- Optional local LLM: Ollama
- Default Ollama model: `llama3.2:3b`
- Log storage: `backend/data/logs.json`

## Project Structure

```text
operational_agent/
├── backend/
│   ├── data/
│   │   └── logs.json
│   ├── prompts/
│   │   └── operations_agent_prompt.txt
│   ├── services/
│   │   ├── agent_skills.py
│   │   ├── analyzer.py
│   │   ├── identity_skill.py
│   │   ├── logger.py
│   │   ├── ollama_client.py
│   │   └── sample_data.py
│   ├── main.py
│   ├── schemas.py
│   └── utils_network.py
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── tests/
│   └── test_api.py
├── .env.example
├── package.json
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- Node.js and npm for the frontend dev server
- Ollama only if you want local LLM-backed analysis

## Quick Start

### 1. Install Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the backend

From the repository root:

```bash
python3 backend/main.py
```

Backend URLs:

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

### 3. Start the frontend

```bash
npm install
npm run frontend
```

Frontend URL:

- `http://127.0.0.1:5173`

To run backend and frontend together:

```bash
npm run dev
```

## Ollama Setup

Ollama is optional. If it is unavailable, the backend falls back to deterministic analysis.

### 1. Start Ollama

```bash
ollama serve
```

### 2. Pull the default model

```bash
ollama pull llama3.2:3b
```

### 3. Check backend model status

```bash
curl http://127.0.0.1:8000/ollama-status
```

You can also override defaults with environment variables:

- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`

## API Endpoints

### System

- `GET /health` - health and version status
- `GET /ollama-status` - Ollama connectivity, endpoint, and model

### Ticket Analysis

- `POST /analyze-ticket` - analyze a ticket from `title` and `description`
- `GET /sample-tickets` - return built-in sample incidents

### Chat

- `POST /chat` - chat-based triage and structured response generation
- `GET /conversation/{conversation_id}` - fetch in-memory conversation history
- `DELETE /conversation/{conversation_id}` - clear one conversation

### Logs

- `GET /logs` - list recent analysis logs
- `GET /logs/{ticket_id}` - fetch one logged analysis result
- `DELETE /logs` - clear stored log entries

## Example Requests

### Analyze a ticket

```bash
curl -X POST http://127.0.0.1:8000/analyze-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production database timeout",
    "description": "Users cannot log in and the app is timing out while connecting to PostgreSQL."
  }'
```

### Chat with the assistant

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "VPN users cannot access the internal portal and around 50 employees are affected."
  }'
```

## Frontend Behavior

The frontend:

- checks backend health on page load
- sends messages to `POST /chat`
- stores `conversation_id` client-side for chat continuity
- renders a compact analysis card for ticket-style responses
- opens a modal with expanded triage details

## Running the Test Script

Start the backend first, then run:

```bash
python3 tests/test_api.py
```

The script validates:

- health endpoint
- sample ticket endpoint
- ticket analysis endpoint
- log retrieval

## Data and Persistence

- analysis logs are stored in `backend/data/logs.json`
- chat conversations are stored in memory only
- restarting the backend clears conversation history

## Current Caveats

- `.env.example` is outdated and still references an older OpenAI-based setup
- `requirements.txt` includes packages that are not essential for the current Ollama-first local flow
- conversation history is not persisted beyond process memory

## Suggested Next Improvements

- update `.env.example` to reflect the Ollama configuration
- trim unused Python dependencies
- add automated coverage for `/chat` and conversation endpoints
- persist conversations beyond runtime memory
- make the Ollama model configurable from the UI
