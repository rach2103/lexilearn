"""
Logging configuration for LexiLearn backend
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO):
    """Setup logger with file and console handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(
            LOG_DIR / log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Create loggers
api_logger = setup_logger('api', 'api.log')
db_logger = setup_logger('database', 'database.log')
ai_logger = setup_logger('ai_tutor', 'ai_tutor.log')
auth_logger = setup_logger('auth', 'auth.log')
chat_logger = setup_logger('chat', 'chat.log')
error_logger = setup_logger('error', 'errors.log')

def log_request(method: str, path: str, status: int, duration: float):
    """Log API request"""
    api_logger.info(f'{method} {path} - Status: {status} - Duration: {duration:.2f}ms')

def log_error(error: Exception, context: dict = None):
    """Log error with context"""
    error_logger.error(
        f'Error: {str(error)}',
        exc_info=True,
        extra=context or {}
    )

# Main logger (for general use)
main_logger = setup_logger('main', 'main.log', logging.INFO)

