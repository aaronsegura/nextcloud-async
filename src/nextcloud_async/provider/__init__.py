from typing import Any, Protocol


class HttpClientBasicAuth(Protocol):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    @property
    def user(self) -> str:
        """Return User from BasicAuth."""
        ...


class HttpClientResponse(Protocol):
    def __init__(self, response: Any) -> None: ...

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
        json: dict[str, Any] | None = None,
        content: bytes | None = None,
    ) -> Any:
        """Make an HTTP Request."""

    async def delete_cookie(self, cookie: str) -> None:
        """Delete a cookie."""


class HttpClientException(BaseException): ...
