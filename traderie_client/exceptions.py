"""
Exceptions for the Traderie API client.
"""


class TraderieError(Exception):
    """Base exception for Traderie API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(TraderieError):
    """Raised when authentication fails."""
    pass


class RateLimitError(TraderieError):
    """Raised when rate limited by the API."""
    pass
