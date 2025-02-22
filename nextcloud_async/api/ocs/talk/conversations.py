"""Nextcloud Talk Entrypoint.

https://github.com/nextcloud/spreed/blob/b5bed8c1157df02492afb420cfa607e014212575/openapi-full.json

Conversations() is the entry-point into the Spreed/Talk back-end.

Where appropriate, functions return a tuple of data and headers.

All calls to the API are checked for status codes >=400 and an appropriate exception is
raised. See .driver.talk.NextcloudTalkApi.request() for more information.

API calls that require a specific capability that is missing on the server will raise a
NextcloudNotCapable exception.
"""
import httpx

import datetime as dt

from dataclasses import dataclass, field

from typing import Dict, Optional, Any, List, Tuple, TypedDict, TYPE_CHECKING

import sys
if sys.version_info < (3, 11):
    from typing_extensions import TypedDict, NotRequired, Unpack
else:
    from typing import TypedDict, NotRequired, Unpack

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule
from nextcloud_async.client import NextcloudClient
from nextcloud_async.helpers import bool2int

from .avatars import ConversationAvatars
from .bots import Bots, Bot
from .calls import Calls
from .chat import Chat, Message, MessageReminder, Suggestion, ChatFileShareMetadata
from .integrations import Integrations
from .participants import Participants, Participant
from .polls import Polls, Poll
from .rich_objects import NextcloudTalkRichObject
from .signaling import InternalSignaling
from .webinars import Webinars

if TYPE_CHECKING:
    from .breakout_rooms import BreakoutRoom

from .constants import (
    ConversationType,
    ConversationReadOnlyState,
    ConversationNotificationLevel,
    ObjectSources,
    ParticipantPermissions,
    ListableScope,
    MentionPermissions,
    RoomObjectType,
    WebinarLobbyState,
    SipState,
    ConversationPermissionMode,
    CallNotificationLevel,
    SharedItemType,
    ParticipantInCallFlags,
    PollMode,
    BreakoutRoomAssignmentMode)


