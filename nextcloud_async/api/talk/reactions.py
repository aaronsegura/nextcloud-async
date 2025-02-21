"""Nextcloud Talk Reactions API.

Requires capability: reactions

https://nextcloud-talk.readthedocs.io/en/latest/reaction/
"""
import datetime as dt
from dateutil.tz import tzlocal

from dataclasses import dataclass

from typing import Optional, Dict, Any, List

from nextcloud_async.driver import NextcloudModule, NextcloudTalkApi


@dataclass
class Reaction:
    data: Dict[str, Any]

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    @property
    def actor_type(self) -> str:
        """Alias for self.actorType.

        Returns:
            self.actorType
        """
        return self.actorType

    @property
    def actor_id(self) -> str:
        """Alias for self.actorId.

        Returns:
            self.actorId
        """
        return self.actorId

    @property
    def actor_display_name(self) -> str:
        """Alias for self.actorDisplayName.

        Returns:
            self.actorDisplayName
        """
        return self.actorDisplayName

    @property
    def timestamp(self) -> dt.datetime:
        """Returns timestamp as a datetime object.

        Returns:
            datetime of reaction
        """
        return dt.datetime.fromtimestamp(self.data['timestamp'], tz=tzlocal())


class Reactions(NextcloudModule):
    """Interact with Nextcloud Talk API."""

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '1') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}/reaction'
        self.api: NextcloudTalkApi = api

    async def add(
            self,
            room_token: str,
            message_id: int,
            reaction: str) -> List[Reaction]:
        """React to a message.

        Args:
            room_token:
                Token of conversation

            message_id:
                Message ID

            reaction:
                Reaction emoji

        Returns:
            List of reactions to message
        """
        await self.api.require_talk_feature('reactions')
        response, _ = await self._post(
            path=f'/{room_token}/{message_id}',
            data={'reaction': reaction})
        return [Reaction(data) for data in response]

    async def delete(
            self,
            room_token: str,
            message_id: int,
            reaction: str) -> List[Reaction]:
        """Delete a reaction.

        Args:
            room_token:
                Token of description

            message_id:
                Message ID

            reaction:
                Emoji reaction to delete

        Returns:
            List of reactions to message.
        """
        await self.api.require_talk_feature('reactions')
        response, _ = await self._delete(
            path=f'/{room_token}/{message_id}',
            data={'reaction': reaction})
        return [Reaction(data) for data in response]

    async def list(
            self,
            room_token: str,
            message_id: int,
            reaction: Optional[str]) -> List[Reaction]:
        """Retrieve reactions of a message by type.

        Args:
            room_token:
                Token of conversation

            message_id:
                Message ID

            reaction:
                If present, filters by this type of reaction

        Returns:
            List of Reaction
        """
        await self.api.require_talk_feature('reactions')
        response, _ = await self._get(
            path=f'/{room_token}/{message_id}',
            data={'reaction': reaction} if reaction else None)
        return [Reaction(data) for data in response]
