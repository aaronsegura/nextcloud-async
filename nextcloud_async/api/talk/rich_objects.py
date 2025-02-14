"""Classes representing Rich Objects for sharing.

https://github.com/nextcloud/server/blob/master/lib/public/RichObjectStrings/Definitions.php

I don't really understand why most of these exist when they don't
seem to enforce any kind of argument checking.  You can put in
whatever you want for 'id' in most of them, and it'll be accepted
and entered into the chat.
"""


class NextcloudTalkRichObject(object):
    """Base Class for Rich Objects."""

    object_type = None

    def __init__(self, id: str, name: str, **kwargs):
        """Set object metadata."""
        self.__dict__.update(kwargs)
        self.id = id
        self.name = name

    @property
    def metadata(self):
        """Return metadata array."""
        return {'id': self.id, 'name': self.name}


class AddressBook(NextcloudTalkRichObject):
    """Address book."""

    object_type = 'addressbook'


class AddressBookContact(NextcloudTalkRichObject):
    """Addressbook contact."""

    object_type = 'addressbook-contact'


class Announcement(NextcloudTalkRichObject):
    """Announcement."""

    object_type = 'announcement'


class Calendar(NextcloudTalkRichObject):
    """Calendar."""

    object_type = 'calendar'


class CalendarEvent(NextcloudTalkRichObject):
    """Calendar Event."""

    object_type = 'calendar-event'


class Call(NextcloudTalkRichObject):
    """Nextcloud Talk Call."""

    object_type = 'call'
    call_type = ''

    @property
    def metadata(self):
        """Return object metadata."""
        return {
            'id': self.id,
            'name': self.name,
            'call-type': self.call_type
        }


class Circle(NextcloudTalkRichObject):
    """Cirle."""

    object_type = 'circle'


class DeckBoard(NextcloudTalkRichObject):
    """Deck board."""

    object_type = 'deck-board'


class DeckCard(NextcloudTalkRichObject):
    """Deck card."""

    object_type = 'deck-card'


class Email(NextcloudTalkRichObject):
    """E-mail."""

    object_type = 'email'


class File(NextcloudTalkRichObject):
    """File."""

    object_type = 'file'
    path = ''

    allowed_props = ['size', 'link', 'mimetype', 'preview-available', 'mtime']

    def __init__(self, name: str, path: str, **kwargs):
        """Set file object metadata."""

        if not all(key in self.allowed_props for key in kwargs):
            raise ValueError(f'Supported properties {self.allowed_props}')

        init = {
            'id': name,
            'name': name,
            'path': path,
        }
        data = { **init, **kwargs }
        super().__init__(**data)

    @property
    def metadata(self):
        """Return object metadata."""
        return self.__dict__

class Form(NextcloudTalkRichObject):
    """Form."""

    object_type = 'forms-form'


class GeoLocation(NextcloudTalkRichObject):
    """Geo-location."""

    object_type = 'geo-location'
    latitude = None
    longitude = None

    def __init__(self, name: str, latitude: str, longitude: str):
        """Set Geolocation metadata."""
        data = {
            'id': f'geo:{latitude},{longitude}',
            'name': name,
            'longitude': longitude,
            'latitude': latitude}
        super().__init__(**data)

    def __str__(self):
        return f'{__class__.__name__}'\
               f'(latitude={self.latitude}, longitude={self.longitude}, name={self.name})'

    @property
    def metadata(self):
        """Return geolocation metadata."""
        return {
            'id': f'geo:{self.latitude},{self.longitude}',
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }


class TalkAttachment(NextcloudTalkRichObject):
    """Talk Attachment."""

    object_type = 'talk-attachment'


class User(NextcloudTalkRichObject):
    """User."""

    object_type = 'user'


class UserGroup(NextcloudTalkRichObject):
    """User group."""

    object_type = 'user-group'
