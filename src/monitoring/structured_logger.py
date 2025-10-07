"""
Structured JSON logging for BookGen application
Provides structured logging with correlation IDs for request tracing
"""
import logging
import json
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variable for correlation ID (request tracing)
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    Outputs log records as JSON with consistent structure
    """
    
    def __init__(self, app_name: str = "bookgen"):
        """
        Initialize structured formatter
        
        Args:
            app_name: Application name to include in logs
        """
        super().__init__()
        self.app_name = app_name
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string representation of log record
        """
        # Base log structure
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app": self.app_name,
        }
        
        # Add correlation ID if available
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        
        # Add extra fields from record
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add location info
        log_data["location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName
        }
        
        # Add process/thread info
        log_data["process"] = {
            "pid": record.process,
            "thread": record.thread,
            "thread_name": record.threadName
        }
        
        return json.dumps(log_data)


class StructuredLogger:
    """
    Wrapper for structured logging with additional context
    """
    
    def __init__(self, name: str):
        """
        Initialize structured logger
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
    
    def _log(self, level: int, message: str, **kwargs):
        """
        Internal logging method with extra context
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context to include in log
        """
        extra = kwargs.pop('extra', {})
        extra.update(kwargs)
        self.logger.log(level, message, extra={'extra': extra})
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        extra = kwargs.pop('extra', {})
        extra.update(kwargs)
        self.logger.exception(message, extra={'extra': extra})


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    app_name: str = "bookgen"
) -> None:
    """
    Setup structured logging for the application
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON format (default True)
        app_name: Application name for logs
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter
    if json_format:
        formatter = StructuredFormatter(app_name=app_name)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set correlation ID for request tracing
    
    Args:
        correlation_id: Optional correlation ID. If not provided, generates a new UUID
        
    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """
    Get current correlation ID
    
    Returns:
        Current correlation ID or None if not set
    """
    return correlation_id_var.get()


def clear_correlation_id() -> None:
    """Clear current correlation ID"""
    correlation_id_var.set(None)
