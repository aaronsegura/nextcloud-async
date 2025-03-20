import json
import logging
from typing import Any

import asyncio_atexit
from aiohttp import (
    BasicAuth,
    ClientConnectionError,
    ClientResponse,
    ClientSession,
    ServerConnectionError,
)

from . import (
    HttpClientBasicAuth,
    HttpClientException,
    HttpClientProvider,
    HttpClientResponse,
)

log = logging.getLogger("nextcloud_async.provider")


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
        return json.loads(self.text)

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
        log.debug("Starting aiohttp session.")
        self._client = ClientSession(*args, **kwargs)
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
        content: bytes | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Make an HTTP Request."""
        try:
            _r = await self._client.request(
                method,
                url=url,
                auth=auth._auth,
                data=data or content,
                headers=headers,
                json=json,
            )
        except (ClientConnectionError, ServerConnectionError) as e:
            raise HttpClientException(str(e))
        else:
            response = AioHttpResponse(_r)
            await response.pop_fields()
            return response

    async def delete_cookie(self, _: str) -> None:
        """Delete a cookie from the session."""
        self._client.cookie_jar.update_cookies({"oc_sessionPassphrase": ""})
