"""Nextcloud Talk Constants.

https://nextcloud-talk.readthedocs.io/en/latest/constants/
"""

from enum import IntFlag, Enum


class ConversationType(Enum):
    """Conversation Types."""

    one_to_one = 1
    group = 2
    public = 3
    changelog = 4


class NotificationLevel(Enum):
    """Notification Levels."""

    default = 0
    always_notify = 1
    notify_on_mention = 2
    never_notify = 3


class CallNotificationLevel(Enum):
    """Call notification levels."""

    off = 0
    on = 1  # Default


class ReadStatusPrivacy(Enum):
    """Show user read status."""

    public = 0
    private = 1


class ListableScope(Enum):
    """Conversation Listing Scope."""

    participants = 0
    users = 1
    everyone = 2


class Permissions(IntFlag):
    """Participant permissions."""

    default = 0
    custom = 1
    start_call = 2
    join_call = 4
    can_ignore_lobby = 8
    can_publish_audio = 16
    can_publish_video = 32
    can_publish_screen_sharing = 64


class ParticipantType(Enum):
    """Participant Types."""

    owner = 1
    moderator = 2
    user = 3
    guest = 4
    public_link_user = 5
    guest_moderator = 6


class ParticipantInCallFlags(IntFlag):
    """Participant Call Status Flags."""

    disconnected = 0
    in_call = 1
    provides_audio = 2
    provides_video = 4
    uses_sip_dial_in = 8


class WebinarLobbyStates(Enum):
    """Webinar Lobby States."""

    no_lobby = 0
    lobby = 1
