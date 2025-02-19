"""
    https://nextcloud-talk.readthedocs.io/en/latest/bot-management/
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from nextcloud_async.driver import NextcloudModule, NextcloudTalkApi


@dataclass
class Bot:
    data: Dict[str, Any]
    talk_api: NextcloudTalkApi

    def __post_init__(self):
        self.api = Bots(self.talk_api)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Talk Poll "{self.question}" from {self.actorId}>'

    def __repr__(self):
        return str(self)

    async def enable(self):
        await self.api.enable_bot(self.token, self.id)

    async def disable(self):
        await self.api.disable_bot(self.token, self.id)


class Bots(NextcloudModule):
    """Interact with Nextcloud Talk Bots API."""

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '1'):
        self.stub = f'/apps/spreed/api/v{api_version}/bot'
        self.api: NextcloudTalkApi = api

    async def _validate_capability(self) -> None:
            await self.api.require_talk_feature('bots-v1')

    async def list_installed(self) -> List[Bot]:
        await self._validate_capability()
        response, _ = await self._get(path='/admin')
        return [Bot(data, self.api) for data in response]

    async def list_conversation_bots(
            self,
            room_token: str) -> List[Bot]:
        await self._validate_capability()
        response, _ = await self._get(path=f'/{room_token}')
        return [Bot(data, self.api) for data in response]

    async def enable_bot(
            self,
            room_token: str,
            bot_id: int) -> None:
        await self._validate_capability()
        await self._post(path=f'/{room_token}/{bot_id}')

    async def disable_bot(
            self,
            room_token: str,
            bot_id: int) -> None:
        await self._validate_capability()
        await self._delete(path=f'/{room_token}/{bot_id}')