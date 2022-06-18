"""
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html
"""

import json


class Wipe(object):

    endpoint = None
    password = None

    async def get_wipe_status(self) -> bool:
        """Check for remote wipe flag."""
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
        """Notify server that device has been wiped."""
        return await self.request(
            method='POST',
            url=f'{self.endpoint}/index.php/core/wipe/success',
            data={'token': {self.password}})
