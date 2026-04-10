"""
Operations Agent - FastAPI Backend
IT Operations Ticket Triage System
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

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


if __name__ == "__main__":
    import uvicorn

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n" + "="*60)
        print("WARNING: No OPENAI_API_KEY found in environment.")
        print("Running in MOCK mode (keyword-based analysis).")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("API Key detected. Using LangChain with OpenAI.")
        print("="*60 + "\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)