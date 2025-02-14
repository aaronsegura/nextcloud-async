"""
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
"""
import httpx
import xmltodict
import json

from typing import Dict, Any, Hashable, Optional, cast

from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.client import NextcloudClient

from nextcloud_async.exceptions import NextcloudException

from nextcloud_async.exceptions import (
    NextcloudBadRequest,
    NextcloudForbidden,
    NextcloudNotModified,
    NextcloudUnauthorized,
    NextcloudNotFound,
    NextcloudRequestTimeout,
    NextcloudTooManyRequests)


class NextcloudDavApi(NextcloudHttpApi):
    """Interace with Nextcloud DAV interface for file operations."""
    def __init__(
            self,
            client: NextcloudClient,
            api_stub: Optional[str] = None):
        super().__init__(client)
        if api_stub:
            self.stub = api_stub
        else:
            self.stub = '/remote.php/dav'

    async def request(
            self,
            method: str = 'GET',
            path: str = '',
            data: Any = {},
            headers: Optional[Dict[Hashable, Any]] = {}) -> Dict[Hashable, Any]:
        """Send a query to the Nextcloud DAV Endpoint.

        Args
        ----
            method (str): HTTP Method to use

            path (str, optional): The part after the url stub. Defaults to ''.

            data (dict, optional): Data to submit. Defaults to {}.

            headers (dict, optional): Headers for submission. Defaults to {}.

        Raises
        ------
            NextcloudException: Server API Errors

        Returns
        -------
            Dict: Response content

        """
        try:
            response = await self.client.request(
                method,
                url=f'{self.endpoint}{self.stub}{path}',
                data=data,
                headers=cast(Dict[str, Any], headers))
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

        if response.content:
            response_data = json.loads(json.dumps(xmltodict.parse(response.content)))
            if 'd:error' in response_data:
                err = response_data['d:error']

                raise NextcloudException(
                    status_code=408, reason=f'{err["s:exception"]}: {err["s:message"]}'.replace('\n', ''))

            return response_data['d:multistatus']['d:response']
        else:
            return {}
