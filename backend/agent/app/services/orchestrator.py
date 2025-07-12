from google.genai import types
from typing import Optional, List, Any
import logging

import base64
import re
from app.schemas.chat import Message 

from .llm_client_interface import LLMClientInterface
from app.prompts.ocr_prompts import MEDICAL_DOCUMENT_ANALYSIS_PROMPT

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
        last_message: Message,
        temperature: Optional[float] = 0.1,
        max_output_tokens: Optional[int] = None
    ) -> str:
        """
        Processa uma mensagem baseada em texto (pode conter uma imagem em base64 no campo 'data').
        Este método é chamado pelo endpoint principal de chat.
        
        Args:
            chat_session: A sessão de chat ativa para usar.
            last_message: O último objeto de mensagem do usuário.
            temperature: Criatividade da resposta (0.0 a 1.0).
            max_output_tokens: Máximo de tokens na resposta.
            
        Returns:
            A resposta do LLM.
        """
        try:
            message_parts = [last_message.content]

            if last_message.data and "imageUrl" in last_message.data:
                data_url = last_message.data["imageUrl"]
                logger.info("Dados de imagem encontrados em base64, processando...")
                try:
                    match = re.match(r'data:(image\/\w+);base64,(.*)', data_url)
                    if not match:
                        raise ValueError("Formato de Data URL da imagem inválido")
                    
                    mime_type, base64_data = match.groups()
                    image_bytes = base64.b64decode(base64_data)

                    image_part = {"mime_type": mime_type, "data": image_bytes}
                    message_parts.append(image_part)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar imagem em base64: {e}")
                    return "Desculpe, não consegui ler o arquivo de imagem que você enviou. Poderia tentar novamente?"

            response = await self.llm_client.send_message(
                chat_session=chat_session,
                message_parts=message_parts,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                tools=self.tools
            )
            
            logger.info(f"User message: {last_message.content} | LLM Response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Erro em process_message: {e}")
            return f"Desculpe, encontrei um erro: {str(e)}"
        
    async def process_image_upload(self, chat_session: Any, file_bytes: bytes, mime_type: str) -> str:
        """
        Processa uma imagem enviada diretamente como bytes.
        """
        from app.prompts.ocr_prompts import MEDICAL_DOCUMENT_ANALYSIS_PROMPT # Supondo que você tenha este arquivo

        if isinstance(MEDICAL_DOCUMENT_ANALYSIS_PROMPT, list):
            prompt_text = "\n".join(MEDICAL_DOCUMENT_ANALYSIS_PROMPT)
        else:
            prompt_text = MEDICAL_DOCUMENT_ANALYSIS_PROMPT

    
        message_parts = [prompt_text,types.Part.from_bytes(
            mime_type=mime_type,
            data=file_bytes
        )]


        response = await self.llm_client.send_message(
            chat_session=chat_session,
            message_parts=message_parts
        )
        return response