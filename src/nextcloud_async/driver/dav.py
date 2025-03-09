"""https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html"""

import httpx
import xmltodict

from typing import Dict, Any, Optional, cast, ByteString

from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.client import NextcloudClient
from nextcloud_async.exceptions import (
    NextcloudError,
    NextcloudRequestTimeoutError,
)


class NextcloudDavApi(NextcloudHttpApi):
    """Interace with Nextcloud DAV interface for file operations."""

    def __init__(self, client: NextcloudClient, api_stub: Optional[str] = None):
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
        if headers:
            headers["User-Agent"] = self.client.user_agent
        else:
            headers = {"User-Agent": self.client.user_agent}

        if method.lower() == "get":
            path = self._massage_get_data(data, path)
            data = None

        # TODO: DeprecationWarning: Use 'content=<...>' to upload raw bytes/text content.
        try:
            print(f"DAV {method} {self.client.endpoint}{self.stub}{path}")
            response = await self.client.http_client.request(
                method,
                auth=httpx.BasicAuth(self.client.user, self.client.password),
                url=f"{self.client.endpoint}{self.stub}{path}",
                data=data,
                headers=headers,
            )

        except httpx.ReadTimeout:
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
            exception_message = exception_data["d:error"]["s:message"].replace(
                "\t", " "
            )

            await self._raise_response_exception(
                response.status_code, exception_message
            )

            raise NextcloudError(
                status_code=response.status_code, reason=exception_message
            )
