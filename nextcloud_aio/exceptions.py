"""Our very own exception classes."""


class NextCloudASyncException(Exception):
    """Generic Exception"""


class NextCloudLoginFlowTimeout(NextCloudASyncException):
    """When the login flow times out."""
