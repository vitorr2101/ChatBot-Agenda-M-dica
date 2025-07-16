from app.configs.settings import SYSTEM_INSTRUCTION
from google import genai
from google.genai import types
import google.api_core.exceptions as core_exceptions
from fastapi import UploadFile, HTTPException, status
from typing import Optional, Any, List
import asyncio
import random

from .llm_client_interface import LLMClientInterface
from app.configs.logging_config import get_logger

logger = get_logger(__name__)

class GeminiLLMClient(LLMClientInterface):
    """
    Manages Gemini LLM client and chat sessions.
    """
    
    def __init__(self, api_key: str, model_name: str, max_retries: int = 3):
        """
        Initialize the Gemini client.

        Args:
            api_key: The API key for the Gemini service.
            model_name: The name of the Gemini model to use.
            max_retries: Maximum number of retry attempts for service unavailable errors.
        """
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        self.max_retries = max_retries
    
    def create_chat(
        self, 
        system_instruction: Optional[str] = None,
        history: Optional[list[types.ContentOrDict]] = None
    ) -> Any:
        """
        Create a new chat session.

        Args:
            system_instruction: Optional system instruction for the chat session.
            history: Optional list of previous messages to initialize the chat history.
        
        Returns:
            genai.Chat: New chat instance configured with system instruction.
        """
        instruction_to_use = system_instruction if system_instruction is not None else SYSTEM_INSTRUCTION
        
        return self.client.aio.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=instruction_to_use
            ),
            history=history
        )
    
    async def format_file_part(self, file: UploadFile) -> types.Part:
        """
        Converte um UploadFile em um objeto Part do Gemini SDK.
        Levanta uma exceção se o tipo MIME não for encontrado.
        
        Args:
            file: O arquivo enviado via FastAPI.
            
        Returns:
            types.Part: Objeto Part formatado para o Gemini SDK.
            
        Raises:
            HTTPException: Se o tipo MIME não for fornecido.
        """
        if not file.content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File MIME type is required but was not provided."
            )

        file_bytes = await file.read()
        return types.Part.from_bytes(mime_type=file.content_type, data=file_bytes)
    
    async def _retry_with_exponential_backoff(self, func, *args, **kwargs):
        """
        Retry a function with exponential backoff for service unavailable errors.
        
        Args:
            func: The async function to retry.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Returns:
            The result of the function call.
            
        Raises:
            The last exception if all retries are exhausted.
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except core_exceptions.ServiceUnavailable as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) exhausted for service unavailable error")
                    break
                    
                base_delay = 2 ** attempt
                jitter = random.uniform(0.1, 0.3) * base_delay
                delay = base_delay + jitter
                
                logger.warning(f"Service unavailable (attempt {attempt + 1}/{self.max_retries + 1}). "
                             f"Retrying in {delay:.2f} seconds...")
                
                await asyncio.sleep(delay)
            except Exception as e:
                raise e
                
        if last_exception is not None:
            raise last_exception
        else:
            raise Exception("Unknown error occurred during retries.")
    
    async def send_message(
        self, 
        chat_session: Any, 
        content: List,
        temperature: Optional[float] = 0.1,
        max_output_tokens: Optional[int] = None,
        tools: Optional[list] = None
    ) -> str:
        """
        Send a message using the provided chat session.
        The message can be composed of multiple parts (text, image).

        Args:
            chat_session: The active chat session.
            content: A list containing message content (e.g., [text, image_data]).
            temperature: Optional response creativity (0.0 to 1.0).
            max_output_tokens: Optional maximum number of tokens in the response.
            tools: Optional list of tools for function calling.

        Returns:
            str: LLM response text.
        """
        config_params = {}
        if temperature is not None:
            config_params['temperature'] = temperature
        if max_output_tokens is not None:
            config_params['max_output_tokens'] = max_output_tokens
        if tools is not None:
            config_params['tools'] = tools
            config_params['automatic_function_calling'] = types.AutomaticFunctionCallingConfig(
                disable = False,
                ignore_call_history = False
            )

        generation_config = types.GenerateContentConfig(**config_params) if config_params else None

        async def _send_request():
            response = await chat_session.send_message(
                content,
                config=generation_config
            )
            return response.text
        
        try:
            return await self._retry_with_exponential_backoff(_send_request)
        except core_exceptions.ServiceUnavailable as e:
            return f"Service unavailable after {self.max_retries} retries: {e.message if hasattr(e, 'message') else str(e)}"
        except Exception as e:
            logger.error(f"Error during send_message to Gemini: {e}")
            return f"Error sending message: {str(e)}"