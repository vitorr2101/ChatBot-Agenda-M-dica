from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from mcp.client.stdio import StdioServerParameters
from contextlib import asynccontextmanager
import logging

from .services.orchestrator import ChatOrchestrator
from .services.llm_client import GeminiLLMClient
from .services.mcp_client import MCPStdioClient
from .configs.settings import GEMINI_API_KEY, DEFAULT_MODEL
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

        app.state.llm_client = GeminiLLMClient(
            api_key=GEMINI_API_KEY, 
            model_name=DEFAULT_MODEL,
            max_retries=5
        )

        app.state.mcp_client = MCPStdioClient(
            StdioServerParameters(
                command=MCP_SERVERS["Medical Appointment System"]["command"],
                args=MCP_SERVERS["Medical Appointment System"]["args"],
                env=MCP_SERVERS["Medical Appointment System"]["env"]
            )
        )
        await app.state.mcp_client.connect()

        app.state.orchestrator = ChatOrchestrator(
            llm_client=app.state.llm_client,
            tools=[app.state.mcp_client.session],
        )

        logger.info("Application startup completed")

        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    finally:
        logger.info("Shutting down application...")

        if hasattr(app.state, 'mcp_client'):
            await app.state.mcp_client.disconnect()
            logger.info("Disconnected from MCP client")

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

app.add_exception_handler(HTTPException, http_exception_handler)

from .routers import chat, status

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(status.router, prefix="/api/v1/status", tags=["status"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    logger.info("FastAPI server started at http://localhost:8000")