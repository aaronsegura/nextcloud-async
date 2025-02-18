"""Nextcloud Talk Conversations API.

    https://nextcloud-talk.readthedocs.io/en/latest/conversation/
"""
import httpx

from dataclasses import dataclass, field

from typing import Dict, Optional, Any, List, Tuple

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule
from nextcloud_async import NextcloudClient
from nextcloud_async.exceptions import NextcloudNotCapable
from nextcloud_async.helpers import bool2int


from .avatars import ConversationAvatars
from .participants import Participants, Participant
from .chat import Chat, Message, MessageReminder, Suggestion
from .calls import Calls

from .constants import (
    ConversationType,
    NotificationLevel,
    ObjectSources,
    ParticipantPermissions,
    ListableScope,
    MentionPermissions)


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
        if not self.api.api.has_feature('circles-support'):
            raise NextcloudNotCapable()
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

    async def list_shares(self, **kwargs) -> List[Message]:
        return await self.chat_api.list_shares(room_token=self.token, **kwargs)

    async def list_share_by_type(self, **kwargs) -> Tuple[List[Message], httpx.Headers]:
        return await self.chat_api.list_shares_by_type(room_token=self.token, **kwargs)

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

    async def join_call(self, **kwargs: Dict[str, Any]):
        await self.calls_api.join_call(room_token=self.token, **kwargs)  # type: ignore

    async def send_call_notification(self, **kwargs: Dict[str, Any]):
        await self.calls_api.send_notification(room_token=self.token, **kwargs)  # type: ignore

    async def send_call_sip_dialout_request(self, **kwargs: Dict[str, Any]):
        await self.calls_api.send_sip_dialout_request(room_token=self.token, **kwargs)  # type: ignore

    async def update_call_flags(self, **kwargs: Dict[str, Any]):
        await self.calls_api.update_flags(room_token=self.token, **kwargs)  # type: ignore

    async def leave_call(self, **kwargs: Dict[str, Any]):
        await self.calls_api.leave(room_token=self.token, **kwargs)  # type: ignore


class Conversations(NextcloudModule):
    """Interact with Nextcloud Talk API."""

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
        if await self.api.has_feature('room-description'):
            raise NextcloudNotCapable()

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
            if not await self.api.has_feature('conversation-creation-password'):
                raise NextcloudNotCapable()
            else:
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
        if await self.api.has_feature('read-only-rooms'):
            raise NextcloudNotCapable()

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
        if await self.api.has_feature('favorites'):
            raise NextcloudNotCapable()

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
        if await self.api.has_feature('favorites'):
            raise NextcloudNotCapable()

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
        if not await self.api.has_feature('notification-calls'):
            raise NextcloudNotCapable()

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
        if not await self.api.has_feature('message-expiration'):
            raise NextcloudNotCapable()

        await self._post(
            path=f'/room/{room_token}/message-expiration',
            data={'seconds': seconds})

    async def set_recording_consent(
            self,
            room_token: str,
            consent: bool = True) -> None:
        if not await self.api.has_feature('recording-consent'):
            raise NextcloudNotCapable()

        await self._put(
            path=f'/room/{room_token}/recording-consent',
            data={'recordingConsent': bool2int(consent)})

    async def set_scope(
            self,
            room_token: str,
            scope: ListableScope) -> None:
        if not await self.api.has_feature('listable-rooms'):
            raise NextcloudNotCapable()

        await self._put(
            path=f'/room/{room_token}/listable',
            data={'scope': scope.value})

    async def set_mention_permissions(
            self,
            room_token: str,
            permissions: MentionPermissions) -> None:
        if not await self.api.has_feature('mention-permissions'):
            raise NextcloudNotCapable()

        await self._put(
            path=f'/room/{room_token}/mention-permissions',
            data={'mentionPermissions': permissions.value})
