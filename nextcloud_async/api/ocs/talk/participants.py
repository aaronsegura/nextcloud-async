"""Nextcloud Talk Participants API.

https://nextcloud-talk.readthedocs.io/en/latest/participant/

"""
import httpx

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule
from nextcloud_async.helpers import phone_number_to_e164

from .types import ConversationData

from .constants import (
    ParticipantPermissions,
    SessionState,
    PermissionAction,
    ObjectSources)

@dataclass
class Participant:
    data: Dict[str, Any]
    api: NextcloudTalkApi

    def __post_init__(self) -> None:
        self.participants_api = Participants(self.api)

    def __str__(self) -> str:
        return f'<Participant, room: {self.data['roomToken']}, '\
               f'Id: {self.data['attendeeId']}>'

    def __repr__(self) -> str:
        return str(self.data)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    @property
    def id(self) -> int:
        """Alias for self.attendeeId.

        Returns:
            self.attendeeId
        """
        return self.data['attendeeId']

    @property
    def name(self) -> str:
        """Alias for self.actorId.

        Returns:
            self.actorId
        """
        return self.data['actorId']

    @property
    def room_token(self) -> str:
        """Alias for self.roomToken.

        Returns:
            self.roomToken
        """
        return self.data['roomToken']

    async def leave_conversation(self) -> None:
        """Leave the conversation."""
        await self.participants_api.leave(self.room_token)


