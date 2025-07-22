"""
Comprehensive Error Handling System
Provides standardized error responses and exception management
"""

import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from flask import jsonify, request
import logging

from .logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)

class ErrorCode(Enum):
    """Standardized error codes"""
    # Validation Errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_DATE_FORMAT = "INVALID_DATE_FORMAT"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    INVALID_CURRENCY = "INVALID_CURRENCY"
    
    # Processing Errors (5xx)
    OCR_PROCESSING_FAILED = "OCR_PROCESSING_FAILED"
    IMAGE_PROCESSING_FAILED = "IMAGE_PROCESSING_FAILED"
    PARSING_FAILED = "PARSING_FAILED"
    
    # Database Errors (5xx)
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_CONSTRAINT_ERROR = "DATABASE_CONSTRAINT_ERROR"
    DATABASE_TIMEOUT = "DATABASE_TIMEOUT"
    
    # External Service Errors (5xx)
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # System Errors (5xx)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    
    # Security Errors (4xx)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    MALICIOUS_FILE_DETECTED = "MALICIOUS_FILE_DETECTED"

@dataclass
class ErrorDetails:
    """Detailed error information"""
    field: Optional[str] = None
    value: Optional[Any] = None
    constraint: Optional[str] = None
    suggestion: Optional[str] = None
    documentation_url: Optional[str] = None

class ApplicationError(Exception):
    """Base application exception with structured error information"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Union[ErrorDetails, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        self.cause = cause
        self.correlation_id = get_correlation_id()
        self.timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Log the error
        self._log_error()
    
    def _log_error(self):
        """Log the error with full context"""
        logger.error(
            f"Application Error: {self.message}",
            error_code=self.error_code.value,
            status_code=self.status_code,
            details=self.details,
            cause=str(self.cause) if self.cause else None,
            correlation_id=self.correlation_id
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response"""
        error_dict = {
            'success': False,
            'error': {
                'code': self.error_code.value,
                'message': self.message,
                'timestamp': self.timestamp,
                'correlation_id': self.correlation_id
            }
        }
        
        if self.details:
            if isinstance(self.details, ErrorDetails):
                error_dict['error']['details'] = {
                    'field': self.details.field,
                    'value': self.details.value,
                    'constraint': self.details.constraint,
                    'suggestion': self.details.suggestion,
                    'documentation_url': self.details.documentation_url
                }
            else:
                error_dict['error']['details'] = self.details
        
        return error_dict

# Specific Exception Classes

class ValidationError(ApplicationError):
    """Validation-related errors"""
    
    def __init__(self, message: str, field: str = None, value: Any = None, suggestion: str = None):
        details = ErrorDetails(
            field=field,
            value=value,
            suggestion=suggestion
        )
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details
        )

class ProcessingError(ApplicationError):
    """Processing-related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.OCR_PROCESSING_FAILED, cause: Exception = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=500,
            cause=cause
        )

class DatabaseError(ApplicationError):
    """Database-related errors"""
    
    def __init__(self, message: str, operation: str = None, table: str = None, cause: Exception = None):
        details = {
            'operation': operation,
            'table': table
        }
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_QUERY_ERROR,
            status_code=500,
            details=details,
            cause=cause
        )

class ExternalServiceError(ApplicationError):
    """External service-related errors"""
    
    def __init__(self, message: str, service: str, cause: Exception = None):
        details = {'service': service}
        super().__init__(
            message=message,
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=503,
            details=details,
            cause=cause
        )

class SecurityError(ApplicationError):
    """Security-related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.FORBIDDEN):
        status_code = 401 if error_code == ErrorCode.UNAUTHORIZED else 403
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code
        )

# Error Handler Functions

