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


class NextcloudNotModified(NextcloudException):
    """304 - Content not modified."""

    status_code = 304
    reason = 'Not modified.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudException, self).__init__()


class NextcloudBadRequest(NextcloudException):
    """User made an invalid request."""

    status_code = 400
    reason = 'Bad request.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudUnauthorized(NextcloudException):
    """User account is not authorized."""

    status_code = 401
    reason = 'Invalid credentials.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)

class NextcloudForbidden(NextcloudException):
    """Forbidden action due to permissions."""

    status_code = 403
    reason = 'Forbidden action due to permissions.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudDeviceWipeRequested(NextcloudException):
    """User has revoked this appKey, and requests a device wipe."""

    status_code = 403
    reason = 'User revoked key. Please wipe this device and confirm with Wipe.notify_wiped().'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudNotFound(NextcloudException):
    """Object not found."""

    status_code = 404
    reason = 'Object not found.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudMethodNotAllowed(NextcloudException):
    """HTTP Request timed out."""

    status_code = 405
    reason = "Method not allowed for object."

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudNotSupported(NextcloudException):
    """Federation endpoints not enabled."""

    status_code = 406
    reason = "Federation not supported."

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudRequestTimeout(NextcloudException):
    """HTTP Request timed out."""

    status_code = 408
    reason = "Request timed out."

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudLoginFlowTimeout(NextcloudException):
    """LoginFlowv2 request timed out.

    The wait_confirm() function can be called multiple times.
    """

    status_code = 408
    reason = "Login flow request timed out.  Try again."

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudConflict(NextcloudException):
    """Curent state disallows the action."""

    status_code = 409
    reason = 'User has duplicate Talk sessions.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudPreconditionFailed(NextcloudException):
    """Precondition of action failed."""

    status_code = 412
    reason = 'User tried to join chat room without going to lobby.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudFederationRemoteError(NextcloudException):
    """Precondition of action failed."""

    status_code = 422
    reason = 'Remote federation peer error.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudUpgradeRequired(NextcloudException):
    """Precondition of action failed."""

    status_code = 426
    reason = 'Client software update is required.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudTooManyRequests(NextcloudException):
    """Too many requests"""

    status_code = 429
    reason = "Too many requests. Try again later."

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudNotCapable(NextcloudException):
    """Raised when server does not have required capability."""

    status_code = 499
    reason = 'Server does not support required capability.'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudServiceNotAvailable(NextcloudException):
    """Raised when server does not have required capability."""

    status_code = 503
    reason = 'Service is not avaiable'

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudChunkedUploadException(NextcloudException):
    """When there is more than one chunk in the local cache directory."""

    status_code = 999
    reason = "Unable to determine chunked upload state."

    def __init__(self, reason: Optional[str] = None):
        """Configure exception."""
        super().__init__(reason=reason or self.reason)
