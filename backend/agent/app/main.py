from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from starlette.middleware.sessions import SessionMiddleware
from mcp.client.stdio import StdioServerParameters
from contextlib import asynccontextmanager
import logging

from .services.orchestrator import ChatOrchestrator
from .services.llm_client import GeminiLLMClient
from .services.mcp_client import MCPStdioClient
from .configs.settings import GEMINI_API_KEY, DEFAULT_MODEL, SESSION_SECRET_KEY

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    from .configs.mcp_server_config import MCP_SERVERS
except ImportError:
    logger.warning("MCP server configuration file not found. Create 'mcp_server_config.py' from 'mcp_server_config.py.example' to enable MCP servers.")
    MCP_SERVERS = {}


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

        app.state.mcp_client = None
        mcp_tools = []
        
        try:
            if not MCP_SERVERS:
                logger.info("No MCP servers configured, skipping MCP client initialization")
            elif "Medical Appointment System" not in MCP_SERVERS:
                logger.warning("Medical Appointment System not found in MCP servers configuration")
            else:
                logger.info("Attempting to initialize MCP client...")
                app.state.mcp_client = MCPStdioClient(
                    StdioServerParameters(
                        command=MCP_SERVERS["Medical Appointment System"]["command"],
                        args=MCP_SERVERS["Medical Appointment System"]["args"],
                        env=MCP_SERVERS["Medical Appointment System"]["env"]
                    )
                )
                await app.state.mcp_client.connect()
                mcp_tools = [app.state.mcp_client.session]
                logger.info("MCP client initialized successfully")
            
        except Exception as mcp_error:
            logger.warning(mcp_error)
            logger.warning("Application will continue without MCP tools")
            app.state.mcp_client = None

        app.state.orchestrator = ChatOrchestrator(
            llm_client=app.state.llm_client,
            tools=mcp_tools,
        )

        logger.info("Application startup completed")

        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    finally:
        logger.info("Shutting down application...")

        if hasattr(app.state, 'mcp_client') and app.state.mcp_client:
            try:
                await app.state.mcp_client.disconnect()
                logger.info("Disconnected from MCP client")
            except Exception as disconnect_error:
                logger.warning(f"Error disconnecting MCP client: {disconnect_error}")

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

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    session_cookie="session",               
    same_site="lax",             
    https_only=False             
)

app.add_exception_handler(HTTPException, http_exception_handler)

from .routers import chat, status

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(status.router, prefix="/api/v1/status", tags=["status"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    logger.info("FastAPI server started at http://localhost:8000")