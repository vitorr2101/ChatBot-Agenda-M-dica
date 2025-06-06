from dotenv import load_dotenv
import os
import secrets
from pathlib import Path

load_dotenv()

def get_required_env(key: str) -> str:
    """
    Get a required environment variable.
    
    Args:
        key: The environment variable key to retrieve.
        
    Returns:
        The environment variable value.
        
    Raises:
        ValueError: If the environment variable is not set or empty.
    """
    
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value

def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt file from the prompts directory.
    
    Args:
        prompt_name: Name of the prompt file (e.g., 'system_instruction.md').
        
    Returns:
        Contents of the prompt file with whitespace stripped.
        
    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """

    current_file = Path(__file__).resolve()
    prompts_dir = current_file.parent.parent / 'prompts'
    prompt_path = prompts_dir / prompt_name
    return prompt_path.read_text(encoding='utf-8').strip()

GEMINI_API_KEY = get_required_env("GEMINI_API_KEY")
MCP_SERVER_DIR = get_required_env("MCP_SERVER_DIR")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))
SYSTEM_INSTRUCTION = load_prompt('system_instruction.md')


