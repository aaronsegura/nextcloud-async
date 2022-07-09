"""Implement Nextcloud Remote Wiping functionality.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html

In order for this to work, you must be logged in using an app token.
See api.loginflow.LoginFlowV2.
"""

import json


class Wipe(object):
    """Interact with Nextcloud Remote Wipe API.

    Two simple functions: one to check if the user wants their data
    to be removed, one to notify the server upon removal of local
    user data.

        wipe_status = await get_wipe_status()
        if wipe_status:
            os.remove('.appdatata')  # for example
            await notify_wipe_status()
    """

    endpoint = None
    password = None

    async def get_wipe_status(self) -> bool:
        """Check for remote wipe flag.

        Returns
        -------
            bool: Whether user has flagged this device for remote wiping.

        """
        response = await self.request(
            method='POST',
            url=f'{self.endpoint}/index.php/core/wipe/check',
            data={'token': self.password})

        try:
            result = response.json()
        except json.decoder.JSONDecodeError:
            return False

        if 'wipe' in result:
            return result['wipe']
        return False

    async def notify_wipe_status(self):
        """Notify server that device has been wiped.

        Returns
        -------
            Empty 200 Response

        """
        return await self.request(
            method='POST',
            url=f'{self.endpoint}/index.php/core/wipe/success',
            data={'token': self.password})
