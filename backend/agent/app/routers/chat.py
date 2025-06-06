from fastapi import APIRouter, Depends, HTTPException, status
import logging
import uuid
from datetime import datetime, timezone

from app.dependencies import get_orchestrator
from app.services.orchestrator import ChatOrchestrator
from app.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse, summary="Send chat message")
async def send_message(
    request: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
):
    """Process a chat message for medical appointment scheduling."""
    
    session_id = request.session_id or str(uuid.uuid4())
    
    logger.info(f"Processing message for session {session_id[:8]}")
    
    try:
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        chat_session = await orchestrator.create_chat()
        response_text = await orchestrator.process_message(
            chat_session=chat_session,
            message=request.message,
        )

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error for session {session_id[:8]}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )
