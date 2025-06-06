from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from agent.app.dependencies import get_orchestrator
from agent.app.services.orchestrator import ChatOrchestrator

router = APIRouter()

class ChatRequest(BaseModel):
    """
    Request model for chat messages.
    
    Attributes:
        message: The user's message to process.
    """
    message: str = Field(..., description="The message to send to the chat service.")

class ChatResponse(BaseModel):
    """
    Response model for chat messages.
    
    Attributes:
        response: The response from the chat service.
    """
    response: str = Field(..., description="The response from the chat service.")


@router.post("/chat")
async def chat(
    request: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
    response_model=ChatResponse
):
    """
    Process a chat message and return the response.
    
    Args:
        message: The user's message to process.
        orchestrator: The chat orchestrator dependency that handles LLM interactions.
        
    Returns:
        str: The response from the LLM.
    """
    try:
        chat_session = await orchestrator.create_chat()

        response = await orchestrator.process_message(
            chat_session=chat_session,
            message=request.message,
        )

        return ChatResponse(
            response=response
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))