def handle_application_error(error: ApplicationError):
    """Handle application-specific errors"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def handle_validation_error(error: Exception):
    """Handle validation errors from Pydantic or other validators"""
    if hasattr(error, 'errors'):
        # Pydantic validation error
        details = []
        for err in error.errors():
            details.append({
                'field': '.'.join(str(x) for x in err['loc']),
                'message': err['msg'],
                'type': err['type']
            })
        
        app_error = ValidationError(
            message="Validation failed",
            field="multiple",
            suggestion="Please check the provided data format"
        )
        app_error.details = {'validation_errors': details}
    else:
        app_error = ValidationError(
            message=str(error),
            suggestion="Please check your input data"
        )
    
    return handle_application_error(app_error)

def handle_database_error(error: Exception, operation: str = None, table: str = None):
    """Handle database-related errors"""
    error_message = "Database operation failed"
    
    # Classify database errors
    error_str = str(error).lower()
    if 'connection' in error_str or 'connect' in error_str:
        error_code = ErrorCode.DATABASE_CONNECTION_ERROR
        error_message = "Database connection failed"
    elif 'timeout' in error_str:
        error_code = ErrorCode.DATABASE_TIMEOUT
        error_message = "Database operation timed out"
    elif 'constraint' in error_str or 'unique' in error_str:
        error_code = ErrorCode.DATABASE_CONSTRAINT_ERROR
        error_message = "Database constraint violation"
    else:
        error_code = ErrorCode.DATABASE_QUERY_ERROR
    
    app_error = ApplicationError(
        message=error_message,
        error_code=error_code,
        status_code=500,
        details={'operation': operation, 'table': table},
        cause=error
    )
    
    return handle_application_error(app_error)

def handle_unexpected_error(error: Exception):
    """Handle unexpected/unclassified errors"""
    logger.critical(
        f"Unexpected error: {str(error)}",
        error_type=type(error).__name__,
        traceback=traceback.format_exc()
    )
    
    app_error = ApplicationError(
        message="An unexpected error occurred",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        status_code=500,
        cause=error
    )
    
    return handle_application_error(app_error)

# Decorator for error handling

def handle_errors(operation_name: str = None):
    """Decorator to handle errors in functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                return func(*args, **kwargs)
            except ApplicationError:
                # Re-raise application errors as-is
                raise
            except Exception as e:
                # Convert unexpected errors to application errors
                logger.error(
                    f"Unexpected error in {op_name}: {str(e)}",
                    operation=op_name,
                    error_type=type(e).__name__
                )
                raise ApplicationError(
                    message=f"Operation {op_name} failed",
                    error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                    cause=e
                )
        return wrapper
    return decorator

# Input validation helpers

def validate_file_upload(file, allowed_extensions: set, max_size_mb: int = 10):
    """Validate uploaded file"""
    if not file or not file.filename:
        raise ValidationError(
            message="No file provided",
            field="file",
            suggestion="Please select a file to upload"
        )
    
    # Check file extension
    if '.' not in file.filename:
        raise ValidationError(
            message="File has no extension",
            field="file.filename",
            value=file.filename,
            suggestion=f"Please upload a file with one of these extensions: {', '.join(allowed_extensions)}"
        )
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        raise ValidationError(
            message=f"Invalid file type: {extension}",
            field="file.extension",
            value=extension,
            suggestion=f"Allowed file types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size (if we can determine it)
    if hasattr(file, 'content_length') and file.content_length:
        max_size_bytes = max_size_mb * 1024 * 1024
        if file.content_length > max_size_bytes:
            raise ValidationError(
                message=f"File too large: {file.content_length / (1024*1024):.1f}MB",
                field="file.size",
                value=f"{file.content_length / (1024*1024):.1f}MB",
                suggestion=f"Maximum file size is {max_size_mb}MB"
            )

def validate_amount(amount: Any):
    """Validate monetary amount"""
    if amount is None:
        raise ValidationError(
            message="Amount is required",
            field="amount",
            suggestion="Please provide a valid amount"
        )
    
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValidationError(
                message="Amount must be positive",
                field="amount",
                value=amount,
                suggestion="Please provide a positive amount"
            )
        if amount_float > 1000000:  # 1 million limit
            raise ValidationError(
                message="Amount too large",
                field="amount",
                value=amount,
                suggestion="Maximum amount is 1,000,000"
            )
    except (ValueError, TypeError):
        raise ValidationError(
            message="Invalid amount format",
            field="amount",
            value=amount,
            suggestion="Please provide a numeric amount"
        )

def validate_currency(currency: str):
    """Validate currency code"""
    valid_currencies = {'INR', 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD'}
    
    if not currency:
        raise ValidationError(
            message="Currency is required",
            field="currency",
            suggestion="Please provide a valid currency code"
        )
    
    if currency.upper() not in valid_currencies:
        raise ValidationError(
            message=f"Invalid currency: {currency}",
            field="currency",
            value=currency,
            suggestion=f"Supported currencies: {', '.join(valid_currencies)}"
        )

def validate_date(date_str: str):
    """Validate date string"""
    if not date_str:
        raise ValidationError(
            message="Date is required",
            field="transaction_date",
            suggestion="Please provide a valid date"
        )
    
    try:
        from datetime import datetime
        # Try to parse the date
        datetime.fromisoformat(date_str)
    except ValueError:
        raise ValidationError(
            message="Invalid date format",
            field="transaction_date",
            value=date_str,
            suggestion="Please use YYYY-MM-DD format"
        )