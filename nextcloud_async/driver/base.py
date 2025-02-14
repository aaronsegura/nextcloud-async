"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import httpx

from urllib.parse import urlencode
from typing import Optional, Any, Dict, Hashable

from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.client import NextcloudClient

from nextcloud_async.exceptions import (
    NextcloudBadRequest,
    NextcloudForbidden,
    NextcloudNotModified,
    NextcloudUnauthorized,
    NextcloudNotFound,
    NextcloudRequestTimeout,
    NextcloudTooManyRequests)


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
            data: Optional[Dict[Hashable, Any]] = dict(),
            headers: Optional[Dict[Hashable, Any]] = {}) -> httpx.Response:
        """Send a request to the Nextcloud endpoint.

        Args
        ----
            method (str, optional): HTTP Method. Defaults to 'GET'.

            path (str, optional): The part after the host. Defaults to ''.

            data (dict, optional): Data for submission. Defaults to {}.

            headers (dict, optional): Headers for submission. Defaults to {}.

        Raises
        ------

            304 - NextcloudNotModified

            400 - NextcloudBadRequest

            401 - NextcloudUnauthorized

            403 - NextcloudForbidden

            404 - NextcloudNotFound

            429 - NextcloudTooManyRequests

        Returns
        -------
            httpx.Response: An httpx Response Object

        """
        if method.lower() == 'get':
            if data:
                path = f'{path}?{urlencode(data, True)}'
            else:
                data = None

        if headers:
            headers['user-agent'] = self.user_agent
        else:
            headers = {'user-agent' : self.user_agent}

        try:
            response = await self.client.request(
                method=method,
                auth=(self.user, self.password),
                url=f'{self.endpoint}{self.stub}{path}',
                data=data,   # type: ignore
                headers=headers) # type: ignore

        except httpx.ReadTimeout:
            raise NextcloudRequestTimeout()

        match response.status_code:
            case 304:
                raise NextcloudNotModified()
            case 400:
                raise NextcloudBadRequest()
            case 401:
                raise NextcloudUnauthorized()
            case 403:
                raise NextcloudForbidden()
            case 404:
                raise NextcloudNotFound()
            case 429:
                raise NextcloudTooManyRequests()
            case _:
                pass

        return response
