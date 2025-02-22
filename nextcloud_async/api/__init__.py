"""Nextcloud APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

from .ocs.apps import Apps, App
from .dav.files import Files, File
from .ocs.groupfolders import GroupFolders
from .ocs.groups import Groups
from .base.loginflowv2 import LoginFlowV2
from .base.maps import Maps
from .ocs.notifications import Notifications
from .ocs.shares import Shares, Share, ShareType, SharePermission
from .ocs.sharees import Sharees
from .ocs.status import Status, StatusType
from .ocs.users import Users
from .ocs.talk import (
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
    SessionState,
    SharedItemType,
    SipState,
    WebinarLobbyState,
  )
from .base.wipe import Wipe

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
    "SessionState",
    "SharedItemType",
    "SipState",
    "WebinarLobbyState",
]
