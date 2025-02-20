"""
    https://nextcloud-talk.readthedocs.io/en/latest/call/
"""
from typing import Optional, List

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule

from .participants import Participant
from .constants import ParticipantInCallFlags


class Calls(NextcloudModule):
    """Interact with Nextcloud Talk API."""

    api: NextcloudTalkApi

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '4'):

        self.stub = f'/apps/spreed/api/v{api_version}/call'
        self.api = api

    async def get_connected_participants(self, room_token: str) -> List[Participant]:
        response = await self._get(path=f'/{room_token}')
        return [Participant(data, self.api) for data in response]

    async def join_call(
            self,
            room_token: str,
            flags: ParticipantInCallFlags,
            silent: bool,
            recording_consent: bool):
        await self._post(
            path=f'/{room_token}',
            data={
                'flags': flags.value,
                'silent': silent,
                'recordingConsent': recording_consent})

    async def send_notification(
            self,
            room_token: str,
            user_id: str) -> None:
        await self.api.require_talk_feature('send-call-notification')
        await self._post(
            path=f'/{room_token}/ring/{user_id}',
            data={'attendeeId': user_id})

    async def send_sip_dialout_request(
            self,
            room_token: str,
            user_id: str) -> None:
        await self.api.require_talk_feature('sip-support-dialout')
        await self._post(
            path=f'/{room_token}/dialout/{user_id}',
            data={'attendeeId': user_id})

    async def update_flags(
            self,
            room_token: str,
            flags: ParticipantInCallFlags) -> None:
        await self._put(
            path=f'/{room_token}',
            data={'flags': flags.value})

    async def leave(self, room_token: str, end_for_all: bool = False):
        await self._delete(
            path=f'/{room_token}',
            data={'all': end_for_all})
