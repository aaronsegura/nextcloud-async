"""Nextcloud Talk Conversations API.

    https://nextcloud-talk.readthedocs.io/en/latest/conversation/
"""
import httpx
import json
import datetime as dt
from dataclasses import dataclass

from typing import Dict, Optional, List, Tuple, Any

from nextcloud_async import NextcloudClient
from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule
from nextcloud_async.exceptions import NextcloudNotCapable, NextcloudBadRequest
from nextcloud_async.helpers import bool2int, filter_headers

from .reactions import Reactions
from .rich_objects import NextcloudTalkRichObject
from .constants import SharedItemType


@dataclass
class Message:
    data: Dict[str, Any]
    chat_api: 'Chat'

    def __post_init__(self):
        self.reaction_api = Reactions(self.chat_api.client, self.chat_api.api)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Talk Message {self.data}>'
        #return f'<Talk Message from {self.actorDisplayName} at {self.timestamp}>'

    def __repr__(self):
        return str(self)

    async def add_reaction(self, reaction: str):
        await self.reaction_api.add(room_token=self.token, message_id=self.id, reaction=reaction)

    async def remove_reaction(self, reaction: str):
        await self.reaction_api.delete(room_token=self.token, message_id=self.id, reaction=reaction)

    # @classmethod
    # async def init(
    #         cls,
    #         api: 'Chat',
    #         data: Dict[str, Any]):
    #     return cls(
    #         api=api,
    #         data=data)

@dataclass
class MessageReminder:
    userId: str
    token: str
    messageId: int
    timestamp: int

    @property
    def user_id(self):
        return self.userId

    @property
    def message_id(self):
        return self.messageId

@dataclass
class Suggestion:
    mentionId: Optional[str]
    id: str
    label: str
    source: str
    status: Optional[str]
    statusIcon: Optional[str]
    statusMessage: Optional[str]
    details: Optional[str]

    @property
    def mention_id(self):
        return self.mentionId

    @property
    def status_icon(self):
        return self.statusIcon

    @property
    def status_message(self):
        return self.statusMessage


