"""Request Wrapper for Nextcloud OCS Talk APIs.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

import httpx

from typing import Dict, Any, Optional, Tuple

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudHttpApi, NextcloudCapabilities

from nextcloud_async.exceptions import NextcloudRequestTimeout, NextcloudNotCapable


class NextcloudTalkApi(NextcloudHttpApi):
    """Nextcloud Talk OCS API.

    All OCS queries must have an {'OCS-APIRequest': 'true'} header. Additionally, we
    request all data to be returned to us in json format.
    """

    def __init__(
            self,
            client: NextcloudClient,
            ocs_version: Optional[str] = '2',
            stub: Optional[str] = None):

        if stub:
            self.stub = stub
        else:
            self.stub = f'/ocs/v{ocs_version}.php'

        self.ocs_version = ocs_version
        self.capabilities_api = NextcloudCapabilities(client)

        super().__init__(client)

    async def has_talk_feature(self, capability: str) -> bool:
        features = await self.capabilities_api.supported('.'.join(['spreed.features', capability]))
        local_features = await self.capabilities_api.supported('.'.join(['spreed.features-local', capability]))
        return features or local_features

    has_talk_capability = has_talk_feature

    async def require_talk_feature(self, capability: str) -> None:
        if not self.has_talk_feature(capability):
            raise NextcloudNotCapable()

    require_talk_capability = require_talk_feature

    async def request(
            self,
            method: str = 'GET',
            path: str = '',
            data: Optional[Dict[str, Any]] = {},
            headers: Optional[Dict[str, Any]] = {}) -> Tuple[Dict[str, Any], httpx.Headers]:
        """Submit OCS-type query to cloud endpoint.

        Args
        ----
            method (str): HTTP Method (eg, `GET`, `POST`, etc...)

            url (str, optional): Use a URL outside of the given endpoint. Defaults to None.

            path (str, optional): The portion of the URL after the host. Defaults to ''.

            data (Dict, optional): Data for submission.  Data for GET requests is translated by
            urlencode and tacked on to the end of the URL as arguments. Defaults to {}.

            headers (Dict, optional): Headers for submission. Defaults to {}.


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
            Tuple[Dict, Dict]: Response Data and headers


        Raises
        ------
            NextcloudException - when invalid response from server
        """
        if headers:
            headers.update({'OCS-APIRequest': 'true'})
            headers['User-Agent'] = self.client.user_agent
        else:
            headers = {
                'OCS-APIRequest': 'true',
                'User-Agent': self.client.user_agent}

        if data:
            data.update({'format': 'json'})
        else:
            data = {'format': 'json'}

        if method.lower() == 'get':
            path = self._massage_get_data(data, path)
            data = None

        try:
            # print(f"TALK {method} {self.client.endpoint}{self.stub}{path}", data)
            response = await self.client.http_client.request(
                method,
                auth=(self.client.user, self.client.password),
                url=f'{self.client.endpoint}{self.stub}{path}',
                json=data,
                headers=headers)
        except httpx.ReadTimeout:
            raise NextcloudRequestTimeout()

        await self.raise_response_exception(response)
        return response.json()['ocs']['data'], response.headers

