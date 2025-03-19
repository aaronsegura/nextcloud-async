"""Nextcloud DAV Driver.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
"""

import logging
from typing import Any
from xml.parsers.expat import ExpatError

import httpx
import xmltodict

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudHttpDriver
from nextcloud_async.exceptions import NextcloudAsyncError, NextcloudRequestTimeoutError

log = logging.getLogger("nextcloud_async.driver")

_HTTP_USER_ERROR = 400


class NextcloudDavDriver(NextcloudHttpDriver):
    """Interace with Nextcloud DAV interface for file operations."""

    def __init__(self, client: NextcloudClient, api_stub: str | None = None) -> None:
        super().__init__(client)
        if api_stub:
            self.stub = api_stub
        else:
            self.stub = "/remote.php/dav"

    # TODO: DeprecationWarning: Use 'content=<...>' to upload raw bytes/text content.
    async def request(
        self,
        method: str = "GET",
        path: str = "",
        data: Any = {},
        headers: dict[str, Any] | None = None,
        content: bytes | None = None,
        raw_response: bool = False,
    ) -> dict[str, Any] | bytes:
        """Send a query to the Nextcloud DAV Endpoint.

        Args:
            method:
                HTTP Method to use

            path:
                The part after the url stub. Defaults to ''.

            data:
                Data to submit. Defaults to {}.

            headers:
                Headers for submission. Defaults to {}.

            content:
                Content to submit.  Use this when data is binary.

            raw_response:
                Do no xml -> json manipulation on returned data.  Return exactly what
                    is sent.

        Raises:
            NextcloudRequestTimeoutError: Request timeout

        Returns:
            Dict: Response content
            Bytstring: Raw response content if raw_response=True

        """
        headers = self._munge_headers(headers)
        if method.lower() == "get":
            path = self._path_args(data, path)
            data = None

        try:
            log.debug(f"{method} {self.client.endpoint}{self.stub}{path} :: {data}")
            response = await self.client.http_client.request(
                method,
                auth=self.client.auth,
                url=f"{self.client.endpoint}{self.stub}{path}",
                data=data,
                headers=headers,
                content=content,
            )
            log.debug(f"Response: [{response.status_code}] {response.content}")

        except httpx.ReadTimeout:
            log.warning("Request timed out.")
            raise NextcloudRequestTimeoutError()

        await self.raise_response_exception(response)

        if raw_response:
            return response.content

        if response.content:
            try:
                response_data = xmltodict.parse(response.content)
            except ExpatError as e:
                raise NextcloudAsyncError(
                    f"Unable to parse response: {str(e)} :: {response.content}"
                )
            return response_data["d:multistatus"]["d:response"]
        else:
            return {}

    async def raise_response_exception(self, response: httpx.Response) -> None:
        """Parse response and raises exception, if necessary.

        Args:
            response:
                Response from server

        """
        if response.status_code >= _HTTP_USER_ERROR:
            exception_data = xmltodict.parse(response.content)
            exception_message = exception_data["d:error"]["s:message"].replace("\t", " ")

            await self._raise_response_exception(response.status_code, exception_message)
