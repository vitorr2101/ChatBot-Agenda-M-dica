from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from mcp.client.stdio import StdioServerParameters
from contextlib import asynccontextmanager

from .services.orchestrator import ChatOrchestrator
from .services.llm_client import GeminiLLMClient
from .services.mcp_client import MCPStdioClient
from .configs.settings import (
    GEMINI_API_KEY, 
    DEFAULT_MODEL, 
    SESSION_SECRET_KEY,
    DEBUG,
    LOG_LEVEL,
    API_HOST,
    API_PORT,
    CORS_ORIGINS
)
from .configs.logging_config import configure_root_logger, get_logger
from .exception_handlers import http_exception_handler

# Configure logging
configure_root_logger()
logger = get_logger(__name__)

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
                        env=MCP_SERVERS["Medical Appointment System"]["env"],
                        cwd=MCP_SERVERS["Medical Appointment System"]["cwd"]
                    )
                )
                await app.state.mcp_client.connect()
                if app.state.mcp_client.is_connected:
                    mcp_tools.append(app.state.mcp_client)

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
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    session_cookie="session",               
    same_site="lax",  
    https_only=False,
    max_age=86400,  
    path="/",
    domain=None 
)

app.add_exception_handler(HTTPException, http_exception_handler)

from .routers import chat, status

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(status.router, prefix="/api/v1/status", tags=["status"])

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,  # Pass the app directly instead of string
        host=API_HOST, 
        port=API_PORT, 
        log_level=LOG_LEVEL.lower(),
        reload=DEBUG
    )