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
from backend.services.ollama_client import query_ollama, check_ollama_health, OLLAMA_MODEL
from backend.services.agent_skills import (
    classify_issue,
    detect_priority,
    route_to_team,
    suggest_solution,
    calculate_confidence,
    get_impacted_area,
    confidence_to_level,
    execute_skills
)
from backend.services.logger import logger as analysis_logger
from backend.services.sample_data import SAMPLE_TICKETS
from backend.services.identity_skill import is_identity_question, get_skill_response


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
    is_healthy = check_ollama_health()
    return {
        "status": "connected" if is_healthy else "disconnected",
        "model": OLLAMA_MODEL,
        "endpoint": "http://localhost:11434"
    }


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
                        result["issue_type"] = llm_result.get("issue_type", result["issue_type"])
                        result["priority"] = llm_result.get("priority", result["priority"])
                        result["assigned_team"] = llm_result.get("assigned_team", result["assigned_team"])
                        result["impacted_area"] = llm_result.get("impacted_area", result["impacted_area"])
                        if llm_result.get("solution_steps"):
                            result["solution_steps"] = llm_result.get("solution_steps")
                        if llm_result.get("analysis"):
                            result["analysis"] = llm_result.get("analysis")
                        confidence_val = llm_result.get("confidence", "medium")
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
    Chat endpoint for conversational ticket analysis.
    Uses Ollama (llama3) for intelligent analysis with skill-based fallback.
    Maintains conversation history and provides chatbot-style responses.
    """
    import re
    import json

    # Generate or retrieve conversation ID
    conversation_id = request.conversation_id or f"conv-{uuid.uuid4().hex[:8]}"

    # Get or create conversation history (keep last 3 messages for memory)
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    # Add user message to history
    user_message = ChatMessage(role="user", content=request.message)
    conversations[conversation_id].append(user_message.model_dump())

    # Keep only last 3 messages in memory
    if len(conversations[conversation_id]) > 6:  # 3 user + 3 assistant
        conversations[conversation_id] = conversations[conversation_id][-6:]

    # --- Identity skill: handle greetings / who-are-you locally ---
    if is_identity_question(request.message):
        assistant_message = ChatMessage(role="assistant", content=get_skill_response(request.message))
        conversations[conversation_id].append(assistant_message.model_dump())
        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_message,
            analysis=None
        )

    # --- Ticket analysis skill: for IT issues ---
    try:
        # First, use skill-based analysis as fallback
        skill_result = execute_skills(request.message)
        confidence = skill_result["confidence"]
        confidence_score = skill_result["confidence_score"]

        # Try LLM if available and requested
        llm_result = None
        if request.use_llm and check_ollama_health():
            try:
                # Build context from recent conversation
                context = ""
                if len(conversations[conversation_id]) > 1:
                    context = "Recent conversation:\n"
                    for msg in conversations[conversation_id][-4:]:
                        context += f"{msg['role']}: {msg['content'][:200]}\n"

                prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser issue: {request.message}\n\nRespond with ONLY valid JSON."

                llm_response = query_ollama(prompt, timeout=60)

                # Parse LLM response
                json_match = re.search(r'\{[^{}]*\}', llm_response, re.DOTALL)
                if json_match:
                    llm_result = json.loads(json_match.group())
                    logger.info(f"LLM parsed result: {llm_result}")
            except Exception as e:
                logger.warning(f"LLM analysis failed: {e}. Using skill-based result.")

        # Merge results - use LLM if available, otherwise use skills
        if llm_result:
            if llm_result.get("issue_type") and llm_result.get("issue_type") != "unknown":
                skill_result["issue_type"] = llm_result.get("issue_type", skill_result["issue_type"])
                skill_result["priority"] = llm_result.get("priority", skill_result["priority"])
                skill_result["assigned_team"] = llm_result.get("assigned_team", skill_result["assigned_team"])
                skill_result["impacted_area"] = llm_result.get("impacted_area", skill_result["impacted_area"])
                if llm_result.get("solution_steps"):
                    skill_result["solution_steps"] = llm_result.get("solution_steps")
                if llm_result.get("analysis"):
                    skill_result["analysis"] = llm_result.get("analysis")

                # Convert confidence string to score
                conf_level = llm_result.get("confidence", "medium")
                skill_result["confidence"] = conf_level
                skill_result["confidence_score"] = 0.85 if conf_level == "high" else 0.6 if conf_level == "medium" else 0.4

        # Build TicketResponse
        analysis = TicketResponse(
            ticket_id=f"ticket-{uuid.uuid4().hex[:8]}",
            issue_type=skill_result["issue_type"],
            priority=skill_result["priority"],
            impacted_area=skill_result["impacted_area"],
            recommended_team=skill_result["assigned_team"],
            troubleshooting_steps=skill_result["solution_steps"],
            confidence_score=skill_result["confidence_score"],
            reasoning_summary=skill_result["analysis"],
            timestamp=skill_result["timestamp"]
        )

        # Generate user-friendly response
        response_text = generate_chatbot_response(analysis)

        assistant_message = ChatMessage(role="assistant", content=response_text)
        conversations[conversation_id].append(assistant_message.model_dump())

        # Log the analysis
        analysis_logger.log_analysis(
            title=request.message[:50],
            description=request.message,
            result=analysis
        )

        # Build structured response
        structured = {
            "issue_type": skill_result["issue_type"],
            "priority": skill_result["priority"],
            "assigned_team": skill_result["assigned_team"],
            "analysis": skill_result["analysis"],
            "solution_steps": skill_result["solution_steps"],
            "confidence": skill_result["confidence"]
        }

        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_message,
            analysis=analysis,
            structured=structured
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        error_message = ChatMessage(
            role="assistant",
            content=f"I encountered an error analyzing your ticket: {str(e)}. Please try again."
        )
        conversations[conversation_id].append(error_message.model_dump())

        return ChatResponse(
            conversation_id=conversation_id,
            message=error_message,
            analysis=None,
            structured=None
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


def generate_chatbot_response(analysis: TicketResponse) -> str:
    """Generate a natural, chatbot-style response from analysis results."""

    priority_emoji = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }

    issue_emoji = {
        "server": "🖥️",
        "network": "🌐",
        "database": "🗄️",
        "application": "📱",
        "access/request": "🔐",
        "unknown": "❓"
    }

    priority = analysis.priority
    issue_type = analysis.issue_type

    response = f"""🔍 **Analysis Complete**

