import json as _json
import logging
from typing import Any

import asyncio_atexit
from aiohttp import (
    BasicAuth,
    ClientConnectionError,
    ClientResponse,
    ClientSession,
    ClientTimeout,
    ServerConnectionError,
)

from . import (
    HttpClientBasicAuth,
    HttpClientException,
    HttpClientProvider,
    HttpClientResponse,
    HttpResponseMock,
)

log = logging.getLogger("nextcloud_async.provider")


class AioHttpResponseMock(HttpResponseMock):
    _response: bytes
    _status_code: int

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

    def json(self) -> Any:
        """Mock json."""
        return _json.loads(self._response.decode())

    def headers(self) -> Any:
        """Return mock headers."""
        return self._headers


class AioHttpResponse(HttpClientResponse):
    _content: bytes
    _response: ClientResponse

    def __init__(self, response: ClientResponse) -> None:
        log.debug("Response init")
        self._response = response

    async def pop_fields(self) -> None:
        """Populate the _content field.

        This **MUST** be called after request().
        """
        self._content = await self._response.read()

    @property
    def status_code(self) -> int:
        """Return status code of response."""
        return self._response.status

    @property
    def content(self) -> bytes:
        """Return the raw response content bytes."""
        return self._content

    @property
    def text(self) -> str:
        """Return the response in str format."""
        return self._content.decode()

    def json(self) -> Any:
        """Return the json response content."""
        return _json.loads(self.text)

    @property
    def headers(self) -> Any:
        """Return response headers."""
        return self._response.headers


class AioHttpBasicAuth(HttpClientBasicAuth):
    _auth: BasicAuth

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._auth = BasicAuth(*args, **kwargs)

    @property
    def user(self) -> str:
        """Return the user value."""
        return self._auth.login


class AioHttpClientProvider(HttpClientProvider):
    _client: ClientSession

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "timeout" in kwargs:
            timeout = ClientTimeout(total=kwargs["timeout"])
            kwargs.pop("timeout")
        else:
            timeout = ClientTimeout(total=30)

        log.debug("Starting aiohttp session.")
        self._client = ClientSession(*args, timeout=timeout or None, **kwargs)
        asyncio_atexit.register(self.close_session)

    async def close_session(self) -> None:
        """Close the open session."""
        log.debug("Closing session.")
        await self._client.close()

    async def request(
        self,
        method: str,
        url: str,
        headers: dict[str, Any] | None = None,
        auth: AioHttpBasicAuth | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        content: bytes | None = None,
    ) -> Any:
        """Make an HTTP Request."""
        try:
            if content:
                _r = await self._client.request(
                    method,
                    url=url,
                    auth=auth._auth if auth else None,
                    data=content,
                    headers=headers,
                )
            elif json:
                _r = await self._client.request(
                    method,
                    url=url,
                    auth=auth._auth if auth else None,
                    json=json,
                    headers=headers,
                )
            else:
                _r = await self._client.request(
                    method,
                    url=url,
                    auth=auth._auth if auth else None,
                    data=data,
                    headers=headers,
                )
        except (ClientConnectionError, ServerConnectionError) as e:
            raise HttpClientException(str(e))
        else:
            response = AioHttpResponse(_r)
            await response.pop_fields()
            return response

    @property
    def cookie_jar(self) -> Any:
        """Return cookies."""
        return self._client.cookie_jar

    def delete_cookie(self, endpoint: str, cookie: str) -> None:
        """Delete a cookie from the session."""
        from yarl import URL

        log.debug(f"Deleting cookie '{cookie}'")
        self.cookie_jar.update_cookies({cookie: ""}, response_url=URL(endpoint))
