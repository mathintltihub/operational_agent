# Operations Agent

IT Operations Ticket Triage System (local-first, Ollama-powered).

## Overview

Operations Agent is a local chatbot for IT operations triage. It analyzes incidents and access requests, then returns:

- issue type
- priority
- impacted area
- recommended team
- safe troubleshooting steps
- confidence score

The app combines deterministic skill-based triage with local Ollama inference for refinement.

## Current Features

- Chat-style incident triage UI
- FastAPI backend with conversation support
- Skill-based fallback when LLM output is incomplete
- Local Ollama model detection and runtime status reporting
- OS-based automatic model selection
- Local JSON logging of analyzed tickets
- Sample tickets and API test script

## Project Structure

```text
operations_agent/
|- frontend/
|  |- index.html
|  |- style.css
|  \- app.js
|- backend/
|  |- main.py
|  |- schemas.py
|  |- data/
|  |  \- logs.json
|  |- prompts/
|  |  \- operations_agent_prompt.txt
|  \- services/
|     |- agent_skills.py
|     |- analyzer.py
|     |- identity_skill.py
|     |- logger.py
|     |- ollama_client.py
|     \- sample_data.py
|- tests/
|  \- test_api.py
|- package.json
|- requirements.txt
\- README.md
```

## Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend live server + concurrent dev run)
- Ollama installed and running locally

## Setup

### 1) Create and activate virtual environment

```bash
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### 2) Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3) Install frontend dev dependencies

```bash
npm install
```

### 4) Ensure Ollama is available

```bash
ollama serve
ollama list
```

Install a model if needed:

```bash
ollama pull llama3.2:3b
```

## Run the App

### Option A: Start frontend + backend together

```bash
npm run dev
```

- Frontend: http://127.0.0.1:5173
- Backend: http://127.0.0.1:8000

### Option B: Run backend only

```bash
python backend/main.py
```

## Model Selection by OS

Default model is selected automatically:

- Windows: llama3.2:3b
- macOS: phi3
- Linux: llama3.2:3b

Optional environment variable overrides:

- OLLAMA_MODEL (global override)
- OLLAMA_MODEL_WINDOWS
- OLLAMA_MODEL_MAC
- OLLAMA_MODEL_LINUX

Frontend status badge behavior:

- Online - model when Ollama is connected and selected model is installed
- Connected - Missing model when Ollama is reachable but selected model is not installed
- Offline - model when backend cannot reach Ollama

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| /health | GET | Backend health |
| /ollama-status | GET | Ollama connectivity, active model, available models |
| /analyze-ticket | POST | One-shot ticket triage |
| /chat | POST | Conversational triage |
| /conversation/{conversation_id} | GET | Conversation history |
| /conversation/{conversation_id} | DELETE | Delete conversation |
| /sample-tickets | GET | Sample tickets |
| /logs | GET | Recent analysis logs |
| /logs/{ticket_id} | GET | Single log by ticket ID |
| /logs | DELETE | Clear logs |

## Testing

Run API validation script:

```bash
python tests/test_api.py
```

## Troubleshooting

### UI shows Offline

1. Confirm backend is running at http://127.0.0.1:8000.
2. Confirm Ollama is running and reachable at http://127.0.0.1:11434.
3. Call status endpoint:

```bash
curl http://127.0.0.1:8000/ollama-status
```

4. Refresh the browser after backend starts.

### Port already in use on 8000

Stop existing backend process, then run one backend instance only.

### Chat returns fallback text

The backend now guards against incomplete LLM fields. If needed, provide more detail in the ticket text: system, exact error, and impact scope.

## Notes

- Logs are stored in backend/data/logs.json.
- The assistant is scoped to IT operations topics.