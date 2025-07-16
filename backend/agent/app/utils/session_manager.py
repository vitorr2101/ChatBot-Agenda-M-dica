import uuid
from fastapi import Request
from app.services.orchestrator import ChatOrchestrator
from app.services.chat_store import chat_store
from app.configs.logging_config import get_logger

logger = get_logger(__name__)


async def get_or_create_session(request: Request, orchestrator: ChatOrchestrator):
    """Obtém a sessão de chat existente ou cria uma nova."""
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
        logger.info(f"Created new session: {session_id[:8]}")

    chat_session = chat_store.get_session(session_id)
    if not chat_session:
        logger.info(f"No active session for {session_id[:8]}. Creating new one.")
        chat_session = await orchestrator.create_chat(history=[]) 
        chat_store.set_session(session_id, chat_session)
    return chat_session
