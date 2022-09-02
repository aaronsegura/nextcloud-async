"""Talk API interface."""

import json

from typing import List, Dict, Optional

from .constants import (
    Permissions,
    ConversationType,
    NotificationLevel,
    ListableScope)
from .rich_objects import NextCloudTalkRichObject
from .exceptions import NextCloudTalkNotCapable


TALK_CAPS = 'capabilities.spreed.features'


class NextCloudTalkAPI(object):
    """Interact with Nextcloud Talk API."""

    conv_stub = None
    chat_sub = None

    async def __get_stubs(self):
        if 'conversation-v4' in await self.get_capabilities(TALK_CAPS):
            self.conv_stub = '/ocs/v2.php/apps/spreed/api/v4'
        else:
            raise NextCloudTalkNotCapable('Unable to determine active Conversation endpoint.')

        if 'chat-v2' in await self.get_capabilities(TALK_CAPS):
            self.chat_stub = '/ocs/v2.php/apps/spreed/api/v1'
        else:
            raise NextCloudTalkNotCapable('Unable to determine chat endpoint.')

    async def get_conversations(
            self,
            status_update: bool = False,
            include_status: bool = False) -> List[Dict]:
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
        if not self.conv_stub:
            await self.__get_stubs()

        data = {
            'noStatusUpdate': 1 if status_update else 0,
            'includeStatus': include_status,
        }
        request = await self.ocs_query(
            method='GET',
            sub=f'{self.conv_stub}/room',
            data=data)
        return request

    async def create_conversation(
            self,
            room_type: str,
            invite: str = '',
            room_name: str = '',
            source: str = '') -> Dict:
        """Create a new conversation.

        Method: POST
        Endpoint: /room

        #### Arguments:
        room_type   [str]   See constants list
        invite	[str]	user id (roomType = 1), group id (roomType = 2 - optional),
        circle id (roomType = 2, source = 'circles'], only available
        with circles-support capability))

        source	[str]	The source for the invite, only supported on roomType = 2 for
        groups and circles (only available with circles-support capability)

        room_name	[str]	conversation name (Not available for roomType = 1)
        #### Exceptions:
        400 Bad Request When an invalid conversation type was given

        400 Bad Request When the conversation name is empty for type = 3

        401 Unauthorized When the user is not logged in

        404 Not Found When the target to invite does not exist
        """
        if not self.conv_stub:
            await self.__get_stubs()

        data = {
            'roomType': ConversationType[room_type].value,
            'invite': invite,
            'source': source,
            'roomName': room_name
        }
        return await self.ocs_query(
            method="POST",
            sub=f'{self.conv_stub}/room',
            data=data)

    async def get_conversation(self, room_token: str) -> Dict:
        """Get a specific conversation.

        Method: GET
        Endpoint: /room/{token}

        #### Exceptions:
        404 Not Found When the conversation could not be found for the participant
        """
        if not self.conv_stub:
            await self.__get_stubs()

        room_data = await self.ocs_query(
            sub=f'{self.conv_stub}/room/{room_token}')
        return room_data

    async def get_open_conversation_list(self) -> List[Dict]:
        """Get list of open rooms."""
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(method='GET', sub=f'{self.conv_stub}/listed-room')

    async def rename_conversation(self, token: str, new_name: str) -> Dict:
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
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(
            method='PUT',
            sub=f'{self.conv_stub}/room/{token}',
            data={'roomName': new_name})

    async def remove_conversations(self, token) -> Dict:
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
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(
            method='DELETE',
            sub=f'{self.conv_stub}/room/{token}')

    async def set_conversation_description(self, token, description: str) -> Dict:
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

        NextCloudTalkNotCapable When server is lacking required capability
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if 'room-description' not in self.get_capabilities(TALK_CAPS):
            raise NextCloudTalkNotCapable('Server does not support setting room descriptions')

        response = await self.ocs_query(
            method='PUT',
            sub=f'{self.conv_stub}/room/{token}/description',
            data={'description': description})

        return response

    async def conversation_allow_guests(self, token: str, allow_guests: bool) -> Dict:
        """Allow guests in a conversation.

        Method: POST or DELETE
        Endpoint: /room/{token}/public

        #### Arguments:
        allow_guests [bool] Allow (True) or disallow (False) guests

        #### Exceptions:
        400 Bad Request When the conversation is not a group conversation

        403 Forbidden When the current user is not a moderator/owner

        404 Not Found When the conversation could not be found for the participant
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if allow_guests:
            return await self.ocs_query(
                method='POST',
                sub=f'{self.conv_stub}/room/{token}/public')
        else:
            return await self.ocs_query(
                method='DELETE',
                sub=f'{self.conv_stub}/room/{token}/public')

    async def read_only(self, token: str, state: int) -> Dict:
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

        NextCloudTalkNotCapable When server is lacking required capability
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if 'read-only-rooms' not in self.get_capabilies(TALK_CAPS):
            raise NextCloudTalkNotCapable('Server doesn\'t support read-only rooms.')

        return await self.ocs_query(
            method='PUT',
            sub=f'{self.conv_stub}/room/{token}/read-only',
            data={'state': state})

    async def set_conversation_password(self, token: str, password: str) -> Dict:
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
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(
            method='PUT',
            sub=f'{self.conv_stub}/room/{token}/password',
            data={'password': password})

    async def add_conversation_to_favorites(self, token) -> Dict:
        """Add conversation to favorites

        Required capability: favorites
        Method: POST
        Endpoint: /room/{token}/favorite

        #### Exceptions:
        401 Unauthorized When the participant is a guest

        404 Not Found When the conversation could not be found for the participant

        NextCloudTalkNotCapable When server is lacking required capability
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if 'favorites' not in self.get_capabilities(TALK_CAPS):
            raise NextCloudTalkNotCapable('Server does not support user favorites.')

        return await self.ocs_query(
            method='POST',
            sub=f'{self.conv_stub}/room/{token}/favorite')

    async def remove_conversation_from_favorites(self, token) -> Dict:
        """Remove conversation from favorites

        Required capability: favorites
        Method: DELETE
        Endpoint: /room/{token}/favorite

        #### Exceptions:
        401 Unauthorized When the participant is a guest

        404 Not Found When the conversation could not be found for the participant

        NextCloudTalkNotCapable When server is lacking required capability
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if 'favorites' not in self.get_capabilities(TALK_CAPS):
            raise NextCloudTalkNotCapable('Server does not support user favorites.')

        return await self.ocs_query(
            method='DELETE',
            sub=f'{self.conv_stub}/room/{token}/favorites')

    async def set_conversation_notification_level(
            self,
            token: str,
            notification_level: str) -> Dict:
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
        if not self.conv_stub:
            await self.__get_stubs()

        data = {
            'level': NotificationLevel[notification_level].value
        }
        return await self.ocs_query(
            method='POST',
            sub=f'{self.conv_stub}/room/{token}/notify',
            data=data)

    async def set_call_notification_level(
            self,
            token: str,
            notification_level: str) -> Dict:
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

        NextCloudTalkNotCapable When server is lacking required capability
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if 'notification-calls' not in self.get_capabilities(TALK_CAPS):
            raise NextCloudTalkNotCapable(
                'Server does not support setting call notification levels.')

        data = {
            'level': NotificationLevel[notification_level].value
        }
        return await self.ocs_query(
            method='POST',
            sub=f'{self.conv_stub}/room/{token}/notify-calls',
            data=data)

    async def set_participant_permissions(
            self,
            token: str,
            scope: str = 'default',
            permissions: Permissions = Permissions(0)) -> Dict:
        """Set default or call permissions.

        Method: PUT
        Endpoint: /room/{token}/permissions/{mode}

        #### Arguments:
        mode [str]	'default' or 'call', in case of call the permissions will be
            reset to 0 (default) after the end of a call.

        permissions	[int] New permissions for the attendees, see constants list. If
            permissions are not 0 (default), the 1 (custom) permission
            will always be added. Note that this will reset all custom
            permissions that have been given to attendees so far.

        #### Exceptions:

        400 Bad Request When the conversation type does not support setting publishing
            permissions, e.g. one-to-one conversations

        400 Bad Request When the mode is invalid

        403 Forbidden When the current user is not a moderator, owner or guest moderator

        404 Not Found When the conversation could not be found for the participant
        """
        if not self.conv_stub:
            await self.__get_stubs()

        data = {
            'mode': scope,
            'permissions': permissions,
        }
        return await self.ocs_query(
            method='PUT',
            sub=f'{self.conv_stub}/room/{token}/permissions/{scope}',
            data=data)

    async def join_conversation(
            self,
            token: str,
            password: Optional[str],
            force: bool = True) -> Dict:
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
        if not self.conv_stub:
            await self.__get_stubs()

        data = {
            'password': password,
            'force': force,
        }
        return await self.ocs_query(
            method='POST',
            sub=f'{self.conv_stub}/room/{token}/participants/active',
            data=data)

    async def leave_conversation(self, token: str) -> Dict:
        """Remove yourself from a conversation.

        Method: DELETE
        Endpoint: /room/{token}/participants/self

        #### Exceptions:
        400 Bad Request When the participant is a moderator or owner and there are
            no other moderators or owners left.

        404 Not Found When the conversation could not be found for the participant
        """
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(
            method='DELETE',
            sub=f'{self.conv_stub}/room/{token}/participants/self')

    async def invite_to_conversation(
            self,
            token: str,
            invitee: str,
            source: str = 'users') -> Optional[int]:
        """Invite a user to this room.

        Method: POST
        Endpoint: /room/{token}/participants

        #### Arguments:
        invitee	[str]	User, group, email or circle to add

        source  [str]	Source of the participant(s) as
            returned by the autocomplete suggestion endpoint (default is 'users')

        #### Exceptions:
        400 Bad Request
            When the source type is unknown, currently users, groups, emails
            are supported. circles are supported with circles-support capability

        400 Bad Request
            When the conversation is a one-to-one conversation or a conversation
            to request a password for a share

        403 Forbidden - When the current user is not a moderator or owner

        404 Not Found - When the conversation could not be found for the participant

        404 Not Found - When the user or group to add could not be found

        Returns:
        type	[int]   In case the conversation type changed, the new value is
                        returned
        """
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(
            sub=f'{self.conv_stub}/room/{token}/participants',
            data={'newParticipant': invitee, 'source': source})

    async def get_conversation_participants(
            self,
            token: str,
            include_status: bool = False) -> List[Dict]:
        """Return list of participants."""
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(
            sub=f'{self.conv_stub}/room/{token}/participants',
            data={'includeStatus': include_status})

    async def send_to_conversation(
            self,
            message: str,
            token: str,
            reply_to: int = 0,
            display_name: Optional[str] = None,
            reference_id: Optional[str] = None,
            silent: bool = False) -> Dict:
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
        X-Chat-Last-Common-Read	[int]	ID of the last message read by every user that has
                                        read privacy set to public. When the user themself
                                        has it set to private the value the header is not
                                        set (only available with chat-read-status capability)
        """
        if not self.conv_stub:
            await self.__get_stubs()

        response = await self.ocs_query(
            method='POST',
            sub=f'{self.chat_stub}/chat/{token}',
            data={
                "message": message,
                "replyTo": reply_to,
                "displayName": display_name,
                "referenceId": reference_id,
                "silent": silent
            },
            include_headers=['X-Chat-Last-Common-Read'])

        return response

    async def set_conversation_scope(self, token, scope: str) -> Optional[Dict]:
        """Change scope for conversation.

        Change who can see the conversation.
        See ListableScope, above.

        Required capability: listable-rooms
        Method: PUT
        Endpoint: /room/{token}/listable

        #### Arguments:
        scope	[str]	New flags for the conversation (see constants)

        #### Exceptions:
        400 Bad Request When the conversation type does not support making it listable
        (only group and public conversation)

        403 Forbidden When the current user is not a moderator/owner or the conversation
        is not a public conversation

        404 Not Found When the conversation could not be found for the participant

        NextCloudTalkNotCapable When server is lacking required capability
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if 'listable-rooms' not in self.get_capabilities(TALK_CAPS):
            raise NextCloudTalkNotCapable('Server does not support listable rooms.')

        self.ocs_query(
            method='PUT',
            sub=f'{self.conv_stub}/room/{token}/listable',
            data={'scope': ListableScope[scope].value})

    async def set_conversation_permissions_for_participants(
            self,
            token: str,
            permissions: Permissions,
            mode: str = 'add') -> Dict:
        """Set permissions for all attendees in a conversation.

        Method: PUT
        Endpoint: /room/{token}/attendees/permissions/all

        #### Arguments:
        mode	[str]	Mode of how permissions should be manipulated.  See constants list.
        If the permissions were 0 (default) and the modification is add or remove, they will
        be initialised with the call or default conversation permissions before, falling back
        to 126 for moderators and 118 for normal participants.

        permissions	[int]	New permissions for the attendees, see constants list. If
        permissions are not 0 (default), the 1 (custom) permission will always be added.

        #### Exceptions:
        400 Bad Request When the conversation type does not support setting publishing
        permissions, e.g. one-to-one conversations

        400 Bad Request When the mode is invalid

        403 Forbidden When the current user is not a moderator, owner or guest moderator

        404 Not Found When the conversation could not be found for the participant
        """
        if not self.conv_stub:
            await self.__get_stubs()

        data = {
            'mode': mode,
            'permissions': permissions.value,
        }
        return await self.ocs_query(
            method='PUT',
            sub=f'{self.conv_stub}/room/{token}/attendees/permissions/all',
            data=data)

    async def set_conversation_guest_display_name(
            self,
            token: str,
            display_name: str) -> Dict:
        """Set display name as a guest.

        API: Only v1
        Method: POST
        Endpoint: /guest/{token}/name

        #### Arguments:
        displayName	string	The new display name

        #### Exceptions:
        403 Forbidden When the current user is not a guest

        404 Not Found When the conversation could not be found for the
        participant
        """
        return await self.ocs_query(
            method='POST',
            url=f'{self.endpoint}/ocs/v2.php/apps/spreed/api/v1',
            sub=f'{self.conv_stub}/guest/{token}/name',
            data={'displayName': display_name})

    async def get_conversation_messages(
            self,
            token: str,
            look_into_future: bool = False,
            limit: int = 100,
            timeout: int = 30,
            last_known_message: Optional[int] = None,
            last_common_read: Optional[int] = None,
            set_read_marker: bool = True,
            include_last_known: bool = False) -> List[Dict]:
        """Receive chat messages of a conversation.

        Method: GET
        Endpoint: /chat/{token}

        #### Arguments:
        look_into_future	[bool]	1 Poll and wait for new message or 0 get history
        of a conversation

        limit	[int]	Number of chat messages to receive (100 by default, 200 at most)

        last_known_message	[int]	Serves as an offset for the query. The lastKnownMessageId
        for the next page is available in the X-Chat-Last-Given header.

        last_common_read	[int]	Send the last X-Chat-Last-Common-Read header you got, if
        you are interested in updates of the common read value. A 304 response does not allow
        custom headers and otherwise the server can not know if your value is modified or not.

        timeout	[int]	$lookIntoFuture = 1 only, Number of seconds to wait for new messages
        (30 by default, 60 at most)

        set_read_marker	[bool]	True to automatically set the read timer after fetching the
        messages, use False when your client calls Mark chat as read manually. (Default: True)

        include_last_known    [bool]	True to include the last known message as well (Default:
        False)

        #### Exceptions:
        304 Not Modified When there were no older/newer messages

        404 Not Found When the conversation could not be found for the participant

        412 Precondition Failed When the lobby is active and the user is not a moderator

        #### Response Header:

        X-Chat-Last-Given	[int]	Offset (lastKnownMessageId) for the next page.
        X-Chat-Last-Common-Read	[int]	ID of the last message read by every user that has
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
        data = {
            'lookIntoFuture': 1 if look_into_future else 0,
            'limit': limit,
            'timeout': timeout,
            'setReadMaker': 1 if set_read_marker else 0,
            'includeLastKnown': 1 if include_last_known else 0
        }
        if last_known_message:
            data['lastKnownMessageId'] = last_known_message
        if last_common_read:
            data['lastCommonReadId'] = last_common_read

        response, headers = await self.ocs_query(
            method='GET',
            sub=f'{self.chat_stub}/chat/{token}',
            data=data,
            include_headers=['X-Chat-Last-Given', 'X-Chat-Last-Common-Read']
        )
        return response, headers

    async def send_rich_object_to_conversation(
            self,
            token: str,
            rich_object: NextCloudTalkRichObject,
            reference_id: Optional[str] = None,
            actor_display_name: str = 'Guest') -> Dict:
        """Share a rich object to the chat.

        https://github.com/nextcloud/server/blob/master/lib/public/RichObjectStrings/Definitions.php

        Required capability: rich-object-sharing
        Method: POST
        Endpoint: /chat/{token}/share
        Data:

        #### Arguments:
        rich_object	[NextCloudTalkRichObject]	The rich object

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
        X-Chat-Last-Common-Read	[int]	ID of the last message read by every user that has
        read privacy set to public. When the user themself has it set to private the value
        the header is not set (only available with chat-read-status capability)

        #### Response Data:
        The full message array of the new message, as defined in Receive chat messages
        of a conversation
        """
        if not self.conv_stub:
            await self.__get_stubs()

        response = await self.ocs_query(
            method='POST',
            sub=f'{self.chat_stub}/chat/{token}/share',
            data={
                'objectType': rich_object.object_type,
                'objectId': rich_object.id,
                'metaData': json.dumps(rich_object.metadata),
                'actorDisplayName': actor_display_name,
                'referenceId': reference_id
            },
            include_headers=['X-Chat-Last-Common-Read']
        )
        return response

    async def clear_conversation_history(self, token: str) -> Dict:
        """Clear chat history.

        Required capability: clear-history
        Method: DELETE
        Endpoint: /chat/{token}

        #### Exceptions:
        403 Forbidden When the user is not a moderator

        404 Not Found When the conversation could not be found for the participant

        #### Response Header:
        X-Chat-Last-Common-Read	[int]	ID of the last message read by every user that
        has read privacy set to public. When the user themself has it set to private
        the value the header is not set (only available with chat-read-status capability)

        #### Response Data:
        The full message array of the new system message "You cleared the history
        of the conversation", as defined in Receive chat messages of a conversation.  When
        rendering this message the client should also remove all messages from any
        cache/storage of the device.
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if 'clear-history' not in self.get_capabilities(TALK_CAPS):
            raise NextCloudTalkNotCapable('Server does not support deletion of chat history.')

        response = await self.ocs_query(
            method='DELETE',
            sub=f'{self.chat_stub}/chat/{token}',
            include_headers=['X-Chat-Last-Common-Read'],
        )
        return response

    async def get_conversation_autocomplete_suggestions(
            self,
            token: str,
            search: str,
            limit: int = 20,
            include_status: bool = False) -> Dict:
        """Get mention autocomplete suggestions

        Method: GET
        Endpoint: /chat/{token}/mentions

        #### Arguments:
        search	[str]	Search term for name suggestions (should at least be 1 character)

        limit	[int]	Number of suggestions to receive (20 by default)

        include_status	[bool]	Whether the user status information also needs to be loaded

        #### Exceptions:
        403 Forbidden When the conversation is read-only

        404 Not Found When the conversation could not be found for the participant

        412 Precondition Failed When the lobby is active and the user is not a moderator

        #### Response Data:
        Each suggestion has at least:

        id	[str]	The user id which should be sent as @<id> in the message (user ids
        that contain spaces as well as guest ids need to be wrapped in double-quotes when
        sending in a message: @"space user" and @"guest/random-string")

        label	[str]	The displayname of the user

        source	[str]	The type of the user, currently only `users`, `guests` or `calls` (for
        mentioning the whole conversation)

        status	[str]	Optional: Only available with include_status=true and for users with a
        set status

        statusIcon	[str]	Optional: Only available with include_status=true and for users
        with a set status

        statusMessage	[str]	Optional: Only available with includeStatus=true and for
        users with a set status
        """
        if not self.conv_stub:
            await self.__get_stubs()

        return self.ocs_query(
            method='GET',
            sub=f'{self.chat_stub}/chat/{token}/mentions',
            data={
                'search': search,
                'limit': limit,
                'includeStatus': include_status})

    async def share_file_to_conversation(
            self,
            token: str,
            path: str,
            reference_id: Optional[str] = None,
            metadata_type: str = 'comment') -> Dict:
        """Share a file to the chat.

        Method: POST
        Endpoint: ocs/v2.php/apps/files_sharing/api/v1/shares

        #### Arguments:
        path	string	The file path inside the user's root to share

        reference_id	string	A reference string to be able to identify the generated chat
        message again in a "get messages" request, should be a random sha256 (only available
        with chat-reference-id capability)

        talkMetaData	[str]	JSON encoded array of the meta data

        #### talkMetaData:
        messageType [str]   A message type to show the message in different styles. Currently
        known: `voice-message` and `comment`

        #### Exceptions:
        403 When path is already shared
        """
        self.ocs_query(
            method='POST',
            url=f'{self.endpoint}/ocs/v2.php/apps/files_sharing/api/v1/shares',
            data={
                'shareType': 10,
                'shareWith': {token},
                'path': path,
                'reference_id': reference_id,
                'talkMetaData': json.dumps(
                    {'messageType': metadata_type}
                )
            }
        )

    async def remove_participant_from_conversation(
            self,
            token: str,
            attendee_id: int) -> Dict:
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
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(
            method='DELETE',
            sub=f'{self.conv_stub}/room/{token}/attendees',
            data={'attendeeId': attendee_id})

    async def promote_conversation_participant(
            self,
            token: str,
            attendee_id: int) -> Dict:
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
        return await self.ocs_query(
            method='POST',
            sub=f'{self.conv_stub}/room/{token}/moderators',
            data={'attendeeId': attendee_id})

    async def demote_conversation_participant(
            self,
            token: str,
            attendee_id: int) -> Dict:
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
        if not self.conv_stub:
            await self.__get_stubs()

        return await self.ocs_query(
            method='DELETE',
            sub=f'{self.conv_stub}/room/{self.room.token}/moderators',
            data={'attendeeId': attendee_id})

    async def set_conversation_participant_permissions(
            self,
            token: str,
            attendee_id: int,
            permissions: Permissions,
            mode: str = 'add') -> Dict:
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
        if not self.conv_stub:
            await self.__get_stubs()

        data = {
            'attendeeId': attendee_id,
            'mode': mode,
            'permissions': permissions.value
        }
        return self.ocs_query(
            method='PUT',
            sub=f'{self.conv_stub}/room/{token}/attendees/permissions',
            data=data
        )

    async def remove_conversation_message(
            self,
            token: str,
            message_id: int):
        """Delete a chat message.

        Required capability: delete-messages or rich-object-delete
        Method: DELETE
        Endpoint: /chat/{token}/{messageId}

        #### Exceptions:
        400 Bad Request The message is already older than 6 hours
        403 Forbidden When the message is not from the current user and the user not a
        moderator
        403 Forbidden When the conversation is read-only
        404 Not Found When the conversation or chat message could not be found for the
        participant
        405 Method Not Allowed When the message is not a normal chat message
        412 Precondition Failed When the lobby is active and the user is not a moderator

        #### Response Header:
        X-Chat-Last-Common-Read	[int]	ID of the last message read by every user that has read
        privacy set to public. When the user themself has it set to private the value the
        header is not set (only available with chat-read-status capability)

        #### Response Data:
        The full message array of the new system message "You deleted a message", as defined in
        Receive chat messages of a conversation The parent message is the object of the deleted
        message with the replaced text "Message deleted by you". This message should NOT be
        displayed to the user but instead be used to remove the original message from any
        cache/storage of the device.
        """
        if not self.conv_stub:
            await self.__get_stubs()

        if self.message == r'{object}':
            if 'rich-object-delete' not in self.get_capabilities(TALK_CAPS):
                raise NextCloudTalkNotCapable(
                    'Server does not support deletion of rich objects.')
        else:
            if 'delete-messages' not in self.get_capabilities(TALK_CAPS):
                raise NextCloudTalkNotCapable('Server does not support message deletion.')

        response = await self.ocs_query(
            method='DELETE',
            sub=f'{self.chat_stub}/chat/{token}/{message_id}',
            include_headers=['X-Chat-Last-Common-Read'])

        return response

    async def mark_conversation_message_read(
            self,
            token: str,
            message_id: int) -> Dict:
        """Mark chat as read.

        Required capability: chat-read-marker
        Method: POST
        Endpoint: /chat/{token}/read

        #### Arguments:
        lastReadMessage	[int]	The last read message ID

        #### Exceptions:
        404 Not Found When the room could not be found for the participant, or the
        participant is a guest.

        #### Response Header:
        X-Chat-Last-Common-Read	[int]	ID of the last message read by every user that
        has read privacy set to public. When the user themself has it set to private the
        value the header is not set (only available with chat-read-status capability)
        """
        await self.__mark_message_status(token=token, message_id=message_id, read=True)

    async def mark_conversation_message_unread(
            self,
            token: str,
            message_id: int) -> Dict:
        """Mark chat as unread.

        Required capability: chat-unread
        Method: DELETE
        Endpoint: /chat/{token}/read

        #### Exceptions:
        404 Not Found When the room could not be found for the participant, or the participant
        is a guest.

        #### Response Headers:
        X-Chat-Last-Common-Read	[int]	ID of the last message read by every user that has read
        privacy set to public. When the user themself has it set to private the value the
        header is not set (only available with chat-read-status capability)
        """
        return await self.__mark_message_status(token=token, message_id=message_id, read=False)

    async def __mark_message_status(
            self,
            token: str,
            message_id: int,
            read: bool) -> Dict:

        if not self.conv_stub:
            await self.__get_stubs()

        response = await self.ocs_query(
            method='POST' if read else 'DELETE',
            sub=f'{self.chat_stub}/chat/{token}/read',
            data={'lastReadMessage': {message_id}},
            include_headers=['X-Chat-Last-Common-Read']
        )
        return response
