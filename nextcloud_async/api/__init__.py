"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

from .apps import Apps, App
from .files import Files, File
from .groupfolders import GroupFolders
from .groups import Groups
from .loginflowv2 import LoginFlowV2
from .maps import Maps
from .notifications import Notifications
from .shares import Shares, Share, ShareType, SharePermission
from .sharees import Sharees
from .status import Status, StatusType
from .talk import (
    ConversationAvatars,
    Bot, Bots,
    Calls,
    Chat, Message, MessageReminder, Suggestion,
    Conversations, Conversation, Webinars, BreakoutRoom, BreakoutRooms,
    Integrations,
    Participants, Participant,
    Polls, Poll,
    Reactions,
    InternalSignaling,
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
    SessionStates,
    SharedItemType,
    SipState,
    WebinarLobbyState
  )
from .users import Users
from .wipe import Wipe

__all__ = [
    "Apps", "App",
    "Chat",
    "Conversations", "Conversation",
    "ConversationAvatars",
    "Polls", "Poll",
    "Suggestion",
    "Files", "File",
    "GroupFolders",
    "Groups",
    "LoginFlowV2",
    "Maps",
    "Message", "MessageReminder",
    "Notifications",
    "Participants", "Participant",
    "Shares", "Share", "ShareType", "SharePermission",
    "Sharees",
    "Status", "StatusType",
    "Users",
    "Wipe",
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
    "SessionStates",
    "SharedItemType",
    "SipState",
    "WebinarLobbyState"
]
