"""Nextcloud Talk Calls API.

https://nextcloud-talk.readthedocs.io/en/latest/call/
"""
from typing import List

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule

from .constants import ParticipantInCallFlags
from .types import ParticipantData

class Calls(NextcloudModule):
    """Interact with Nextcloud Talk API."""

    api: NextcloudTalkApi

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '4') -> None:

        self.stub = f'/apps/spreed/api/v{api_version}/call'
        self.api = api

    async def get_connected_participants(self, room_token: str) -> List[ParticipantData]:
        """Get list of connected participants.

        Args:
            room_token:
                Token of conversation

        Returns:
            List of ParticipantData
        """
        response = await self._get(path=f'/{room_token}')
        return response

    async def join_call(
            self,
            room_token: str,
            flags: ParticipantInCallFlags,
            silent: bool,
            recording_consent: bool) -> None:
        """Join a call.

        Args:
            room_token:
                Token of conversation

            flags:
                ParticipantInCallFlags

            silent:
                Disable start call notifications for group/public calls

            recording_consent:
                When the user ticked a checkbox and agreed with being recorded (Only
                needed when the config => call => recording-consent capability is set
                to 1 or the capability is 2 and the conversation recordingConsent value
                is 1)
        """
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
        """Send call notification.

        Requires capability: send-call-notification

        Args:
            room_token:
                Token of Conversation

            user_id:
                Participant to notify.
        """
        await self.api.require_talk_feature('send-call-notification')
        await self._post(
            path=f'/{room_token}/ring/{user_id}',
            data={'attendeeId': user_id})

    async def send_sip_dialout_request(
            self,
            room_token: str,
            user_id: str) -> None:
        """Send SIP dial-out request.

        Requires capability: sip-support-dialout

        Args:
            room_token:
                Token of Conversation

            user_id:
                The participant to call
        """
        await self.api.require_talk_feature('sip-support-dialout')
        await self._post(
            path=f'/{room_token}/dialout/{user_id}',
            data={'attendeeId': user_id})

    async def update_flags(
            self,
            room_token: str,
            flags: ParticipantInCallFlags) -> None:
        """Update call flags.

        Args:
            room_token:
                Token of conversation

            flags:
                ParticipantInCallFlags
        """
        await self._put(
            path=f'/{room_token}',
            data={'flags': flags.value})

    async def leave(self, room_token: str, end_for_all: bool = False) -> None:
        """Leave a call (but staying in the conversation for future calls and chat).

        Args:
            room_token:
                Token of conversation

            end_for_all:
                If sent as a moderator, end the meeting and all participants leave the
                call.
        """
        await self._delete(
            path=f'/{room_token}',
            data={'all': end_for_all})
