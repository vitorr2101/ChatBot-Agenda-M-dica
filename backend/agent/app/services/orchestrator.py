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



if __name__ == "__main__":
    import asyncio
    
    async def test_orchestrator():
        """Test the orchestrator functionality."""
        print("🚀 Testing Chat Orchestrator with Dependency Injection...")
        
        try:
            orchestrator = create_default_orchestrator()
            
            async with orchestrator:
                print("✅ Orchestrator initialized successfully")
                
                status = await orchestrator.get_server_status()
                print(f"📊 Server status: {status}")
                
                chat_status = await orchestrator.get_chat_status()
                print(f"💬 Chat status: {chat_status}")
                
                tools = await orchestrator.get_available_tools()
                print(f"🔧 Available tools: {len(tools)}")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']} (from {tool['server']})")
                
                print("\n💬 Creating chat session...")
                await orchestrator.create_chat()
                
                print("💬 Testing message processing...")
                response = await orchestrator.process_message(
                    "Hello! What can you help me with regarding medical appointments?"
                )
                print(f"🤖 Response: {response}")
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(test_orchestrator())