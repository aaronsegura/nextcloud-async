"""Request Wrapper for Nextcloud OCS APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html
"""

import json
import httpx

from urllib.parse import urlencode

from typing import Dict, Any, Optional, List

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudHttpApi, NextcloudCapabilities
from nextcloud_async.exceptions import NextcloudException

from nextcloud_async.exceptions import NextcloudRequestTimeout


class NextcloudOcsApi(NextcloudHttpApi):
    """Nextcloud OCS API.

    All OCS queries must have an {'OCS-APIRequest': 'true'} header. Additionally, we
    request all data to be returned to us in json format.
    """
    __capabilities: Dict[str, Any] = {}

    def __init__(
            self,
            client: NextcloudClient,
            ocs_version: Optional[str] = '1',
            ocs_stub: Optional[str] = None):
        super().__init__(client)
        if ocs_stub:
            self.stub = ocs_stub
        else:
            self.stub = f'/ocs/v{ocs_version}.php'
        self.capabilities_api = NextcloudCapabilities(client)

    async def request(
            self,
            method: str = 'GET',
            path: str = '',
            data: Optional[Dict[str, Any]] = {},
            headers: Optional[Dict[str, Any]] = {},
            return_full_response: bool = False) -> Dict[str, Any] | List[Dict[str, Any]]:
        """Submit OCS-type query to cloud endpoint.

        Args
        ----
            method (str): HTTP Method (eg, `GET`, `POST`, etc...)

            url (str, optional): Use a URL outside of the given endpoint. Defaults to None.

            path (str, optional): The portion of the URL after the host. Defaults to ''.

            data (Dict, optional): Data for submission.  Data for GET requests is translated by
            urlencode and tacked on to the end of the URL as arguments. Defaults to {}.

            headers (Dict, optional): Headers for submission. Defaults to {}.

            return_full_response (bool): Return full OCS response with metadata.  Defaults to False


        Raises
        ------
            304 - NextcloudNotModified

            400 - NextcloudBadRequest

            401 - NextcloudUnauthorized

            403 - NextcloudForbidden

            403 - NextcloudDeviceWipeRequested

            404 - NextcloudNotFound

            408 - NextcloudRequestTimeout

            429 - NextcloudTooManyRequests


        Returns
        -------
            Dict: Response Data

            The OCS Endpoint returns metadata about the response in addition to the data
            what was requested.  The metadata is stripped after checking for request
            success, and only the data portion of the response is returned.

            >>> response = await self.ocs_query(path='/ocs/v1.php/cloud/capabilities')

            Dict, Dict: Response Data and Included Headers

            If ocs_query() is called with an `include_headers` argument, both response data
            and the requested headers are returned.

            >>> response, headers = await self.ocs_query(..., include_headers=['Some-Header'])

        Raises
        ------
            NextcloudException - when invalid response from server

        """
        if headers:
            headers.update({'OCS-APIRequest': 'true'})
        else:
            headers = {'OCS-APIRequest' : 'true'}

        if data:
            data.update({'format': 'json'})
        else:
            data = {'format': 'json'}

        if method.lower() == 'get':
            path = f'{path}?{urlencode(data, True)}'
            data = None

        try:
            # print(f"OCS {method} {self.client.endpoint}{self.stub}{path}")
            response = await self.client.http_client.request(
                method,
                auth=(self.client.user, self.client.password),
                url=f'{self.client.endpoint}{self.stub}{path}',
                json=data,
                headers=headers)
        except httpx.ReadTimeout:
            raise NextcloudRequestTimeout()

        await self.raise_response_exception(response)

        if response.content:
            try:
                response_content = json.loads(response.content.decode('utf-8'))
            except json.JSONDecodeError:
                raise NextcloudException(status_code=500, reason='Error decoding JSON response.')
            ocs_meta = response_content['ocs']['meta']
            if ocs_meta['status'] != 'ok':
                raise NextcloudException(
                    status_code=ocs_meta['statuscode'],
                    reason=ocs_meta['message'])
            else:
                if return_full_response:
                    return response_content
                else:
                    return response_content['ocs']['data']
        else:
            raise NextcloudException(status_code=500, reason='Invalid response from server.')

    async def has_capability(self, capability: str) -> bool:
        return await self.capabilities_api.supported(capability)

    # TODO: Move this to another module

    # async def get_file_guest_link(self, file_id: int) -> str:
    #     """Generate a generic sharable link for a file.

    #     Link expires in 8 hours.

    #     https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html#direct-download

    #     Args
    #     ----
    #         file_id (int): File ID to generate link for

    #     Returns
    #     -------
    #         str: Link to file

    #     Raises
    #     ------
    #         NextcloudNotFound - file not found

    #     """

    #     result = await self.request(
    #         method='POST',
    #         path=r'/ocs/v2.php/apps/dav/api/v1/direct',
    #         data={'fileId': file_id})

    #     return result['url']


    # # TODO: Move this to another module
    # async def get_activity(
    #         self,
    #         since: Optional[int] = 0,
    #         object_id: Optional[str] = None,
    #         object_type: Optional[str] = None,
    #         sort: Optional[str] = 'desc',
    #         limit: Optional[int] = 50) -> Dict[str, Any]:
    #     """Get Recent activity for the current user.

    #     Args
    #     ----
    #         since (int optional): Only return ativity since activity with given ID. Defaults
    #         to 0.

    #         object_id (str optional): object_id filter. Defaults to None.

    #         object_type (str optional): object_type filter. Defaults to None.

    #         sort (str optional): Sort order; either `asc` or `desc`. Defaults to 'desc'.

    #         limit (int optional): How many results per request. Defaults to 50.

    #     Raises
    #     ------
    #         NextcloudException: When given invalid argument combination

    #     Returns
    #     -------
    #         Tuple(dict, dict): activity results and headers

    #     Raises
    #     ------
    #         NextcloudException - when Activities isn't installed.

    #     """
    #     await self.get_capabilities('activity.apiv2')

    #     data: Dict[str, Any] = {}
    #     filter = ''
    #     if object_id and object_type:
    #         filter = '/filter'
    #         data.update({
    #             'object_type': object_type,
    #             'object_id': object_id})
    #     elif object_id or object_type:
    #         raise NextcloudException(
    #             403,
    #             'filter_object_type and filter_object are both required.')

    #     data.update({
    #         'limit': limit,
    #         'sort': sort,
    #         'since': since})

    #     response = await self.request(
    #         method='GET',
    #         path=f'/ocs/v2.php/apps/activity/api/v2/activity{filter}',
    #         data=data,
    #         return_full_response=True)

    #     return response
