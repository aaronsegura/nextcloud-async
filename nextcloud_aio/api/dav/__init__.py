"""
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
"""

import xmltodict
import json

from typing import Dict

from nextcloud_aio.exceptions import NextCloudAsyncException

from nextcloud_aio.api import NextCloudBaseAPI


class NextCloudDAVAPI(NextCloudBaseAPI):

    async def dav_query(
            self,
            method: str,
            url: str = None,
            sub: str = '',
            data: Dict[str, object] = {},
            headers: Dict[str, object] = {}) -> Dict:

        response = await self.request(method, url=url, sub=sub, data=data, headers=headers)
        if response.content:
            response_data = json.loads(json.dumps(xmltodict.parse(response.content)))
            if 'd:error' in response_data:
                err = response_data['d:error']

                raise NextCloudAsyncException(
                    f'{err["s:exception"]}: {err["s:message"]}'.replace('\n', ''))

            return response_data['d:multistatus']['d:response']
        else:
            return None
