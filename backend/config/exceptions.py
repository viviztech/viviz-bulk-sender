"""
Custom exception handlers for Viviz Bulk Sender API.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': get_error_message(exc),
                'details': response.data if hasattr(response, 'data') else None,
            }
        }
        response.data = custom_response_data
    
    # Handle specific exceptions
    if isinstance(exc, ValidationError):
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Validation error',
                'details': exc.messages if hasattr(exc, 'messages') else str(exc),
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, Http404):
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Resource not found',
                'details': str(exc),
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Log unexpected errors
    if response is None:
        logger.exception(f"Unhandled exception: {exc}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Internal server error',
                'details': str(exc) if str(exc) else 'An unexpected error occurred',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def get_error_message(exc):
    """Extract a user-friendly error message from an exception."""
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, str):
            return exc.detail
        elif isinstance(exc.detail, list):
            return exc.detail[0] if exc.detail else 'An error occurred'
        elif isinstance(exc.detail, dict):
            return list(exc.detail.values())[0][0] if exc.detail else 'An error occurred'
    return str(exc)


class APIException(Exception):
    """Base exception for API errors."""
    def __init__(self, message, code='error', status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class ValidationException(APIException):
    """Exception for validation errors."""
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='validation_error',
            status_code=400
        )
        self.details = details


class AuthenticationException(APIException):
    """Exception for authentication errors."""
    def __init__(self, message='Authentication failed'):
        super().__init__(
            message=message,
            code='authentication_error',
            status_code=401
        )


class PermissionException(APIException):
    """Exception for permission errors."""
    def __init__(self, message='You do not have permission to perform this action'):
        super().__init__(
            message=message,
            code='permission_error',
            status_code=403
        )


class NotFoundException(APIException):
    """Exception for not found errors."""
    def __init__(self, message='Resource not found'):
        super().__init__(
            message=message,
            code='not_found',
            status_code=404
        )


class RateLimitException(APIException):
    """Exception for rate limit errors."""
    def __init__(self, message='Rate limit exceeded'):
        super().__init__(
            message=message,
            code='rate_limit_exceeded',
            status_code=429
        )


class GreenAPIException(APIException):
    """Exception for Green API errors."""
    def __init__(self, message='Green API error', details=None):
        super().__init__(
            message=message,
            code='green_api_error',
            status_code=502
        )
        self.details = details
