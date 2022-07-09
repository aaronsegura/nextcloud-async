"""Our own Exception classes."""


class NextCloudTalkException(Exception):
    """Generic Exception."""

    pass


class NextCloudTalkBadRequest(NextCloudTalkException):
    """User made a bad request."""

    code = 400
    reason = 'User made a bad request.'


class NextCloudTalkUnauthorized(NextCloudTalkException):
    """User account is not authorized."""

    code = 401
    reason = 'User account is not authorized.'


class NextCloudTalkForbidden(NextCloudTalkException):
    """Forbidden action due to permissions."""

    code = 403
    reason = 'Forbidden action due to permissions.'


class NextCloudTalkNotFound(NextCloudTalkException):
    """Object not found."""

    code = 404
    reason = 'Object not found.'


class NextCloudTalkConflict(NextCloudTalkException):
    """User has duplicate Talk sessions."""

    code = 409
    reason = 'User has duplicate Talk sessions.'


class NextCloudTalkPreconditionFailed(NextCloudTalkException):
    """User tried to join chat room without going to lobby."""

    code = 412
    reason = 'User tried to join chat room without going to lobby.'


class NextCloudTalkNotCapable(NextCloudTalkException):
    """Raised when server does not have required capability."""

    code = 499
    reason = 'Server does not support required capability.'
