"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import httpx
import logging

from typing import Optional, Any, Dict

from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.client import NextcloudClient

from nextcloud_async.exceptions import NextcloudRequestTimeoutError

log = logging.getLogger("nextcloud_async.driver")


class NextcloudBaseApi(NextcloudHttpApi):
    """The Base API interface."""

    def __init__(self, client: NextcloudClient, api_stub: Optional[str] = None):
        super().__init__(client)
        if api_stub:
            self.stub = api_stub
        else:
            self.stub = "/index.php"

    def raise_response_exception(self, status_code: int, reason: str): ...

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

        Raises:
            304 - NextcloudNotModified

            400 - NextcloudBadRequest

            401 - NextcloudUnauthorized

            403 - NextcloudForbidden

            403 - NextcloudDeviceWipeRequested

            404 - NextcloudNotFound

            429 - NextcloudTooManyRequests

        Returns:
            httpx.Response: An httpx Response Object
        """
        if method.lower() == "get":
            path = self._munge_path_data(data, path)
            data = None

        headers = self._munge_headers(headers)
        auth = self._get_auth()

        try:
            log.debug(f"{method} {self.client.endpoint}{self.stub}{path} {data}")
            response = await self.client.http_client.request(
                method=method,
                auth=auth,
                url=f"{self.client.endpoint}{self.stub}{path}",
                json=data,
                headers=headers,
            )
            log.debug(f"Response: [{response.status_code}] {response.content}")

        except httpx.ReadTimeout:
            log.warning("Request timed out.")
            raise NextcloudRequestTimeoutError()

        await self._raise_response_exception(response.status_code, str(response.content))

        return response.json()

    def _get_auth(self) -> httpx.BasicAuth | None:
        if self.client.app_token:
            auth = None
        elif self.client.password:
            auth = httpx.BasicAuth(self.client.user, self.client.password)
        return auth

    def _munge_headers(self, headers: dict[str, Any] | None) -> dict[str, Any]:
        if headers:
            headers["User-Agent"] = self.client.user_agent
        else:
            headers = {"User-Agent": self.client.user_agent}

        if self.client.app_token:
            headers["Authorization"] = f"Bearer {self.client.app_token}"

        return headers
