# Utils Module

This module contains utility functions and configurations for logging, error handling, and resource management.

## Components

### 📝 logging_config.py
**Comprehensive logging system with structured output and correlation tracking**

**Key Classes:**
- `ContextualLogger` - Enhanced logger with contextual information
- `CorrelationIdFilter` - Add correlation IDs to log records
- `StructuredFormatter` - JSON formatter for structured logging

**Key Functions:**
- `setup_logging()` - Initialize application-wide logging
- `get_logger(name)` - Get a contextual logger instance
- `set_correlation_id(corr_id)` - Set correlation ID for request tracking
- `log_performance()` - Performance monitoring decorator

### 🚨 error_handling.py
**Centralized error handling and response formatting**

**Key Classes:**
- `ErrorType` - Enumeration of error categories
- `ErrorContext` - Error context information
- `APIError` - Custom API exception class

**Key Functions:**
- `handle_api_error()` - Standardized API error responses
- `log_error_with_context()` - Enhanced error logging
- `create_error_response()` - Consistent error response format

### 🔧 resource_manager.py
**System resource monitoring and management**

**Key Functions:**
- `monitor_memory_usage()` - Track memory consumption
- `cleanup_temp_files()` - Temporary file management
- `check_disk_space()` - Disk space monitoring
- `optimize_gpu_memory()` - GPU memory management

## Logging System

### Basic Usage
```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("Processing started")
logger.warning("Low memory detected")
logger.error("Processing failed")

# Contextual logging
logger.info("User action completed", 
           user_id="12345", 
           action="upload_receipt", 
           duration=2.5)
```

### Structured Logging
```python
# Log with additional context
logger.info("Receipt processed successfully",
           receipt_id=123,
           vendor="Starbucks",
           amount=4.50,
           processing_time=1.2,
           ai_enhanced=True)

# Performance logging
logger.log_performance("ocr_processing", 
                      duration=3.5, 
                      engine="qwen2vl",
                      success=True)

# API request logging
logger.log_api_request("POST", 
                      "/process-receipt", 
                      status_code=200,
                      duration=2.1,
                      file_size=1024000)
```

### Correlation ID Tracking
```python
from utils.logging_config import set_correlation_id, get_correlation_id

# Set correlation ID for request tracking
correlation_id = set_correlation_id()  # Auto-generated UUID
# or
correlation_id = set_correlation_id("custom-id-123")

# All subsequent logs will include this correlation ID
logger.info("Processing request")  # Will include correlation_id in output

# Get current correlation ID
current_id = get_correlation_id()
```

### Performance Monitoring
```python
from utils.logging_config import log_performance

@log_performance("receipt_processing")
def process_receipt(file_bytes):
    # Function implementation
    return result

# Or with custom operation name
@log_performance()
def custom_function():
    # Will log as "module_name.custom_function"
    pass
```

### Log Output Format
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "services.ai_parser",
  "message": "Receipt processed successfully",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "ai_parser",
  "function": "extract_receipt_data",
  "line": 145,
  "process_id": 12345,
  "thread_id": 67890,
  "receipt_id": 123,
  "vendor": "Starbucks",
  "amount": 4.50,
  "processing_time": 1.2,
  "ai_enhanced": true
}
```

## Error Handling

### Error Types
```python
from utils.error_handling import ErrorType, APIError

class ErrorType(Enum):
    VALIDATION_ERROR = "validation_error"
    PROCESSING_ERROR = "processing_error"
    SYSTEM_ERROR = "system_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
```

### Custom API Errors
```python
from utils.error_handling import APIError, ErrorType

# Raise custom API error
raise APIError(
    message="Invalid file format",
    error_type=ErrorType.VALIDATION_ERROR,
    status_code=400,
    details={"allowed_formats": ["jpg", "png", "pdf"]}
)

# Error handling in Flask routes
@app.route('/process-receipt', methods=['POST'])
def process_receipt():
    try:
        # Processing logic
        return success_response(data)
    except APIError as e:
        return e.to_response()
    except Exception as e:
        return handle_unexpected_error(e)
```

### Error Context
```python
from utils.error_handling import ErrorContext, log_error_with_context

# Create error context
context = ErrorContext(
    user_id="user123",
    request_id="req456",
    operation="file_upload",
    additional_data={"file_size": 1024000, "file_type": "jpg"}
)

# Log error with context
try:
    risky_operation()
except Exception as e:
    log_error_with_context(e, context)
    raise
```

### Standardized Error Responses
```python
from utils.error_handling import create_error_response

# Create consistent error response
error_response = create_error_response(
    message="File processing failed",
    error_code="PROCESSING_FAILED",
    status_code=500,
    details={"stage": "ocr_extraction", "engine": "tesseract"}
)

# Returns:
{
    "success": false,
    "error": {
        "message": "File processing failed",
        "code": "PROCESSING_FAILED",
        "timestamp": "2024-01-15T10:30:45.123Z",
        "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
        "details": {
            "stage": "ocr_extraction",
            "engine": "tesseract"
        }
    }
}
```

## Resource Management

### Memory Monitoring
```python
from utils.resource_manager import monitor_memory_usage, cleanup_memory

# Monitor memory usage
memory_info = monitor_memory_usage()
print(f"Memory usage: {memory_info['percent']}%")
print(f"Available: {memory_info['available_gb']:.2f} GB")

# Cleanup memory if needed
if memory_info['percent'] > 80:
    cleanup_memory()
    logger.warning("High memory usage detected, cleanup performed")
