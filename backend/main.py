"""
Operations Agent - FastAPI Backend
IT Operations Ticket Triage System - Chatbot Edition
"""
import os
import sys
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

from backend.schemas import (
    TicketRequest,
    TicketResponse,
    SampleTicket,
    HealthResponse
)
from backend.services.analyzer import analyzer
from backend.services.logger import logger
from backend.services.sample_data import SAMPLE_TICKETS
from backend.services.identity_skill import is_identity_question, get_identity_response


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


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: str
    message: ChatMessage
    analysis: Optional[TicketResponse] = None


# Create FastAPI app
app = FastAPI(
    title="Operations Agent API",
    description="IT Operations Ticket Triage System",
    version="1.0.0"
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


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/analyze-ticket", response_model=TicketResponse)
async def analyze_ticket(request: TicketRequest):
    """
    Analyze a support ticket and return classification results.
    """
    try:
        # Validate input
        if not request.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        if not request.description.strip():
            raise HTTPException(status_code=400, detail="Description cannot be empty")

        # Analyze the ticket
        result = analyzer.analyze(
            title=request.title.strip(),
            description=request.description.strip()
        )

        # Log the analysis
        logger.log_analysis(
            title=request.title,
            description=request.description,
            result=TicketResponse(**result)
        )

        return TicketResponse(**result)

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

    logs = logger.get_logs(limit)
    return {
        "count": len(logs),
        "logs": logs
    }


@app.get("/logs/{ticket_id}")
async def get_log_by_id(ticket_id: str):
    """
    Get a specific log entry by ticket ID.
    """
    log = logger.get_log_by_id(ticket_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Log not found for ticket ID: {ticket_id}")
    return log


@app.delete("/logs")
async def clear_logs():
    """
    Clear all analysis logs. Use with caution.
    """
    logger.clear_logs()
    return {"message": "All logs cleared successfully"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for conversational ticket analysis.
    Maintains conversation history and provides chatbot-style responses.
    """
    import uuid

    # Generate or retrieve conversation ID
    conversation_id = request.conversation_id or f"conv-{uuid.uuid4().hex[:8]}"

    # Get or create conversation history
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    # Add user message to history
    user_message = ChatMessage(role="user", content=request.message)
    conversations[conversation_id].append(user_message.model_dump())

    # --- Identity skill: handle greetings / who-are-you locally ---
    if is_identity_question(request.message):
        assistant_message = ChatMessage(role="assistant", content=get_identity_response())
        conversations[conversation_id].append(assistant_message.model_dump())
        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_message,
            analysis=None
        )

    # --- Ticket analysis skill: only for real IT issues ---
    try:
        result = analyzer.analyze(
            title=request.message[:100],
            description=request.message
        )

        analysis = TicketResponse(**result)
        response_text = generate_chatbot_response(analysis)

        assistant_message = ChatMessage(role="assistant", content=response_text)
        conversations[conversation_id].append(assistant_message.model_dump())

        logger.log_analysis(
            title=request.message[:50],
            description=request.message,
            result=analysis
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_message,
            analysis=analysis
        )

    except Exception as e:
        error_message = ChatMessage(
            role="assistant",
            content=f"I encountered an error analyzing your ticket: {str(e)}. Please try again."
        )
        conversations[conversation_id].append(error_message.model_dump())

        return ChatResponse(
            conversation_id=conversation_id,
            message=error_message,
            analysis=None
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


    # Always use hardcoded OpenAI API key for realtime agent
    print("\n" + "="*60)
    print("Realtime agent mode: Using hardcoded OpenAI API key.")
    print("="*60 + "\n")

    local_url = "http://127.0.0.1:8000"
    network_ip = get_local_ip()
    network_url = f"http://{network_ip}:8000" if network_ip != "Unavailable" else "Unavailable"

    print("Backend running at:")
    print(f"  Local:   {local_url}")
    print(f"  Network: {network_url}\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)