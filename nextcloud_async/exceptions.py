"""Our very own exception classes."""


class NextCloudException(Exception):
    """Generic Exception."""

    status_code = None
    reason = None

    def __init__(self, status_code: int = None, reason: str = None):
        """Initialize our very own exception."""
        super(BaseException, self).__init__()
        self.status_code = status_code
        self.reason = reason

    def __str__(self):
        if self.status_code:
            return f'[{self.status_code}] {self.reason}'
        else:
            return self.reason


class NextCloudNotModified(NextCloudException):
    """304 - Content not modified."""

    status_code = 304
    reason = 'Not modified.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudException, self).__init__()


class NextCloudBadRequest(NextCloudException):
    """User made an invalid request."""

    status_code = 400
    reason = 'Bad request.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudException, self).__init__()


class NextCloudUnauthorized(NextCloudException):
    """User account is not authorized."""

    status_code = 401
    reason = 'Invalid credentials.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudException, self).__init__()


class NextCloudForbidden(NextCloudException):
    """Forbidden action due to permissions."""

    status_code = 403
    reason = 'Forbidden action due to permissions.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudException, self).__init__()


class NextCloudNotFound(NextCloudException):
    """Object not found."""

    status_code = 404
    reason = 'Object not found.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudException, self).__init__()


class NextCloudRequestTimeout(NextCloudException):
    """HTTP Request timed out."""

    status_code = 408
    reason = "Request timed out."

    def __init__(self):
        """Configure exception."""
        super(NextCloudException, self).__init__()


class NextCloudLoginFlowTimeout(NextCloudException):
    """When the login flow times out."""

    status_code = 408
    reason = "Login flow timed out.  Try again."

    def __init__(self):
        """Configure exception."""
        super(NextCloudException, self).__init__()


class NextCloudChunkedUploadException(NextCloudException):
    """When there is more than one chunk in the local cache directory."""

    status_code = 999
    reason = "Unable to determine chunked upload state."

    def __init__(self):
        """Configure exception."""
        super(NextCloudException, self).__init__()
