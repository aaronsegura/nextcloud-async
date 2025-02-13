"""Our own Exception classes."""

from nextcloud_async.exceptions import NextcloudException


class NextcloudTalkException(NextcloudException):
    """Generic Exception."""

    def __init__(self, status_code: int = None, reason: str = None):
        """Configure exception."""
        super(NextcloudException, self).__init__(status_code=status_code, reason=reason)


class NextCloudTalkBadRequest(NextcloudTalkException):
    """User made a bad request."""

    status_code = 400
    reason = 'User made a bad request.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudTalkException, self).__init__()


class NextCloudTalkConflict(NextcloudTalkException):
    """User has duplicate Talk sessions."""

    status_code = 409
    reason = 'User has duplicate Talk sessions.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudTalkException, self).__init__()


class NextCloudTalkPreconditionFailed(NextcloudTalkException):
    """User tried to join chat room without going to lobby."""

    status_code = 412
    reason = 'User tried to join chat room without going to lobby.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudTalkException, self).__init__()


class NextCloudTalkNotCapable(NextcloudTalkException):
    """Raised when server does not have required capability."""

    status_code = 499
    reason = 'Server does not support required capability.'

    def __init__(self):
        """Configure exception."""
        super(NextcloudTalkException, self).__init__()
