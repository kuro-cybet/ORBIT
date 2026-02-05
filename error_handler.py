"""
ORBIT Global Error Handler

Provides centralized error handling, logging, and recovery mechanisms.
"""

import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
from functools import wraps

# Custom exception classes
class ORBITException(Exception):
    """Base exception for ORBIT application"""
    pass

class SecurityException(ORBITException):
    """Security-related exceptions"""
    pass

class FileOperationException(ORBITException):
    """File operation exceptions"""
    pass

class NetworkException(ORBITException):
    """Network-related exceptions"""
    pass

class ConfigurationException(ORBITException):
    """Configuration-related exceptions"""
    pass

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging system"""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"orbit_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_formatter)
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        self.logger = logger
    
    def log_error(self, error: Exception, context: str = ""):
        """
        Log error with context
        
        Args:
            error: Exception to log
            context: Additional context information
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_msg)
        
        if self.debug_mode:
            self.logger.debug(traceback.format_exc())
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        Global exception handler
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        self.logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> Optional[any]:
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result or None if error occurred
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.log_error(e, f"Error executing {func.__name__}")
            return None

def safe_function(error_handler: ErrorHandler, default_return=None):
    """
    Decorator for safe function execution
    
    Args:
        error_handler: ErrorHandler instance
        default_return: Default value to return on error
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(e, f"Error in {func.__name__}")
                return default_return
        return wrapper
    return decorator

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    continue
            
            # All attempts failed
            raise last_exception
        return wrapper
    return decorator

# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None

def initialize_error_handler(debug_mode: bool = False) -> ErrorHandler:
    """
    Initialize global error handler
    
    Args:
        debug_mode: Enable debug mode
        
    Returns:
        ErrorHandler instance
    """
    global _global_error_handler
    _global_error_handler = ErrorHandler(debug_mode)
    
    # Set global exception handler
    sys.excepthook = _global_error_handler.handle_exception
    
    return _global_error_handler

def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = initialize_error_handler()
    return _global_error_handler
