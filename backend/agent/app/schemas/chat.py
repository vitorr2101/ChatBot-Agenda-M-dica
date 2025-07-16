from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ChatRequest(BaseModel):
    """Modelo para a requisição de chat da Vercel AI SDK."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")

class ChatResponse(BaseModel):
    """Schema para a resposta do chat."""
    response: str = Field(..., description="AI response")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Response timestamp")