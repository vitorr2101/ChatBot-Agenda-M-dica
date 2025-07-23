import logging
import sys
from pathlib import Path
from typing import Optional
from .settings import LOG_LEVEL, DEBUG


def setup_logger(
    name: Optional[str] = None,
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: Logger name. If None, returns root logger.
        level: Log level. If None, uses LOG_LEVEL from settings.
        log_file: Optional file path to write logs to.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.addHandler(console_handler)
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        logger.addHandler(file_handler)
    
    logger.propagate = False
    
    return logger


def configure_root_logger() -> None:
    """
    Configure the root logger with application-wide settings.
    This should be called once at application startup.
    """
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    if not DEBUG:
        logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('google').setLevel(logging.WARNING)
    
    app_logger = logging.getLogger('app')
    app_logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module/component.
    
    Args:
        name: Logger name (typically __name__ of the module).
        
    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


app_logger = get_logger('app')
services_logger = get_logger('app.services')
routers_logger = get_logger('app.routers')
utils_logger = get_logger('app.utils')
