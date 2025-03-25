import pytest

from nextcloud_async.api import ConversationType
from nextcloud_async.api.ocs.talk.conversations import Conversation, ConversationsApi
from nextcloud_async.exceptions import NextcloudNotFoundError


# @pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestAvatars:
