from typing import Any

from httpx import AsyncClient, BasicAuth, RequestError, Response

from . import (
    HttpClientBasicAuth,
    HttpClientException,
    HttpClientProvider,
    HttpClientResponse,
)


class HttpXResponse(HttpClientResponse):
    def __init__(self, response: Response) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        """Return response HTTP status code."""
        return self._response.status_code

    @property
    def content(self) -> bytes:
        """Return response content in bytes."""
        return self._response.content

    @property
    def text(self) -> str:
        """Return response content as a string."""
        return self._response.text

    def json(self) -> dict[str, Any]:
        """Return response content json-parsed."""
        return self._response.json()

    @property
    def headers(self) -> Any:
        """Return respons headers."""
        return self._response.headers


class HttpXBasicAuth(HttpClientBasicAuth):
    _auth: BasicAuth

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._auth = BasicAuth(*args, **kwargs)

    @property
    def user(self) -> str:
        """Return the user value."""
        from base64 import b64decode

        auth_header = self._auth._auth_header.split(" ")[1]
        user, _ = b64decode(auth_header).decode().split(":")
        return user


class HttpXClientProvider(HttpClientProvider):
    _client: AsyncClient

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._client = AsyncClient(*args, **kwargs)

    async def request(
        self,
        method: str,
        url: str,
        headers: dict[str, Any] | None = None,
        auth: HttpXBasicAuth | None = None,
        data: dict[str, Any] | None = None,
        content: bytes | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Make an HTTP Request."""
        try:
            _r = await self._client.request(
                method,
                url=url,
                auth=auth._auth,
                data=data,
                headers=headers,
                content=content,
                json=json,
            )
        except RequestError as e:
            raise HttpClientException(str(e))
        else:
            return HttpXResponse(_r)

    async def delete_cookie(self, cookie: str) -> None:
        """Delete a cookie from the session."""
        self._client.cookies.delete(cookie)
