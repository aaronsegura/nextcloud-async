"""
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
"""

import xmltodict
import json

from typing import Dict, Any

from nextcloud_async.exceptions import NextCloudException

from nextcloud_async.api import NextCloudBaseAPI


class NextCloudDAVAPI(NextCloudBaseAPI):
    """Interace with Nextcloud DAV interface for file operations."""

    async def dav_query(
            self,
            method: str,
            url: str = None,
            sub: str = '',
            data: Dict[str, Any] = {},
            headers: Dict[str, Any] = {}) -> Dict:
        """Send a query to the Nextcloud DAV Endpoint.

        Args
        ----
            method (str): HTTP Method to use

            url (str, optional): URL, if outside of provided cloud. Defaults to None.

            sub (str, optional): The part after the URL. Defaults to ''.

            data (dict, optional): Data to submit. Defaults to {}.

            headers (dict, optional): Headers for submission. Defaults to {}.

        Raises
        ------
            NextCloudException: Server API Errors

        Returns
        -------
            Dict: Response content

        """
        response = await self.request(method, url=url, sub=sub, data=data, headers=headers)
        if response.content:
            response_data = json.loads(json.dumps(xmltodict.parse(response.content)))
            if 'd:error' in response_data:
                err = response_data['d:error']

                raise NextCloudException(
                    f'{err["s:exception"]}: {err["s:message"]}'.replace('\n', ''))

            return response_data['d:multistatus']['d:response']
        else:
            return None
