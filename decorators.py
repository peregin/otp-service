from functools import wraps
from flask import request, jsonify
from http import HTTPStatus
from typing import Callable, Any

def handle_validation_error(error: str) -> tuple:
    """
    Standardize validation error responses

    Args:
        error (str): Error message

    Returns:
        tuple: JSON response and status code
    """
    return jsonify({"error": error}), HTTPStatus.BAD_REQUEST


class RequestValidators:
    """Collection of request validation decorators"""

    @staticmethod
    def validate_username(f: Callable) -> Callable:
        """Validate username presence in request"""

        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            username = request.json.get("username")
            if not username:
                return handle_validation_error("Username is required")
            return f(username, *args, **kwargs)

        return decorated_function

    @staticmethod
    def validate_otp(f: Callable) -> Callable:
        """Validate OTP presence in request"""

        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            data = request.json
            otp = data.get("otp")
            if not otp:
                return handle_validation_error("OTP is required")
            kwargs['otp'] = otp
            return f(*args, **kwargs)

        return decorated_function