"""
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html
"""

import xmltodict
import json

from typing import Dict, Any, Optional, List

from nextcloud_aio.api import NextCloudBaseAPI
from nextcloud_aio.exceptions import NextCloudASyncException


class NextCloudOCSAPI(NextCloudBaseAPI):

    __capabilities = None

    async def ocs_query(
            self,
            method: str,
            url: str = None,
            sub: str = '',
            data: Dict[Any, Any] = {},
            headers: Dict[Any, Any] = {},
            include_headers: Optional[List] = []) -> Dict:

        headers.update({'OCS-APIRequest': 'true'})

        response = await self.request(
            method, url=url, sub=sub, data=data, headers=headers)

        if response.content:
            response_data = json.loads(
                json.dumps(
                    xmltodict.parse(response.content.decode('utf-8'))
                )
            )
            ocs_meta = response_data['ocs']['meta']
            if ocs_meta['status'] != 'ok':
                raise NextCloudASyncException(
                    f'{ocs_meta["statuscode"]}: {ocs_meta["message"]}')
            else:
                ret = response_data['ocs']['data']
                for header in include_headers:
                    ret.setdefault('response_headers', {})\
                        .setdefault(header, response.headers.get(header, None))
                return ret

        else:
            return None

    async def get_capabilities(self, slice: Optional[str] = '') -> Dict:
        """Get and cache capabilities for this server."""
        if not self.__capabilities:
            self.__capabilities = await self.ocs_query(
                method='GET',
                sub=r'/ocs/v1.php/cloud/capabilities')
        ret = self.__capabilities

        for item in slice.split('.'):
            ret = ret[item] if item else ret

        return ret

    async def get_file_guest_link(self, file_id: int) -> str:
        """
        Generate a generic sharable link for a file.
        Expires in 8 hours.

        Returns: (str) link to file
        """
        result = await self.ocs_query(
            method='POST',
            sub=r'/ocs/v2.php/apps/dav/api/v1/direct',
            data={'fileId': file_id})
        return result['url']

    async def get_notifications(self):
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v2.php/apps/notifications/api/v2/notifications')

    async def get_activity(
            self,
            since: Optional[int] = 0,
            filter_object: Optional[str] = None,
            filter_object_type: Optional[str] = None,
            sort: Optional[str] = 'desc',
            limit: Optional[int] = 50,
            offset: Optional[int] = 0):
        """Get user's activity."""
        data = {}
        filter = ''
        if filter_object and filter_object_type:
            filter = '/filter'
            data.update({
                'object_type': filter_object_type,
                'object_id': filter_object})
        elif filter_object or filter_object_type:
            raise NextCloudASyncException('Filter must have object_type and object_id')

        data['limit'] = limit
        data['sort'] = sort
        data['since'] = since

        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v2.php/apps/activity/api/v2/activity{filter}',
            data=data)
