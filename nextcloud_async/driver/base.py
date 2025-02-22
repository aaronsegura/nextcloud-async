"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import httpx

from typing import Optional, Any, Dict

from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.client import NextcloudClient

from nextcloud_async.exceptions import NextcloudRequestTimeoutError

class NextcloudBaseApi(NextcloudHttpApi):
    """The Base API interface."""
    def __init__(
            self,
            client: NextcloudClient,
            api_stub: Optional[str] = None):
        super().__init__(client)
        if api_stub:
            self.stub = api_stub
        else:
            self.stub = '/index.php'

    async def request(
            self,
            method: str = 'GET',
            path: Optional[str] = None,
            data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a request to the Nextcloud endpoint.

        Args:
        ----
            method (str, optional): HTTP Method. Defaults to 'GET'.

            path (str, optional): The part after the host. Defaults to ''.

            data (dict, optional): Data for submission. Defaults to {}.

            headers (dict, optional): Headers for submission. Defaults to {}.

        Raises:
        ------
            304 - NextcloudNotModified

            400 - NextcloudBadRequest

            401 - NextcloudUnauthorized

            403 - NextcloudForbidden

            403 - NextcloudDeviceWipeRequested

            404 - NextcloudNotFound

            429 - NextcloudTooManyRequests

        Returns:
        -------
            httpx.Response: An httpx Response Object
        """
        if method.lower() == 'get':
            path = self._massage_get_data(data, path)
            data = None

        if headers:
            headers['User-Agent'] = self.client.user_agent
        else:
            headers = {'User-Agent': self.client.user_agent}

        try:
            print(f'BASE {method} {self.client.endpoint}{self.stub}{path}')
            response = await self.client.http_client.request(
                method=method,
                auth=(self.client.user, self.client.password),
                url=f'{self.client.endpoint}{self.stub}{path}',
                json=data,
                headers=headers)
        except httpx.ReadTimeout:
            raise NextcloudRequestTimeoutError()

        await self.raise_response_exception(response)

        return response.json()
