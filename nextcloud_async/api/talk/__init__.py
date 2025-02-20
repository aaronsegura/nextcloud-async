"""Connectivity to Nextcloud Talk back-end.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

from .avatars import ConversationAvatars
from .bots import Bot, Bots
from .calls import Calls
from .chat import Chat, Message, MessageReminder, Suggestion
from .conversations import Conversations, Conversation, Webinars, BreakoutRoom, BreakoutRooms
from .integrations import Integrations
from .participants import Participants, Participant
from .polls import Polls, Poll
from .reactions import Reactions
from .signaling import InternalSignaling


from .constants import (
    BreakoutRoomAssignmentMode,
    BreakoutRoomStatus,
    CallNotificationLevel,
    ConversationType,
    FileShareMessageType,
    ListableScope,
    MentionPermissions,
    ConversationNotificationLevel,
    ObjectSources,
    ParticipantInCallFlags,
    ParticipantPermissions,
    ParticipantType,
    PermissionAction,
    PollMode,
    PollStatus,
    ReadStatusPrivacy,
    RoomObjectType,
    SignalingMode,
    SessionState,
    SharedItemType,
    SipState,
    WebinarLobbyState,
)

__all__ = [
    "ConversationAvatars",
    "Bot", "Bots",
    "Calls",
    "Chat", "Message", "MessageReminder", "Suggestion",
    "Conversations", "Conversation", "Webinars", "BreakoutRoom", "BreakoutRooms",
    "Integrations",
    "Participants", "Participant",
    "Polls", "Poll",
    "Reactions",
    "InternalSignaling",
    "BreakoutRoomAssignmentMode",
    "BreakoutRoomStatus",
    "CallNotificationLevel",
    "ConversationType",
    "FileShareMessageType",
    "ListableScope",
    "MentionPermissions",
    "ConversationNotificationLevel",
    "ObjectSources",
    "ParticipantInCallFlags",
    "ParticipantPermissions",
    "ParticipantType",
    "PermissionAction",
    "PollMode",
    "PollStatus",
    "ReadStatusPrivacy",
    "RoomObjectType",
    "SignalingMode",
    "SessionState",
    "SharedItemType",
    "SipState",
    "WebinarLobbyState"]