class Participants(NextcloudModule):
    """Interact with Nextcloud Talk API."""

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '4') -> None:

        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    async def list(
            self,
            room_token: str,
            include_status: bool = False,
            include_breakout_rooms: bool = False) -> \
                Tuple[List[Participant], httpx.Headers]:
        """Return list of participants."""
        path = f'/room/{room_token}/participants'
        if include_breakout_rooms:
            await self.api.require_talk_feature('breakout-rooms-v1')
            path = f'/room/{room_token}/breakout-rooms/participants'

        response, headers = await self._get(
            path=path,
            data={'includeStatus': include_status})

        return [Participant(data, self.api) for data in response], headers

    async def add_to_conversation(
            self,
            room_token: str,
            invitee: str,
            source: ObjectSources = ObjectSources.user) -> None:
        """Add a participant to a conversation.

        Adding a participant to a breakout room will automatically add them to the parent
        room as well.

        Only ObjectSources.user can be added directly to a breakout room.

        Adding a participant to a breakout room, that is already a participant in another
        breakout room of the same parent will remove them from there.

        Args:
            room_token:
                Token of conversation.

            invitee:
                Name of object to invite

            source:
                ObjectSources : Type of object to invite.
        """
        await self._post(
            path=f'/room/{room_token}/participants',
            data={'newParticipant': invitee, 'source': source.value})

    async def remove_from_conversation(
            self,
            room_token: str,
            attendee_id: int) -> None:
        """Delete an attendee by id from a conversation.

        Args:
            room_token:
                Token of conversation.

            attendee_id:
                Attendee ID to remove.
        """
        await self._delete(
            path=f'/room/{room_token}/attendees',
            data={'attendeeId': attendee_id})

    async def set_state(self, room_token: str, state: SessionState) -> None:
        """Set session state.

        Args:
            room_token:
                Token of Conversation.

            state:
                SessionState
        """
        await self.api.require_talk_feature('session-state')
        await self._put(
            path=f'/room/{room_token}/participants/state',
            data={'state': state.value})

    async def leave(self, token: str) -> None:
        """Leave a conversation.

        Args:
            token:
                Token of conversation
        """
        await self._delete(path=f'/room/{token}/participants/self')

    async def join(
            self,
            room_token: str,
            password: Optional[str],
            force: bool = True) -> ConversationData:
        """Join a conversation.

        Args:
            room_token:
                Token of conversation

            password:
                Optional: Password is only required for users which are self joined or
                guests and only when the conversation has hasPassword set to true.

            force:
                If set to false and the user has an active session already a 409 Conflict
                will be returned (Default: true - to keep the old behaviour)

        Returns:
            ConversationData
        """
        response, _ = await self._post(
            path=f'/room/{room_token}/participants/active',
            data={
            'password': password,
            'force': force})
        return response

    async def resend_invitation_emails(
            self,
            room_token: str,
            participant_id: Optional[int] = None) -> None:
        """Resent invitaition emails.

        Requires capability: sip-support

        Args:
            room_token:
                Token of conversation.

            participant_id:
                Attendee id can be used for guests and users, not setting it will resend
                all invitations
        """
        await self.api.require_talk_feature('sip-support')
        await self._post(
            path=f'/room/{room_token}/participants/resend-invitations',
            data={'attendeeId': participant_id or "none"})

    async def promote_to_moderator(
            self,
            room_token: str,
            attendee_id: int) -> None:
        """Promote a user or guest to moderator.

        Args:
            room_token:
                Token of conversation

            attendee_id:
                Attendee ID to promot
        """
        await self._post(
            path=f'/room/{room_token}/moderators',
            data={'attendeeId': attendee_id})

    async def demote(
            self,
            room_token: str,
            attendee_id: int) -> None:
        """Demote a moderator to user or guest.

        Args:
            room_token:
                Token of conversastion

            attendee_id:
                ID of attendee to demote
        """
        await self._delete(
            path=f'/room/{room_token}/moderators',
            data={'attendeeId': attendee_id})

    async def set_conversation_permissions(
            self,
            room_token: str,
            attendee_id: int,
            permissions: ParticipantPermissions,
            mode: PermissionAction) -> None:
        """Set permissions for an attendee.

        Setting custom permissions for a self-joined user will also make them a permanent
        user to the conversation.

        Args:
            room_token:
                Token of conversation

            attendee_id:
                Attendee ID

            permissions:
                ParticipantPermissions

            mode:
                Mode of how permissions should be manipulated constants list. If the
                permissions were 0 (default) and the modification is add or remove, they
                will be initialised with the call or default conversation permissions
                before, falling back to 126 for moderators and 118 for normal
                participants.
        """
        await self._put(
            path=f'/room/{room_token}/attendees/permissions',
            data={
                'attendeeId': attendee_id,
                'method': mode.value,
                'permissions': permissions.value})

    async def verify_dial_in_pin(self, room_token: str, pin: int) -> Participant:
        """Verify a dial-in PIN.

        Args:
            room_token:
                Token of conversation

            pin:
                PIN the participant used to dial-in

        Returns:
            Participant
        """
        await self.api.require_talk_feature('sip-support-dialout')
        response, _ = await self._post(
            path=f'/room/{room_token}/verify-dialin',
            data={'pin': pin})
        return Participant(response, self.api)

    async def verify_dial_out_number(
            self,
            room_token: str,
            number: str,
            actor_id: str,
            actor_type: str,
            attendee_id: int) -> Participant:
        """Verify a dial-out number.

        Requires capability: sip-support-dialout

        Args:
            room_token:
                Token of conversation

            number:
                E164 formatted phone number (see .helpers.phone_number_to_E164())

            actor_id:
                Additional details to verify the validity of the request

            actor_type:
                Additional details to verify the validity of the request

            attendee_id:
                Attendee ID

        Returns:
            Participant
        """
        await self.api.require_talk_feature('sip-support-dialout')
        response, _ = await self._post(
            path=f'/room/{room_token}/verify-dialout',
            data={
                'number': phone_number_to_e164(number),
                'actorId': actor_id,
                'actorType': actor_type,
                'attendeeId': attendee_id})
        return Participant(response, self.api)

    async def reset_rejected_dial_out(
            self,
            room_token: str,
            call_id: str,
            options: str) -> None:
        """Reset call ID of rejected dial-out.

        Requires capability: sip-support-dialout

        Args:
            room_token:
                Token of conversation

            call_id:
                The call ID that was rejected.

            options:
                The options as received in the dialout request.
        """
        await self.api.require_talk_feature('sip-support-dialout')
        await self._delete(
            path=f'/room/{room_token}/rejected-dialout',
            data={
                'options': options,
                'callId': call_id})

    async def set_guest_display_name(
            self,
            room_token: str,
            name: str) -> None:
        """Set display name as a guest.

        Args:
            room_token:
                Token of conversation.

            name:
                Your new name
        """
        await self.api.request(
            path=f'/guest/{room_token}/name"',
            data={'displayName': name})
