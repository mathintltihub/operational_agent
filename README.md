# Operations Agent

Operations Agent is a local-first IT operations triage assistant with a FastAPI backend and chat UI.

It is designed to stay in IT operations scope only:
- classify incidents and support issues
- detect priority
- route to the right team
- suggest troubleshooting steps
- provide natural-language triage guidance

## Current Behavior

The backend uses a hybrid approach:

- Ollama-first reasoning for chat (`/chat`)
- deterministic skill-based fallback for stability
- strict response validation and sanitization to block placeholder outputs like `...`, `step1`, or invalid labels

This means the agent can keep a natural chat style while preserving reliable structured triage data.

## Scope Restrictions

The chat agent is intentionally restricted to operations tasks.

- In-scope:
  - incidents, outages, access requests, troubleshooting, routing, triage workflows
  - assistant usage/help/status questions
- Out-of-scope:
  - general knowledge, personal advice, schoolwork, unrelated coding, and non-operations requests

Out-of-scope prompts are redirected back to operations support use cases.

## Architecture

```text
operational_agent/
├── backend/
│   ├── data/
│   │   └── logs.json
│   ├── services/
│   │   ├── agent_skills.py      # deterministic triage fallback logic
│   │   ├── analyzer.py          # local keyword analyzer
│   │   ├── identity_skill.py    # fallback identity replies when LLM unavailable
│   │   ├── logger.py            # JSON logging service
│   │   ├── ollama_client.py     # local Ollama client
│   │   └── sample_data.py       # sample tickets
│   ├── main.py                  # FastAPI app and chat orchestration
│   ├── schemas.py               # request/response models
│   └── utils_network.py
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── tests/
│   └── test_api.py
├── .env
├── package.json
├── requirements.txt
└── README.md
```

## Tech Stack

- Backend: FastAPI
- Frontend: HTML + CSS + vanilla JavaScript
- Local model runtime: Ollama
- Log storage: `backend/data/logs.json`

## Environment

Current local config in `.env`:

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=phi3:latest
```

If `OLLAMA_MODEL` is not set, code default is `llama3.2:3b`.

## Setup

### 1. Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Frontend dependencies

```bash
npm install
```

### 3. Start Ollama

```bash
ollama serve
```

Optional model check:

```bash
ollama list
```

### 4. Start backend

```bash
python3 backend/main.py
```

Backend URLs:

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### 5. Start frontend

```bash
npm run frontend
```

Frontend URL:

- `http://127.0.0.1:5173`

Or run both together:

```bash
npm run dev
```

## API Endpoints

### System

- `GET /health` - backend health status
- `GET /ollama-status` - Ollama connectivity and configured model

### Ticket Analysis

- `POST /analyze-ticket` - triage from title/description payload
- `GET /sample-tickets` - built-in sample dataset

### Chat

- `POST /chat` - operations-agent chat and triage
- `GET /conversation/{conversation_id}` - in-memory conversation retrieval
- `DELETE /conversation/{conversation_id}` - conversation cleanup

### Logs

- `GET /logs` - list recent logs
- `GET /logs/{ticket_id}` - fetch single log entry
- `DELETE /logs` - clear all logs

## Chat Pipeline

For each chat request:

1. Build a skill-based triage baseline.
2. Query Ollama with a strict JSON contract (`conversation`, `ticket`, or `out_of_scope`).
3. Validate/normalize model fields.
4. Reject weak placeholders and invalid enums.
5. Merge only safe model values into the baseline.
6. Generate a natural-language assistant message plus structured data for the UI card.

## Reliability and Guardrails

- operations-only scope guard
- out-of-scope redirect response
- fallback behavior when Ollama is unavailable
- sanitizer for weak text (`...`, `step1`, empty fields)
- typed response models with FastAPI + Pydantic

## Example Requests

### Chat triage request

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Production app is returning HTTP 500 for all users"
  }'
```

### Structured ticket request

```bash
curl -X POST http://127.0.0.1:8000/analyze-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "title": "VPN users cannot access internal portal",
    "description": "Around 50 remote users affected since morning. Connection is timing out."
  }'
```

## Testing

With backend running:

```bash
python3 tests/test_api.py
```

This verifies:

- health endpoint
- sample tickets
- ticket analysis
- logs

## Data Persistence

- analysis logs are persisted in `backend/data/logs.json`
- conversation memory is in-process only
- restarting backend clears conversation history

## Known Notes

- startup banner text in `backend/main.py` still mentions `LLaMA 3`, even when `.env` uses `phi3:latest`
- `requirements.txt` still includes older packages not essential for the current local Ollama flow

## Roadmap Ideas

- persist conversation history to disk/db
- add automatic model/profile switching by ticket type
- expose model and scope settings in UI
- improve test coverage for chat mode and guardrails
