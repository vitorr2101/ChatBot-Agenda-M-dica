
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    """Representa uma única mensagem no histórico do chat."""
    role: str
    content: str
    data: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    """Modelo para a requisição de chat da Vercel AI SDK."""
    messages: List[Message]