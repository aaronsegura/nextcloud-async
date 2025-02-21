"""Nextcloud Talk Bots API.

https://nextcloud-talk.readthedocs.io/en/latest/bot-management/
"""

from dataclasses import dataclass
from typing import List, Dict, Any

from nextcloud_async.driver import NextcloudModule, NextcloudTalkApi


@dataclass
class Bot:
    data: Dict[str, Any]
    talk_api: NextcloudTalkApi

    def __post_init__(self) -> None:
        self.api = Bots(self.talk_api)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<Talk Bot #{self.id}, {self.name}>'

    def __repr__(self) -> str:
        return str(self.data)

    async def enable(self, room_token: str) -> None:
        """Enable this bot."""
        await self.api.enable_bot(room_token=room_token, bot_id=self.id)

    async def disable(self, room_token: str) -> None:
        """Disable this bot."""
        await self.api.disable_bot(room_token=room_token, bot_id=self.id)


class Bots(NextcloudModule):
    """Interact with Nextcloud Talk Bots API.

    Requires capability: bots-v1
    """

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '1') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}/bot'
        self.api: NextcloudTalkApi = api

    async def _validate_capability(self) -> None:
            await self.api.require_talk_feature('bots-v1')

    async def list_installed(self) -> List[Bot]:
        """Get list of bots installed on the server.

        This is an administrator-only method.

        Returns:
            List of Bot objects
        """
        await self._validate_capability()
        response, _ = await self._get(path='/admin')
        return [Bot(data, self.api) for data in response]

    async def list_conversation_bots(
            self,
            room_token: str) -> List[Bot]:
        """Get list of bots for a conversation.

        This is a moderator-level method.

        Args:
            room_token:
                Token of conversation

        Returns:
            List of Bot objects
        """
        await self._validate_capability()
        response, _ = await self._get(path=f'/{room_token}')
        return [Bot(data, self.api) for data in response]

    async def enable_bot(
            self,
            room_token: str,
            bot_id: int) -> None:
        """Enable a bot for a conversation as a moderator.

        Args:
            room_token:
                Token for conversation

            bot_id:
                Bot ID
        """
        await self._validate_capability()
        await self._post(path=f'/{room_token}/{bot_id}')

    async def disable_bot(
            self,
            room_token: str,
            bot_id: int) -> None:
        """Disable a bot for a conversation as a moderator.

        Args:
            room_token:
                Token of conversation

            bot_id:
                _description_
        """
        await self._validate_capability()
        await self._delete(path=f'/{room_token}/{bot_id}')
