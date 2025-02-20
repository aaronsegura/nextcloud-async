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
    former_one_to_one = 5
    note_to_self = 6


class ConversationReadOnlyState(Enum):
    read_write = 0
    read_only = 1


class ConversationNotificationLevel(Enum):
    """Notification Levels."""

    default = 0
    always_notify = 1
    notify_on_mention = 2
    never_notify = 3


class MentionPermissions(Enum):
    """Mention Permissions."""

    everyone = 0
    moderators = 1


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


class ParticipantPermissions(IntFlag):
    """Participant permissions."""

    default = 0
    custom = 1
    start_call = 2
    join_call = 4
    can_ignore_lobby = 8
    publish_audio = 16
    publish_video = 32
    publish_screen_sharing = 64
    post_share_react = 128


class PermissionAction(Enum):
    add = 'add'
    remove = 'remove'


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


class SessionStates(Enum):
    inactive = 0
    active = 1


class ObjectSources(Enum):
    user = 'users'
    group = 'groups'
    email = 'emails'
    circle = 'circles'


class FileShareMessageType(Enum):
    voice_message = 'voice-message'
    comment = 'comment'


class SharedItemType(Enum):
    audio = 'audio'
    deckcard = 'deckcard'
    file = 'file'
    location = 'location'
    media = 'media'
    other = 'other'
    voice = 'voice'
    recording = 'recording'
    comment = 'comment'
    voice_message = 'voice-message'


class PollMode(Enum):
    public = 0
    private = 1


class PollStatus(Enum):
    open = 0
    closed = 1
    draft = 2


class BreakoutRoomAssignmentMode(Enum):
    not_configured = 0
    automatic = 1
    manual = 2
    free = 3


class BreakoutRoomStatus(Enum):
    stopped = 0
    started = 1


class RoomObjectType(Enum):
    file = 'file'
    share_password = 'share:password'
    room = 'room'
    phone = 'phone'
    sample = 'sample'


class WebinarLobbyState(Enum):
    no_lobby = 0
    lobby = 1


class SipState(Enum):
    disabled = 0
    enabled = 1
    no_pin = 2


class SignalingMode(Enum):
    internal = 'internal'
    external = 'external'
    conversation_cluster = 'conversation_cluster'

class ConversationPermissionMode(Enum):
    default = 'default'
    call = 'call'
