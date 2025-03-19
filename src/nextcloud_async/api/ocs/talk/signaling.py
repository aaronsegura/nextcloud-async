from typing import Any

from nextcloud_async.api import NextcloudModule
from nextcloud_async.driver import NextcloudTalkDriver


class InternalSignalingApi(NextcloudModule):
    """Internal Signaling API.

    https://nextcloud-talk.readthedocs.io/en/latest/internal-signaling/
    """

    def __init__(self, api: NextcloudTalkDriver, api_version: str = "3") -> None:
        self.stub = f"/apps/spreed/api/v{api_version}/signaling"
        self.api: NextcloudTalkDriver = api

    async def get_settings(self, room_token: str) -> dict[str, Any]:
        """Get signaling settings."""
        return await self._get(path="/settings", data={"token": room_token})
