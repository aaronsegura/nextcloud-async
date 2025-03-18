"""Connectivity to Nextcloud Talk back-end.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

from .avatars import ConversationAvatarsApi
from .bots import Bot, BotsApi
from .breakout_rooms import BreakoutRoom, BreakoutRoomsApi
from .calls import CallsApi
from .chat import ChatApi, Message, MessageReminder, Suggestion
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
from .conversations import Conversation, ConversationsApi
from .integrations import IntegrationsApi
from .participants import Participant, ParticipantsApi
from .polls import Poll, PollsApi
from .reactions import Reactions
from .signaling import InternalSignalingApi
from .webinars import WebinarsApi

__all__ = [
    "ConversationAvatarsApi",
    "Bot",
    "BotsApi",
    "BreakoutRoom",
    "BreakoutRoomsApi",
    "CallsApi",
    "ChatApi",
    "Message",
    "MessageReminder",
    "Suggestion",
    "ConversationsApi",
    "Conversation",
    "IntegrationsApi",
    "ParticipantsApi",
    "Participant",
    "PollsApi",
    "Poll",
    "Reactions",
    "InternalSignalingApi",
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
    "WebinarsApi",
    "WebinarLobbyState",
]
