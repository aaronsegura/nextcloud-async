"""Nextcloud Talk Conversations API.

    https://nextcloud-talk.readthedocs.io/en/latest/conversation/
"""
import httpx

import datetime as dt

from dataclasses import dataclass, field

from typing import Dict, Optional, Any, List, Tuple

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule
from nextcloud_async.client import NextcloudClient
from nextcloud_async.helpers import bool2int


from .avatars import ConversationAvatars
from .participants import Participants, Participant
from .chat import Chat, Message, MessageReminder, Suggestion
from .calls import Calls
from .polls import Polls, Poll
from .bots import Bots, Bot
from .constants import (
    ConversationType,
    NotificationLevel,
    ObjectSources,
    ParticipantPermissions,
    ListableScope,
    MentionPermissions,
    BreakoutRoomMode,
    BreakoutRoomStatus,
    RoomObjectType,
    WebinarLobbyState,
    SipState)


@dataclass
class Conversation:
    data: Dict[str, Any]
    talk_api: NextcloudTalkApi

    _participants: List[Participant] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.api = Conversations(self.talk_api.client)
        self.avatar_api = ConversationAvatars(self.talk_api)
        self.participant_api = Participants(self.talk_api)
        self.chat_api = Chat(self.talk_api)
        self.calls_api = Calls(self.talk_api)
        self.polls_api = Polls(self.talk_api)
        self.bots_api = Bots(self.talk_api)
        self.breakout_rooms_api = BreakoutRooms(self.talk_api)
        self.webinars_api = Webinars(self.talk_Api)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Conversation: "{self.data['displayName']}" token: "{self.data['token']}">'

    def __repr__(self):
        return str(self)

    @property
    def token(self):
        return self.data['token']

    @property
    def display_name(self):
        return self.data['displayName']

    @display_name.setter
    def display_name(self, v: str):
        self.data['displayName'] = v

    @property
    def is_breakout_room(self):
        return False

    async def get_participants(self):
        if not self._participants:
            await self.refresh_participants()

        return self._participants

    async def refresh_participants(self) -> None:
        self._participants, _ = await self.participants_api.list(self.token)

    async def rename(self, new_name: str) -> None:
        await self.api.rename(room_token=self.token, new_name=new_name)
        self.display_name = new_name

    async def delete(self) -> None:
        await self.api.delete(self.token)

    async def add_user(self, user_id: str) -> None:
        await self.participants_api.add_to_conversation(room_token=self.token, invitee=user_id, source=ObjectSources.user)

    async def add_group(self, group_id: str) -> None:
        await self.participants_api.add_to_conversation(room_token=self.token, invitee=group_id, source=ObjectSources.group)

    async def add_email(self, email: str) -> None:
        await self.participants_api.add_to_conversation(room_token=self.token, invitee=email, source=ObjectSources.email)

    async def add_circle(self, circle_id: str) -> None:
        await self.talk_api.require_talk_feature('circles-support')
        await self.participants_api.add_to_conversation(room_token=self.token, invitee=circle_id, source=ObjectSources.circle)

    async def remove_participant(self, participant: Participant):
        await self.participants_api.remove_from_conversation(room_token=self.token, attendee_id=participant.id)
        self._participants.remove(participant)

    async def resend_invitiation_emails(self):
        await self.participants_api.resend_invitation_emails(room_token=self.token)

    async def get_messages(self, **kwargs) -> Tuple[List[Message], httpx.Headers]:
        return await self.chat_api.get_messages(room_token=self.token, **kwargs)

    async def message_context(self, **kwargs) -> Tuple[List[Message], httpx.Headers]:
        return await self.chat_api.get_context(room_token=self.token, **kwargs)

    async def send(self, **kwargs) -> Tuple[Message, httpx.Headers]:
        return await self.chat_api.send(room_token=self.token, **kwargs)

    async def send_rich_object(self, **kwargs) -> Tuple[Message, httpx.Headers]:
        return await self.chat_api.send_rich_object(room_token=self.token, **kwargs)

    async def share_file(self, **kwargs) -> int:
        return await self.chat_api.share_file(room_token=self.token, **kwargs)

    async def list_shared_items(self, **kwargs) -> List[Message]:
        return await self.chat_api.list_shared_items(room_token=self.token, **kwargs)

    async def list_shared_items_by_type(self, **kwargs) -> Tuple[List[Message], httpx.Headers]:
        return await self.chat_api.list_shared_items_by_type(room_token=self.token, **kwargs)

    async def clear_history(self) -> Message:
        return await self.chat_api.clear_history(room_token=self.token)

    async def delete_message(self, **kwargs) -> Tuple[Message, httpx.Headers]:
        return await self.chat_api.delete(room_token=self.token, **kwargs)

    async def edit_message(self, **kwargs) -> Tuple[Message, httpx.Headers]:
        return await self.chat_api.edit(room_token=self.token, **kwargs)

    async def set_message_reminder(self, **kwargs) -> MessageReminder:
        return await self.chat_api.set_reminder(room_token=self.token, **kwargs)

    async def get_message_reminder(self, **kwargs) -> MessageReminder:
        return await self.chat_api.get_reminder(room_token=self.token, **kwargs)

    async def delete_message_reminder(self, **kwargs) -> None:
        return await self.chat_api.delete_reminder(room_token=self.token, **kwargs)

    async def mark_as_read(self, **kwargs) -> None:
        await self.chat_api.mark_as_read(room_token=self.token, **kwargs)

    async def mark_as_unread(self) -> None:
        await self.chat_api.mark_as_unread(room_token=self.token)

    async def suggest_autocompletes(self, **kwargs) -> List[Suggestion]:
        return await self.chat_api.suggest_autocompletes(room_token=self.token, **kwargs)

    async def set_name_as_guest(self, **kwargs) -> None:
        await self.participants_api.set_guest_display_name(room_token=self.token, **kwargs)

    async def set_default_permissions(self, **kwargs) -> None:
        await self.api.set_default_permissions(room_token=self.token, **kwargs)

    async def participants_connected_to_call(self):
        return await self.calls_api.get_connected_participants(self.token)

    async def join_call(self, **kwargs):
        await self.calls_api.join_call(room_token=self.token, **kwargs)  # type: ignore

    async def send_call_notification(self, **kwargs):
        await self.calls_api.send_notification(room_token=self.token, **kwargs)  # type: ignore

    async def send_call_sip_dialout_request(self, **kwargs):
        await self.calls_api.send_sip_dialout_request(room_token=self.token, **kwargs)  # type: ignore

    async def update_call_flags(self, **kwargs):
        await self.calls_api.update_flags(room_token=self.token, **kwargs)  # type: ignore

    async def leave_call(self, **kwargs: Dict[str, Any]):
        await self.calls_api.leave(room_token=self.token, **kwargs)  # type: ignore

    async def set_avatar(self, **kwargs) -> None:
        await self.avatar_api.set(self.token, **kwargs)  # type: ignore

    async def set_avatar_emoji(self, **kwargs) -> None:
        await self.avatar_api.set_emoji(room_token=self.token, **kwargs)  # type: ignore

    async def delete_avatar(self) -> None:
        await self.avatar_api.delete(room_token=self.token)

    async def get_avatar(self, **kwargs) -> bytes:
        return await self.avatar_api.get(room_token=self.token, **kwargs)

    async def get_federated_avatar(self, **kwargs) -> bytes:
        return await self.get_federated_avatar(room_token=self.token, **kwargs)

    async def create_poll(self, **kwargs) -> Poll:
        return await self.polls_api.create(room_token=self.token, **kwargs)

    async def edit_draft_poll(self, **kwargs) -> Poll:
        return await self.polls_api.edit_draft(room_token=self.token, **kwargs)

    async def get_poll(self, **kwargs) -> Poll:
        return await self.polls_api.get(room_token=self.token, **kwargs)

    async def list_draft_polls(self, **kwargs) -> List[Poll]:
        return await self.polls_api.list_drafts(room_token=self.token, **kwargs)

    async def vote_on_poll(self, **kwargs) -> None:
        await self.polls_api.vote(room_token=self.token, **kwargs)

    async def close_poll(self, **kwargs) -> None:
        await self.polls_api.close(room_token=self.token, **kwargs)

    async def list_installed_bots(self) -> List[Bot]:
        return await self.bots_api.list_installed()

    async def list_bots(self) -> List[Bot]:
        return await self.bots_api.list_conversation_bots(self.token)

    async def list_breakout_rooms(self) -> List['BreakoutRoom']:
        return await self.api.list_breakout_rooms(self.token)

    async def configure_breakout_rooms(self, **kwargs) -> Tuple['Conversation', List['BreakoutRoom']]:
        response = await self.breakout_rooms_api.configure(room_token=self.token, **kwargs)
        return self._sort_room_types(response)

    async def create_additional_breakout_room(self, **kwargs) -> 'BreakoutRoom':
        response = await self.api.create(object_id=self.token, **kwargs)
        return BreakoutRoom.from_conversation(response)

    async def remove_breakout_rooms(self) -> 'Conversation':
        return await self.breakout_rooms_api.remove(self.token)

    async def start_breakout_rooms(self) -> Tuple['Conversation', List['BreakoutRoom']]:
        return await self.breakout_rooms_api.start(self.token)

    async def broadcast_breakout_rooms_message(self, **kwargs) -> None:
        return await self.breakout_rooms_api.broadcast_message(self.token, **kwargs)

    async def reorganize_breakout_room_attendees(self, **kwargs) -> Tuple['Conversation', List['BreakoutRoom']]:
        return await self.breakout_rooms_api.reorganize_attendees(room_token=self.token, **kwargs)

    async def switch_breakout_room(self, **kwargs) -> 'BreakoutRoom':
        return await self.breakout_rooms_api.switch_rooms(room_token=self.token, **kwargs)

    async def enable_lobby(self, **kwargs) -> 'Conversation':
        return await self.webinars_api.set_lobby_state(self.token, WebinarLobbyState.lobby, **kwargs)

    async def disable_lobby(self, **kwargs) -> 'Conversation':
        return await self.webinars_api.set_lobby_state(self.token, WebinarLobbyState.no_lobby)

    async def enable_sip_dialin(self) -> 'Conversation':
        return await self.webinars_api.set_sip_dialin(self.token, SipState.enabled)

    async def disable_sip_dialin(self) -> 'Conversation':
        return await self.webinars_api.set_sip_dialin(self.token, SipState.disabled)

