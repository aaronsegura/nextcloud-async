"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import httpx

from urllib.parse import urlencode
from typing import Dict, Optional

from nextcloud_async.exceptions import (
    NextCloudBadRequest,
    NextCloudForbidden,
    NextCloudNotModified,
    NextCloudUnauthorized,
    NextCloudNotFound,
    NextCloudRequestTimeout)


class NextCloudBaseAPI(object):
    """The Base API interface."""

    def __init__(
            self,
            client: httpx.AsyncClient,
            endpoint: str,
            user: str = '',
            password: str = ''):  # noqa: D416
        """Set up the basis for endpoint interaction.

        Args
        ----
            client (httpx.AsyncClient): AsyncClient.  Only httpx supported, but others may
            work.

            endpoint (str): The nextcloud endpoint URL

            user (str, optional): User login. Defaults to ''.

            password (str, optional): User password. Defaults to ''.

        """
        self.user = user
        self.password = password
        self.endpoint = endpoint
        self.client = client

    async def request(
            self,
            method: str = 'GET',
            url: str = None,
            sub: str = '',
            data: Optional[Dict] = {},
            headers: Optional[Dict] = {}) -> httpx.Response:
        """Send a request to the Nextcloud endpoint.

        Args
        ----
            method (str, optional): HTTP Method. Defaults to 'GET'.

            url (str, optional): URL, if outside of cloud endpoint. Defaults to None.

            sub (str, optional): The part after the host. Defaults to ''.

            data (dict, optional): Data for submission. Defaults to {}.

            headers (dict, optional): Headers for submission. Defaults to {}.

        Raises
        ------
            304 - NextCloudNotModified

            400 - NextCloudBadRequest

            401 - NextCloudUnauthorized

            403 - NextCloudForbidden

            404 - NextCloudNotFound

        Returns
        -------
            httpx.Response: An httpx Response Object

        """
        if method.lower() == 'get':
            sub = f'{sub}?{urlencode(data, True)}'
            data = None

        try:
            response = await self.client.request(
                method=method,
                auth=(self.user, self.password),
                url=f'{url}{sub}' if url else f'{self.endpoint}{sub}',
                data=data,
                headers=headers)
        except httpx.ReadTimeout:
            raise NextCloudRequestTimeout()

        match response.status_code:
            case 304:
                raise NextCloudNotModified()
            case 400:
                raise NextCloudBadRequest()
            case 401:
                raise NextCloudUnauthorized()
            case 403:
                raise NextCloudForbidden()
            case 404:
                raise NextCloudNotFound()

        return response
