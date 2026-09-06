import json as _json
import logging
from typing import Any

from httpx import AsyncClient, BasicAuth, RequestError, Response

from . import (
    HttpClientBasicAuth,
    HttpClientException,
    HttpClientProvider,
    HttpClientResponse,
    HttpResponseMock,
)

log = logging.getLogger("nextcloud_async.provider")


class HttpXResponseMock(HttpResponseMock):
    _status_code: int
    _response: bytes

    def __init__(
        self,
        status_code: int,
        response: bytes | None = None,
        json: Any = None,
        headers: Any | None = None,
    ) -> None:
        self._response = response if response else bytes(_json.dumps(json), "utf-8")
        self._status_code = status_code
        self._headers = headers

    @property
    def status_code(self) -> int:
        """Mock status code."""
        return self._status_code

    @property
    def content(self) -> bytes:
        """Mock content."""
        return self._response

    @property
    def text(self) -> str:
        """Mock text."""
        return self._response.decode()

    def json(self) -> dict[str, Any]:
        """Mock json."""
        return _json.loads(self._response.decode())

    def headers(self) -> Any:
        """Mock headers."""
        return self._headers


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
        """Return response headers."""
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
        json: Any | None = None,
        file: bytes | None = None,
    ) -> Any:
        """Make an HTTP Request."""
        try:
            if content:
                _r = await self._client.request(
                    method,
                    url=url,
                    auth=auth._auth if auth else None,
                    headers=headers,
                    content=content,
                )
            elif json:
                log.debug("Sending JSON request")
                _r = await self._client.request(
                    method,
                    url=url,
                    auth=auth._auth if auth else None,
                    headers=headers,
                    json=json,
                )
            elif file:
                log.debug(f"Sending file of size {len(file)}")
                _r = await self._client.request(
                    method,
                    url=url,
                    auth=auth._auth if auth else None,
                    headers=headers,
                    files={"file": file},
                    data={"format": "json"},
                )
            else:
                log.debug("Sending Data!")
                _r = await self._client.request(
                    method,
                    url=url,
                    auth=auth._auth if auth else None,
                    headers=headers,
                    data=data,
                )
        except RequestError as e:
            raise HttpClientException(repr(e))
        else:
            return HttpXResponse(_r)

    @property
    def cookie_jar(self) -> Any:
        """Return cookies."""
        self._client.cookies

    def delete_cookie(self, _: str, cookie: str) -> None:
        """Delete a cookie from the session."""
        self._client.cookies.delete(cookie)