class Conversations(NextcloudModule):
    """Interact with Nextcloud Talk API."""
    api: NextcloudTalkApi

    def __init__(
            self,
            client: NextcloudClient,
            api_version: Optional[str] = '4'):

        self.client: NextcloudClient = client
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api = NextcloudTalkApi(client)
        self.avatar_api = ConversationAvatars(self.api)
        self.participants_api = Participants(self.api)
        self.chat_api = Chat(self.api)
        self.integrations_api = Integrations(self.api)

    async def list(
            self,
            status_update: bool = False,
            include_status: bool = False) -> List[Conversation]:
        """Return list of user's conversations.

        Method: GET
        Endpoint: /room

        #### Arguments:
        status_update  [bool]  Whether the "online" user status of the current
        user should be "kept-alive" (True) or not (False) (defaults to False)

        include_status   [bool] Whether the user status information of all
        one-to-one conversations should be loaded (default false)

        #### Exceptions:
        401 Unauthorized when the user is not logged in
        """
        data: Dict[str, Any] = {
            'noStatusUpdate': 1 if status_update else 0,
            'includeStatus': include_status
            }
        response, _ = await self._get(
            path='/room',
            data=data)

        return [Conversation(data, self.api) for data in response]

    async def create(
            self,
            room_type: ConversationType,
            invite: str = '',
            room_name: str = '',
            object_type: RoomObjectType = RoomObjectType.room,
            object_id: str = '',
            source: str = '') -> Conversation:
        """Create a new conversation.

        More info:
            https://nextcloud-talk.readthedocs.io/en/latest/conversation/#creating-a-new-conversation
            https://github.com/nextcloud/spreed/blob/88d1e4b11872f96745201c6e8921e7848eab0be8/openapi-full.json#L11726

        Args
        -----
            room_type   [str]   See constants list
            invite	[str]	user id (roomType = 1), group id (roomType = 2 - optional),
            circle id (roomType = 2, source = 'circles'], only available
            with circles-support capability))

            source	[str]	The source for the invite, only supported on roomType = 2 for
            groups and circles (only available with circles-support capability)

            room_name	[str]	conversation name (Not available for roomType = 1)

        Raises
        ------
            400 Bad Request When an invalid conversation type was given

            400 Bad Request When the conversation name is empty for type = 3

            401 Unauthorized When the user is not logged in

            404 Not Found When the target to invite does not exist

        """
        data: Dict[str, Any] = {
            'roomType': room_type.value,
            'invite': invite,
            'source': source,
            'roomName': room_name
        }

        ### For creating breakout rooms
        # object_type is 'room'
        # object_id is parent room_token
        if object_type:
            data.update({'objectType': object_type})
        if object_id:
            data.update({'objectId': object_id})

        # TODO: headers
        response, _ = await self._post(path='/room', data=data)
        return Conversation(data, self.api)

    async def get(self, room_token: str) -> Conversation:
        """Get a specific conversation.

        Method: GET
        Endpoint: /room/{token}

        #### Exceptions:
        404 Not Found When the conversation could not be found for the participant
        """
        # TODO: headers
        data, _ = await self._get(path=f'/room/{room_token}')
        return Conversation(data, self.api)

    async def get_note_to_self(self) -> Conversation:
        # TODO: headers
        data, _ = await self._get(path='/room/note-to-self')
        return Conversation(data, self.api)

    async def list_open(self) -> List[Conversation]:
        """Get list of open rooms."""
        response, _ = await self._get(path='/listed-room')
        return [Conversation(data, self.api) for data in response]

    async def list_breakout_rooms(self, room_token: str) -> List['BreakoutRoom']:
        await self.api.require_talk_feature('breakout-rooms-v1')
        response, _ = await self._get(path=f'/{room_token}/breakout-rooms')
        return [BreakoutRoom(data, self.api) for data in response]

    async def rename(self, room_token: str, new_name: str) -> None:
        """Rename the room.

        Method: PUT
        Endpoint: /room/{token}

        #### Arguments:
        roomName  [str]  New name for the conversation (1-200 characters)

        #### Exceptions:
        400 Bad Request When the name is too long or empty

        400 Bad Request When the conversation is a one to one conversation

        403 Forbidden When the current user is not a moderator/owner

        404 Not Found When the conversation could not be found for the
            participant
        """
        await self._put(
            path=f'/room/{room_token}',
            data={'roomName': new_name})

    async def delete(self, room_token: str) -> None:
        """Delete the room.

        Method: DELETE
        Endpoint: /room/{token}

        #### Exceptions:
        400 Bad Request When the conversation is a one-to-one conversation
            (Use Remove yourself from a conversation instead)

        403 Forbidden When the current user is not a moderator/owner

        404 Not Found When the conversation could not be found for the
            participant
        """
        await self._delete(path=f'/room/{room_token}')

    async def set_description(self, room_token: str, description: str) -> None:
        """Set description on room.

        Required capability: room-description
        Method: PUT
        Endpoint: /room/{token}/description

        #### Arguments:
        description [str] New description for the conversation

        #### Exceptions:
        400 Bad Request When the description is too long

        400 Bad Request When the conversation is a one to one conversation

        403 Forbidden When the current user is not a moderator/owner

        404 Not Found When the conversation could not be found for the participant

        NextcloudNotCapable When server is lacking required capability
        """
        await self.api.require_talk_feature('room-description')
        await self._put(
            path=f'/room/{room_token}/description',
            data={'description': description})

    async def allow_guests(self, room_token: str, password: Optional[str]) -> None:
        """Allow guests in a conversation.

        Method: POST
        Endpoint: /room/{token}/public

        #### Arguments:
        allow_guests [bool] Allow (True) or disallow (False) guests

        #### Exceptions:
        400 Bad Request When the conversation is not a group conversation

        403 Forbidden When the current user is not a moderator/owner

        404 Not Found When the conversation could not be found for the participant
        """
        data: Dict[str, str] = {}
        if password:
            await self.api.require_talk_feature('conversation-creation-password')
            data = {'password': password}

        await self._post(path=f'/room/{room_token}/public', data=data)

    async def disallow_guests(self, room_token: str) -> None:
        """Disallow guests in a conversation.

        Method: DELETE
        Endpoint: /room/{token}/public

        #### Arguments:
        allow_guests [bool] Allow (True) or disallow (False) guests

        #### Exceptions:
        400 Bad Request When the conversation is not a group conversation

        403 Forbidden When the current user is not a moderator/owner

        404 Not Found When the conversation could not be found for the participant
        """
        return await self._delete(path=f'/room/{room_token}/public')

    async def read_only(self, room_token: str, state: int) -> None:
        """Set read-only for a conversation

        Required capability: read-only-rooms
        Method: PUT
        Endpoint: /room/{token}/read-only

        #### Arguments:
        state	[int]	New state for the conversation, see constants list

        #### Exceptions:
        400 Bad Request When the conversation type does not support read-only
            (only group and public conversation)

        403 Forbidden When the current user is not a moderator/owner or the
            conversation is not a public conversation

        404 Not Found When the conversation could not be found for the
            participant

        NextcloudNotCapable When server is lacking required capability
        """
        await self.api.require_talk_feature('read-only-rooms')
        await self._put(path=f'/room/{room_token}/read-only', data={'state': state})

    async def set_conversation_password(self, token: str, password: str) -> None:
        """Set password for a conversation

        Method: PUT
        Endpoint: /room/{token}/password

        #### Arguments:
        password	string	New password for the conversation

        #### Exceptions
        403 Forbidden When the current user is not a moderator or owner

        403 Forbidden When the conversation is not a public conversation

        404 Not Found When the conversation could not be found for the participant
        """
        await self._put(
            path=f'/room/{token}/password',
            data={'password': password})

    async def set_default_permissions(
            self,
            room_token: str,
            permissions: ParticipantPermissions,
            mode: str = 'default') -> None:
        data: Dict[str, Any] = {
            'mode': mode,
            'permissions': permissions.value}
        await self._put(
            path=f'/room/{room_token}/permissions/{mode}', data=data)

    async def add_to_favorites(self, room_token: str) -> None:
        """Add conversation to favorites

        Required capability: favorites
        Method: POST
        Endpoint: /room/{token}/favorite

        #### Exceptions:
        401 Unauthorized When the participant is a guest

        404 Not Found When the conversation could not be found for the participant

        NextcloudNotCapable When server is lacking required capability
        """
        await self.api.require_talk_feature('favorites')
        await self._post(path=f'/room/{room_token}/favorite')

    async def remove_from_favorites(self, room_token: str) -> None:
        """Remove conversation from favorites

        Required capability: favorites
        Method: DELETE
        Endpoint: /room/{token}/favorite

        #### Exceptions:
        401 Unauthorized When the participant is a guest

        404 Not Found When the conversation could not be found for the participant

        NextcloudNotCapable When server is lacking required capability
        """
        await self.api.require_talk_feature('favorites')
        await self._delete(path=f'/room/{room_token}/favorites')

    async def set_notification_level(
            self,
            token: str,
            notification_level: str) -> None:
        """Set notification level

        Required capability: notification-levels
        Method: POST
        Endpoint: /room/{token}/notify

        #### Arguments:
        notification_level	[str]	The notification level (See constants)

        #### Exceptions:
        400 Bad Request When the given level is invalid

        401 Unauthorized When the participant is a guest

        404 Not Found When the conversation could not be found for the participant
        """
        data = {
            'level': NotificationLevel[notification_level].value
        }
        return await self._post(
            path=f'/room/{token}/notify',
            data=data)

    async def set_call_notification_level(
            self,
            room_token: str,
            notification_level: str) -> None:
        """Set notification level for calls.

        Required capability: notification-calls
        Method: POST
        Endpoint: /room/{token}/notify-calls

        #### Arguments:
        level [int]	The call notification level (See constants)

        #### Exceptions:
        400 Bad Request When the given level is invalid

        401 Unauthorized When the participant is a guest

        404 Not Found When the conversation could not be found for the participant

        NextcloudNotCapable When server is lacking required capability
        """
        await self.api.require_talk_feature('notification-calls')
        data = {
            'level': NotificationLevel[notification_level].value
        }
        await self._post(
            path=f'/room/{room_token}/notify-calls',
            data=data)

    async def set_message_expiration(
            self,
            room_token: str,
            seconds: int) -> None:
        await self.api.require_talk_feature('message-expiration')
        await self._post(
            path=f'/room/{room_token}/message-expiration',
            data={'seconds': seconds})

    async def set_recording_consent(
            self,
            room_token: str,
            consent: bool = True) -> None:
        await self.api.require_talk_feature('recording-consent')
        await self._put(
            path=f'/room/{room_token}/recording-consent',
            data={'recordingConsent': bool2int(consent)})

    async def set_scope(
            self,
            room_token: str,
            scope: ListableScope) -> None:
        await self.api.require_talk_feature('listable-rooms')
        await self._put(
            path=f'/room/{room_token}/listable',
            data={'scope': scope.value})

    async def set_mention_permissions(
            self,
            room_token: str,
            permissions: MentionPermissions) -> None:
        await self.api.require_talk_feature('mention-permissions')
        await self._put(
            path=f'/room/{room_token}/mention-permissions',
            data={'mentionPermissions': permissions.value})

    async def create_password_request(self, share_id: int) -> Dict[str, Any]:
        return await self.integrations_api.create_password_request_conversation(share_id)

