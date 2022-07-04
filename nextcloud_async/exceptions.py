"""Our very own exception classes."""


class NextCloudAsyncException(Exception):
    """Generic Exception."""

    def __init__(self, *args, **kwargs):
        super(BaseException, self).__init__()


class NextCloudLoginFlowTimeout(NextCloudAsyncException):
    """When the login flow times out."""