class Chat(NextcloudModule):
    """Interact with Nextcloud Talk Chat API."""

    def __init__(
            self,
            client: NextcloudClient,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '1'):
        self.client: NextcloudClient = client
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api  # type: ignore

    @classmethod
    async def init(
            cls,
            client: NextcloudClient,
            skip_capabilities: bool = False):
        api = await NextcloudTalkApi.init(client, skip_capabilities=skip_capabilities, ocs_version='2')

        return cls(client, api)

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
            mark_notifications_as_read: bool = True) -> Tuple[List[Message], httpx.Headers]:
        """Receive chat messages of a conversation.

        More info:
            https://nextcloud-talk.readthedocs.io/en/latest/chat/#receive-chat-messages-of-a-conversation
            https://github.com/nextcloud/spreed/blob/88d1e4b11872f96745201c6e8921e7848eab0be8/openapi-full.json#L5659

        Method: GET
        Endpoint: /chat/{token}

        #### Arguments:
        look_into_future	[bool]	1 Poll and wait for new message or 0 get history
        of a conversation

        limit	[int]	Number of chat messages to receive (100 by default, 200 at most)

        last_known_message	[int]	Serves as an offset for the query. The lastKnownMessageId
        for the next page is available in the x-chat-last-given header.

        last_common_read	[int]	Send the last x-chat-last-common-read header you got, if
        you are interested in updates of the common read value. A 304 response does not allow
        custom headers and otherwise the server can not know if your value is modified or not.

        timeout	[int]	$lookIntoFuture = 1 only, Number of seconds to wait for new messages
        (30 by default, 60 at most)

        set_read_marker	[bool]	True to automatically set the read timer after fetching the
        messages, use False when your client calls Mark chat as read manually. (Default: True)

        include_last_known    [bool]	True to include the last known message as well (Default:
        False)

        no_status_update    [bool]  When the user status should not be automatically set to online
        set to 1 (default 0)


        #### Exceptions:
        304 Not Modified When there were no older/newer messages

        404 Not Found When the conversation could not be found for the participant

        412 Precondition Failed When the lobby is active and the user is not a moderator

        #### Response Header:

        x-chat-last-given	[int]	Offset (lastKnownMessageId) for the next page.
        x-chat-last-common-read	[int]	ID of the last message read by every user that has
        read privacy set to public. When the user themself has it set to private the value
        the header is not set (only available with chat-read-status capability and when
        lastCommonReadId was sent)

        #### Response Data (As Message() object attributes):
        id	[int]	ID of the comment

        token	[str]	Conversation token

        actorType	[str]	See Constants - Actor types of chat messages

        actorId	[str]	Actor id of the message author

        actorDisplayName	[str]	Display name of the message author

        timestamp	[int]	Timestamp in seconds and UTC time zone

        systemMessage	[str]	empty for normal chat message or the type of the system message
        (untranslated)

        messageType	[str]	Currently known types are comment, comment_deleted, system
        and command

        isReplyable	[bool]	True if the user can post a reply to this message (only available
        with chat-replies capability)

        referenceId	[str]	A reference string that was given while posting the message to be
        able to identify a sent message again (available with chat-reference-id capability)

        message	[str]	Message string with placeholders (see Rich Object String)

        messageParameters	[array]	Message parameters for message (see Rich Object String)

        parent	[array]	Optional: See Parent data below

        reactions	[array]	Optional: An array map with relation between reaction emoji and
        total count of reactions with this emoji

        reactionsSelf	[array]	Optional: When the user reacted this is the list of emojis
        the user reacted with
        """
        return_headers: List[str] = ['x-chat-last-given', 'x-chat-last-common-read']
        data = {
            'lookIntoFuture': bool2int(look_into_future),
            'limit': limit,
            'timeout': timeout,
            'setReadMaker': bool2int(set_read_marker),
            'includeLastKnown': bool2int(include_last_known),
            'noStatusUpdate': bool2int(no_status_update)
        }
        if last_known_message_id:
            data['lastKnownMessageId'] = last_known_message_id
        if last_common_read_id:
            data['lastCommonReadId'] = last_common_read_id

        if mark_notifications_as_read is False and not self.api.has_capability('chat-keep-notifications'):
            raise NextcloudNotCapable()

        response, headers = await self._get(
            path=f'/chat/{room_token}',
            data=data)
        return [Message(data, self) for data in response], filter_headers(return_headers, headers)

    async def get_context(
            self,
            room_token: str,
            message_id: int,
            limit: int = 50) -> Tuple[List[Message], httpx.Headers]:
        response, headers = await self._get(
            path=f'/chat/{room_token}/{message_id}/context',
            data={'limit': limit})
        return_headers: List[str] = ['x-chat-last-given', 'x-chat-last-common-read']
        return [Message(data, self) for data in response], filter_headers(return_headers, headers)

    async def send(
            self,
            room_token: str,
            message: str,
            reply_to: int = 0,
            display_name: Optional[str] = 'Guest',
            reference_id: Optional[str] = None,
            silent: bool = False) -> Tuple[Message, httpx.Headers]:
        """Sending a new chat message

        Method: POST
        Endpoint: /chat/{token}
        Data:

        #### Arguments:
        message	[str]	The message the user wants to say

        actorDisplayName	[str]	Guest display name (ignored for logged in users)

        replyTo	[int]	The message ID this message is a reply to (only allowed for
                        messages from the same conversation and when the message type
                        is not system or command)

        referenceId	[str]	A reference string to be able to identify the message
                                again in a "get messages" request, should be a random
                                sha256 (only available with chat-reference-id capability)

        silent	[bool]	If sent silent the message will not create chat notifications
                        even for mentions (only available with silent-send capability)

        #### Exceptions:
        400 Bad Request In case of any other error

        403 Forbidden When the conversation is read-only

        404 Not Found When the conversation could not be found for the participant

        412 Precondition Failed When the lobby is active and the user is not a moderator

        413 Payload Too Large When the message was longer than the allowed limit of 32000
            characters (or 1000 until Nextcloud 16.0.1, check the spreed => config => chat
            => max-length capability for the limit)

        #### Response Header:
        x-chat-last-common-read	[int]	ID of the last message read by every user that has
                                        read privacy set to public. When the user themself
                                        has it set to private the value the header is not
                                        set (only available with chat-read-status capability)
        """
        return_headers: List[str] = ['x-chat-last-common-read']

        data: Dict[str, Any] = {
            "message": message,
            "actorDisplayName": display_name,
            "replyTo": reply_to,
            "silent": silent}

        if reference_id:
            if not self.api.has_capability('chat-reference-id'):
                raise NextcloudNotCapable()
            elif len(reference_id) != 64:
                raise NextcloudBadRequest()
            else:
                data['referenceId'] = reference_id

        response, headers = await self._post(
            path=f'/chat/{room_token}',
            data=data)

        return Message(response, self), filter_headers(return_headers, headers)

    async def send_rich_object(
            self,
            room_token: str,
            rich_object: NextcloudTalkRichObject,
            reference_id: Optional[str] = None,
            actor_display_name: str = 'Guest') -> Tuple[Message, httpx.Headers]:
        """Share a rich object to the chat.

        https://github.com/nextcloud/server/blob/master/lib/public/RichObjectStrings/Definitions.php

        Required capability: rich-object-sharing
        Method: POST
        Endpoint: /chat/{token}/share
        Data:

        #### Arguments:
        rich_object	[NextcloudTalkRichObject]	The rich object

        actor_display_name	[str]   Guest display name (ignored for logged in users)

        reference_id	[str]	A reference string to be able to identify the message
        again in a "get messages" request, should be a random sha256 (only available
        with chat-reference-id capability)

        #### Exceptions:
        400 Bad Request In case the meta data is invalid

        403 Forbidden When the conversation is read-only

        404 Not Found When the conversation could not be found for the participant

        412 Precondition Failed When the lobby is active and the user is not a moderator

        413 Payload Too Large When the message was longer than the allowed limit of
        32000 characters (or 1000 until Nextcloud 16.0.1, check the spreed => config =>
        chat => max-length capability for the limit)

        #### Response Header:
        x-chat-last-common-read	[int]	ID of the last message read by every user that has
        read privacy set to public. When the user themself has it set to private the value
        the header is not set (only available with chat-read-status capability)

        #### Response Data:
        The full message array of the new message, as defined in Receive chat messages
        of a conversation
        """
        return_headers = ['x-chat-last-common-read']
        if not self.api.has_capability('rich-object-sharing'):
            raise NextcloudNotCapable()

        data: Dict[str, Any] = {
            'objectType': rich_object.object_type,
            'objectId': rich_object.id,
            'metaData': json.dumps(rich_object.metadata),
            'actorDisplayName': actor_display_name}

        if reference_id:
            if not self.api.has_capability('chat-reference-id'):
                raise NextcloudNotCapable()
            elif len(reference_id) != 64:
                raise NextcloudBadRequest()
            else:
                data['referenceId'] = reference_id

        response, headers = await self._post(
            path=f'/chat/{room_token}/share',
            data=data)
        return Message(response, self), filter_headers(return_headers, headers)

    async def share_file(
            self,
            room_token: str,
            path: str,
            reference_id: Optional[str] = None,
            metadata: Dict[str, Any]  = {}) -> int:
        """Share a file to the chat.

        More info:
            https://nextcloud-talk.readthedocs.io/en/latest/chat/#share-a-file-to-the-chat

        Method: POST
        Endpoint: /shares

        #### Arguments:
        path	string	The file path inside the user's root to share

        reference_id	string	A reference string to be able to identify the generated chat
        message again in a "get messages" request, should be a random sha256 (only available
        with chat-reference-id capability)

        metadata	[str]	See documenation # TODO: Fixme

        #### metadata:
        messageType [str]   A message type to show the message in different styles. Currently
        known: `voice-message` and `comment`

        #### Exceptions:
        403 When path is already shared
        """
        data: Dict[str, Any] = {
            'shareType': 10,
            'shareWith': room_token,
            'path': path,
            'talkMetaData': json.dumps(metadata)}

        if reference_id:
            if not self.api.has_capability('chat-reference-id'):
                raise NextcloudNotCapable()
            elif len(reference_id) != 64:
                raise NextcloudBadRequest()
            else:
                data['referenceId'] = reference_id

        response = await self._post(
            path=r'../../../files_sharing/api/v1/shares',
            data=data)

        return response

    async def list_shares(
            self,
            room_token: str,
            limit: int = 7) -> List[Message]:
        if not self.api.has_capability('rich-object-list-media'):
            raise NextcloudNotCapable

        response, _ = await self._get(
            path=f'/chat/{room_token}/share/overview',
            data = {'limit': limit})

        return [Message(data, self) for data in response]

    async def list_shares_by_type(
            self,
            room_token: str,
            object_type: SharedItemType,
            last_known_message_id: int,
            limit: int = 7) -> Tuple[List[Message], httpx.Headers]:
        return_headers = ['x-chat-last-given']

        if not self.api.has_capability('rich-object-list-media'):
            raise NextcloudNotCapable
        data: Dict[str, Any] = {
            'objectType': object_type.value,
            'lastKnownMessageId': last_known_message_id,
            'limit': limit}

        response, headers = await self._get(
            path=f'/chat/{room_token}/share',
            data=data)
        return [Message(data, self) for data in response], filter_headers(return_headers, headers)

    async def clear_history(
            self,
            room_token: str) -> Message:
        if not self.api.has_capability('clear-history'):
            raise NextcloudNotCapable()

        response = await self._delete(path=f'/chat/{room_token}')
        return Message(response, self)

    async def delete(
            self,
            room_token: str,
            message_id: int) -> Tuple[Message, httpx.Headers]:
        """Delete a message.

        More info:
            https://nextcloud-talk.readthedocs.io/en/latest/chat/#deleting-a-chat-message
            https://github.com/nextcloud/spreed/blob/88d1e4b11872f96745201c6e8921e7848eab0be8/openapi-full.json#L6485

        Args
        ----

            room_token (str): Room

            message_id (int): Message
        """
        return_headers = ['x-chat-last-common-read']

        # TODO: Validate if is regular message or rich media
        if not self.api.has_capability('delete-messages'):
            raise NextcloudNotCapable()

        response, headers = await self._delete(path=f'/chat/{room_token}/{message_id}')
        return Message(response, self), filter_headers(return_headers, headers)

    async def edit(
            self,
            room_token: str,
            message_id: int,
            message: str) -> Tuple[Message, httpx.Headers]:
        return_headers = ['x-chat-last-common-read']

        if not self.api.has_capability('edit-messages'):
            raise NextcloudNotCapable()

        response, headers = await self._put(
            path=f'/chat/{room_token}/{message_id}',
            data={'message': message})

        return Message(response, self), filter_headers(return_headers, headers)

    async def set_reminder(
            self,
            room_token: str,
            message_id: int,
            timestamp: dt.datetime) -> MessageReminder:
        if not self.api.has_capability('remind-me-later'):
            raise NextcloudNotCapable()

        response, _ = await self._post(
            path=f'/chat/{room_token}/{message_id}/reminder',
            data={'timestamp': int(timestamp.timestamp())})

        return MessageReminder(**response)

    async def get_reminder(
            self,
            room_token: str,
            message_id: int) -> MessageReminder:
        if not self.api.has_capability('remind-me-later'):
            raise NextcloudNotCapable()

        response, _ = await self._get(
            path=f'/chat/{room_token}/{message_id}/reminder')

        return MessageReminder(**response)

    async def delete_reminder(
            self,
            room_token: str,
            message_id: int) -> None:
        if not self.api.has_capability('remind-me-later'):
            raise NextcloudNotCapable()

        await self._delete(path=f'/chat/{room_token}/{message_id}/reminder')

    async def mark_as_read(
            self,
            room_token: str,
            last_read_message: Optional[int] = None) -> httpx.Headers:
        return_headers = ['x-chat-last-common-read']
        if not self.api.has_capability('chat-read-marker'):
            raise NextcloudNotCapable()

        data: Dict[str, Any] = {}
        if last_read_message:
            if not self.api.has_capability('chat-read-last'):
                raise NextcloudNotCapable()
            else:
                data = {'lastReadMessage': last_read_message}

        _, headers = await self._post(path=f'/chat/{room_token}/read', data=data)
        return filter_headers(return_headers, headers)

    async def mark_as_unread(
            self,
            room_token: str) -> httpx.Headers:
        return_headers = ['x-chat-last-common-read']
        if not self.api.has_capability('chat-unread'):
            raise NextcloudNotCapable()

        _, headers = await self._delete(path=f'/chat/{room_token}/read')
        return filter_headers(return_headers, headers)

    async def suggest_autocompletes(
            self,
            room_token: str,
            search: str,
            include_status: bool = False,
            limit: int = 20) -> List[Suggestion]:

        data: Dict[str, Any] = {
            'search': search,
            'includeStatus': include_status,
            'limit': limit}
        response, _ = await self._get(
            path=f'/chat/{room_token}/mentions',
            data=data)

        return [Suggestion(**x) for x in response]
