"""
Operations Agent - FastAPI Backend
IT Operations Ticket Triage System - Chatbot Edition with Ollama (llama3)
"""
import os
import sys
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError, BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from backend.schemas import (
    TicketRequest,
    TicketResponse,
    SampleTicket,
    HealthResponse
)
from backend.services.ollama_client import (
    query_ollama,
    check_ollama_health,
    get_ollama_runtime_status,
    get_active_model,
)
from backend.services.agent_skills import (
    execute_skills
)
from backend.services.analyzer import conversational_analyzer, build_fallback_conversation
from backend.services.logger import logger as analysis_logger
from backend.services.sample_data import SAMPLE_TICKETS


# Chatbot-specific schemas
class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for history")
    use_llm: bool = Field(True, description="Whether to use LLM for analysis (default: True)")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: str
    message: ChatMessage
    analysis: Optional[TicketResponse] = None
    structured: Optional[dict] = None  # New structured response format


# Create FastAPI app
app = FastAPI(
    title="Operations Agent API",
    description="IT Operations Ticket Triage System with Ollama (llama3)",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation store (for demo purposes)
conversations = {}

# System prompt for LLaMA
SYSTEM_PROMPT = """You are an IT Operations Triage Assistant. Your role is to analyze support tickets and classify them accurately.

## Classification Rules

### Issue Types
- server: system down, VM unavailable, CPU issues, memory, disk full, host unreachable
- network: connectivity issues, DNS, latency, VPN, firewall, packet loss
- database: DB timeout, connection refused, query failures, replication lag
- application: app crash, HTTP 500 errors, service unavailable, code errors
- access/request: password reset, access needed, permission denied, role request
- security: security breach, suspicious activity, unauthorized access
- unknown: unclear or insufficient information

### Priority Levels
- critical: outage, production down, all users affected, core service down
- high: major functionality affected, many users impacted
- medium: user blocked but workaround may exist
- low: minor issue, informational request

### Output Format
Respond with ONLY valid JSON in this exact structure:

{
  "issue_type": "...",
  "priority": "...",
  "assigned_team": "...",
  "impacted_area": "...",
  "analysis": "...",
  "solution_steps": ["step1", "step2"],
  "confidence": "high|medium|low"
}

Important: Be concise, accurate, and do NOT hallucinate. If unclear, use "unknown" issue_type and route to Manual Review."""


def _is_non_empty_text(value) -> bool:
    """Return True when value is a non-empty string."""
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_steps(value) -> bool:
    """Return True when value is a list with at least one non-empty step."""
    if not isinstance(value, list):
        return False
    return any(_is_non_empty_text(step) for step in value)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # Check Ollama status
    ollama_status = "connected" if check_ollama_health() else "disconnected"

    return HealthResponse(
        status="healthy" if check_ollama_health() else "degraded",
        version="2.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/ollama-status")
async def get_ollama_status():
    """Check Ollama service status."""
    return get_ollama_runtime_status()


@app.post("/analyze-ticket", response_model=TicketResponse)
async def analyze_ticket(request: TicketRequest):
    """
    Analyze a support ticket and return classification results.
    Uses the skill-based agent system.
    """
    try:
        # Validate input
        if not request.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        if not request.description.strip():
            raise HTTPException(status_code=400, detail="Description cannot be empty")

        # Combine title and description for analysis
        full_description = f"Title: {request.title}\nDescription: {request.description}"

        # Execute skills to get analysis
        result = execute_skills(full_description)

        # Also try LLM if available
        llm_result = None
        if check_ollama_health():
            try:
                prompt = f"{SYSTEM_PROMPT}\n\nTitle: {request.title}\nDescription: {request.description}\n\nRespond with ONLY valid JSON."
                llm_response = query_ollama(prompt)

                # Try to parse LLM response
                import json
                import re
                json_match = re.search(r'\{[^{}]*\}', llm_response, re.DOTALL)
                if json_match:
                    llm_result = json.loads(json_match.group())
                    # Use LLM results if available, but keep skills as fallback
                    if llm_result.get("issue_type") and llm_result.get("issue_type") != "unknown":
                        if _is_non_empty_text(llm_result.get("issue_type")):
                            result["issue_type"] = llm_result["issue_type"]
                        if _is_non_empty_text(llm_result.get("priority")):
                            result["priority"] = llm_result["priority"]
                        if _is_non_empty_text(llm_result.get("assigned_team")):
                            result["assigned_team"] = llm_result["assigned_team"]
                        if _is_non_empty_text(llm_result.get("impacted_area")):
                            result["impacted_area"] = llm_result["impacted_area"]
                        if _is_non_empty_steps(llm_result.get("solution_steps")):
                            result["solution_steps"] = [step for step in llm_result["solution_steps"] if _is_non_empty_text(step)]
                        if _is_non_empty_text(llm_result.get("analysis")):
                            result["analysis"] = llm_result["analysis"]
                        confidence_val = llm_result.get("confidence", "medium") if _is_non_empty_text(llm_result.get("confidence")) else "medium"
                        result["confidence"] = confidence_val
                        result["confidence_score"] = 0.85 if confidence_val == "high" else 0.6 if confidence_val == "medium" else 0.4
            except Exception as e:
                logger.warning(f"LLM analysis failed, using skill-based result: {e}")

        # Build TicketResponse
        response = TicketResponse(
            ticket_id=f"ticket-{uuid.uuid4().hex[:8]}",
            issue_type=result["issue_type"],
            priority=result["priority"],
            impacted_area=result["impacted_area"],
            recommended_team=result["assigned_team"],
            troubleshooting_steps=result["solution_steps"],
            confidence_score=result["confidence_score"],
            reasoning_summary=result["analysis"],
            timestamp=result["timestamp"]
        )

        # Log the analysis
        analysis_logger.log_analysis(
            title=request.title,
            description=request.description,
            result=response
        )

        return response

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/sample-tickets", response_model=list[SampleTicket])
async def get_sample_tickets():
    """
    Get sample tickets for testing.
    """
    return SAMPLE_TICKETS


@app.get("/logs")
async def get_logs(limit: int = 100):
    """
    Get recent analysis logs.
    """
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")

    logs = analysis_logger.get_logs(limit)
    return {
        "count": len(logs),
        "logs": logs
    }


@app.get("/logs/{ticket_id}")
async def get_log_by_id(ticket_id: str):
    """
    Get a specific log entry by ticket ID.
    """
    log = analysis_logger.get_log_by_id(ticket_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Log not found for ticket ID: {ticket_id}")
    return log


@app.delete("/logs")
async def clear_logs():
    """
    Clear all analysis logs. Use with caution.
    """
    analysis_logger.clear_logs()
    return {"message": "All logs cleared successfully"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational chat endpoint.
    LLM is primary response engine with skill-based fallback if LLM is empty or low-confidence.
    """
    conversation_id = request.conversation_id or f"conv-{uuid.uuid4().hex[:8]}"

    if conversation_id not in conversations:
        conversations[conversation_id] = []

    user_message = ChatMessage(role="user", content=request.message)
    conversations[conversation_id].append(user_message.model_dump())

    # Keep a larger rolling window for multi-turn context.
    if len(conversations[conversation_id]) > 40:
        conversations[conversation_id] = conversations[conversation_id][-40:]

    try:
        llm_payload = {
            "reply": "",
            "confidence": "low",
            "source": "llm_disabled",
            "raw": "",
        }

        if request.use_llm and check_ollama_health():
            llm_payload = conversational_analyzer.generate_chat_reply(
                user_message=request.message,
                conversation_history=conversations[conversation_id],
            )

        response_text = llm_payload.get("reply", "").strip()
        fallback_used = False
        fallback_tags = {}

        if (not _is_non_empty_text(response_text)) or llm_payload.get("confidence") == "low":
            skill_result = execute_skills(request.message)
            fallback_text = build_fallback_conversation(skill_result, request.message)
            response_text = response_text if _is_non_empty_text(response_text) else fallback_text
            fallback_used = True
            fallback_tags = {
                "issue_type": skill_result.get("issue_type"),
                "priority": skill_result.get("priority"),
                "assigned_team": skill_result.get("assigned_team"),
            }

        assistant_message = ChatMessage(role="assistant", content=response_text)
        conversations[conversation_id].append(assistant_message.model_dump())

        metadata = {
            "source": llm_payload.get("source", "unknown"),
            "confidence": llm_payload.get("confidence", "unknown"),
            "fallback_used": fallback_used,
            "tags": fallback_tags,
        }

        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_message,
            analysis=None,
            structured=metadata
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        error_message = ChatMessage(
            role="assistant",
            content=(
                "I could not complete the triage in the standard format this time. "
                "Please share a bit more detail (system, exact error, and impact), and I will retry."
            )
        )
        conversations[conversation_id].append(error_message.model_dump())

        return ChatResponse(
            conversation_id=conversation_id,
            message=error_message,
            analysis=None,
            structured={"source": "runtime_error", "fallback_used": False}
        )


@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history by ID."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }


@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")


if __name__ == "__main__":
    import uvicorn
    from utils_network import get_local_ip


    # Ollama mode
    print("\n" + "="*60)
    active_model = get_active_model()
    print(f"Operations Agent v2.0 - Running with Ollama ({active_model})")
    print("="*60 + "\n")

    # Check Ollama status
    ollama_status = get_ollama_runtime_status()
    if ollama_status["status"] == "connected":
        if ollama_status["model_available"]:
            print(f"[OK] Ollama connected - model ready: {active_model}")
        else:
            print(f"[WARN] Ollama connected, but model '{active_model}' is not installed")
            if ollama_status["available_models"]:
                print(f"  Available: {', '.join(ollama_status['available_models'])}")
    else:
        print("[WARN] Ollama not detected - using skill-based fallback")
        print("  Make sure Ollama is running: ollama serve")

    local_url = "http://127.0.0.1:8000"
    network_ip = get_local_ip()
    network_url = f"http://{network_ip}:8000" if network_ip != "Unavailable" else "Unavailable"

    print("\nBackend running at:")
    print(f"  Local:   {local_url}")
    print(f"  Network: {network_url}\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)