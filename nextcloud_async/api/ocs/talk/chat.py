"""Nextcloud Talk Conversations API.

https://nextcloud-talk.readthedocs.io/en/latest/conversation/
"""
import httpx
import json
import datetime as dt
from dataclasses import dataclass, field

from typing import Dict, Optional, List, Tuple, Any

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule
from nextcloud_async.exceptions import NextcloudBadRequestError
from nextcloud_async.helpers import bool2int, filter_headers

from .reactions import Reactions, Reaction
from .rich_objects import NextcloudTalkRichObject
from .constants import SharedItemType

_HASH_LENGTH = 64


@dataclass
class ChatFileShareMetadata:
    message_type: SharedItemType
    caption: str
    reply_to: Optional[int] = field(default=None)
    silent: bool = field(default=False)


@dataclass
class Message:
    data: Dict[str, Any]
    talk_api: NextcloudTalkApi

    def __post_init__(self) -> None:
        self._reactions: List[Reaction] = []
        self.chat_api = Chat(self.talk_api)
        self.reaction_api = Reactions(self.talk_api)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<Talk Message from {self.actorDisplayName} at {self.timestamp}>'

    def __repr__(self) -> str:
        return str(self.data)

    @property
    def reactions(self) -> List[Reaction]:
        """Property wrapper for lazy loading reactions.

        Returns:
            List of reactions to message
        """
        if not self._reactions:
            self._pop_reactions
        return self._reactions

    async def _pop_reactions(self) -> None:
        self._reactions = await self.get_reactions()

    async def add_reaction(self, reaction: str) -> None:
        """Add reaction to this message.

        Args:
            reaction:
                Reaction emoji to add
        """
        response = await self.reaction_api.add(
            room_token=self.token,
            message_id=self.id,
            reaction=reaction)
        self._reactions = response

    async def remove_reaction(self, reaction: str) -> None:
        """Remove reaction from this message.

        Args:
            reaction:
                Reaction emoji to remove
        """
        response = await self.reaction_api.delete(
            room_token=self.token,
            message_id=self.id,
            reaction=reaction)
        self._reactions = response

    async def set_reminder(self, timestamp: dt.datetime) -> 'MessageReminder':
        """Set reminder for this message.

        Requires capability: remind-me-later

        Args:
            timestamp:
                DateTime for reminder.

        Returns:
            MessageReminder
        """
        reminder = await self.chat_api.set_reminder(
            self.token,
            self.message_id,
            timestamp)
        self._reminder = reminder
        return reminder

    async def get_reminder(self) -> 'MessageReminder':
        """Get existing reminder for this message.

        Requires capability: remind-me-later

        Returns:
            MessageReminder
        """
        if not self._reminder:
            return await self.chat_api.get_reminder(self.token, self.message_id)
        return self._reminder

    async def delete_reminder(self) -> None:
        """Delete reminder for this message.

        Requires capability: remind-me-later
        """
        await self.chat_api.delete_reminder(self.token, self.message_id)

    async def delete(self) -> httpx.Headers:
        """Delete this message.

        Returns:
            Header: 'X-Chat-Last-Common-Read'
        """
        message, headers = await self.chat_api.delete(
            room_token=self.token,
            message_id=self.id)
        self.data = message.data
        return headers

    async def get_reactions(self, reaction: Optional[str] = None) -> List[Reaction]:
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
        response = await self.reaction_api.list(self.token, self.id, reaction)
        self._reactions = response
        return response


@dataclass
class MessageReminder:
    data: Dict[str, Any]

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<MessageReminder {self.userId}>'

    def __repr__(self) -> str:
        return str(self.data)


    @property
    def user_id(self) -> str:
        """Alias for self.userId.

        Returns:
            self.userId
        """
        return self.userId

    @property
    def message_id(self) -> int:
        """Alias for self.messageId.

        Returns:
            self.messageId
        """
        return self.messageId


