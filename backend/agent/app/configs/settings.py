from dotenv import load_dotenv
import os
import secrets
from pathlib import Path
from string import Template
from typing import Dict, Any, Optional
from datetime import datetime

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

def load_prompt(prompt_name: str, template_vars: Optional[Dict[str, Any]] = None) -> str:
    """
    Load a prompt file from the prompts directory with template support.
    
    Args:
        prompt_name: Name of the prompt file (e.g., 'system_instruction.md').
        template_vars: Dictionary of variables to substitute in the template.
        
    Returns:
        Contents of the prompt file with variables substituted and whitespace stripped.
        
    Raises:
        FileNotFoundError: If the prompt file does not exist.
        KeyError: If a template variable is missing.
    """
    current_file = Path(__file__).resolve()
    prompts_dir = current_file.parent.parent / 'prompts'
    prompt_path = prompts_dir / prompt_name
    
    content = prompt_path.read_text(encoding='utf-8').strip()
    
    if template_vars:
        template = Template(content)
        try:
            content = template.substitute(template_vars)
        except KeyError as e:
            raise KeyError(f"Missing template variable: {e}")
    
    return content


def get_default_template_vars() -> Dict[str, Any]:
    """
    Get default template variables for system instructions.
    
    Returns:
        Dictionary with default template variables.
    """
    return {
        'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'clinic_name': 'Clínica Ampla Saúde'
    }

GEMINI_API_KEY = get_required_env("GEMINI_API_KEY")
MCP_SERVER_DIR = os.getenv("MCP_SERVER_DIR", "../server")  
MONGODB_URI = get_required_env("MONGODB_URI")
MONGODB_NAME = os.getenv("MONGODB_DB_NAME", "Cluster0")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
DATABASE_URL = os.getenv("DATABASE_URL")
SYSTEM_INSTRUCTION = load_prompt('system_instruction_V1.md', get_default_template_vars())
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))


