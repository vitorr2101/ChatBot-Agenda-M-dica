from abc import ABC, abstractmethod
from typing import Any, List, Optional
from google.genai import types
from fastapi import UploadFile

class LLMClientInterface(ABC):
    """
    Interface for Large Language Model clients.
    Defines the contract for initializing a client, creating chat sessions,
    and sending messages.
    """

    @abstractmethod
    def __init__(
        self,
        api_key: str,
        model_name: str,
        max_retries: int = 3
    ):
        """
        Initialize the LLM client.

        Args:
            api_key: The API key for the LLM service.
            model_name: The name of the model to use.
            max_retries: Maximum number of retry attempts for service unavailable errors.
        """
        pass

    @abstractmethod
    def create_chat(
        self,
        system_instruction: Optional[str] = None,
        history: Optional[List[types.ContentOrDict]] = None
    ) -> Any:
        """
        Create a new chat session.

        Args:
            system_instruction: Optional system instruction or initial prompt for the chat.

        Returns:
            A chat session object specific to the LLM client implementation.
        """
        pass

    @abstractmethod
    async def send_message(
        self,
        chat_session: Any,
        content: List,
        temperature: Optional[float] = 0.1,
        max_output_tokens: Optional[int] = None,
        tools: Optional[list] = None
    ) -> str:
        """
        Send a message to the LLM using the provided chat session.
        The message can be composed of multiple parts (text, image).

        Args:
            chat_session: The active chat session.
            content: A list containing message content (e.g., [text, image_data]).
            temperature: Optional creativity/randomness for the response (0.0 to 1.0).
            max_output_tokens: Optional maximum number of tokens in the response.
            tools: Optional list of tools/sessions for function calling.

        Returns:
            The LLM's response text.
        """
        pass

    @abstractmethod
    async def format_file_part(self, file: UploadFile) -> types.Part:
        """
        Converte um UploadFile em um objeto Part do LLM SDK.
        
        Args:
            file: O arquivo enviado via FastAPI.
            
        Returns:
            types.Part: Objeto Part formatado para o LLM SDK.
        """
        pass

    api_key: str
    client: Any
    model_name: str
    max_retries: int
