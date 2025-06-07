from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str = Field(..., description="AI response")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Response timestamp")
