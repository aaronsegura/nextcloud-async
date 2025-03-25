import pytest

from nextcloud_async.api import ConversationType
from nextcloud_async.api.ocs.talk.conversations import Conversation, ConversationsApi
from nextcloud_async.exceptions import NextcloudNotFoundError


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestConversationsApi:
    async def test_get_all(self, conversations: ConversationsApi):
        rooms = await conversations.get_all()
        for room in rooms:
            assert isinstance(room, Conversation)

    async def test_get(self, conversations: ConversationsApi, group_room: Conversation):
        room = await conversations.get(group_room.token)
        assert room == group_room

    async def test_get_noexist(self, conversations: ConversationsApi):
        with pytest.raises(NextcloudNotFoundError):
            await conversations.get("noexist")

    async def test_get_note_to_self(self, conversations: ConversationsApi):
        notes = await conversations.get_note_to_self()
        assert isinstance(notes, Conversation)
        assert notes.objectType == ConversationType.note_to_self.name

    async def test_list_open(
        self, conversations: ConversationsApi, public_room: Conversation
    ):
        public_rooms = await conversations.list_open()
        assert [room.is_listable for room in public_rooms if room == public_room]