{issue_emoji.get(issue_type, '📋')} *Issue Type:* {issue_type.title()}
{priority_emoji.get(priority, '⚪')} *Priority:* {priority.upper()}
👥 *Recommended Team:* {analysis.recommended_team}
📍 *Impacted Area:* {analysis.impacted_area}
📊 *Confidence:* {analysis.confidence_score * 100:.0f}%

**Troubleshooting Steps:**
"""

    for i, step in enumerate(analysis.troubleshooting_steps, 1):
        response += f"\n{i}. {step}"

    response += f"\n\n💡 *Reasoning:* {analysis.reasoning_summary}"

    return response


if __name__ == "__main__":
    import uvicorn
    from utils_network import get_local_ip


    # Ollama mode
    print("\n" + "="*60)
    print("Operations Agent v2.0 - Running with Ollama (LLaMA 3)")
    print("="*60 + "\n")

    # Check Ollama status
    if check_ollama_health():
        print("✓ Ollama connected - LLaMA 3 model available")
    else:
        print("⚠ Ollama not detected - using skill-based fallback")
        print("  Make sure Ollama is running: ollama serve")

    local_url = "http://127.0.0.1:8000"
    network_ip = get_local_ip()
    network_url = f"http://{network_ip}:8000" if network_ip != "Unavailable" else "Unavailable"

    print("\nBackend running at:")
    print(f"  Local:   {local_url}")
    print(f"  Network: {network_url}\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)