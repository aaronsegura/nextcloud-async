"""Our own Exception classes."""


class NextCloudTalkException(Exception):
    """Generic Exception."""

    pass


class NextCloudTalkBadRequest(NextCloudTalkException):

    code = 400
    reason = 'User made a bad request.'


class NextCloudTalkUnauthorized(NextCloudTalkException):

    code = 401
    reason = 'User account is not authorized.'


class NextCloudTalkForbidden(NextCloudTalkException):

    code = 403
    reason = 'Forbidden action due to permissions.'


class NextCloudTalkNotFound(NextCloudTalkException):

    code = 404
    reason = 'Object not found.'


class NextCloudTalkConflict(NextCloudTalkException):

    code = 409
    reason = 'User has duplicate sessions.'


class NextCloudTalkPreconditionFailed(NextCloudTalkException):

    code = 412
    reason = 'User tried to join chat room without going to lobby.'


class NextCloudTalkNotCapable(NextCloudTalkException):
    """Raised when server does not have required capability."""

    code = 499
    reason = 'Server does not support required capability.'
