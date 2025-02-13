"""Our very own exception classes."""

from typing import Optional

class NextcloudException(Exception):
    """Generic Exception."""

    status_code = None
    reason = None

    def __init__(self, status_code: Optional[int] = None, reason: Optional[str] = None):
        """Initialize our very own exception."""
        super(BaseException, self).__init__()
        self.status_code = status_code
        self.reason = reason

    def __str__(self) -> str:  # noqa: D105
        if self.status_code:
            return f'[{self.status_code}] {self.reason}'
        else:
            return str(self.reason)


class NextCloudNotModified(NextcloudException):
    """304 - Content not modified."""

    status_code = 304
    reason = 'Not modified.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()


class NextCloudBadRequest(NextcloudException):
    """User made an invalid request."""

    status_code = 400
    reason = 'Bad request.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()


class NextCloudUnauthorized(NextcloudException):
    """User account is not authorized."""

    status_code = 401
    reason = 'Invalid credentials.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()


class NextCloudForbidden(NextcloudException):
    """Forbidden action due to permissions."""

    status_code = 403
    reason = 'Forbidden action due to permissions.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()


class NextCloudNotFound(NextcloudException):
    """Object not found."""

    status_code = 404
    reason = 'Object not found.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()


class NextCloudRequestTimeout(NextcloudException):
    """HTTP Request timed out."""

    status_code = 408
    reason = "Request timed out."

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()


class NextCloudLoginFlowTimeout(NextcloudException):
    """When the login flow times out."""

    status_code = 408
    reason = "Login flow timed out.  Try again."

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()

class NextCloudTooManyRequests(NextcloudException):
    """Too many requests"""

    status_code = 429
    reason = "Too many requests. Try again later."

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()

class NextCloudChunkedUploadException(NextcloudException):
    """When there is more than one chunk in the local cache directory."""

    status_code = 999
    reason = "Unable to determine chunked upload state."

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()
