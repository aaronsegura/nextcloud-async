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
from .talk import Conversations
from .users import Users
from .wipe import Wipe

__all__ = [
    "Apps", "App",
    "Conversations",
    "Files", "File",
    "GroupFolders",
    "Groups",
    "LoginFlowV2",
    "Maps",
    "Notifications",
    "Shares", "Share", "ShareType", "SharePermission",
    "Sharees",
    "Status", "StatusType",
    "Users",
    "Wipe",
]
