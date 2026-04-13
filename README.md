# Operations Agent

Local-first IT operations triage assistant with a FastAPI backend, chat-style frontend, JSON logging, and optional Ollama-powered analysis.

## Overview

Operations Agent helps triage IT support issues by turning a free-form problem description into:

- an issue category
- a priority level
- a recommended team
- an impacted area summary
- troubleshooting steps
- a confidence score

The app is designed to work locally. When Ollama is running, it can enrich the classification with a local LLM. When Ollama is unavailable, the backend falls back to deterministic skill and keyword-based logic.

## Current Stack

- Backend: FastAPI
- Frontend: static HTML, CSS, and vanilla JavaScript
- LLM option: Ollama at `http://localhost:11434`
- Default Ollama model: `llama3.2:3b`
- Logging: local JSON file at `backend/data/logs.json`

## Features

- Conversational ticket intake through a chat UI
- Structured ticket analysis via REST API
- Local-first deployment with no cloud dependency required
- Ollama health detection and graceful fallback behavior
- Sample tickets for demos and testing
- Conversation memory for recent chat history
- Local analysis log retrieval and cleanup endpoints
- Identity/help responses handled without calling the LLM

## Project Structure

```text
operational_agent/
├── backend/
│   ├── data/
│   │   └── logs.json
│   ├── services/
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
├── package.json
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- Node.js and npm if you want to use the frontend dev scripts
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

- Local: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

### 3. Start the frontend

If Node dependencies are already installed:

```bash
npm run frontend
```

This serves the frontend at:

- `http://127.0.0.1:5173`

You can also run backend and frontend together:

```bash
npm run dev
```

## Ollama Setup

Ollama is optional but recommended if you want the app to augment the local rule-based analysis with an LLM.

### 1. Start Ollama

```bash
ollama serve
```

### 2. Pull the configured model

```bash
ollama pull llama3.2:3b
```

### 3. Verify status

Once the backend is running, check:

```bash
curl http://127.0.0.1:8000/ollama-status
```

If Ollama is unavailable, the app still runs and returns fallback analysis.

## API Endpoints

### System

- `GET /health` - API health status
- `GET /ollama-status` - whether Ollama is reachable and which model is configured

### Ticket Analysis

- `POST /analyze-ticket` - analyze a structured ticket with `title` and `description`
- `GET /sample-tickets` - fetch built-in sample tickets

### Chat

- `POST /chat` - conversational analysis endpoint
- `GET /conversation/{conversation_id}` - retrieve recent conversation history
- `DELETE /conversation/{conversation_id}` - delete a conversation from in-memory storage

### Logs

- `GET /logs` - fetch recent analysis logs
- `GET /logs/{ticket_id}` - fetch a specific log entry
- `DELETE /logs` - clear all stored logs

## Example Requests

### Analyze a ticket

```bash
curl -X POST http://127.0.0.1:8000/analyze-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production database timeout",
    "description": "Users cannot log in and the app is timing out when connecting to PostgreSQL."
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

The frontend is a chat interface that:

- checks backend health on load
- sends messages to `POST /chat`
- keeps a `conversation_id` client-side for continuity
- renders a compact analysis card for structured results
- opens a detailed modal for the full analysis payload

## Running the Basic API Test Script

Start the backend first, then run:

```bash
python3 tests/test_api.py
```

The script checks:

- health
- sample tickets
- ticket analysis
- logs

## Data and Persistence

- Analysis logs are stored in `backend/data/logs.json`
- Chat conversations are stored in memory only
- restarting the backend clears conversation history

## Known Caveats

- `.env.example` still contains older OpenAI-era setup text and does not reflect the current Ollama-based flow.
- `requirements.txt` includes some libraries that are not central to the current local-first path.
- `backend/main.py` references a `backend.services.agent_skills` module; make sure that module exists in your working tree if you are running the current backend entrypoint.

## Next Improvements

- Align `.env.example` with the current Ollama workflow
- Trim unused dependencies from `requirements.txt`
- Persist conversations beyond process memory
- Add automated tests for the `/chat` and conversation endpoints
- Expose configurable model selection instead of hardcoding `llama3.2:3b`
