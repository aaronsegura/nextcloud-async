"""Our own Exception classes."""

from nextcloud_async.exceptions import NextCloudException


class NextCloudTalkException(NextCloudException):
    """Generic Exception."""

    def __init__(self, status_code: int = None, reason: str = None):
        """Configure exception."""
        super(NextCloudException, self).__init__(status_code=status_code, reason=reason)


class NextCloudTalkBadRequest(NextCloudTalkException):
    """User made a bad request."""

    status_code = 400
    reason = 'User made a bad request.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudTalkException, self).__init__()


class NextCloudTalkConflict(NextCloudTalkException):
    """User has duplicate Talk sessions."""

    status_code = 409
    reason = 'User has duplicate Talk sessions.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudTalkException, self).__init__()


class NextCloudTalkPreconditionFailed(NextCloudTalkException):
    """User tried to join chat room without going to lobby."""

    status_code = 412
    reason = 'User tried to join chat room without going to lobby.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudTalkException, self).__init__()


class NextCloudTalkNotCapable(NextCloudTalkException):
    """Raised when server does not have required capability."""

    status_code = 499
    reason = 'Server does not support required capability.'

    def __init__(self):
        """Configure exception."""
        super(NextCloudTalkException, self).__init__()
