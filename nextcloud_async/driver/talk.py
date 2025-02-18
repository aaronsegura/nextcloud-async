"""Request Wrapper for Nextcloud OCS Talk APIs.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

import httpx

from urllib.parse import urlencode

from typing import Dict, Any, Optional, Hashable, List, Tuple

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudHttpApi

from nextcloud_async.exceptions import NextcloudRequestTimeout, NextcloudException


class NextcloudTalkApi(NextcloudHttpApi):
    """Nextcloud Talk OCS API.

    All OCS queries must have an {'OCS-APIRequest': 'true'} header. Additionally, we
    request all data to be returned to us in json format.
    """
    capabilities: List[str] = []

    def __init__(
            self,
            client: NextcloudClient,
            capabilities: Optional[List[str]] = [],
            ocs_version: Optional[str] = '2',
            stub: Optional[str] = None):
        if not capabilities:
            raise NextcloudException(status_code=400, reason='Cannot instantiate NextcloudTalkApi directly.  Use NextcloudTalkApi.create()')
        else:
            self.capabilities = capabilities
        super().__init__(client)
        if stub:
            self.stub = stub
        else:
            self.stub = f'/ocs/v{ocs_version}.php'

        self.ocs_version = ocs_version

    @classmethod
    async def init(
            cls,
            client: NextcloudClient,
            skip_capabilities: bool = False,
            ocs_version: Optional[str] = '1',
            stub: Optional[str] = None):
        capabilities: List[str] = []
        if not skip_capabilities:
            capabilities = await cls.get_capabilities(client)
        return cls(client, capabilities, ocs_version, stub)

    @classmethod
    async def get_capabilities(
            cls,
            client: NextcloudClient):
        response = await client.http_client.get(
            url=f'{client.endpoint}/ocs/v1.php/cloud/capabilities?format=json',
            auth=(client.user, client.password),
            headers={'OCS-APIRequest' : 'true'})
        return response.json()['ocs']['data']['capabilities']['spreed']['features']

    async def pop_capabilities(self):
        self.capabilities = await self.get_capabilities(self.client)

    def has_capability(self, capability: str) -> bool:
        if not self.capabilities:
            raise NextcloudException(
                status_code=404,
                reason='Talk API instantiated with `skip_capabilities`.  Run pop_capabilities().')

        return capability in self.capabilities

    async def request(
            self,
            method: str = 'GET',
            path: str = '',
            data: Optional[Dict[Hashable, Any]] = {},
            headers: Optional[Dict[Hashable, Any]] = {}) -> Tuple[Dict[Hashable, Any], httpx.Headers]:
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
        else:
            headers = {'OCS-APIRequest' : 'true',}

        if data:
            data.update({'format': 'json'})
        else:
            data = {'format': 'json'}

        if method.lower() == 'get':
            path = f'{path}?{urlencode(data, True)}'
            data = None

        try:
            # print(f"TALK {method} {self.client.endpoint}{self.stub}{path}")
            response = await self.client.http_client.request(
                method,
                auth=(self.client.user, self.client.password),
                url=f'{self.client.endpoint}{self.stub}{path}',
                data=data, # type: ignore
                headers=headers) # type: ignore
        except httpx.ReadTimeout:
            raise NextcloudRequestTimeout()

        await self.raise_response_exception(response)
        return response.json()['ocs']['data'], response.headers

