from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# WARNING: This is a simplified in-memory store for development purposes.
# In production, consider using a persistent store like Redis or a database.
class ChatStore:
    """In-memory store for chat sessions."""
    
    def __init__(self):
        self._sessions: Dict[str, Any] = {}
        logger.warning("In production, consider using a persistent store like Redis or a database.")
    
    def set_session(self, session_id: str, chat_session: Any) -> None:
        """Store a chat session."""
        self._sessions[session_id] = chat_session
        logger.debug(f"Stored chat session for {session_id[:8]}")
    
    def get_session(self, session_id: str) -> Optional[Any]:
        """Retrieve a chat session."""
        session = self._sessions.get(session_id)
        if session:
            logger.debug(f"Retrieved chat session for {session_id[:8]}")
        return session
    
    def remove_session(self, session_id: str) -> None:
        """Remove a chat session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.debug(f"Removed chat session for {session_id[:8]}")
    
    def clear_all(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
        logger.info("Cleared all chat sessions")
    
    def get_session_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._sessions)

chat_store = ChatStore()