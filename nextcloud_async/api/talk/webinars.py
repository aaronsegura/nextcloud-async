import datetime as dt

from nextcloud_async.driver import NextcloudModule, NextcloudTalkApi

from typing import Optional

from .types import ConversationData
from .constants import WebinarLobbyState, SipState

class Webinars(NextcloudModule):
    """Nextcloud Talk Webinars API.

    https://nextcloud-talk.readthedocs.io/en/latest/webinar/
    """

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '4') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    async def set_lobby_state(
            self,
            room_token: str,
            lobby_state: WebinarLobbyState,
            reset_time: Optional[dt.datetime] = None) -> ConversationData:
        """Set lobby requirement for Conversation.

        Args:
            room_token:
                Token of conversation

            lobby_state:
                WebinarLobbyState

            reset_time:
                Time at which to remove lobby requirement.

        Returns:
            Updated Conversation object.
        """
        await self.api.require_capability('webinary-lobby')
        response, _ = await self._put(
            path=f'/room/{room_token}/webinar/lobby',
            data={
                'state': lobby_state.name,
                'timer': reset_time.strftime('%s') if reset_time else 0})
        return response

    async def set_sip_dialin(
            self,
            room_token: str,
            state: SipState) -> ConversationData:
        """Enable or Disable SIP dialin for webinar.

        Args:
            room_token:
                Token of conversation.

            state:
                SipState

        Returns:
            Updated Conversation object
        """
        await self.api.require_capability('sip-support')
        response, _ = await self._put(
            path=f'/room/{room_token}/webinar/sip',
            data={'state': state.value})
        return response

