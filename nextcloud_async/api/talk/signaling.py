from typing import Optional, Dict, Any

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule

class InternalSignaling(NextcloudModule):
    """Internal Signaling API.

    https://nextcloud-talk.readthedocs.io/en/latest/internal-signaling/
    """

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '3'):
        self.stub = f'/apps/spreed/api/v{api_version}/signaling'
        self.api: NextcloudTalkApi = api

    async def get_settings(self, room_token: str) -> Dict[str, Any]:
        return await self._get(path='/settings', data={'token': room_token})
