"""
Comprehensive Logging Configuration
Provides structured logging with correlation IDs and contextual information
"""

import logging
import logging.config
import json
import uuid
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
import sys
import os

# Context variable for correlation ID
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')

class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records"""
    
    def filter(self, record):
        record.correlation_id = correlation_id.get('')
        return True

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', ''),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, default=str)

class ContextualLogger:
    """Enhanced logger with contextual information and correlation IDs"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with appropriate handlers and formatters"""
        if not self.logger.handlers:
            # Console handler with structured format
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(StructuredFormatter())
            console_handler.addFilter(CorrelationIdFilter())
            
            # File handler for persistent logging
            file_handler = logging.FileHandler('logs/application.log')
            file_handler.setFormatter(StructuredFormatter())
            file_handler.addFilter(CorrelationIdFilter())
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)
    
    def _log_with_context(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log message with additional context"""
        if extra_fields:
            extra = {'extra_fields': extra_fields}
        else:
            extra = {}
        
        self.logger.log(level, message, extra=extra, exc_info=exc_info)
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self._log_with_context(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self._log_with_context(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self._log_with_context(logging.ERROR, message, kwargs, exc_info=True)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context"""
        self._log_with_context(logging.CRITICAL, message, kwargs, exc_info=True)
    
    def log_performance(self, operation: str, duration: float, **metadata):
        """Log performance metrics"""
        self.info(
            f"Performance: {operation}",
            operation=operation,
            duration_ms=duration * 1000,
            performance_metric=True,
            **metadata
        )
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, duration: float, **metadata):
        """Log API request details"""
        self.info(
            f"API Request: {method} {endpoint}",
            http_method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration * 1000,
            api_request=True,
            **metadata
        )
    
    def log_database_operation(self, operation: str, table: str, duration: float, **metadata):
        """Log database operation details"""
        self.info(
            f"Database: {operation} on {table}",
            db_operation=operation,
            table=table,
            duration_ms=duration * 1000,
            database_metric=True,
            **metadata
        )

def setup_logging():
    """Setup application-wide logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('paddleocr').setLevel(logging.WARNING)

def get_logger(name: str) -> ContextualLogger:
    """Get a contextual logger instance"""
    return ContextualLogger(name)

def set_correlation_id(corr_id: str = None) -> str:
    """Set correlation ID for request tracking"""
    if corr_id is None:
        corr_id = str(uuid.uuid4())
    correlation_id.set(corr_id)
    return corr_id

def get_correlation_id() -> str:
    """Get current correlation ID"""
    return correlation_id.get('')

# Performance monitoring decorator
def log_performance(operation_name: str = None):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            logger = get_logger(func.__module__)
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log_performance(op_name, duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.log_performance(op_name, duration, success=False, error=str(e))
                raise
        return wrapper
    return decorator

# Initialize logging on module import
setup_logging()