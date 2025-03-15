"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import logging
from typing import Any, Dict, Optional

import httpx

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.exceptions import NextcloudRequestTimeoutError

log = logging.getLogger("nextcloud_async.driver")


class NextcloudBaseApi(NextcloudHttpApi):
    """The Base API interface."""

    def __init__(self, client: NextcloudClient, api_stub: Optional[str] = None) -> None:
        super().__init__(client)
        if api_stub:
            self.stub = api_stub
        else:
            self.stub = "/index.php"

    def raise_response_exception(self, status_code: int, reason: str) -> None:
        """No need to implement for this driver.

        Args:
            status_code:
                N/a

            reason:
                N/a
        """

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
            path = self._munge_path_data(data, path)
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
            headers.update(self.client.request_headers)

        return headers
