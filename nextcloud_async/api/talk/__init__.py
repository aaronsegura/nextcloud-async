"""Connectivity to Nextcloud Talk back-end.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

from .avatars import ConversationAvatars
from .bots import Bot, Bots
from .breakout_rooms import BreakoutRoom, BreakoutRooms
from .calls import Calls
from .chat import Chat, Message, MessageReminder, Suggestion
from .conversations import Conversations, Conversation
from .integrations import Integrations
from .participants import Participants, Participant
from .polls import Polls, Poll
from .reactions import Reactions
from .signaling import InternalSignaling
from .webinars import Webinars


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
    "BreakoutRoom", "BreakoutRooms",
    "Calls",
    "Chat", "Message", "MessageReminder", "Suggestion",
    "Conversations", "Conversation",
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
    "Webinars", "WebinarLobbyState"]
