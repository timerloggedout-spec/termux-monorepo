"""Error handling for SKYHOOK protocol layer.

Defines standardized error codes and exception classes for consistent
error handling across all SKYHOOK integrations.

Agent: Grok | Jules
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorCode(Enum):
    """Standardized error codes for SKYHOOK operations."""
    
    # Authentication errors
    AUTH_MISSING_API_KEY = "AUTH_001"
    AUTH_INVALID_API_KEY = "AUTH_002"
    AUTH_TOKEN_EXPIRED = "AUTH_003"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_004"
    
    # Configuration errors
    CONFIG_MISSING_REPO = "CONFIG_001"
    CONFIG_INVALID_BRANCH = "CONFIG_002"
    CONFIG_INVALID_SESSION_TYPE = "CONFIG_003"
    CONFIG_UNSUPPORTED_API_VERSION = "CONFIG_004"
    
    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "RATE_001"
    RATE_LIMIT_RETRY_AFTER = "RATE_002"
    
    # Resource errors
    RESOURCE_OUT_OF_MEMORY = "RESOURCE_001"
    RESOURCE_CPU_LIMIT = "RESOURCE_002"
    RESOURCE_STORAGE_LIMIT = "RESOURCE_003"
    RESOURCE_TIMEOUT = "RESOURCE_004"
    
    # Session errors
    SESSION_NOT_FOUND = "SESSION_001"
    SESSION_ALREADY_EXISTS = "SESSION_002"
    SESSION_INVALID_STATE_TRANSITION = "SESSION_003"
    SESSION_TIMED_OUT = "SESSION_004"
    
    # Network errors
    NETWORK_CONNECTION_FAILED = "NETWORK_001"
    NETWORK_TIMEOUT = "NETWORK_002"
    NETWORK_DNS_FAILURE = "NETWORK_003"
    
    # API errors
    API_INVALID_REQUEST = "API_001"
    API_INVALID_RESPONSE = "API_002"
    API_VERSION_MISMATCH = "API_003"
    API_ENDPOINT_NOT_FOUND = "API_004"
    
    # Integration errors
    INTEGRATION_UNSUPPORTED_FEATURE = "INTEGRATION_001"
    INTEGRATION_INCOMPATIBLE_VERSION = "INTEGRATION_002"
    INTEGRATION_MISSING_DEPENDENCY = "INTEGRATION_003"
    
    # Generic errors
    INTERNAL_ERROR = "INTERNAL_001"
    UNKNOWN_ERROR = "UNKNOWN_001"
    
    @property
    def category(self) -> str:
        """Get the error category from the code."""
        return self.value.split("_")[0]
    
    @property
    def code(self) -> str:
        """Get the error code string."""
        return self.value


class ErrorType(Enum):
    """Error type classification."""
    
    TRANSIENT = "transient"           # Can be retried
    CONFIGURATION = "configuration"   # Requires user intervention
    AUTHENTICATION = "authentication" # Token/permission issues
    RATE_LIMIT = "rate_limit"         # Rate limiting
    RESOURCE = "resource"             # Resource constraints
    VALIDATION = "validation"         # Input validation
    NETWORK = "network"               # Network issues
    INTEGRATION = "integration"       # Integration problems
    INTERNAL = "internal"             # Internal errors
    UNKNOWN = "unknown"               # Unknown errors


# Mapping from error codes to types
ERROR_CODE_TO_TYPE: Dict[ErrorCode, ErrorType] = {
    # Authentication
    ErrorCode.AUTH_MISSING_API_KEY: ErrorType.AUTHENTICATION,
    ErrorCode.AUTH_INVALID_API_KEY: ErrorType.AUTHENTICATION,
    ErrorCode.AUTH_TOKEN_EXPIRED: ErrorType.AUTHENTICATION,
    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS: ErrorType.AUTHENTICATION,
    
    # Configuration
    ErrorCode.CONFIG_MISSING_REPO: ErrorType.CONFIGURATION,
    ErrorCode.CONFIG_INVALID_BRANCH: ErrorType.CONFIGURATION,
    ErrorCode.CONFIG_INVALID_SESSION_TYPE: ErrorType.CONFIGURATION,
    ErrorCode.CONFIG_UNSUPPORTED_API_VERSION: ErrorType.CONFIGURATION,
    
    # Rate limiting
    ErrorCode.RATE_LIMIT_EXCEEDED: ErrorType.RATE_LIMIT,
    ErrorCode.RATE_LIMIT_RETRY_AFTER: ErrorType.RATE_LIMIT,
    
    # Resource
    ErrorCode.RESOURCE_OUT_OF_MEMORY: ErrorType.RESOURCE,
    ErrorCode.RESOURCE_CPU_LIMIT: ErrorType.RESOURCE,
    ErrorCode.RESOURCE_STORAGE_LIMIT: ErrorType.RESOURCE,
    ErrorCode.RESOURCE_TIMEOUT: ErrorType.RESOURCE,
    
    # Session
    ErrorCode.SESSION_NOT_FOUND: ErrorType.VALIDATION,
    ErrorCode.SESSION_ALREADY_EXISTS: ErrorType.VALIDATION,
    ErrorCode.SESSION_INVALID_STATE_TRANSITION: ErrorType.VALIDATION,
    ErrorCode.SESSION_TIMED_OUT: ErrorType.RESOURCE,
    
    # Network
    ErrorCode.NETWORK_CONNECTION_FAILED: ErrorType.TRANSIENT,
    ErrorCode.NETWORK_TIMEOUT: ErrorType.TRANSIENT,
    ErrorCode.NETWORK_DNS_FAILURE: ErrorType.TRANSIENT,
    
    # API
    ErrorCode.API_INVALID_REQUEST: ErrorType.VALIDATION,
    ErrorCode.API_INVALID_RESPONSE: ErrorType.INTERNAL,
    ErrorCode.API_VERSION_MISMATCH: ErrorType.INTEGRATION,
    ErrorCode.API_ENDPOINT_NOT_FOUND: ErrorType.INTEGRATION,
    
    # Integration
    ErrorCode.INTEGRATION_UNSUPPORTED_FEATURE: ErrorType.INTEGRATION,
    ErrorCode.INTEGRATION_INCOMPATIBLE_VERSION: ErrorType.INTEGRATION,
    ErrorCode.INTEGRATION_MISSING_DEPENDENCY: ErrorType.INTEGRATION,
    
    # Generic
    ErrorCode.INTERNAL_ERROR: ErrorType.INTERNAL,
    ErrorCode.UNKNOWN_ERROR: ErrorType.UNKNOWN,
}


@dataclass
class SkyhookErrorDetails:
    """Detailed error information."""
    
    code: ErrorCode
    message: str
    error_type: ErrorType
    retry_after: Optional[float] = None
    suggestions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code.code,
            "message": self.message,
            "type": self.error_type.value,
            "retry_after": self.retry_after,
            "suggestions": self.suggestions,
            "context": self.context,
        }


class SkyhookError(Exception):
    """Base exception class for SKYHOOK errors."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        retry_after: Optional[float] = None,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.error_type = ERROR_CODE_TO_TYPE.get(code, ErrorType.UNKNOWN)
        self.retry_after = retry_after
        self.suggestions = suggestions or []
        self.context = context or {}
        
        # Build full message
        full_message = f"[{code.code}] {message}"
        if self.suggestions:
            full_message += f"\nSuggestions: {', '.join(self.suggestions)}"
        
        super().__init__(full_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return SkyhookErrorDetails(
            code=self.code,
            message=self.message,
            error_type=self.error_type,
            retry_after=self.retry_after,
            suggestions=self.suggestions,
            context=self.context,
        ).to_dict()
    
    @property
    def is_retryable(self) -> bool:
        """Check if this error can be retried."""
        return self.error_type in (ErrorType.TRANSIENT, ErrorType.RATE_LIMIT, ErrorType.NETWORK)
    
    @property
    def requires_user_action(self) -> bool:
        """Check if this error requires user intervention."""
        return self.error_type in (ErrorType.CONFIGURATION, ErrorType.AUTHENTICATION)


class TransientError(SkyhookError):
    """Transient errors that can be retried."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        retry_after: Optional[float] = None,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code, message, retry_after=retry_after, suggestions=suggestions, context=context)
        # Ensure this is a transient error type
        if ERROR_CODE_TO_TYPE.get(code) != ErrorType.TRANSIENT:
            raise ValueError(f"Error code {code} is not a transient error")


class ConfigurationError(SkyhookError):
    """Configuration errors that require user intervention."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code, message, suggestions=suggestions, context=context)
        # Ensure this is a configuration error type
        if ERROR_CODE_TO_TYPE.get(code) != ErrorType.CONFIGURATION:
            raise ValueError(f"Error code {code} is not a configuration error")


class AuthenticationError(SkyhookError):
    """Authentication errors that require re-authentication."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code, message, suggestions=suggestions, context=context)
        # Ensure this is an authentication error type
        if ERROR_CODE_TO_TYPE.get(code) != ErrorType.AUTHENTICATION:
            raise ValueError(f"Error code {code} is not an authentication error")


class RateLimitError(SkyhookError):
    """Rate limiting errors."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        retry_after: float,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code, message, retry_after=retry_after, suggestions=suggestions, context=context)
        # Ensure this is a rate limit error type
        if ERROR_CODE_TO_TYPE.get(code) != ErrorType.RATE_LIMIT:
            raise ValueError(f"Error code {code} is not a rate limit error")


class ResourceError(SkyhookError):
    """Resource constraint errors."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code, message, suggestions=suggestions, context=context)
        # Ensure this is a resource error type
        if ERROR_CODE_TO_TYPE.get(code) != ErrorType.RESOURCE:
            raise ValueError(f"Error code {code} is not a resource error")


def create_error_from_response(
    response: Dict[str, Any],
    default_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    default_message: str = "Unknown error occurred",
) -> SkyhookError:
    """Create a SkyhookError from an API response.
    
    This method attempts to extract error information from various Jules API
    response formats and create a standardized SkyhookError.
    """
    # Try to extract error information from different response formats
    
    # Format 1: jules-dispatch-cli style
    if "error" in response and isinstance(response["error"], dict):
        error_data = response["error"]
        code_str = error_data.get("code", default_code.code)
        message = error_data.get("message", default_message)
        
        # Try to map code string to ErrorCode
        for ec in ErrorCode:
            if ec.code == code_str:
                code = ec
                break
        else:
            code = default_code
        
        return SkyhookError(
            code=code,
            message=message,
            context=error_data,
        )
    
    # Format 2: jules-mcp-server style
    if "error" in response and isinstance(response["error"], str):
        return SkyhookError(
            code=default_code,
            message=response["error"],
        )
    
    # Format 3: HTTP error with status code
    if "status" in response and "message" in response:
        status = response["status"]
        message = response["message"]
        
        # Map HTTP status codes to error codes
        if status == 401:
            code = ErrorCode.AUTH_INVALID_API_KEY
        elif status == 403:
            code = ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS
        elif status == 429:
            code = ErrorCode.RATE_LIMIT_EXCEEDED
        elif status == 404:
            code = ErrorCode.SESSION_NOT_FOUND
        elif status >= 500:
            code = ErrorCode.INTERNAL_ERROR
        else:
            code = default_code
        
        return SkyhookError(code=code, message=message)
    
    # Default case
    return SkyhookError(code=default_code, message=default_message)
