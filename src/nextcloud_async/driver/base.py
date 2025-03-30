"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import json
import logging
from typing import Any

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver.http import NextcloudHttpDriver
from nextcloud_async.exceptions import NextcloudAsyncError
from nextcloud_async.provider import HttpClientException, HttpClientResponse

log = logging.getLogger("nextcloud_async.driver")


class NextcloudBaseDriver(NextcloudHttpDriver):
    """The Base API interface."""

    def __init__(self, client: NextcloudClient, api_stub: str | None = None) -> None:
        super().__init__(client)
        if api_stub:
            self.stub = api_stub
        else:
            self.stub = "/index.php"

    async def raise_response_exception(self, response: HttpClientResponse) -> None:
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
        data: dict[str, Any] | None = None,
        content: bytes | None = None,
        headers: dict[str, Any] | None = None,
        json: Any | None = None,
        raw_response: bool = False,
    ) -> dict[str, Any] | HttpClientResponse:
        """Send a request to the Nextcloud endpoint.

        Only one of json/data/content may be used.

        Args:
            method:
                HTTP Method. Defaults to 'GET'.

            path:
                The part after the host. Defaults to ''.

            data:
                Data for submission. Defaults to {}.

            headers:
                Headers for submission. Defaults to {}.

            json:
                Json data passthrough.

            content:
                Raw bytes to pass through

            raw_response:
                Return the HttpClientResponse object

        Returns:
            dict[str, Any]: Dictionary of reponse data

        """
        if method.lower() == "get":
            path = self._path_args(data, path)
            data = None

        headers = self._munge_headers(headers)
        json, data = self._munge_json_data(json, data)

        if json and method.lower() == "get":
            path = self._path_args(json, path)
            json = None

        if data and method.lower() == "get":
            path = self._path_args(data, path)
            data = None

        try:
            log.debug(f"{method} {self.client.endpoint}{self.stub}{path} {data}")
            response = await self.client.http_client.request(
                method=method,
                auth=self.client.auth if self.client.auth else None,
                url=f"{self.client.endpoint}{self.stub}{path}",
                headers=headers,
                data=data,
                content=content,
                json=json,
            )
            log.debug(f"Response: [{response.status_code}] {response.content}")

        except HttpClientException as e:
            log.critical(str(e))
            raise

        await self.raise_response_exception(response)

        if raw_response:
            return response
        else:
            return response.json()
