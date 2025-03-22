"""Implement Nextcloud Remote Wiping functionality.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html

In order for this to work, you must be logged in using an app token.
See api.loginflow.LoginFlowV2.
"""

import logging

from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudBaseDriver
from nextcloud_async.exceptions import NextcloudNotFoundError
from nextcloud_async.provider import HttpClientResponse

log = logging.getLogger("nextcloud_async.wipe")


class WipeApi(NextcloudModule):
    """Interact with Nextcloud Remote Wipe API.

    Two simple functions: one to check if the user wants their data
    to be removed, one to notify the server upon removal of local
    user data.

    ````
    wipe_status = await get_wipe_status()
    if wipe_status:
        os.remove('.appdatata')  # for example
        await notify_wipe_status()

    ````

    """

    def __init__(self, base_driver: NextcloudBaseDriver) -> None:
        self.driver = base_driver
        self.stub = "/core/wipe"

    async def check(self) -> bool:
        """Check for remote wipe flag.

        Returns:
            bool: Whether user has flagged this device for remote wiping.

        """
        if not self.driver.client.app_token:
            return False

        try:
            response = await self._post(
                path="/check",
                data={"token": self.driver.client.app_token},
            )
        except NextcloudNotFoundError:
            return False

        if "wipe" in response:
            return response["wipe"]
        return False

    async def notify_wiped(self) -> HttpClientResponse:
        """Notify server that device has been wiped.

        Here we must use the direct client post method without authentication.

        Returns:
            Empty 200 Response

        """
        return await self.driver.client.http_client.request(
            method="POST",
            url=f"{self.driver.client.endpoint}{self.stub}/success",
            data={"token": self.driver.client.app_token},
        )


def wipe_api(client: NextcloudClient) -> WipeApi:
    """WipeApi Factory."""
    base_driver = NextcloudBaseDriver(client)
    return WipeApi(base_driver)
