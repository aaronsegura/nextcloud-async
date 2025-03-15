"""Nextcloud DAV Driver.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
"""

import logging
from typing import Any, ByteString, Dict, Optional, cast

import httpx
import xmltodict

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.exceptions import (
    NextcloudError,
    NextcloudRequestTimeoutError,
)

log = logging.getLogger("nextcloud_async.driver")

_HTTP_USER_ERROR = 400


class NextcloudDavApi(NextcloudHttpApi):
    """Interace with Nextcloud DAV interface for file operations."""

    def __init__(self, client: NextcloudClient, api_stub: Optional[str] = None) -> None:
        super().__init__(client)
        if api_stub:
            self.stub = api_stub
        else:
            self.stub = "/remote.php/dav"

    async def request(
        self,
        method: str = "GET",
        path: str = "",
        data: Any = {},
        headers: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Dict[str, Any] | ByteString:
        """Send a query to the Nextcloud DAV Endpoint.

        Args:
            method (str): HTTP Method to use

            path (str, optional): The part after the url stub. Defaults to ''.

            data (dict, optional): Data to submit. Defaults to {}.

            headers (dict, optional): Headers for submission. Defaults to {}.

        Raises:
            NextcloudException: Server API Errors

        Returns:
            Dict: Response content
        """
        headers = self._munge_headers(headers)

        if method.lower() == "get":
            path = self._munge_path_data(data, path)
            data = None

        # TODO: DeprecationWarning: Use 'content=<...>' to upload raw bytes/text content.
        try:
            log.debug(f"{method} {self.client.endpoint}{self.stub}{path} :: {data}")
            response = await self.client.http_client.request(
                method,
                auth=self.client.auth,
                url=f"{self.client.endpoint}{self.stub}{path}",
                data=data,
                headers=headers,
            )
            log.debug(f"Response: [{response.status_code}] {response.content}")

        except httpx.ReadTimeout:
            log.warning("Request timed out.")
            raise NextcloudRequestTimeoutError()

        await self.raise_response_exception(response)

        if raw_response:
            ret: ByteString = response.content
            return ret

        if response.content:
            response_data = xmltodict.parse(response.content)
            return response_data["d:multistatus"]["d:response"]
        else:
            return {}

    def _munge_headers(self, headers: dict[str, Any] | None) -> dict[str, Any]:
        if headers:
            headers["User-Agent"] = self.client.user_agent
        else:
            headers = {"User-Agent": self.client.user_agent}

        if self.client.request_headers:
            headers.update(self.client.request_headers)

        return headers

    async def raw_request(
        self,
        method: str = "GET",
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> ByteString:
        response = cast(
            ByteString,
            await self.request(
                method=method, path=path, data=data, headers=headers, raw_response=True
            ),
        )
        return response

    async def raise_response_exception(self, response: httpx.Response) -> None:
        if response.status_code >= 300:
            response_content = response.content
            exception_data = xmltodict.parse(response_content)
            exception_message = exception_data["d:error"]["s:message"].replace("\t", " ")

            await self._raise_response_exception(response.status_code, exception_message)

            raise NextcloudError(
                status_code=response.status_code, reason=exception_message
            )
