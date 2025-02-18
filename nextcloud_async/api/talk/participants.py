"""Nextcloud Talk Participants API.

https://nextcloud-talk.readthedocs.io/en/latest/participant/

"""
import httpx

from typing import Optional, List, Dict, Any, Tuple

from nextcloud_async import NextcloudClient
from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule
from nextcloud_async.helpers import bool2str, phone_number_to_E164
from nextcloud_async.exceptions import NextcloudNotCapable

from .constants import (
    ParticipantPermissions,
    SessionStates,
    PermissionAction,
    ResponseTupleDict,
    ObjectSources)


class Participant:
    def __init__(
            self,
            api: 'Participants',
            data: Dict[str, Any]):
        self.data = data
        self.api = api

    def __str__(self):
        return f'<Participant, room: {self.data['roomToken']}, Id: {self.data['attendeeId']}>'

    def __repr__(self):
        return str(self)

    def __get__(self, k: str):
        return self.data[k]

    @property
    def id(self):
        return self.data['attendeeId']

    @property
    def name(self):
        return self.data['actorId']

    @property
    def room_token(self):
        return self.data['roomToken']


class Participants(NextcloudModule):
    """Interact with Nextcloud Talk API."""

    def __init__(
            self,
            client: NextcloudClient,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '4'):
        self.client: NextcloudClient = client
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    @classmethod
    async def init(
            cls,
            client: NextcloudClient,
            skip_capabiliites: bool = False):
        api = await NextcloudTalkApi.init(client, skip_capabilities=skip_capabiliites, ocs_version='2')
        return cls(client, api)

    async def list(
            self,
            room_token: str,
            include_status: bool = False,
            include_breakout_rooms: bool = False) -> Tuple[List[Participant], httpx.Headers]:
        """Return list of participants."""
        path = f'/room/{room_token}/participants'
        if include_breakout_rooms:
            if self.api.has_capability('breakout-rooms-v1'):
                path = f'/room/{room_token}/breakout-rooms/participants'
            else:
                raise NextcloudNotCapable()
        response, headers = await self._get(
            path=path,
            data={'includeStatus': include_status})

        return [Participant(self, data=x) for x in response], headers

    async def add_to_conversation(
            self,
            room_token: str,
            invitee: str,
            source: ObjectSources = ObjectSources.user) -> Optional[int]:
        """Add a user to to room.

        Method: POST
        Endpoint: /room/{token}/participants

        Args:
        ----
            token (str): Room token

            invitee (str): User, group, email or circle to add

            source (str, optional): Source of the participant(s) as
            returned by the autocomplete suggestion endpoint.  Defaults
            to 'users'

        Raises
        ------
            400 Bad Request
                When the source type is unknown, currently users, groups, emails
                are supported. circles are supported with circles-support capability

            400 Bad Request
                When the conversation is a one-to-one conversation or a conversation
                to request a password for a share

            403 Forbidden - When the current user is not a moderator or owner

            404 Not Found - When the conversation could not be found for the participant

            404 Not Found - When the user or group to add could not be found

        Returns
        -------
            Optional[int]: In case the conversation type changed, the new value is
            returned

        """
        return await self._post(
            path=f'/room/{room_token}/participants',
            data={'newParticipant': invitee, 'source': source.value})

    async def remove_from_conversation(
            self,
            room_token: str,
            attendee_id: int) -> ResponseTupleDict:
        """Delete an attendee from conversation.

        Method: DELETE
        Endpoint: /room/{token}/attendees

        #### Arguments:
        attendeeId	[int]	The participant to delete

        #### Exceptions:
        400 Bad Request When the participant is a moderator or owner

        400 Bad Request When there are no other moderators or owners left

        403 Forbidden When the current user is not a moderator or owner

        403 Forbidden When the participant to remove is an owner

        404 Not Found When the conversation could not be found for the participant

        404 Not Found When the participant to remove could not be found
        """
        return await self._delete(
            path=f'/room/{room_token}/attendees',
            data={'attendeeId': attendee_id})

    async def set_state(self, room_token: str, state: SessionStates) -> ResponseTupleDict:
        """Set user session state.

        SessionState.active: No notifications should be sent
        SessionState.inactive: Notifications should still be sent, even though the user has this session in the room

        Capability required: session-state

        Args
        ----

            room_token (str): Room for new session

            state (SessionStates): New state

        Raises
        ------

            NextcloudNotCapable: _description_

        Returns
        -------

            ResponseTupleDict: _description_
        """
        if not self.api.has_capability('session-state'):
            raise NextcloudNotCapable()

        return await self._put(
            path=f'/room/{room_token}/participants/state',
            data={'state': state.value})

    async def leave(self, token: str) -> ResponseTupleDict:
        """Remove yourself from a conversation.

        Method: DELETE
        Endpoint: /room/{token}/participants/self

        #### Exceptions:
        400 Bad Request When the participant is a moderator or owner and there are
            no other moderators or owners left.

        404 Not Found When the conversation could not be found for the participant
        """
        return await self._delete(path=f'/room/{token}/participants/self')

    async def join(
            self,
            room_token: str,
            password: Optional[str],
            force: bool = True) -> ResponseTupleDict:
        """Join a conversation (available for call and chat)

        Method: POST
        Endpoint: /room/{token}/participants/active

        #### Arguments:
        password	[str]	Optional: Password is only required for users
        which are self joined or guests and only when the conversation has
        hasPassword set to true.

        force   [bool]  If set to false and the user has an active
        session already a 409 Conflict will be returned (Default: true - to
        keep the old behaviour)

        #### Exceptions:

        * 403 Forbidden When the password is required and didn't match

        * 404 Not Found When the conversation could not be found for the participant

        * 409 Conflict When the user already has an active Talk session in the conversation
            with this Nextcloud session. The suggested behaviour is to ask the
            user whether they want to kill the old session and force join unless
            the last ping is older than 60 seconds or older than 40 seconds when
            the conflicting session is not marked as in a call.

        #### Data in case of 409 Conflict:

        sessionId   [str]  512 character long session string

        inCall	    [int]   Flags whether the conflicting session is in a potential call

        lastPing	[int]   Timestamp of the last ping of the conflicting session
        """
        return await self._post(
            path=f'/room/{room_token}/participants/active',
            data={
            'password': password,
            'force': bool2str(force)})

    async def resend_invitation_emails(self, room_token: str, participant_id: Optional[int] = None) -> ResponseTupleDict:
        if not self.api.has_capability('sip-support'):
            raise NextcloudNotCapable()

        return await self._post(
            path=f'/room/{room_token}/participants/resend-invitations',
            data={'attendeeId': participant_id or "none"})

    async def promote_to_moderator(
            self,
            room_token: str,
            attendee_id: int) -> ResponseTupleDict:
        """Promote a user or guest to moderator.

        Method: POST
        Endpoint: /room/{token}/moderators

        #### Arguments:
        attendeeId	int	Attendee id can be used for guests and users

        #### Exceptions:
        400 Bad Request When the participant to promote is not a normal
        user (type 3) or normal guest (type 4)

        403 Forbidden When the current user is not a moderator or owner

        403 Forbidden When the participant to remove is an owner

        404 Not Found When the conversation could not be found for the
        participant

        404 Not Found When the participant to remove could not be found
        """
        return await self._post(
            path=f'/room/{room_token}/moderators',
            data={'attendeeId': attendee_id})

    async def demote(
            self,
            room_token: str,
            attendee_id: int) -> ResponseTupleDict:
        """Demote a moderator to user or guest.

        Method: DELETE
        Endpoint: /room/{token}/moderators

        #### Arguments:
        attendeeId	[int]	Attendee id can be used for guests and users

        #### Exceptions:
        400 Bad Request When the participant to demote is not a moderator
        (type 2) or guest moderator (type 6)

        403 Forbidden When the current participant is not a moderator or owner

        403 Forbidden When the current participant tries to demote themselves

        404 Not Found When the conversation could not be found for the participant

        404 Not Found When the participant to demote could not be found
        """
        return await self._delete(
            path=f'/room/{room_token}/moderators',
            data={'attendeeId': attendee_id})

    async def set_conversation_permissions(
            self,
            room_token: str,
            attendee_id: int,
            permissions: ParticipantPermissions,
            mode: PermissionAction) -> ResponseTupleDict:
        """Set permissions for an attendee.

        Method: PUT
        Endpoint: /room/{token}/attendees/permissions

        #### Arguments:
        attendeeId	[int]	Attendee id can be used for guests and users

        mode	[str]	Mode of how permissions should be manipulated constants list.
        If the permissions were 0 (default) and the modification is `add` or `remove`,
        they will be initialised with the call or default conversation permissions
        before, falling back to 126 for moderators and 118 for normal participants.

        permissions	[Permissions()] New permissions for the attendee, see constants list.
        If permissions are not 0 (default), the 1 (custom) permission will always be
        added.

        #### Exceptions:
        400 Bad Request When the conversation type does not support setting publishing
        permissions, e.g. one-to-one conversations

        400 Bad Request When the attendee type is groups or circles

        400 Bad Request When the mode is invalid

        403 Forbidden When the current user is not a moderator, owner or guest moderator

        404 Not Found When the conversation could not be found for the participant

        404 Not Found When the attendee to set publishing permissions could not be found
        """
        return await self._put(
            path=f'/room/{room_token}/attendees/permissions',
            data={
                'attendeeId': attendee_id,
                'mode': mode.value,
                'permissions': permissions.value})

    async def verify_dial_in_pin(self, room_token: str, pin: int) -> ResponseTupleDict:
        if not self.api.has_capability('sip-support-dialout'):
            raise NextcloudNotCapable()
        return await self._post(
            path=f'/room/{room_token}/verify-dialin',
            data={'pin': pin})

    async def verify_dial_out_number(
            self,
            room_token: str,
            number: str,
            actor_id: str,
            actor_type: str,
            attendee_id: int):
        """Verify a dial-out number.

        Note: This is only allowed as validate SIP bridge requests

        More info:
            https://nextcloud-talk.readthedocs.io/en/latest/participant/#verify-a-dial-out-number
            https://github.com/nextcloud/spreed/blob/main/openapi-full.json#L22548

        Args
        ----

            room_token (str): _description_

            number (str): _description_

            actor_id (str): _description_

            actor_type (str): _description_

            attendee_id (int): _description_

        Raises
        ------

            NextcloudNotCapable: _description_

        Returns
        -------

            _type_: _description_
        """
        if not self.api.has_capability('sip-support-dialout'):
            raise NextcloudNotCapable()

        return await self._post(
            path=f'/room/{room_token}/verify-dialout',
            data={
                'number': phone_number_to_E164(number),
                'actorId': actor_id,
                'actorType': actor_type,
                'attendeeId': attendee_id})

    async def reset_rejected_dial_out(
            self,
            room_token: str,
            call_id: str,
            options: str):
        """Reset call ID of a dial-out participant when the SIP gateway rejected it.

        https://github.com/nextcloud/spreed/blob/main/openapi-full.json#L22930

        Args
        ----

            room_token (str): Room token
        """
        if not self.api.has_capability('sip-support-dialout'):
            raise NextcloudNotCapable

        return await self._delete(
            path=f'/room/{room_token}/rejected-dialout',
            data={
                'options': options,
                'callId': call_id})

    # TODO: ResponseTupleDict
    async def set_guest_display_name(
            self,
            room_token: str,
            name: str) -> None:
        """Set display name as a guest

        More info:
            https://nextcloud-talk.readthedocs.io/en/latest/participant/#set-display-name-as-a-guest
            https://github.com/nextcloud/spreed/blob/main/openapi-full.json#L8745

        Args
        ----

            room_token (str): Room token

            name (str): New name

        Returns
        -------

            ResponseTupleDict: Probably nothing
        """
        await self.api.request(
            path=f'/guest/{room_token}/name"',
            data={'displayName': name})
