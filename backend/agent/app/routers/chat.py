from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    UploadFile,
    File,
    Form,
)
from datetime import datetime, timezone
from app.dependencies import get_orchestrator
from app.services.orchestrator import ChatOrchestrator
from app.services.chat_store import chat_store
from app.schemas.chat import ChatResponse
from app.utils.session_manager import get_or_create_session
from app.configs.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    tags=["Chat"],
)

@router.post("/", response_model=ChatResponse, summary="Send a message, with or without a document")
async def send_message(
    request: Request,
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
):
    """
    Processa uma mensagem de chat, orquestrando a criação de sessão,
    formatação de conteúdo e chamada ao serviço principal.
    """
    try:
        chat_session = await get_or_create_session(request, orchestrator)

        content_parts: list[object] = [message]

        if file:
            session_id = request.session.get("session_id", "unknown")
            logger.info(f"Formatting document for session {session_id[:8]}")
            file_part = await orchestrator.format_file_part(file)
            content_parts.append(file_part)

        response_text = await orchestrator.process_message(
            chat_session=chat_session,
            content=content_parts
        )
        
        if response_text is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "The service failed to produce a response.")

        return ChatResponse(
            response=response_text, 
            timestamp=datetime.now(timezone.utc)
        )

    except HTTPException:
        raise
    except Exception as e:
        session_id = request.session.get("session_id", "unknown")
        logger.error(f"An unexpected error occurred in chat session {session_id[:8]}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred."
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