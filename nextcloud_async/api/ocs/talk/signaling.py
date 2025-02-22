from typing import Dict, Any

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule

class InternalSignaling(NextcloudModule):
    """Internal Signaling API.

    https://nextcloud-talk.readthedocs.io/en/latest/internal-signaling/
    """

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '3') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}/signaling'
        self.api: NextcloudTalkApi = api

    async def get_settings(self, room_token: str) -> Dict[str, Any]:
        """Get signaling settings."""
        return await self._get(path='/settings', data={'token': room_token})
