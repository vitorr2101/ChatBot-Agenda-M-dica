from dotenv import load_dotenv
import os

load_dotenv()

def get_required_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value

GEMINI_API_KEY = get_required_env("GEMINI_API_KEY")
MCP_SERVER_DIR = get_required_env("MCP_SERVER_DIR")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")


