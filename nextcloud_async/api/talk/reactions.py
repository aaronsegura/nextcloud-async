"""
https://nextcloud-talk.readthedocs.io/en/latest/reaction/
"""

from typing import Optional

from nextcloud_async.driver import NextcloudModule, NextcloudTalkApi


class Reactions(NextcloudModule):
    """Interact with Nextcloud Talk API."""

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '1'):
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    async def add(self, room_token: str, message_id: int, reaction: str):
        await self.api.require_talk_feature('reactions')
        await self._post(
            path=f'/reaction/{room_token}/{message_id}',
            data={'reaction': reaction})

    async def delete(self, room_token: str, message_id: int, reaction: str):
        await self.api.require_talk_feature('reactions')
        await self._delete(
            path=f'/reaction/{room_token}/{message_id}',
            data={'reaction': reaction})
