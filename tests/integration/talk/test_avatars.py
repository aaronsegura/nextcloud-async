import pytest
import pytest_asyncio

from io import BytesIO
from pathlib import PurePath
from typing import reveal_type

import aiofile

from nextcloud_async.api import ConversationType
from nextcloud_async.api.ocs.talk.conversations import Conversation, ConversationsApi


@pytest_asyncio.fixture(loop_scope="session")
async def conversation(conversations: ConversationsApi, room_name: str):
    conversation = await conversations.create(ConversationType.group, room_name=room_name)
    yield conversation
    await conversation.delete()


@pytest.mark.integration
# @pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestConversationAvatars:
    async def test_set_avatar(self, conversation: Conversation):
        avatar_path = PurePath(__file__).parent / "assets/avatar.jpg"
        async with aiofile.async_open(avatar_path.as_posix(), "rb") as fp:
            _sent_data = await fp.read()

        await conversation.set_avatar_image(_sent_data)
        _recv_data = await conversation.get_avatar(dark_mode=False)

        assert _sent_data == _recv_data
