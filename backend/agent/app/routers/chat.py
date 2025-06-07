from fastapi import APIRouter, Depends, HTTPException, status, Request
import logging
import uuid
import json
from datetime import datetime, timezone

from app.dependencies import get_orchestrator
from app.services.orchestrator import ChatOrchestrator
from app.services.chat_store import chat_store
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.chat_formatter import format_chat_history

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse, summary="Send chat message")
async def send_message(
    request: Request,
    chat_request: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
):
    """Process a chat message for medical appointment scheduling."""
    
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
        logger.info(f"Created new session: {session_id[:8]}")

    try:
        if not chat_request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        chat_session = chat_store.get_session(session_id)
        if not chat_session:
            chat_session = await orchestrator.create_chat()
            chat_store.set_session(session_id, chat_session)
            logger.info(f"Created new chat session for {session_id[:8]}")
        
        logger.debug(f"Processing message for session {session_id[:8]}")

        response_text = await orchestrator.process_message(
            chat_session=chat_session,
            message=chat_request.message,
        )

        logger.debug(f"Received response for session {session_id[:8]}")

        history = chat_session.get_history()
        formatted_history = format_chat_history(history)
        history_json = json.dumps(formatted_history, indent=2, ensure_ascii=False)
        logger.debug(f"Chat history for session {session_id[:8]}:\n{history_json}")

        
        if response_text is None:
            logger.error(f"Orchestrator returned None for session {session_id[:8]}")
            response_text = "I apologize, but I couldn't process your message. Please try again."

        return ChatResponse(
            response=response_text,
            timestamp=datetime.now(timezone.utc)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error for session {session_id[:8]}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )

@router.delete("/session", summary="Clear current chat session")
async def clear_session(request: Request):
    """Clear the current chat session."""
    session_id = request.session.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )
    
    chat_store.remove_session(session_id)
    logger.info(f"Cleared chat session for {session_id[:8]}")
    
    return {
        "message": "Chat session cleared successfully",
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc)
    }
