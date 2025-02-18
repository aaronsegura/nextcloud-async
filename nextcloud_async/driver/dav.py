"""
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
"""
import httpx
import xmltodict
import json

from typing import Dict, Any, Hashable, Optional, cast, ByteString

from nextcloud_async.driver import NextcloudHttpApi
from nextcloud_async.client import NextcloudClient
from nextcloud_async.exceptions import NextcloudException, NextcloudRequestTimeout


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
            headers: Optional[Dict[Hashable, Any]] = {},
            raw_response: bool = False) -> Dict[Hashable, Any] | ByteString:
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
            # print(f'DAV {method} {self.client.endpoint}{self.stub}{path}')
            response = await self.client.http_client.request(
                method,
                auth=(self.client.user, self.client.password),
                url=f'{self.client.endpoint}{self.stub}{path}',
                data=data,
                headers=cast(Dict[str, Any], headers))
        except httpx.ReadTimeout:
            raise NextcloudRequestTimeout()

        await self.raise_response_exception(response)

        if raw_response:
            ret: ByteString = response.content
            return ret

        if response.content:
            response_data = json.loads(json.dumps(xmltodict.parse(response.content)))
            if 'd:error' in response_data:
                err = response_data['d:error']

                raise NextcloudException(
                    status_code=408, reason=f'{err["s:exception"]}: {err["s:message"]}'.replace('\n', ''))

            return response_data['d:multistatus']['d:response']
        else:
            return {}

    async def raw_request(self, **kwargs) -> ByteString:  # type: ignore
        response = cast(ByteString, await self.request(**kwargs, raw_response=True))  # type: ignore
        return response