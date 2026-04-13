"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TicketRequest(BaseModel):
    """Request schema for ticket analysis."""
    title: str = Field(..., min_length=1, max_length=500, description="Ticket title")
    description: str = Field(..., min_length=1, max_length=5000, description="Ticket description")


class TicketResponse(BaseModel):
    """Response schema for ticket analysis."""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    issue_type: str = Field(..., description="Classified issue type")
    priority: str = Field(..., description="Detected priority level")
    impacted_area: str = Field(..., description="Area or component impacted")
    recommended_team: str = Field(..., description="Team to assign the ticket")
    troubleshooting_steps: List[str] = Field(..., description="Suggested troubleshooting steps")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning_summary: str = Field(..., description="Brief explanation of classification")
    timestamp: str = Field(..., description="Analysis timestamp")


class SampleTicket(BaseModel):
    """Sample ticket for testing."""
    id: str
    title: str
    description: str
    expected_issue_type: Optional[str] = None
    expected_priority: Optional[str] = None


class LogEntry(BaseModel):
    """Log entry schema."""
    ticket_id: str
    title: str
    description: str
    analysis_result: TicketResponse
    timestamp: str
    metadata: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    mode: Optional[str] = None
    model: Optional[str] = None
