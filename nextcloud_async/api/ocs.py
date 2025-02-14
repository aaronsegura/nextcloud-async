"""Request Wrapper for Nextcloud OCS APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html
"""

import json
import httpx

from urllib.parse import urlencode

from typing import Dict, Any, Optional, List, Hashable, Tuple

from nextcloud_async.api.api import NextcloudHttpApi
from nextcloud_async.exceptions import NextcloudException

from nextcloud_async.exceptions import (
    NextcloudBadRequest,
    NextcloudForbidden,
    NextcloudNotModified,
    NextcloudUnauthorized,
    NextcloudNotFound,
    NextcloudRequestTimeout,
    NextcloudTooManyRequests)

class NextcloudOcsApi(NextcloudHttpApi):
    """Nextcloud OCS API.

    All OCS queries must have an {'OCS-APIRequest': 'true'} header. Additionally, we
    request all data to be returned to us in json format.
    """

    __capabilities: Dict[Hashable, Any] = {}

    async def request(
            self,
            method: str = 'GET',
            url: Optional[str] = None,
            sub: str = '',
            data: Optional[Dict[Hashable, Any]] = {},
            headers: Optional[Dict[Hashable, Any]] = {},
            return_full_response: bool = False) -> Dict[Hashable, Any]:
        """Submit OCS-type query to cloud endpoint.

        Args
        ----
            method (str): HTTP Method (eg, `GET`, `POST`, etc...)

            url (str, optional): Use a URL outside of the given endpoint. Defaults to None.

            sub (str, optional): The portion of the URL after the host. Defaults to ''.

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

            404 - NextcloudNotFound

            408 - NextcloudRequestTimeout

            429 - NextcloudTooManyRequests


        Returns
        -------
            Dict: Response Data

            The OCS Endpoint returns metadata about the response in addition to the data
            what was requested.  The metadata is stripped after checking for request
            success, and only the data portion of the response is returned.

            >>> response = await self.ocs_query(sub='/ocs/v1.php/cloud/capabilities')

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
            headers = {'OCS-APIRequest' : 'true',}

        if data:
            data.update({'format': 'json'})
        else:
            data = {'format': 'json'}

        if method.lower() == 'get':
            sub = f'{sub}?{urlencode(data, True)}'
            data = None

        try:
            response = await self.client.request(
                method,
                url=f'{url}{sub}' if url else f'{self.endpoint}{sub}',
                data=data, # type: ignore
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

    async def request_with_returned_headers(
            self,
            method: str = 'GET',
            url: Optional[str] = None,
            sub: str = '',
            data: Optional[Dict[Hashable, Any]] = {},
            headers: Optional[Dict[Hashable, Any]] = {},
            return_headers: Optional[List[str]] = []) -> Tuple[Dict[Hashable, Any], Dict[Hashable, Any]]:

        response_content = await self.request(
            method=method,
            url=url,
            sub=sub,
            data=data,
            headers=headers,
            return_full_response=True)

        response_headers: Dict[Hashable, Any] = {}

        ocs_meta = response_content['ocs']['meta']
        if ocs_meta['status'] != 'ok':
            raise NextcloudException(
                status_code=ocs_meta['statuscode'],
                reason=ocs_meta['message'])
        else:
            response_data = response_content['ocs']['data']
            if return_headers:
                for header in return_headers:
                    response_headers.setdefault(header, ocs_meta['headers'].get(header, None))
                return response_data, response_headers
            else:
                return response_data

    async def get_capabilities(self, capability: Optional[str] = None) -> Dict[Hashable, Any]:
        """Return capabilities for this server.

        Args
        ----
            slice (str optional): Only return specific portion of results. Defaults to ''.

        Raises
        ------
            NextcloudException(404) on capability mising
            NextcloudException(400) invalid capability string

        Returns
        -------
            Dict: Capabilities filtered by slice.

        """
        if not self.__capabilities:
            response = await self.request(
                method='GET',
                sub=r'/ocs/v1.php/cloud/capabilities')

            if isinstance(response, dict):
                self.__capabilities = response
            else:
                raise NextcloudNotFound

        ret = self.__capabilities

        if capability:
            if capability:
                for item in capability.split('.'):
                    if item in ret:
                        try:
                            ret = ret[item]
                        except TypeError:
                            raise NextcloudException(status_code=404, reason=f'Capability not found: {item}')
                    else:
                        raise NextcloudException(status_code=404, reason=f'Capability not found: {item}')
            else:
                raise NextcloudException(status_code=400, reason='`capability` must be a string.')

        return ret

    # TODO: Move this to another module

    async def get_file_guest_link(self, file_id: int) -> str:
        """Generate a generic sharable link for a file.

        Link expires in 8 hours.

        https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html#direct-download

        Args
        ----
            file_id (int): File ID to generate link for

        Returns
        -------
            str: Link to file

        Raises
        ------
            NextcloudNotFound - file not found

        """

        result = await self.request(
            method='POST',
            sub=r'/ocs/v2.php/apps/dav/api/v1/direct',
            data={'fileId': file_id})

        if isinstance(result, dict):
            return result['url']
        else:
            print(result)
            raise NextcloudNotFound

    # TODO: Move this to another module

    async def get_activity(
            self,
            since: Optional[int] = 0,
            object_id: Optional[str] = None,
            object_type: Optional[str] = None,
            sort: Optional[str] = 'desc',
            limit: Optional[int] = 50) -> Tuple[Dict[Hashable, Any], Dict[Hashable, Any]]:
        """Get Recent activity for the current user.

        Args
        ----
            since (int optional): Only return ativity since activity with given ID. Defaults
            to 0.

            object_id (str optional): object_id filter. Defaults to None.

            object_type (str optional): object_type filter. Defaults to None.

            sort (str optional): Sort order; either `asc` or `desc`. Defaults to 'desc'.

            limit (int optional): How many results per request. Defaults to 50.

        Raises
        ------
            NextcloudException: When given invalid argument combination

        Returns
        -------
            Tuple(dict, dict): activity results and headers

        Raises
        ------
            NextcloudException - when Activities isn't installed.

        """
        await self.get_capabilities('activity.apiv2')

        data: Dict[Hashable, Any] = {}
        filter = ''
        if object_id and object_type:
            filter = '/filter'
            data.update({
                'object_type': object_type,
                'object_id': object_id})
        elif object_id or object_type:
            raise NextcloudException(
                403,
                'filter_object_type and filter_object are both required.')

        data.update({
            'limit': limit,
            'sort': sort,
            'since': since})

        data, headers = await self.request_with_returned_headers(
            method='GET',
            sub=f'/ocs/v2.php/apps/activity/api/v2/activity{filter}',
            data=data,
            return_headers=['X-Activity-First-Known', 'X-Activity-Last-Given'])

        return data, headers
