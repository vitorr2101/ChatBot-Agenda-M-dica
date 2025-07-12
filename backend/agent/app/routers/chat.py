from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    UploadFile,
    File
)
from fastapi.responses import PlainTextResponse
import logging
import uuid
import json
from datetime import datetime, timezone

from app.dependencies import get_orchestrator
from app.services.orchestrator import ChatOrchestrator
from app.services.chat_store import chat_store
from app.schemas.chat import ChatRequest  # O schema que espera {"messages": [...]}
from app.utils.chat_formatter import format_chat_history

logger = logging.getLogger(__name__)

# O prefixo foi removido aqui para corresponder à sua estrutura de projeto
# Ele geralmente é adicionado quando o router é incluído no app principal em main.py
router = APIRouter(
    tags=["Chat"],
)


@router.post("/", response_class=PlainTextResponse, summary="Send a text message")
async def send_message(
    request: Request,
    chat_request: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
):
    """
    Process a text-based chat message.
    Expects a JSON body with a list of messages.
    """
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
        logger.info(f"Created new session: {session_id[:8]}")

    try:
        if not chat_request.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A lista de mensagens não pode estar vazia."
            )
        
        last_message = chat_request.messages[-1]
        
        chat_session = chat_store.get_session(session_id)
        if not chat_session:
            logger.info(f"No active session found for {session_id[:8]}. Creating new one.")
            # Passa o histórico (todas as mensagens menos a última) para criar o chat
            history_for_new_chat = [msg.model_dump(exclude_none=True) for msg in chat_request.messages[:-1]]
            chat_session = await orchestrator.create_chat(history=history_for_new_chat)
            chat_store.set_session(session_id, chat_session)
        
        logger.debug(f"Processing message for session {session_id[:8]}")

        response_text = await orchestrator.process_message(
            chat_session=chat_session,
            last_message=last_message,
        )

        logger.debug(f"Received response for session {session_id[:8]}")
        
        if response_text is None:
            logger.error(f"Orchestrator returned None for session {session_id[:8]}")
            response_text = "Desculpe, não consegui processar sua mensagem. Por favor, tente novamente."

        return PlainTextResponse(content=response_text)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error for session {session_id[:8]}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.post("/upload-document", summary="Upload and process a medical document")
async def handle_document_upload(
    request: Request, # Adicionado para poder acessar a sessão
    file: UploadFile = File(...),
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
):
    """
    Receives an image file, sends it for analysis, and returns the response.
    Expects multipart/form-data.
    """
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
        logger.info(f"Created new session for upload: {session_id[:8]}")
        
    try:
        chat_session = chat_store.get_session(session_id)
        if not chat_session:
             chat_session = await orchestrator.create_chat()
             chat_store.set_session(session_id, chat_session)

        file_bytes = await file.read()
        
        response_text = await orchestrator.process_image_upload(
            chat_session=chat_session,
            file_bytes=file_bytes,
            mime_type=file.content_type
        )

        return {"response": response_text}

    except Exception as e:
        logger.error(f"Erro no upload de documento para sessão {session_id[:8]}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro interno ao processar o documento."
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