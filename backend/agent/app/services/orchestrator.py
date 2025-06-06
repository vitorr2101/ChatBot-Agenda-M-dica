from google.genai import types
from typing import Optional, List, Any
import logging

from .llm_client_interface import LLMClientInterface

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """
    Orchestrates interactions between LLM and MCP clients for chat sessions.
    """
    
    def __init__(self, llm_client: LLMClientInterface, tools: Optional[List[types.Tool]] = None):
        """
        Initialize the orchestrator with injected dependencies.
        
        Args:
            llm_client: The LLM client implementation.
            tools: Optional list of tools to use in chat sessions.
        """
        self.llm_client = llm_client
        self.tools = tools
        
    
    async def create_chat(
        self,
        system_instruction: Optional[str] = None,
        history: Optional[List[types.ContentOrDict]] = None
    ) -> str:
        """
        Create a new chat session.
        
        Args:
            system_instruction: Optional custom system instruction.
            history: Optional conversation history.
            
        Returns:
            genai.Chat: New chat instance configured with system instruction.
        """

        logger.info("Creating new chat session...")

        return self.llm_client.create_chat(
            history=history,
            system_instruction=system_instruction
        )
    
    async def process_message(
        self,
        chat_session: Any,
        message: str,
        temperature: Optional[float] = 0.1,
        max_output_tokens: Optional[int] = None
    ) -> str:
        """
        Process a message and handle any tool calls.
        
        Args:
            chat_session: The active chat session to use.
            message: User message to process.
            temperature: Response creativity (0.0 to 1.0).
            max_output_tokens: Maximum tokens in response.
            
        Returns:
            str: The LLM's response.
        """
        
        try:
            response = await self.llm_client.send_message(
                chat_session=chat_session,
                message=message,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                tools=self.tools
            )
            
            logger.info(f"LLM Response: {response}")
            
            
        except Exception as e:
            logger.error(f"Error in process_message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"