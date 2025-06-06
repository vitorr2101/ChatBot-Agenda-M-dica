from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.client.stdio import StdioServerParams
from contextlib import asynccontextmanager
import logging

from .services.orchestrator import ChatOrchestrator
from .services.llm_client import GeminiLLMClient, LLMClientInterface
from .services.mcp_client import MCPStdioClient, MCPClientInterface
from .configs.settings import GEMINI_API_KEY, GEMINI_MODEL_NAME, SYSTEM_INSTRUCTION
from .configs.mcp_server_config import MCP_SERVERS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the lifespan of the FastAPI application.
    Initialize and cleanup the orchestrator.
    """
    
    try:
        logger.info("Starting medical appointment chatbot backend...")

        llm_client: LLMClientInterface = GeminiLLMClient(
            api_key=GEMINI_API_KEY, 
            model_name=GEMINI_MODEL_NAME,
            max_retries=5
        )

        server = list(MCP_SERVERS.values())[0]
        mcp_clients: list[MCPClientInterface] = [await MCPStdioClient(
            StdioServerParams(
                command=server.get("command", ""),
                args=server.get("args", []),
                env=server.get("env", {}),
            )
        ).connect()]

        app.state.orchestrator = ChatOrchestrator(
            llm_client=llm_client,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=mcp_clients
        )

        logger.info("Application startup completed")

        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    finally:
        logger.info("Shutting down application...")

        if mcp_clients:
            for client in mcp_clients:
                await client.disconnect()

        logger.info("Application shutdown completed")
        


app = FastAPI(
    title="Medical Appointment Chatbot API",
    description="A FastAPI backend for medical appointment scheduling chatbot using LLM and MCP",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routers import chat, status

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(status.router, prefix="/api/v1/status", tags=["status"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
    logger.info("FastAPI server started at http://localhost:8000")