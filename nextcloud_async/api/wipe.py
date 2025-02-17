"""Implement Nextcloud Remote Wiping functionality.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html

In order for this to work, you must be logged in using an app token.
See api.loginflow.LoginFlowV2.
"""

import json
import httpx

from nextcloud_async.driver import NextcloudModule, NextcloudBaseApi
from nextcloud_async.client import NextcloudClient
from nextcloud_async.exceptions import NextcloudBadRequest, NextcloudNotFound

class Wipe(NextcloudModule):
    """Interact with Nextcloud Remote Wipe API.

    Two simple functions: one to check if the user wants their data
    to be removed, one to notify the server upon removal of local
    user data.

        wipe_status = await get_wipe_status()
        if wipe_status:
            os.remove('.appdatata')  # for example
            await notify_wipe_status()
    """
    def __init__(
            self,
            client: NextcloudClient):
        self.api = NextcloudBaseApi(client)
        self.stub = '/index.php/core/wipe'

    async def check(self) -> bool:
        """Check for remote wipe flag.

        Returns
        -------
            bool: Whether user has flagged this device for remote wiping.

        """
        #Here we must use the direct httpx.post method without authentication.
        try:
            response = await self.api.client.http_client.post(
                url=f'{self.api.client.endpoint}{self.stub}/check',
                data={'token': self.api.client.password})
        except NextcloudNotFound:
            return False

        try:
            result = response.json()
        except json.decoder.JSONDecodeError:
            raise NextcloudBadRequest

        if 'wipe' in result:
            return result['wipe']
        return False

    async def notify_wiped(self) -> httpx.Response:
        """Notify server that device has been wiped.

        Here we must use the direct httpx.post method without authentication.

        Returns
        -------
            Empty 200 Response

        """
        return await self.api.client.http_client.post(
            url=f'{self.api.client.endpoint}{self.stub}/success',
            data={'token': self.api.client.password})
