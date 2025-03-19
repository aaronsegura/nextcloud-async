"""Connectivity to Nextcloud Talk back-end.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

from .bots import Bot
from .breakout_rooms import BreakoutRoom
from .chat import Message, MessageReminder, Suggestion
from .constants import (
    BreakoutRoomAssignmentMode,
    BreakoutRoomStatus,
    CallNotificationLevel,
    ConversationNotificationLevel,
    ConversationType,
    FileShareMessageType,
    ListableScope,
    MentionPermissions,
    ObjectSources,
    ParticipantInCallFlags,
    ParticipantPermissions,
    ParticipantType,
    PermissionAction,
    PollMode,
    PollStatus,
    ReadStatusPrivacy,
    RoomObjectType,
    SessionState,
    SharedItemType,
    SignalingMode,
    SipState,
    WebinarLobbyState,
)
from .conversations import Conversation
from .participants import Participant
from .polls import Poll
from .reactions import Reactions
from .talk import talk_api

__all__ = [
    "Bot",
    "BreakoutRoom",
    "BreakoutRoomAssignmentMode",
    "BreakoutRoomStatus",
    "CallNotificationLevel",
    "Conversation",
    "ConversationNotificationLevel",
    "ConversationType",
    "FileShareMessageType",
    "ListableScope",
    "MentionPermissions",
    "Message",
    "MessageReminder",
    "ObjectSources",
    "Participant",
    "ParticipantInCallFlags",
    "ParticipantPermissions",
    "ParticipantType",
    "PermissionAction",
    "Poll",
    "PollMode",
    "PollStatus",
    "Reactions",
    "ReadStatusPrivacy",
    "RoomObjectType",
    "SessionState",
    "SharedItemType",
    "SignalingMode",
    "SipState",
    "Suggestion",
    "talk_api",
    "WebinarLobbyState",
]