@dataclass
class BreakoutRoom:
    data: Dict[str, Any]
    talk_api: NextcloudTalkApi

    def __post_init__(self):
        self.api = BreakoutRooms(self.talk_api)
        self.conversations_api = Conversations(self.talk_api.client)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Talk BreakoutRoom token={self.token}, "{self.name}"">'

    # TODO: Maybe do self.data for all dataclass objects
    def __repr__(self):
        return str(self.data)

    @classmethod
    def from_conversation(cls, conversation: Conversation) -> 'BreakoutRoom':
        return cls(conversation.data, conversation.talk_api)

    @property
    def status(self):
        return BreakoutRoomStatus(self.breakoutRoomStatus).name

    @property
    def mode(self):
        return BreakoutRoomMode(self.breakoutRoomMode).name

    @property
    def is_breakout_room(self):
        return True

    async def delete(self) -> None:
        await self.conversations_api.delete(self.token)

    async def request_assistance(self) -> None:
        await self.api.request_assistance(room_token=self.token)

    async def reset_request_assistance(self) -> None:
        await self.api.reset_request_assistance(room_token=self.token)

class BreakoutRooms(NextcloudModule):
    """Interact with Nextcloud Talk Bots API."""

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '1'):
        self.stub = f'/apps/spreed/api/v{api_version}/breakout-rooms'
        self.api: NextcloudTalkApi = api

    async def _validate_capability(self) -> None:
            await self.api.require_talk_feature('breakout-rooms-v1')

    def _create_room_by_type(self, rooms: List[Dict[str, Any]]) -> Tuple[Conversation, List[BreakoutRoom]]:
        parent_room: Conversation = Conversation(rooms[0], self.api)
        breakout_rooms: List[BreakoutRoom] = []

        for room in rooms:
            if hasattr(room, 'breakoutRoomStatus'):
                breakout_rooms.append(BreakoutRoom(room, self.api))
            else:
                parent_room = Conversation(room, self.api)

        return parent_room, breakout_rooms

    async def configure(
            self,
            room_token: str,
            mode: BreakoutRoomMode,
            num_rooms: int,
            attendee_map: Dict[str, int]) -> List[BreakoutRoom|Conversation]:
        await self._validate_capability()
        response, _ = await self._post(
            path=f'/{room_token}',
            data={
                'mode': mode.value,
                'amount': num_rooms,
                'attendeeMap': attendee_map})
        return [BreakoutRoom(data, self.api) for data in response]

    async def create_additional_room(self):
        """See talk.conversation.create_additional_breakout_room()."""
        ...

    async def delete_room(self):
        """See talk.conversation.delete_breakout_room()."""
        ...

    async def remove(self, room_token: str) -> 'Conversation':
        await self._validate_capability()
        return await self._delete(path=f'/{room_token}')

    async def start(self, room_token: str) -> Tuple[Conversation, List[BreakoutRoom]]:
        await self._validate_capability()
        response = await self._post(path=f'/{room_token}/rooms')
        return self._create_room_by_type(response)

    async def stop(self, room_token: str) -> Tuple[Conversation, List[BreakoutRoom]]:
        await self._validate_capability()
        response = await self._delete(path=f'/{room_token}/rooms')
        return self._create_room_by_type(response)

    async def broadcast_message(self, room_token: str, message: str) -> None:
        await self._validate_capability()
        await self._post(
            path=f'/{room_token}/broadcast',
            data={
                'token': room_token,
                'message': message})

    async def reorganize_attendees(self, room_token: str, attendee_map: Dict[str, int]) -> Tuple[Conversation, List[BreakoutRoom]]:
        await self._validate_capability()
        response = await self._post(
            path=f'/{room_token}/attendees',
            data={'attendeeMap': attendee_map})
        return self._create_room_by_type(response)

    async def request_assistance(self, room_token: str) -> None:
        await self._validate_capability()
        await self._post(path=f'/{room_token}/request-assistance')

    async def reset_request_assistance(self, room_token: str) -> None:
        await self._validate_capability()
        await self._delete(path=f'/{room_token}/request_assistance')

    async def switch_rooms(self, room_token: str, target: int) -> BreakoutRoom:
        await self._validate_capability()
        response = await self._post(
            path=f'/{room_token}/switch',
            data={'target': target})
        return BreakoutRoom(response, self.api)


