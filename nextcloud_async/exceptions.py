"""Our very own exception classes."""

from typing import Optional

#TODO: https://peps.python.org/pep-0008/#exception-names

class NextcloudError(Exception):
    """Generic Exception."""

    status_code = None
    reason = None

    def __init__(self,
                 status_code: Optional[int] = None,
                 reason: Optional[str] = None) -> None:
        """Initialize our very own exception."""
        super(BaseException, self).__init__()
        self.status_code = status_code
        self.reason = reason

    def __str__(self) -> str:
        if self.status_code:
            return f'[{self.status_code}] {self.reason}'
        else:
            return str(self.reason)


class NextcloudNotModified:
    """304 - Content not modified."""

    status_code = 304
    reason = 'Not modified.'

    def __str__(self) -> str:
        return f'[{self.status_code}] {self.reason}'


class NextcloudBadRequestError(NextcloudError):
    """User made an invalid request."""

    status_code = 400
    reason = 'Bad request.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudUnauthorizedError(NextcloudError):
    """User account is not authorized."""

    status_code = 401
    reason = 'Invalid credentials.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)

class NextcloudForbiddenError(NextcloudError):
    """Forbidden action due to permissions."""

    status_code = 403
    reason = 'Forbidden action due to permissions.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudDeviceWipeRequested:
    """User has revoked this appKey, and requests a device wipe."""

    status_code = 403
    reason = 'User revoked key. Please wipe this device '\
             'and confirm with Wipe.notify_wiped().'

    def __str__(self) -> str:
        return f'[{self.status_code}] {self.reason}'


class NextcloudNotFoundError(NextcloudError):
    """Object not found."""

    status_code = 404
    reason = 'Object not found.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudMethodNotAllowedError(NextcloudError):
    """HTTP Request timed out."""

    status_code = 405
    reason = "Method not allowed for object."

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudNotSupportedError(NextcloudError):
    """Action not supported."""

    status_code = 406
    reason = "Action not supported."

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudRequestTimeoutError(NextcloudError):
    """HTTP Request timed out."""

    status_code = 408
    reason = "Request timed out."

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudLoginFlowTimeoutError(NextcloudError):
    """LoginFlowv2 request timed out.

    The wait_confirm() function can be called multiple times.
    """

    status_code = 408
    reason = "Login flow request timed out.  Try again."

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudConflictError(NextcloudError):
    """Curent state disallows the action."""

    status_code = 409
    reason = 'Current conditions disallow action.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudPreconditionError(NextcloudError):
    """Precondition of action failed."""

    status_code = 412
    reason = 'User attempted action that requires other actions first.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudFederationRemoteError(NextcloudError):
    """Federation peering error."""

    status_code = 422
    reason = 'Remote federation peer error.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudUpgradeRequiredError(NextcloudError):
    """Client upgrade required."""

    status_code = 426
    reason = 'Client software update is required.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudTooManyRequestsError(NextcloudError):
    """Too many requests."""

    status_code = 429
    reason = "Too many requests. Try again later."

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudNotCapableError(NextcloudError):
    """Raised when server does not have required capability."""

    status_code = 499
    reason = 'Server does not support required capability.'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudServiceNotAvailableError(NextcloudError):
    """Raised when server returns 503 error."""

    status_code = 503
    reason = 'Service is not avaiable'

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)


class NextcloudChunkedUploadError(NextcloudError):
    """When there is more than one chunk in the local cache directory."""

    status_code = 999
    reason = "Unable to determine chunked upload state."

    def __init__(self, reason: Optional[str] = None) -> None:
        """Configure exception."""
        super().__init__(reason=reason or self.reason)