```

### GPU Memory Management
```python
from utils.resource_manager import optimize_gpu_memory, get_gpu_info

# Check GPU status
gpu_info = get_gpu_info()
if gpu_info['available']:
    print(f"GPU Memory: {gpu_info['memory_used']}/{gpu_info['memory_total']} MB")
    
    # Optimize GPU memory
    if gpu_info['memory_percent'] > 90:
        optimize_gpu_memory()
        logger.info("GPU memory optimized")
```

### Temporary File Management
```python
from utils.resource_manager import cleanup_temp_files, create_temp_file

# Create temporary file
temp_file_path = create_temp_file(suffix='.jpg')
try:
    # Use temporary file
    with open(temp_file_path, 'wb') as f:
        f.write(image_data)
    # Process file
finally:
    # Cleanup is automatic, but can be forced
    cleanup_temp_files(older_than_hours=1)
```

### Disk Space Monitoring
```python
from utils.resource_manager import check_disk_space

# Check available disk space
disk_info = check_disk_space()
if disk_info['free_percent'] < 10:
    logger.warning("Low disk space detected", 
                  free_space_gb=disk_info['free_gb'],
                  total_space_gb=disk_info['total_gb'])
    
    # Trigger cleanup or alert
    cleanup_old_files()
```

## Configuration

### Logging Configuration
```python
# Environment variables
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')  # 'json' or 'text'
LOG_FILE = os.getenv('LOG_FILE', 'logs/application.log')

# Programmatic configuration
setup_logging(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    file_path=LOG_FILE,
    enable_console=True,
    enable_file=True
)
```

### Error Handling Configuration
```python
# Flask error handler registration
from utils.error_handling import register_error_handlers

app = Flask(__name__)
register_error_handlers(app)

# Custom error handler
@app.errorhandler(APIError)
def handle_api_error(error):
    return error.to_response()
```

## Advanced Features

### Custom Log Formatters
```python
class CustomFormatter(StructuredFormatter):
    """Custom log formatter with additional fields"""
    
    def format(self, record):
        log_entry = super().format(record)
        
        # Add custom fields
        log_entry['application'] = 'receipt-analyzer'
        log_entry['version'] = '1.0.0'
        log_entry['environment'] = os.getenv('ENVIRONMENT', 'development')
        
        return json.dumps(log_entry, default=str)
```

### Context Managers
```python
from utils.logging_config import set_correlation_id
from contextlib import contextmanager

@contextmanager
def request_context(request_id=None):
    """Context manager for request-scoped logging"""
    correlation_id = set_correlation_id(request_id)
    logger = get_logger(__name__)
    
    logger.info("Request started", request_id=correlation_id)
    try:
        yield correlation_id
    except Exception as e:
        logger.error("Request failed", error=str(e))
        raise
    finally:
        logger.info("Request completed")

# Usage
with request_context("req-123") as req_id:
    # All logging within this context will include req_id
    process_request()
```

### Performance Profiling
```python
import cProfile
import pstats
from utils.logging_config import get_logger

def profile_function(func):
    """Decorator to profile function performance"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        profiler = cProfile.Profile()
        
        profiler.enable()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            
            # Log profiling results
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            
            logger.info("Function profiling completed",
                       function=func.__name__,
                       total_calls=stats.total_calls,
                       total_time=stats.total_tt)
    
    return wrapper

@profile_function
def expensive_operation():
    # Function implementation
    pass
```

## Testing

### Unit Tests
```python
import unittest
from unittest.mock import patch, MagicMock
from utils.logging_config import get_logger, set_correlation_id

class TestLogging(unittest.TestCase):
    
    def test_correlation_id_setting(self):
        test_id = "test-123"
        result_id = set_correlation_id(test_id)
        self.assertEqual(result_id, test_id)
    
    def test_logger_creation(self):
        logger = get_logger("test_module")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.logger.name, "test_module")
    
    @patch('utils.logging_config.logging.getLogger')
    def test_structured_logging(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger = get_logger("test")
        logger.info("Test message", key="value")
        
        mock_logger.log.assert_called_once()
```

### Integration Tests
```bash
# Test logging output
python -c "
from utils.logging_config import get_logger
logger = get_logger('test')
logger.info('Test log message', test_field='test_value')
"

# Check log file
tail -f logs/application.log
```

## Troubleshooting

### Common Issues

1. **Log File Permission Denied**
   ```
   Error: Permission denied: 'logs/application.log'
   Solution: Create logs directory and set proper permissions
   mkdir -p logs && chmod 755 logs
   ```

2. **Memory Leak in Logging**
   ```
   Error: Memory usage keeps increasing
   Solution: Check for circular references in log handlers
   ```

3. **Correlation ID Not Appearing**
   ```
   Error: Correlation ID missing from logs
   Solution: Ensure set_correlation_id() is called before logging
   ```

### Performance Tips

1. **Use appropriate log levels** - Don't log DEBUG in production
2. **Avoid logging large objects** - Log summaries instead
3. **Use structured logging** - Easier to parse and analyze
4. **Implement log rotation** - Prevent log files from growing too large
5. **Monitor log volume** - High log volume can impact performance

## Future Enhancements

- [ ] Integration with external logging services (ELK, Splunk)
- [ ] Real-time log streaming and monitoring
- [ ] Advanced error categorization and alerting
- [ ] Automated performance regression detection
- [ ] Log-based metrics and dashboards
- [ ] Distributed tracing support
- [ ] Log sampling for high-volume applications