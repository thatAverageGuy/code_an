import logging
import os
import sys
from functools import lru_cache
from typing import Optional
from config import settings

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Determine log level from settings
LOG_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers
    
    Args:
        name: Logger name
        log_file: Optional file path for logging
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

@lru_cache(maxsize=8)
def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Get a logger by name with caching
    
    Args:
        name: Logger name
        log_file: Optional file path for logging
        
    Returns:
        Logger instance
    """
    # If no log file is specified, use the default based on the name
    if not log_file and name != "root":
        log_dir = os.path.join(settings.TEMP_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{name}.log")
    
    return setup_logger(name, log_file)

# Set up the root logger
root_logger = setup_logger("root")

# Common loggers
api_logger = get_logger("api")
service_logger = get_logger("service")