@dataclass
class Suggestion:
    data: Dict[str, Any]

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<Mention Suggestion {self.userId}>'

    def __repr__(self) -> str:
        return str(self.data)


    @property
    def mention_id(self) -> str:
        """Alias for self.mentionId.

        Returns:
            self.mentionId
        """
        return self.mentionId

    @property
    def status_icon(self) -> str:
        """Alias for self.statusIcon.

        Returns:
            self.statusIcon
        """
        return self.statusIcon

    @property
    def status_message(self) -> str:
        """Alias for self.statusMessage.

        Returns:
            self.statusMessage
        """
        return self.statusMessage


class Chat(NextcloudModule):
    """Interact with Nextcloud Talk Chat API."""

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '1') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    async def get_messages(
            self,
            room_token: str,
            look_into_future: bool = False,
            limit: int = 100,
            timeout: int = 30,
            last_known_message_id: Optional[int] = None,
            last_common_read_id: Optional[int] = None,
            set_read_marker: bool = True,
            include_last_known: bool = False,
            no_status_update: bool = False,
            mark_notifications_as_read: bool = True,
        ) -> Tuple[List[Message], httpx.Headers]:
        """Receive messages from a conversation.

        https://nextcloud-talk.readthedocs.io/en/latest/chat/#receive-chat-messages-of-a-conversation
        https://github.com/nextcloud/spreed/blob/88d1e4b11872f96745201c6e8921e7848eab0be8/openapi-full.json#L5659


        Args:
            room_token:
                Conversation token

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
        return_headers: List[str] = ['x-chat-last-given', 'x-chat-last-common-read']
        data = {
            'lookIntoFuture': bool2int(look_into_future),
            'limit': limit,
            'timeout': timeout,
            'setReadMaker': bool2int(set_read_marker),
            'includeLastKnown': bool2int(include_last_known),
            'noStatusUpdate': bool2int(no_status_update)}
        if last_known_message_id:
            data['lastKnownMessageId'] = last_known_message_id
        if last_common_read_id:
            data['lastCommonReadId'] = last_common_read_id

        if mark_notifications_as_read is False:
            await self.api.require_talk_feature('chat-keep-notifications')

        response, headers = await self._get(
            path=f'/chat/{room_token}',
            data=data)
        return \
            [Message(data, self.api) for data in response], \
            filter_headers(return_headers, headers)

    async def get_context(
            self,
            room_token: str,
            message_id: int,
            limit: int = 50) -> Tuple[List[Message], httpx.Headers]:
        """Get context around a message.

        Requires Capability: chat-get-context
        Args:
            room_token:
                Conversation token

            message_id:
                Message ID

            limit:
                Number of chat messages to receive into each direction (50 by default,
                100 at most)

        Returns:
            Messages
        """
        await self.api.require_talk_feature('chat-get-context')
        response, headers = await self._get(
            path=f'/chat/{room_token}/{message_id}/context',
            data={'limit': limit})
        return_headers: List[str] = ['x-chat-last-given', 'x-chat-last-common-read']
        return \
            [Message(data, self.api) for data in response], \
            filter_headers(return_headers, headers)

    async def send(
            self,
            room_token: str,
            message: str,
            reply_to: int = 0,
            display_name: Optional[str] = None,
            reference_id: Optional[str] = None,
            silent: bool = False) -> Tuple[Message, httpx.Headers]:
        """Send message to a conversation.

        Args:
            room_token:
                Token of conversation

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
        return_headers: List[str] = ['x-chat-last-common-read']

        data: Dict[str, Any] = {
            "message": message,
            "actorDisplayName": display_name,
            "replyTo": reply_to}

        if silent:
            await self.api.require_talk_feature('silent-send')
            data.update({"silent": silent})

        if reference_id:
            await self.api.require_talk_feature('chat-reference-id')
            if len(reference_id) != _HASH_LENGTH:
                raise NextcloudBadRequestError()
            else:
                data['referenceId'] = reference_id

        response, headers = await self._post(
            path=f'/chat/{room_token}',
            data=data)

        return Message(response, self.api), filter_headers(return_headers, headers)

    async def send_rich_object(
            self,
            room_token: str,
            rich_object: NextcloudTalkRichObject,
            reference_id: Optional[str] = None,
            actor_display_name: Optional[str] = None) -> Tuple[Message, httpx.Headers]:
        """Share a rich object to the conversation.

        https://github.com/nextcloud/server/blob/master/lib/public/RichObjectStrings/Definitions.php

        Args:
            room_token:
                Token of conversation

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
        await self.api.require_talk_feature('rich-object-sharing')
        return_headers = ['x-chat-last-common-read']
        data = {
            'objectType': rich_object.object_type,
            'objectId': rich_object.id,
            'metaData': json.dumps(rich_object.metadata),
            'actorDisplayName': actor_display_name}

        if reference_id:
            await self.api.require_talk_feature('chat-reference-id')
            if len(reference_id) != _HASH_LENGTH:
                raise NextcloudBadRequestError()
            else:
                data['referenceId'] = reference_id

        response, headers = await self._post(
            path=f'/chat/{room_token}/share',
            data=data)
        return Message(response, self.api), filter_headers(return_headers, headers)


    async def share_file(
            self,
            room_token: str,
            path: str,
            metadata: ChatFileShareMetadata,
            reference_id: Optional[str] = None) -> int:
        """Share a file to the conversation.

        https://nextcloud-talk.readthedocs.io/en/latest/chat/#share-a-file-to-the-chat

        Args:
            room_token:
                Token of conversation.

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
        if metadata.silent:
            await self.api.require_talk_feature('silent-send')
        data: Dict[str, Any] = {
            'shareType': 10,
            'shareWith': room_token,
            'path': path,
            'talkMetaData': {
                'messageType': metadata.message_type,
                'caption': metadata.caption,
                'replyTo': metadata.reply_to,
                'silent': metadata.silent}}

        if reference_id:
            await self.api.require_talk_feature('chat-reference-id')
            if len(reference_id) != _HASH_LENGTH:
                raise NextcloudBadRequestError()
            else:
                data['referenceId'] = reference_id

        response = await self._post(
            path=r'../../../files_sharing/api/v1/shares',
            data=data)

        return response

    async def list_shared_items(
            self,
            room_token: str,
            limit: int = 7) -> List[Message]:
        """List overview of items shared into a chat.

        Args:
            room_token:
                Token of room

            limit:
                Number of chat messages with shares you want to get

        Returns:
            List of Messages with shares.
        """
        await self.api.require_talk_feature('rich-object-list-media')
        response, _ = await self._get(
            path=f'/chat/{room_token}/share/overview',
            data = {'limit': limit})

        return [Message(data, self.api) for data in response]

    async def list_shared_items_by_type(
            self,
            room_token: str,
            object_type: SharedItemType,
            last_known_message_id: int,
            limit: int = 7) -> Tuple[List[Message], httpx.Headers]:
        """List items of type shared in a chat.

        Args:
            room_token:
                Token of conversation.

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
        return_headers = ['x-chat-last-given']

        await self.api.require_talk_feature('rich-object-list-media')
        data: Dict[str, Any] = {
            'objectType': object_type.value,
            'lastKnownMessageId': last_known_message_id,
            'limit': limit}

        response, headers = await self._get(
            path=f'/chat/{room_token}/share',
            data=data)
        messages = [Message(data, self.api) for data in response]
        return messages, filter_headers(return_headers, headers)

    async def clear_history(
            self,
            room_token: str) -> Message:
        """Clear the message history in a conversation.

        Args:
            room_token:
                Token of conversation.

        Returns:
            Message to display in empty channel.
        """
        await self.api.require_talk_feature('clear-history')
        response = await self._delete(path=f'/chat/{room_token}')
        return Message(response, self.api)

    async def delete(
            self,
            room_token: str,
            message_id: int) -> Tuple[Message, httpx.Headers]:
        """Delete a message in a conversation.

        https://nextcloud-talk.readthedocs.io/en/latest/chat/#deleting-a-chat-message
        https://github.com/nextcloud/spreed/blob/88d1e4b11872f96745201c6e8921e7848eab0be8/openapi-full.json#L6485

        Args:
            room_token:
                Token of conversation.

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
        return_headers = ['x-chat-last-common-read']

        await self.api.require_talk_feature('delete-messages')
        response, headers = await self._delete(path=f'/chat/{room_token}/{message_id}')
        return Message(response, self.api), filter_headers(return_headers, headers)

    async def edit(
            self,
            room_token: str,
            message_id: int,
            message: str) -> Tuple[Message, httpx.Headers]:
        """Edit an existing message in a conversation.

        Args:
            room_token:
                Token of conversation.

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
        return_headers = ['x-chat-last-common-read']

        await self.api.require_talk_feature('edit-messages')
        response, headers = await self._put(
            path=f'/chat/{room_token}/{message_id}',
            data={'message': message})

        return Message(response, self.api), filter_headers(return_headers, headers)

    async def set_reminder(
            self,
            room_token: str,
            message_id: int,
            timestamp: dt.datetime) -> MessageReminder:
        """Set reminder for chat message.

        Requires capability: remind-me-later

        Args:
            room_token:
                Token of conversation.

            message_id:
                ID of message

            timestamp:
                DateTime for reminder.

        Returns:
            MessageReminder
        """
        await self.api.require_talk_feature('remind-me-later')
        response, _ = await self._post(
            path=f'/chat/{room_token}/{message_id}/reminder',
            data={'timestamp': int(timestamp.timestamp())})

        return MessageReminder(response)

    async def get_reminder(
            self,
            room_token: str,
            message_id: int) -> MessageReminder:
        """Get existing reminder for chat message.

        Requires capability: remind-me-later

        Args:
            room_token:
                Token of conversation.

            message_id:
                ID of message

        Returns:
            MessageReminder
        """
        await self.api.require_talk_feature('remind-me-later')
        response, _ = await self._get(
            path=f'/chat/{room_token}/{message_id}/reminder')

        return MessageReminder(response)

    async def delete_reminder(
            self,
            room_token: str,
            message_id: int) -> None:
        """Delete reminder for chat message.

        Requires capability: remind-me-later

        Args:
            room_token:
                Token for conversation

            message_id:
                ID of message
        """
        await self.api.require_talk_feature('remind-me-later')
        await self._delete(path=f'/chat/{room_token}/{message_id}/reminder')

    async def mark_as_read(
            self,
            room_token: str,
            last_read_message_id: Optional[int] = None) -> httpx.Headers:
        """Mark conversation as read.

        Args:
            room_token:
                Token of conversation.

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
        return_headers = ['x-chat-last-common-read']
        await self.api.require_talk_feature('chat-read-marker')
        data: Dict[str, Any] = {}
        if last_read_message_id:
            await self.api.require_talk_feature('chat-read-last')
            data = {'lastReadMessage': last_read_message_id}

        _, headers = await self._post(path=f'/chat/{room_token}/read', data=data)
        return filter_headers(return_headers, headers)

    async def mark_as_unread(
            self,
            room_token: str) -> httpx.Headers:
        """Mark conversation as unread.

        Requires capability: chat-unread

        Args:
            room_token:
                Token of conversation.

        Returns:
            Headers:
                X-Chat-Last-Common-Read	[int] ID of the last message read by every user
                that has read privacy set to public. When the user themself has it set to
                private the value the header is not set (only available with
                chat-read-status capability)
        """
        return_headers = ['x-chat-last-common-read']
        await self.api.require_talk_feature('chat-unread')
        _, headers = await self._delete(path=f'/chat/{room_token}/read')
        return filter_headers(return_headers, headers)

    async def suggest_autocompletes(
            self,
            room_token: str,
            search: str,
            include_status: bool = False,
            limit: int = 20) -> List[Suggestion]:
        """Get mention autocomplete suggestions.

        Args:
            room_token:
                Token of conversation

            search:
                Search term for name suggestions (should at least be 1 character)

            include_status:
                Whether the user status information also needs to be loaded

            limit:
                Number of suggestions to receive (20 by default)

        Returns:
            List of Suggestions
        """
        data: Dict[str, Any] = {
            'search': search,
            'includeStatus': include_status,
            'limit': limit}
        response, _ = await self._get(
            path=f'/chat/{room_token}/mentions',
            data=data)

        return [Suggestion(data) for data in response]
