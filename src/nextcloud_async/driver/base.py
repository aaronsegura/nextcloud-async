"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import json
import logging
from typing import Any, Dict, Optional

import httpx

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.exceptions import NextcloudAsyncError, NextcloudRequestTimeoutError

log = logging.getLogger("nextcloud_async.driver")

_HTTP_SERVER_ERROR = 500
_HTTP_USER_ERROR = 400


class NextcloudBaseApi(NextcloudHttpApi):
    """The Base API interface."""

    def __init__(self, client: NextcloudClient, api_stub: Optional[str] = None) -> None:
        super().__init__(client)
        if api_stub:
            self.stub = api_stub
        else:
            self.stub = "/index.php"

    async def raise_response_exception(self, response: httpx.Response) -> None:
        """Raise an exception, if necessary.

        Args:
            response:
                Response object from server.

        Raises:
            NextcloudAsyncError: When content is unintepretable.
        """
        if response.content:
            try:
                response.json()
            except json.JSONDecodeError as e:
                raise NextcloudAsyncError(reason=str(e))

        await self._raise_response_exception(response.status_code, response.text)

    async def request(
        self,
        method: str = "GET",
        path: str = "",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a request to the Nextcloud endpoint.

        Args:
            method (str, optional): HTTP Method. Defaults to 'GET'.

            path (str, optional): The part after the host. Defaults to ''.

            data (dict, optional): Data for submission. Defaults to {}.

            headers (dict, optional): Headers for submission. Defaults to {}.

        Returns:
            dict[str, Any]: Dictionary of reponse data
        """
        if method.lower() == "get":
            path = self._path_args(data, path)
            data = None

        headers = self._munge_headers(headers)

        try:
            log.debug(f"{method} {self.client.endpoint}{self.stub}{path} {data}")
            response = await self.client.http_client.request(
                method=method,
                auth=self.client.auth,
                url=f"{self.client.endpoint}{self.stub}{path}",
                json=data,
                headers=headers,
            )
            log.debug(f"Response: [{response.status_code}] {response.content}")

        except httpx.ReadTimeout:
            log.warning("Request timed out.")
            raise NextcloudRequestTimeoutError()

        await self.raise_response_exception(response)

        return response.json()