class Webinars(NextcloudModule):
    """Interact with Nextcloud Talk Bots API.

    https://nextcloud-talk.readthedocs.io/en/latest/webinar/
    """

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '4'):
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    async def set_lobby_state(
            self,
            room_token: str,
            lobby_state: WebinarLobbyState,
            reset_time: Optional[dt.datetime] = None) -> Conversation:
        await self.api.require_capability('webinary-lobby')
        response, _ = await self._put(
            path=f'/room/{room_token}/webinar/lobby',
            data={
                'state': lobby_state.name,
                'timer': reset_time.strftime('%s') if reset_time else 0})
        return Conversation(response, self.api)

    async def set_sip_dialin(
            self,
            room_token: str,
            state: SipState) -> Conversation:
        await self.api.require_capability('sip-support')
        response, _ = await self._put(
            path=f'/room/{room_token}/webinar/sip',
            data={'state': state.value})
        return Conversation(response, self.api)


class Integrations(NextcloudModule):
    """Interact with Nextcloud Talk Bots API.

    https://nextcloud-talk.readthedocs.io/en/latest/integration/
    """

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '1'):
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    async def get_interal_file_conversation(
            self,
            file_id: int) -> str:
        response, _ = await self._get(path=f'/file/{file_id}')
        return response['token']

    async def get_public_file_share_conversation(
            self,
            share_token: str) -> str:
        response, _ = await self._get(path=f'/publicshare/{share_token}')
        return response['token']

    async def create_password_request_conversation(
            self,
            share_token: str) -> Dict[str, Any]:
        response, _ = await self._post(
            path='/publicshareauth',
            data={'shareToken': share_token})
        return response
