from google.genai import types
from mcp import ClientSession
from fastapi import UploadFile
from typing import Optional, List, Any

from .llm_client_interface import LLMClientInterface
from app.configs.logging_config import get_logger

logger = get_logger(__name__)

class ChatOrchestrator:
    """
    Orchestrates interactions between LLM and MCP clients for chat sessions.
    """
    
    def __init__(self, llm_client: LLMClientInterface, tools: Optional[List[ClientSession]] = None):
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
        content: List,
        temperature: Optional[float] = 0.1,
        max_output_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Processa uma mensagem que pode conter múltiplas partes (texto, imagem).
        
        Args:
            chat_session: A sessão de chat ativa para usar.
            content: Uma lista de partes da mensagem (ex: texto, dados de imagem).
            temperature: Criatividade da resposta (0.0 a 1.0).
            max_output_tokens: Máximo de tokens na resposta.
            
        Returns:
            A resposta do LLM ou None em caso de erro.
        """
        try:
            response = await self.llm_client.send_message(
                chat_session=chat_session,
                content=content,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                tools=self.tools
            )
            
            # O log agora mostra o conteúdo da lista
            logger.info(f"User content: {content[0]} | LLM Response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Erro em process_message: {e}")
            return None
    
    async def format_file_part(self, file: UploadFile) -> types.Part:
        """
        Repassa a chamada de formatação de arquivo para o llm_client.
        
        Args:
            file: O arquivo enviado via FastAPI.
            
        Returns:
            types.Part: Objeto Part formatado para o Gemini SDK.
        """
        return await self.llm_client.format_file_part(file)