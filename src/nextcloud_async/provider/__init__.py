import logging
from abc import ABC
from typing import Any, Protocol

log = logging.getLogger("nextcloud_async.provider")


class HttpResponseMock(ABC):
    _response: bytes
    _status_code: int

    def __init__(
        self,
        status_code: int,
        response: bytes | None = None,
        json: Any = None,
        headers: Any | None = None,
    ) -> None: ...

    @property
    def status_code(self) -> int:
        """Mock status code."""
        ...

    @property
    def content(self) -> bytes:
        """Mock content."""
        ...

    @property
    def text(self) -> str:
        """Mock text."""
        ...

    def json(self) -> Any:
        """Mock json."""
        ...

    def headers(self) -> Any:
        """Return mock headers."""
        ...


class HttpResponseMock(ABC):
    _response: bytes
    _status_code: int

    def __init__(
        self,
        status_code: int,
        response: bytes | None = None,
        json: Any = None,
        headers: Any | None = None,
    ) -> None: ...

    @property
    def status_code(self) -> int:
        """Mock status code."""
        ...

    @property
    def content(self) -> bytes:
        """Mock content."""
        ...

    @property
    def text(self) -> str:
        """Mock text."""
        ...

    def json(self) -> Any:
        """Mock json."""
        ...

    def headers(self) -> Any:
        """Return mock headers."""
        ...


class HttpClientBasicAuth(Protocol):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    @property
    def user(self) -> str:
        """Return User from BasicAuth."""
        ...


class HttpClientResponse(Protocol):
    def __init__(self, status_code: int, response: Any) -> None: ...

    @property
    def status_code(self) -> int:
        """Return response HTTP status code."""
        ...

    @property
    def content(self) -> bytes:
        """Return response content as bytes."""
        ...

    @property
    def text(self) -> str:
        """Return response content as a string."""
        ...

    @property
    def headers(self) -> dict[str, Any]:
        """Return response headers."""
        ...

    def json(self) -> dict[str, Any]:
        """Return json-parsed response content."""
        ...


class HttpClientProvider(Protocol):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    async def request(
        self,
        method: str,
        url: str,
        auth: HttpClientBasicAuth | None = None,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        content: bytes | None = None,
        json: Any | None = None,
        file: bytes | None = None,
    ) -> Any:
        """Make an HTTP Request."""

    def delete_cookie(self, endpoint: str, cookie: str) -> None:
        """Delete a cookie."""

    @property
    def cookie_jar(self) -> Any:
        """Return the cookies."""


class HttpClientException(BaseException):
    _reason: str

    def __init__(self, reason: str) -> None:
        self._reason = reason

    def __str__(self) -> str:
        return self._reason

    def __repr__(self) -> str:
        return str(self)
