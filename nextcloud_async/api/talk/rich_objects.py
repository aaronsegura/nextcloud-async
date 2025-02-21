"""Classes representing Rich Objects for sharing.

https://github.com/nextcloud/server/blob/master/lib/public/RichObjectStrings/Definitions.php

I don't really understand why most of these exist when they don't
seem to enforce any kind of argument checking.  You can put in
whatever you want for 'id' in most of them, and it'll be accepted
and entered into the chat.
"""
from typing import Dict, Optional

from .constants import RichObjectCallType

class NextcloudTalkRichObject:
    """Base Class for Rich Objects."""

    object_type = None

    def __init__(self, id: str, name: str) -> None:
        """Set object metadata."""
        self.id = id
        self.name = name
        self.object_type = self.object_type

    @property
    def metadata(self) -> Dict[str, str]:
        """Return metadata array."""
        return {k:v for k, v in self.__dict__.items() if k not in ['id', 'object_type']}


class AddressBook(NextcloudTalkRichObject):
    """Address book."""

    object_type = 'addressbook'


class AddressBookContact(NextcloudTalkRichObject):
    """Addressbook contact."""

    object_type = 'addressbook-contact'


class Announcement(NextcloudTalkRichObject):
    """Announcement."""

    object_type = 'announcement'

    def __init__(self, id: str, name: str, link: Optional[str] = None) -> None:
        super().__init__(id, name)
        self.link = link


class Calendar(NextcloudTalkRichObject):
    """Calendar."""

    object_type = 'calendar'


class CalendarEvent(NextcloudTalkRichObject):
    """Calendar Event."""

    object_type = 'calendar-event'

    def __init__(self, id: str, name: str, link: Optional[str] = None) -> None:
        super().__init__(id, name)
        self.link = link


class Call(NextcloudTalkRichObject):
    """Nextcloud Talk Call."""

    object_type = 'call'

    def __init__(
            self,
            id: str,
            name: str,
            call_type: RichObjectCallType,
            link: Optional[str] = None,
            icon_url: Optional[str] = None,
            message_id: Optional[str] = None) -> None:
        super().__init__(id, name)
        self.link = link
        self.__dict__['call-type'] = call_type
        self.__dict__['icon-url'] = icon_url
        self.__dict__['message-id'] = message_id


class Circle(NextcloudTalkRichObject):
    """Cirle."""

    object_type = 'circle'

    def __init__(self, id: str, name: str, link: str) -> None:
        super().__init__(id, name)
        self.link = link


class DeckBoard(NextcloudTalkRichObject):
    """Deck board."""

    object_type = 'deck-board'

    def __init__(
            self,
            id: str,
            name: str,
            link: str) -> None:
        super().__init__(id, name)
        self.link = link


class DeckCard(NextcloudTalkRichObject):
    """Deck card."""

    object_type = 'deck-card'

    def __init__(
            self,
            id: str,
            name: str,
            board_name: str,
            stack_name: str,
            link: str) -> None:
        super().__init__(id, name)
        self.link = link
        self.boardname = board_name
        self.stackname = stack_name


class Email(NextcloudTalkRichObject):
    """E-mail."""

    object_type = 'email'


class File(NextcloudTalkRichObject):
    """File."""

    object_type = 'file'
    def __init__(
            self,
            id: str,
            name: str,
            path: str,
            size: Optional[str] = None,
            link: Optional[str] = None,
            mime_type: str = 'text/plain',
            preview_available: Optional[str] = None,
            mtime: Optional[str] = None,
            etag: Optional[str] = None,
            permissions: Optional[str] = None,
            width: Optional[str] = None,
            height: Optional[str] = None,
            blur_hash: Optional[str] = None) -> None:
        super().__init__(id, name)
        self.link = link
        self.path = path

        if size:
            self.size = size
        if mime_type:
            self.__dict__['mimetype'] = mime_type
        if preview_available:
            self.__dict__['preview-available'] = preview_available
        if mtime:
            self.mtime = mtime
        if etag:
            self.etag = etag
        if permissions:
            self.permissions = permissions
        if width:
            self.width = width
        if height:
            self.height = height
        if blur_hash:
            self.blurHash = blur_hash


class Form(NextcloudTalkRichObject):
    """Form."""

    object_type = 'forms-form'

    def __init__(
            self,
            id: str,
            name: str,
            link: str) -> None:
        super().__init__(id, name)
        self.link = link


class Highlight(NextcloudTalkRichObject):
    """Highlight."""

    object_type = 'highlight'

    def __init__(
            self,
            id: str,
            name: str,
            link: str) -> None:
        super().__init__(id, name)
        self.link = link


class GeoLocation(NextcloudTalkRichObject):
    """Geo-location."""

    object_type = 'geo-location'
    latitude = None
    longitude = None

    def __init__(
            self,
            id: str,
            name: str,
            latitude: str,
            longitude: str) -> None:
        super().__init__(id, name)
        self.latitude = latitude
        self.longitude = longitude


class OpenGraph(NextcloudTalkRichObject):
    """Open-Graph Attachment."""

    object_type = 'open-graph'

    def __init__(
            self,
            id: str,
            name: str,
            description: Optional[str],
            thumb: Optional[str],
            website: Optional[str],
            link: Optional[str]) -> None:
        super().__init__(id, name)
        if description:
            self.description = description
        if thumb:
            self.thumb = thumb
        if website:
            self.website = website
        if link:
            self.link = link


class PendingFederatedShare(NextcloudTalkRichObject):
    """Talk Attachment."""

    object_type = 'pending-federated-share'


class SystemTag(NextcloudTalkRichObject):
    """System Tag."""

    object_type = 'systemtag'

    def __init__(
            self,
            id: str,
            name: str,
            visibility: str,
            assignable: str) -> None:
        super().__init__(id, name)
        self.visibility = visibility
        self.assignable = assignable


class TalkAttachment(NextcloudTalkRichObject):
    """Talk Attachment."""

    object_type = 'talk-attachment'

    def __init__(
            self,
            id: str,
            name: str,
            conversation: str,
            mime_type: Optional[str] = None,
            preview_available: Optional[str] = None) -> None:
        super().__init__(id, name)
        self.conversation = conversation
        if mime_type:
            self.mimetime = mime_type
        if preview_available:
            self.__dict__['preview-avialable'] = preview_available


class User(NextcloudTalkRichObject):
    """User."""

    object_type = 'user'

    def __init__(
            self,
            id: str,
            name: str,
            server: Optional[str] = None) -> None:
        super().__init__(id, name)
        if server:
            self.server = server


class UserGroup(NextcloudTalkRichObject):
    """User group."""

    object_type = 'user-group'
