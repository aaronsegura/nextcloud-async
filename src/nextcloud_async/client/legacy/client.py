import logging
import warnings
from dataclasses import dataclass
from typing import Any

from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.provider import HttpClientBasicAuth, HttpClientProvider
from nextcloud_async.version import USER_AGENT

log = logging.getLogger("nextcloud_async")


@dataclass
class _NextcloudApis:
    talk: NextcloudModule


class NextCloudAsync:
    _apis: _NextcloudApis

    def __init__(
        self,
        endpoint: str,
        http_client: HttpClientProvider,
        auth: HttpClientBasicAuth | None = None,
        app_token: str | None = None,
        user_agent: str = USER_AGENT,
    ) -> None:
        from nextcloud_async import NextcloudClient
        from nextcloud_async.api import (
            files_api,
            maps_api,
            sharees_api,
            shares_api,
            talk_api,
        )

        self.client = NextcloudClient(endpoint, http_client, auth, app_token, user_agent)

        log.warning(
            "NextCloudAsync is deprecated and will be removed in the future.",
        )
        warnings.warn(
            "NextCloudAsync is deprecated and will be removed in the future.",
            DeprecationWarning,
            stacklevel=3,
        )

        self._apis = _NextcloudApis(talk_api(self.client))

    @property
    def apis(self) -> Any:
        """Access all the APIs."""
        return self._apis

    async def get_conversations(
        self, status_update: bool = False, include_status: bool = False
    ) -> list[dict[str, Any]]:
        """Return list of user's conversations.

        Args:
            status_update:
                Whether the "online" user status of the current user should be
                "kept-alive" (True) or not (False) (defaults to False)

            include_status:
                Whether the user status information of all one-to-one conversations should
                be loaded (default false)

        """
        conversations = await self.apis.talk.conversations.get_all(
            status_update, include_status
        )
        return [c.data for c in conversations]

    async def create_conversation(
        self, room_type: str, invite: str = "", room_name: str = "", source: str = ""
    ) -> dict[str, Any]:
        """Create a new conversation.

        Args:
            room_type:
                See ConversationType

            invite:
                user id (roomType = 1), group id (roomType = 2 - optional),
                circle id (roomType = 2, source = 'circles'], only available
                with circles-support capability))

            source:
                The source for the invite, only supported on roomType = 2 for
                groups and circles (only available with circles-support capability)

            room_name:
                Conversation name (Not available for roomType = 1)

        """
        from nextcloud_async.api import ConversationType

        new_room = await self.apis.talk.conversations.create(
            ConversationType[room_type], invite, room_name, source=source
        )
        return new_room.data

    async def get_conversation(self, room_token: str) -> dict[str, Any]:
        """Get a specific conversation.

        Args:
            room_token:
                Token for the room

        """
        room = await self.apis.talk.conversations.get(room_token)
        return room.data

    async def get_open_conversation_list(self) -> list[dict[str, Any]]:
        """Get list of open, joinable rooms.

        Returns:
            List of room dicts.

        """
        rooms = await self.apis.talk.conversations.list_open()
        return [r.data for r in rooms]

    # async def rename_conversation(self, token: str, new_name: str) -> dict[str, Any]:
    #     """Rename a conversation.

    #     Args:
    #         token:
    #             Room token

    #         new_name:
    #             The new room name

    #     Returns:
    #         Updated room information
    #     """
    #     # TODO: Come back here and finish this.
    #     await self.talk_api.rename(token, new_name)