@dataclass
class Conversation:
    data: Dict[str, Any]
    talk_api: NextcloudTalkApi

    _participants: List[Participant] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        """Set up all of the APIs needed by this class."""
        from .breakout_rooms import BreakoutRooms

        self.api = Conversations(self.talk_api.client)
        self.avatar_api = ConversationAvatars(self.talk_api)
        self.participants_api = Participants(self.talk_api)
        self.chat_api = Chat(self.talk_api)
        self.calls_api = Calls(self.talk_api)
        self.polls_api = Polls(self.talk_api)
        self.bots_api = Bots(self.talk_api)
        self.breakout_rooms_api = BreakoutRooms(self.talk_api)
        self.webinars_api = Webinars(self.talk_api)
        self.signaling_api = InternalSignaling(self.talk_api)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<Conversation: "{self.data['displayName']}" '\
               f'token: "{self.data['token']}">'

    def __repr__(self) -> str:
        return str(self.data)

    @property
    def display_name(self) -> str:
        """Translate displayName into more python display_name.

        Returns:
            The display name of the conversation.
        """
        return self.data['displayName']

    @display_name.setter
    def display_name(self, v: str) -> None:
        """Setter for self.display_name.

        Args:
            v:
                New display name for this conversation.
        """
        self.data['displayName'] = v

    @property
    def is_breakout_room(self) -> bool:
        """Return True if this conversation is a BreakoutRoom.

        This is used in the room sorting function BreakoutRooms._create_rooms_by_type()

        Returns:
            True = BreakoutRoom, False = Not BreakoutRoom
        """
        return False

    async def get_participants(self) -> List[Participant]:
        """Return list of Participants in this conversation.

        Participants are pulled from the API on first run.  Best effort is made to
        maintain the list of participants (for instance, when a Participant object
        calls .leave())
        # FIXME: REALLY?
        but it is ultimately up to you to keep the list accurate.
        Conversation.refresh_participants() can be called at will to keep the list up to
        date.

        Returns:
            List of conversation participants.
        """
        if not self._participants:
            await self.refresh_participants()

        return self._participants

    async def refresh_participants(self) -> None:
        """Refresh the list of participants in this conversation."""
        self._participants, _ = await self.participants_api.list(self.token)

    async def rename(self, new_name: str) -> None:
        """Rename this conversation.

        The display_name property is updated after a successful call.

        Args:
            new_name:
                New display name of the conversation.
        """
        await self.api.rename(room_token=self.token, new_name=new_name)
        self.display_name = new_name

    async def delete(self) -> None:
        """Delete this conversation."""
        await self.api.delete(self.token)

    async def add_user(self, name: str) -> None:
        """Add a participant to this conversation.

        Args:
            name:
                Participant.display_name or a string representing the user's name.
        """
        await self.participants_api.add_to_conversation(
            room_token=self.token,
            invitee=name,
            source=ObjectSources.user)

    async def add_group(self, group_name: str) -> None:
        """Add a group to this conversation.

        Args:
            group_name:
                Group.name or str representing name of group.
        """
        await self.participants_api.add_to_conversation(
            room_token=self.token,
            invitee=group_name,
            source=ObjectSources.group)

    async def add_email(self, email: str) -> None:
        """Add user to conversation by e-mail.

        Args:
            email:
                E-mail address of participant.
        """
        await self.participants_api.add_to_conversation(
            room_token=self.token,
            invitee=email,
            source=ObjectSources.email)

    async def add_circle(self, circle_id: str) -> None:
        """Add Nextcloud circle to this conversation.

        Args:
            circle_id:
                The ID of the circle to add.
        """
        await self.talk_api.require_talk_feature('circles-support')
        await self.participants_api.add_to_conversation(
            room_token=self.token,
            invitee=circle_id,
            source=ObjectSources.circle)

    async def remove_participant(self, participant: Participant) -> None:
        """Remove a Participant from this conversation.

        Args:
            participant:
                Participant object.
        """
        await self.participants_api.remove_from_conversation(
            room_token=self.token,
            attendee_id=participant.id)
        self._participants.remove(participant)

    async def resend_invitiation_emails(self) -> None:
        """Re-send invitation e-mails for this conversation."""
        await self.participants_api.resend_invitation_emails(room_token=self.token)

    class _GetMessagesArgs(TypedDict):
        look_into_future: bool
        limit: int
        timeout: int
        last_known_message_id: NotRequired[int]
        last_common_read_id: NotRequired[int]
        set_read_marker: bool
        include_last_known: bool
        no_status_update: bool
        mark_notifications_as_read: bool

    async def get_messages(  # noqa: D417
            self,
            **kwargs: Unpack[_GetMessagesArgs]) -> Tuple[List[Message], httpx.Headers]:
        """Receive messages from a conversation.

        https://nextcloud-talk.readthedocs.io/en/latest/chat/#receive-chat-messages-of-a-conversation
        https://github.com/nextcloud/spreed/blob/88d1e4b11872f96745201c6e8921e7848eab0be8/openapi-full.json#L5659


        Args:
            look_into_future:
                Poll and wait for new message (True) or get history of a conversation
                (False)

            limit:
                Number of chat messages to receive (100 by default, 200 at most)

            timeout:
                Number of seconds to wait for new messages (30 by default, 60 at most)
                Only valid if look_into_future=True.

            last_known_message_id:
                Serves as an offset for the query. The lst_known_message_id for the next
                page is available in the X-Chat-Last-Given header.

            last_common_read_id:
                Send the last X-Chat-Last-Common-Read header you got, if you are
                interested in updates of the common read value. A 304 response does not
                allow custom headers and otherwise the server can not know if your value
                is modified or not.

            set_read_marker:
                True to automatically set the read timer after fetching the messages, use
                False when your client calls Mark chat as read manually. (Default: True)

            include_last_known:
                True to include the last known message as well (Default: False)

            no_status_update:
                When the user status should not be automatically set to online set to True
                (default False)

            mark_notifications_as_read:
                False to not mark notifications as read (Default: 1True, only available
                with chat-keep-notifications capability)

        Returns:
            List of Messages, Headers

            Headers:
                x-chat-last-given: Offset (last_known_message_id) for the next page.

                x-chat-last-common-read	[int]	ID of the last message read by every user
                that has read privacy set to public. When the user themself has it set to
                private the value the header is not set (only available with
                chat-read-status capability and when last_common_read_id was sent)
        """
        return await self.chat_api.get_messages(room_token=self.token, **kwargs)

    class _MessageContextArgs(TypedDict):
        message_id: int
        limit: int

    async def message_context(
            self,
            **kwargs: Unpack[_MessageContextArgs]) -> Tuple[List[Message], httpx.Headers]:
        """Get context around a message.

        Requires Capability: chat-get-context
        Args:

            message_id:
                Message ID

            limit:
                Number of chat messages to receive into each direction (50 by default,
                100 at most)

        Returns:
            Messages
        """
        return await self.chat_api.get_context(room_token=self.token, **kwargs)

    class _SendArgs(TypedDict):
        message: str
        reply_to: int
        display_name: NotRequired[str]
        reference_id: NotRequired[str]
        silent: bool

    async def send(self, **kwargs: Unpack[_SendArgs]) -> Tuple[Message, httpx.Headers]:  # noqa: D417
        """Send message to the conversation.

        Args:
            message:
                Message to send

            reply_to:
                The message ID this message is a reply to (only allowed for messages
                from the same conversation and when the message type is not system
                or command)

            display_name:
                Set the display name.  Only valid if guest.

            reference_id:
                A reference string to be able to identify the message again in a "get
                messages" request, should be a random sha256 (only available with
                chat-reference-id capability)

            silent:
                If sent silent the message will not create chat notifications even for
                mentions (only available with silent-send capability)


        Raises:
            NextcloudBadRequest: Invalid reference_id given.

        Returns:
            New Message, Headers

            Headers:
                x-chat-last-common-read	[int]	ID of the last message read by every user
                that has read privacy set to public. When the user themself has it set to
                private the value the header is not set (only available with
                chat-read-status capability and when last_common_read_id was sent)
        """
        return await self.chat_api.send(room_token=self.token, **kwargs)

    class _SendRichObjectArgs(TypedDict):
        rich_object: NextcloudTalkRichObject
        reference_id: NotRequired[str]
        actor_display_name: NotRequired[str]

    async def send_rich_object(  # noqa: D417
            self,
            **kwargs: Unpack[_SendRichObjectArgs]) -> Tuple[Message, httpx.Headers]:
        """Share a rich object to the conversation.

        https://github.com/nextcloud/server/blob/master/lib/public/RichObjectStrings/Definitions.php

        Args:
            rich_object:
                NextcloudTalkRichObject

            reference_id:
                A reference string to be able to identify the message again in a "get
                messages" request, should be a random sha256 (only available with
                chat-reference-id capability)

            actor_display_name:
                Guest display name (ignored for logged in users)

        Raises:
            NextcloudBadRequest: Invalid reference_id given.

        Returns:
            New Message, Headers

            Headers:
                x-chat-last-common-read	[int]	ID of the last message read by every user
                that has read privacy set to public. When the user themself has it set to
                private the value the header is not set (only available with
                chat-read-status capability and when last_common_read_id was sent)
        """
        return await self.chat_api.send_rich_object(room_token=self.token, **kwargs)

    class _ShareFileArgs(TypedDict):
        path: str
        metadata: ChatFileShareMetadata
        reference_id: NotRequired[str]

    async def share_file(self, **kwargs: Unpack[_ShareFileArgs]) -> int:  # noqa: D417
        """Share a file to the conversation.

        https://nextcloud-talk.readthedocs.io/en/latest/chat/#share-a-file-to-the-chat

        Args:
            path:
                The file path inside the user's root to share.

            reference_id:
                A reference string to be able to identify the generated chat message
                again in a "get messages" request, should be a random sha256 (only
                available with chat-reference-id capability)

            metadata:
                ChatFileShareMetadata:
                The only valid values for metadata.message_type are 'comment' and 'voice'.
                metadata.silent only valid with 'silent-send' capability.

        Raises:
            NextcloudBadRequest: Invalid reference_id given.

        Returns:
            Integer ID of new share.
        """
        return await self.chat_api.share_file(room_token=self.token, **kwargs)

    async def list_shared_items(self, limit: int) -> List[Message]:
        """List overview of items shared into this chat.

        Args:
            limit:
                Number of chat messages with shares you want to get

        Returns:
            List of Messages with shares.
        """
        return await self.chat_api.list_shared_items(room_token=self.token, limit=limit)

    class _SharedItemsByTypeArgs(TypedDict):
        object_type: SharedItemType
        last_known_message_id: int
        limit: int

    async def list_shared_items_by_type(  # noqa: D417
            self,
            **kwargs: Unpack[_SharedItemsByTypeArgs]) -> \
            Tuple[List[Message], httpx.Headers]:
        """List items of type shared in the chat.

        Args:
            object_type:
                SharedItemType

            last_known_message_id:
                Serves as an offset for the query. The last_known_message_id for the next
                page is available in the X-Chat-Last-Given header.

            limit:
                Number of chat messages with shares you want to get

        Returns:
            List of relevant Messages, Headers

            Headers:
                X-Chat-Last-Given [int] Offset for the next page.
        """
        return await self.chat_api.list_shared_items_by_type(
            room_token=self.token,
            **kwargs)

    async def clear_history(self) -> Message:
        """Clear the message history in this conversation.

        Returns:
            Message to display in empty channel.
        """
        return await self.chat_api.clear_history(room_token=self.token)

    async def delete_message(self, message_id: int) -> Tuple[Message, httpx.Headers]:
        """Delete a message in a conversation.

        https://nextcloud-talk.readthedocs.io/en/latest/chat/#deleting-a-chat-message
        https://github.com/nextcloud/spreed/blob/88d1e4b11872f96745201c6e8921e7848eab0be8/openapi-full.json#L6485

        Args:
            message_id:
                ID of message

        Returns:
            Message, Headers

            Headers:
                X-Chat-Last-Common-Read	[int] ID of the last message read by every user
                that has read privacy set to public. When the user themself has it set to
                private the value the header is not set (only available with
                chat-read-status capability)
        """
        return await self.chat_api.delete(room_token=self.token, message_id=message_id)

    class _EditMessageArgs(TypedDict):
        message_id: int
        message: str

    async def edit_message(  # noqa: D417
         self,
         **kwargs: Unpack[_EditMessageArgs]) -> Tuple[Message, httpx.Headers]:
        """Edit an existing message in a conversation.

        Args:
            message_id:
                ID of message

            message:
                New message text.

        Returns:
            New Message, Headers

            Headers:
                X-Chat-Last-Common-Read	[int] ID of the last message read by every user
                that has read privacy set to public. When the user themself has it set to
                private the value the header is not set (only available with
                chat-read-status capability)
        """
        return await self.chat_api.edit(room_token=self.token, **kwargs)

    async def set_message_reminder(
            self,
            message_id: int,
            timestamp: dt.datetime) -> MessageReminder:
        """Set reminder for chat message.

        Requires capability: remind-me-later

        Args:
            message_id:
                ID of message

            timestamp:
                DateTime for reminder.

        Returns:
            MessageReminder
        """
        return await self.chat_api.set_reminder(
            room_token=self.token,
            message_id=message_id,
            timestamp=timestamp)

    async def get_message_reminder(self, message_id: int) -> MessageReminder:
        """Get existing reminder for chat message.

        Requires capability: remind-me-later

        Args:
            message_id:
                ID of message

        Returns:
            MessageReminder
        """
        return await self.chat_api.get_reminder(
            room_token=self.token,
            message_id=message_id)

    async def delete_message_reminder(self, message_id: int) -> None:
        """Delete reminder for chat message.

        Requires capability: remind-me-later

        Args:
            message_id:
                ID of message
        """
        return await self.chat_api.delete_reminder(
            room_token=self.token,
            message_id=message_id)

    async def mark_as_read(self, last_read_message_id: int) -> None:
        """Mark conversation as read.

        Args:
            last_read_message_id:
                The last read message ID
                Only valid with chat-read-last capability.

        Returns:
            Headers:
                X-Chat-Last-Common-Read	[int] ID of the last message read by every user
                that has read privacy set to public. When the user themself has it set to
                private the value the header is not set (only available with
                chat-read-status capability)
        """
        await self.chat_api.mark_as_read(
            room_token=self.token,
            last_read_message_id=last_read_message_id)

    async def mark_as_unread(self) -> None:
        """Mark conversation as unread.

        Requires capability: chat-unread

        Returns:
            Headers:
                X-Chat-Last-Common-Read	[int] ID of the last message read by every user
                that has read privacy set to public. When the user themself has it set to
                private the value the header is not set (only available with
                chat-read-status capability)
        """
        await self.chat_api.mark_as_unread(room_token=self.token)

    class _SuggestAutocompletesArgs(TypedDict):
        search: str
        include_status: bool
        limit: int

    async def suggest_autocompletes(  # noqa: D417
            self,
            **kwargs: Unpack[_SuggestAutocompletesArgs]) -> List[Suggestion]:
        """Get mention autocomplete suggestions.

        Args:
            search:
                Search term for name suggestions (should at least be 1 character)

            include_status:
                Whether the user status information also needs to be loaded

            limit:
                Number of suggestions to receive (20 by default)

        Returns:
            List of Suggestions
        """
        return await self.chat_api.suggest_autocompletes(room_token=self.token, **kwargs)

    async def set_name_as_guest(self, name: str) -> None:
        """Set display name as a guest.

        Args:
            name:
                Your new name
        """
        await self.participants_api.set_guest_display_name(
            room_token=self.token,
            name=name)

    async def set_default_permissions(
            self,
            permissions: ParticipantPermissions,
            mode: ConversationPermissionMode = \
                  ConversationPermissionMode.default) -> None:
        """Set default permissions for participants of a conversation.

        Args:
            permissions:
                New permissions for the attendees, see ParticipantPermissions. If
                permissions are not 0 (default), the 1 (custom) permission will always be
                added. Note that this will reset all custom permissions that have been
                given to attendees so far.

            mode:
               ConversationPermissionMode, in case of .call the permissions will be reset
               to 0 (default) after the end of a call. (🏁 .call is no-op since Talk 20)
        """
        await self.api.set_default_permissions(
            room_token=self.token,
            permissions=permissions,
            mode=mode)

    async def participants_connected_to_call(self) -> List[Participant]:
        """Get list of connected participants.

        Returns:
            List of ParticipantData
        """
        response = await self.calls_api.get_connected_participants(self.token)
        return [Participant(data, self.talk_api) for data in response]

    class _JoinCallArgs(TypedDict):
        flags: ParticipantInCallFlags
        silent: bool
        recording_consent: bool

    async def join_call(self, **kwargs: Unpack[_JoinCallArgs]) -> None:  # noqa: D417
        """Join a call.

        Args:
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
        await self.calls_api.join_call(room_token=self.token, **kwargs)

    async def send_call_notification(self, user_id: str) -> None:
        """Send call notification.

        Requires capability: send-call-notification

        Args:
            user_id:
                Participant to notify.
        """
        await self.calls_api.send_notification(room_token=self.token, user_id=user_id)

    async def send_call_sip_dialout_request(self, user_id: str) -> None:
        """Send SIP dial-out request.

        Requires capability: sip-support-dialout

        Args:
            user_id:
                The participant to call
        """
        await self.calls_api.send_sip_dialout_request(
            room_token=self.token,
            user_id=user_id)

    async def update_call_flags(self, flags: ParticipantInCallFlags) -> None:
        """Update call flags.

        Args:
            flags:
                ParticipantInCallFlags
        """
        await self.calls_api.update_flags(room_token=self.token, flags=flags)

    async def leave_call(self, end_for_all: bool) -> None:
        """Leave a call (but staying in the conversation for future calls and chat).

        Args:
            end_for_all:
                If sent as a moderator, end the meeting and all participants leave the
                call.
        """
        await self.calls_api.leave(room_token=self.token, end_for_all=end_for_all)

    async def set_avatar_image(self, image_data: bytes) -> None:
        """Set conversations avatar.

        Args:
            room_token:
                Token of conversation

            image_data:
                Image data
        """
        await self.avatar_api.set_image(self.token, image_data=image_data)

    async def set_avatar_emoji(self, emoji: str, color: str) -> None:
        """Set emoji as avatar.

        Args:
            emoji:
                New emoji avatar

            color:
                HEX color code (6 times 0-9A-F) without the leading # character (omit to
                fallback to the default bright/dark mode icon background color)
        """
        await self.avatar_api.set_emoji(room_token=self.token, emoji=emoji, color=color)

    async def delete_avatar(self) -> None:
        """Delete conversation avatar.

        To determine if the delete option should be presented to the user, it's
        recommended to check the isCustomAvatar property of Conversation object.
        """
        await self.avatar_api.delete(room_token=self.token)

    async def get_avatar(self, dark_mode: bool) -> bytes:
        """Get conversations avatar (binary).

        Args:
            dark_mode:
                Whether to get Dark Mode version.

        Returns:
            Image data
        """
        return await self.avatar_api.get(room_token=self.token, dark_mode=dark_mode)

    class _GetFederatedAvatarArgs(TypedDict):
        cloud_id: str
        size: int
        dark_mode: bool

    async def get_federated_avatar(  # noqa: D417
            self,
            **kwargs: Unpack[_GetFederatedAvatarArgs]) -> bytes:
        """Get federated user avatar (binary).

        Args:
            cloud_id:
                Federation CloudID to get the avatar for

            size:
                Only 64 and 512 are supported

            dark_mode:
                Whether to get Dark Mode version.

        Returns:
            Image data
        """
        return await self.avatar_api.get_federated(room_token=self.token, **kwargs)

    class _CreatePollArgs(TypedDict):
        question: str
        options: List[str]
        result_mode: PollMode
        max_votes: int
        draft: bool

    async def create_poll(self, **kwargs: Unpack[_CreatePollArgs]) -> Poll:  # noqa: D417
        """Create a poll in the conversation.

        Args:
            question:
                The poll topic

            options:
                Voting options

            result_mode:
                PollMode

            max_votes:
                Maximum amount of options a participant can vote for

            draft:
                Whether or not to save this poll as a draft

        Returns:
            Poll object
        """
        return await self.polls_api.create(room_token=self.token, **kwargs)

    class _EditDraftPollArgs(TypedDict):
        question: str
        options: List[str]
        result_mode: PollMode
        max_votes: int

    async def edit_draft_poll(self, **kwargs: Unpack[_EditDraftPollArgs]) -> Poll:  # noqa: D417
        """Edit a draft poll in a conversation.

        Args:
            question:
                Poll topic

            options:
                Voting options

            result_mode:
                PollMode

            max_votes:
                Maximum amount of options a participant can vote for

        Returns:
            Poll object
        """
        return await self.polls_api.edit_draft(room_token=self.token, **kwargs)

    async def get_poll(self, poll_id: int) -> Poll:
        """Get state or result of a poll.

        Args:
            poll_id:
                Poll ID

        Returns:
            Poll object
        """
        return await self.polls_api.get(room_token=self.token, poll_id=poll_id)

    async def list_draft_polls(self) -> List[Poll]:
        """Get a list of all poll drafts in the conversation.

        Returns:
            List of Poll objets
        """
        return await self.polls_api.list_drafts(room_token=self.token)

    async def vote_on_poll(self, poll_id: int, votes: List[int]) -> None:
        """Vote on a poll.

        Args:
            poll_id:
                Poll ID

            votes:
                The option IDs the participant wants to vote for
        """
        await self.polls_api.vote(room_token=self.token, poll_id=poll_id, votes=votes)

    async def close_poll(self, poll_id: int) -> None:
        """Close a poll.

        Args:
             poll_id:
                Poll ID
        """
        await self.polls_api.close(room_token=self.token, poll_id=poll_id)

    async def list_installed_bots(self) -> List[Bot]:
        """Get list of bots installed on the server.

        This is an administrator-only method.

        Returns:
            List of Bot objects
        """
        return await self.bots_api.list_installed()

    async def list_bots(self) -> List[Bot]:
        """Get list of bots for the conversation.

        This is a moderator-level method.

        Returns:
            List of Bot objects
        """
        return await self.bots_api.list_conversation_bots(self.token)

    async def list_breakout_rooms(self) -> List['BreakoutRoom']:
        """Get breakout rooms.

        Get all (for moderators and in case of "free selection") or the assigned breakout
        room

        Returns:
            List of BreakoutRoom
        """
        return await self.api.list_breakout_rooms(self.token)

    class _ConfigureBreakoutRoomsArgs(TypedDict):
        mode: BreakoutRoomAssignmentMode
        num_rooms: int
        attendee_map: Dict[str, int]

    async def configure_breakout_rooms(  # noqa: D417
            self,
            **kwargs: Unpack[_ConfigureBreakoutRoomsArgs]) -> \
                Tuple['Conversation', List['BreakoutRoom']]:
        """Configure breakout rooms for Conversation.

        Args:
            mode:
                Participant assignment mode

            num_rooms:
                Number of breakout rooms to create

            attendee_map:
                A Dict of {attendeeId: room_number} (0 based)
                Only considered when the mode is BreakoutRoomAssignmentMode.manual

        Returns:
            Parent room and all breakout rooms.
        """
        response = await self.breakout_rooms_api.configure(
            room_token=self.token,
            **kwargs)
        return self._sort_room_types(response)

    class _CreateBreakoutRoomArgs(TypedDict):
            room_type: ConversationType
            object_type: RoomObjectType

    async def create_additional_breakout_room(  # noqa: D417
            self,
            **kwargs: Unpack[_CreateBreakoutRoomArgs]) -> 'BreakoutRoom':
        """Create a new breakout room in this conversation.

        Args:
            room_type:
                See constants.ConversationType

            object_type:
                RoomObjectType of an object this room references, currently only allowed
                value is room to indicate the parent of a breakout room

            object_id:
                Id of an object this room references, room token is used for the parent
                of a breakout room

        Returns:
            New Conversation object
        """
        response = await self.api.create(object_id=self.token, **kwargs)
        return BreakoutRoom(response.data, self.talk_api)

    async def remove_breakout_rooms(self) -> 'Conversation':
        """Remove breakout rooms from conversation.

        Returns:
            Parent Conversation object
        """
        return await self.breakout_rooms_api.remove(self.token)

    async def start_breakout_rooms(self) -> Tuple['Conversation', List['BreakoutRoom']]:
        """Start breakout rooms.

        Returns:
            Parent room and all breakout rooms.
        """
        return await self.breakout_rooms_api.start(self.token)

    async def stop_breakout_rooms(self) -> Tuple['Conversation', List['BreakoutRoom']]:
        """Stop breakout rooms for a conversation.

        Returns:
            Parent conversation and all breakout rooms.
        """
        return await self.breakout_rooms_api.stop(self.token)

    async def broadcast_breakout_rooms_message(self, message: str) -> None:
        """Broadcast message to all breakout rooms.

        Must be a moderator in parent Conversation.

        Args:
            message:
                Message to broadcast
        """
        return await self.breakout_rooms_api.broadcast_message(
            self.token,
            message=message)

    async def reorganize_breakout_room_attendees(
            self,
            attendee_map: Dict[str, int]) -> Tuple['Conversation', List['BreakoutRoom']]:
        """Reorganize attendees in breakout rooms.

        Args:
            attendee_map:
                A Dict of {attendeeId: room_number} (0 based)

        Returns:
            Parent conversation and all breakout rooms.
        """
        return await self.breakout_rooms_api.reorganize_attendees(
            room_token=self.token,
            attendee_map=attendee_map)

    async def switch_breakout_room(self, new_room: int) -> 'BreakoutRoom':
        """Switch breakout rooms.

        This endpoint allows participants to switch between breakout rooms when they are
        allowed to choose the breakout room and not are automatically or manually
        assigned by the moderator.

        Args:
            new_room:
                Token of new breakout room

        Returns:
            New breakout room.
        """
        return await self.breakout_rooms_api.switch_rooms(self.token, target=new_room)

    async def enable_lobby(self, reset_time: dt.datetime) -> None:
        """Enable lobby requirement for Conversation.

        Args:
            reset_time:
                Time at which to remove lobby requirement.
        """
        response = await self.webinars_api.set_lobby_state(
            self.token,
            WebinarLobbyState.lobby,
            reset_time)
        self.data = response

    async def disable_lobby(self) -> None:
        """Disable lobby requirement for Conversation."""
        response = await self.webinars_api.set_lobby_state(
            self.token,
            WebinarLobbyState.no_lobby)
        self.data = response

    async def enable_sip_dialin(self) -> None:
        """Enable SIP dialin for webinar."""
        response = await self.webinars_api.set_sip_dialin(self.token, SipState.enabled)
        self.data = response

    async def disable_sip_dialin(self) -> None:
        """Disable SIP dialin for webinar."""
        response = await self.webinars_api.set_sip_dialin(self.token, SipState.disabled)
        self.data = response

    async def get_signaling_settings(self) -> Dict[str, Any]:
        """Get signaling settings."""
        return await self.signaling_api.get_settings(self.token)

    async def join(
            self,
            password: Optional[str] = None,
            force: bool = True) -> 'Conversation':
        """Join a conversation.

        Args:
            password:
                Optional: Password is only required for users which are self joined or
                guests and only when the conversation has hasPassword set to true.

            force:
                If set to false and the user has an active session already a 409 Conflict
                will be returned (Default: true - to keep the old behaviour)

        Returns:
            Conversation object
        """
        response = await self.participants_api.join(
            self.token,
            password=password,
            force=force)
        return Conversation(response, self.talk_api)

class Conversations(NextcloudModule):
    """Nextcloud Talk Conversations API.

    https://nextcloud-talk.readthedocs.io/en/latest/conversation/

    This is your entry-point into the Talk/Spreed back-end.
    """
    api: NextcloudTalkApi

    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '4') -> None:

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

        Args:
            status_update:
                Whether the "online" user status of the current user should
                be "kept-alive" or not.

            include_status:
                Whether the user status information of all one-to-one
                conversations should be loaded.

        Returns:
            List of conversation objects.

        Raises:
            Appropriate exception on HTTP status_code >= 400
        """
        data: Dict[str, Any] = {
            'noStatusUpdate': 1 if status_update else 0,
            'includeStatus': include_status}
        response, _ = await self._get(
            path='/room',
            data=data)

        return [Conversation(data, self.api) for data in response]

    async def create(
            self,
            room_type: ConversationType,
            invite: str = '',
            room_name: str = '',
            object_type: Optional[RoomObjectType] = None,
            object_id: Optional[str] = None,
            source: str = '') -> Conversation:
        """Create a new conversation.

        Args:
            room_type:
                See constants.ConversationType

            invite:
                Object ID to invite, dependent on room_type

            room_name:
                Conversation Name (not valid for roomType = ConversationType.one_to_one)

            object_type:
                RoomObjectType of an object this room references, currently only allowed
                value is room to indicate the parent of a breakout room

            object_id:
                Id of an object this room references, room token is used for the parent
                of a breakout room

            source:
                The source for the invite, only supported with ConversationType.group
                for groups and circles (only available with 'circles-support' capability)

        Returns:
            New Conversation object
        """
        data: Dict[str, Any] = {
            'roomType': room_type.value,
            'invite': invite,
            'source': source,
            'roomName': room_name}

        if object_type:
            data.update({'objectType': object_type})
        if object_id:
            data.update({'objectId': object_id})

        response, _ = await self._post(path='/room', data=data)
        return Conversation(response, self.api)

    async def get(self, room_token: str) -> Conversation:
        """Get a specific conversation.

        Args:
            room_token:
                The room token to get.

        Returns:
            Conversation object.
        """
        data, _ = await self._get(path=f'/room/{room_token}')
        return Conversation(data, self.api)

    async def get_note_to_self(self) -> Conversation:
        """Get special note-to-self channel.

        Returns:
            Conversation object.
        """
        data, _ = await self._get(path='/room/note-to-self')
        return Conversation(data, self.api)

    async def list_open(self) -> List[Conversation]:
        """Get list of open joinable rooms.

        Returns:
            List of open Conversation objects.
        """
        response, _ = await self._get(path='/listed-room')
        return [Conversation(data, self.api) for data in response]

    async def list_breakout_rooms(self, room_token: str) -> List['BreakoutRoom']:
        """List breakout rooms associated with a conversation.

        Requires 'breakout-rooms-v1' capability.

        Returns:
            List of BreakoutRoom objects.
        """
        await self.api.require_talk_feature('breakout-rooms-v1')
        response, _ = await self._get(path=f'/{room_token}/breakout-rooms')
        return [BreakoutRoom(data, self.api) for data in response]

    async def rename(self, room_token: str, new_name: str) -> None:
        """Rename a Conversation.

        Args:
            room_token:
                Token of conversation to rename.

            new_name:
                New displayName
        """
        await self._put(
            path=f'/room/{room_token}',
            data={'roomName': new_name})

    async def delete(self, room_token: str) -> None:
        """Delete a conversation.

        Args:
            room_token:
                Token of conversation to delete.
        """
        await self._delete(path=f'/room/{room_token}')

    async def set_description(self, room_token: str, description: str) -> None:
        """Set description on a conversation.

        Requires 'room-description' capability.

        Args:
            room_token:
                Token of conversation to set.

            description:
                New description.
        """
        await self.api.require_talk_feature('room-description')
        await self._put(
            path=f'/room/{room_token}/description',
            data={'description': description})

    async def allow_guests(self, room_token: str, password: Optional[str]= None) -> None:
        """Allow guests into a conversation.

        Args:
            room_token:
                Token of conversation

            password:
                Require guests to provide this password to join.  Requires
                'conversation-creation-password' capability.
        """
        data: Dict[str, str] = {}
        if password:
            await self.api.require_talk_feature('conversation-creation-password')
            data = {'password': password}

        await self._post(path=f'/room/{room_token}/public', data=data)

    async def disallow_guests(self, room_token: str) -> None:
        """Disallow guests in a conversation.

        Args:
            room_token:
                Token of conversation
        """
        await self._delete(path=f'/room/{room_token}/public')

    async def read_only(self, room_token: str, state: ConversationReadOnlyState) -> None:
        """Set read-only status of a conversation.

        Requires 'read-only-rooms' capability.

        Args:
            room_token:
                Token of the conversation.

            state:
                ConversationReadOnlyState
        """
        await self.api.require_talk_feature('read-only-rooms')
        await self._put(path=f'/room/{room_token}/read-only', data={'state': state.value})

    async def set_conversation_password(self, token: str, password: str) -> None:
        """Set a password on a conversation.

        Args:
            token:
                Token of conversation.

            password:
                The new password.
        """
        await self._put(
            path=f'/room/{token}/password',
            data={'password': password})

    async def set_default_permissions(
            self,
            room_token: str,
            permissions: ParticipantPermissions,
            mode: ConversationPermissionMode = \
                  ConversationPermissionMode.default) -> None:
        """Set default permissions for participants of a conversation.

        Args:
            room_token:
                Token of conversation.

            permissions:
                New permissions for the attendees, see ParticipantPermissions. If
                permissions are not 0 (default), the 1 (custom) permission will always be
                added. Note that this will reset all custom permissions that have been
                given to attendees so far.

            mode:
               ConversationPermissionMode, in case of .call the permissions will be reset
               to 0 (default) after the end of a call. (🏁 .call is no-op since Talk 20)
        """
        data: Dict[str, Any] = {
            'mode': mode,
            'permissions': permissions.value}
        await self._put(
            path=f'/room/{room_token}/permissions/{mode}', data=data)

    async def add_to_favorites(self, room_token: str) -> None:
        """Add a conversation to user favorites.

        Requires 'favorites' capability.

        Args:
            room_token:
                Token of conversation.
        """
        await self.api.require_talk_feature('favorites')
        await self._post(path=f'/room/{room_token}/favorite')

    async def remove_from_favorites(self, room_token: str) -> None:
        """Remove conversation from user favorites.

        Requires 'favorites' capability.

        Args:
            room_token:
                Token of conversation.
        """
        await self.api.require_talk_feature('favorites')
        await self._delete(path=f'/room/{room_token}/favorites')

    async def set_notification_level(
            self,
            token: str,
            notification_level: ConversationNotificationLevel) -> None:
        """Set notification level for a conversation.

        Requires capability: notification-levels

        Args:
            token:
                Token of conversation.

            notification_level:
                NotificationLevel
        """
        await self._post(
            path=f'/room/{token}/notify',
            data={'level': notification_level.value})

    async def set_call_notification_level(
            self,
            room_token: str,
            notification_level: CallNotificationLevel) -> None:
        """Set notification level for calls in a conversation.

        Requires capability: notification-calls

        Args:
            room_token:
                Token of conversation.

            notification_level:
                CallNotificationLevel
        """
        await self.api.require_talk_feature('notification-calls')
        await self._post(
            path=f'/room/{room_token}/notify-calls',
            data={'level': notification_level.value})

    async def set_message_expiration(
            self,
            room_token: str,
            seconds: int) -> None:
        """Set automatic message expiration for conversation.

        Requires capability: message-expiration

        Args:
            room_token:
                Token of conversation.

            seconds:
                Number of seconds before deleting messages.  If is 0, messages will not
                be deleted automatically.
        """
        await self.api.require_talk_feature('message-expiration')
        await self._post(
            path=f'/room/{room_token}/message-expiration',
            data={'seconds': seconds})

    async def set_recording_consent(
            self,
            room_token: str,
            consent_required: bool = True) -> None:
        """Set recording-consent requirement on a conversation.

        Requires capability: recording-consent

        Args:
            room_token:
                Token of conversation

            consent_required:
                New consent setting for the conversation
        """
        await self.api.require_talk_feature('recording-consent')
        await self._put(
            path=f'/room/{room_token}/recording-consent',
            data={'recordingConsent': bool2int(consent_required)})

    async def set_scope(
            self,
            room_token: str,
            scope: ListableScope) -> None:
        """Set scope of a conversation.

        Use this to modify visibility of this room to all users.

        Requires capability: listable-rooms

        Args:
            room_token:
                Token of conversation

            scope:
                ListableScope
        """
        await self.api.require_talk_feature('listable-rooms')
        await self._put(
            path=f'/room/{room_token}/listable',
            data={'scope': scope.value})

    async def set_mention_permissions(
            self,
            room_token: str,
            permissions: MentionPermissions) -> None:
        """Set mention permissions for this conversation.

        Requires capability: mention-permissions

        Args:
            room_token:
                Token of conversation

            permissions:
                MentionPermissions
        """
        await self.api.require_talk_feature('mention-permissions')
        await self._put(
            path=f'/room/{room_token}/mention-permissions',
            data={'mentionPermissions': permissions.value})

    async def get_conversation_for_internal_file(self, file_id: int) -> Conversation:
        """Return conversation token for discussion of internal file.

        Args:
            file_id:
                ID of file

        Returns:
            Conversation token
        """
        return await self.integrations_api.get_interal_file_chat(file_id)

    async def get_token_for_shared_file(self, share_token: str) -> Conversation:
        """Return conversationtoken for discussion of shared file.

        Args:
            share_token:
                Share token.

        Returns:
            Conversation token
        """
        return await self.integrations_api.get_public_file_share_chat(share_token)

    async def create_password_request(self, share_token: str) -> Dict[str, str]:
        """Create a conversation to request the password for a public share.

        Args:
            share_token:
                Share token

        Returns:
            Dictionary
                token:  The token of the conversation for this file
                name:   A technical name for the conversation
                displayName: The visual name of the conversation
        """
        return await self.integrations_api.create_password_request_conversation(
            share_token)

    class _JoinArgs(TypedDict):
        room_token: str
        password: Optional[str]
        force: bool

    async def join(self, **kwargs: Unpack[_JoinArgs]) -> Conversation:  # noqa: D417
        """Join a conversation.

        Args:
            password:
                Optional: Password is only required for users which are self joined or
                guests and only when the conversation has hasPassword set to true.

            force:
                If set to false and the user has an active session already a 409 Conflict
                will be returned (Default: true - to keep the old behaviour)

        Returns:
            Conversation
        """
        response = await self.participants_api.join(**kwargs)
        return Conversation(response, self.api)
