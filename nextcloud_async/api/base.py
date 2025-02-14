"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import httpx

from urllib.parse import urlencode
from typing import Optional, Any, Dict, Hashable

from .api import NextcloudHttpApi

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

    async def request(
            self,
            method: str = 'GET',
            url: Optional[str] = None,
            sub: Optional[str] = None,
            data: Optional[Dict[Hashable, Any]] = dict(),
            headers: Optional[Dict[Hashable, Any]] = {}) -> httpx.Response:
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
                sub = f'{sub}?{urlencode(data, True)}'
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
                url=f'{url}{sub}' if url else f'{self.endpoint}{sub}',
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
