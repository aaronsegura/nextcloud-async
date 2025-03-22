import pytest
import pytest_asyncio

from nextcloud_async import NextcloudClient
from nextcloud_async.api import (
    AppsApi,
    ConversationType,
    TalkApi,
    User,
    UsersApi,
    talk_api,
)
from nextcloud_async.api.ocs.talk.conversations import Conversation, ConversationsApi
from nextcloud_async.exceptions import NextcloudNotFoundError

from .constants import ENDPOINT, USER_AGENT


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def require_maps_enabled(apps_api: AppsApi):
    app_list = await apps_api.get_all("enabled")
    if "spreed" not in app_list:
        pytest.skip("Maps app is not enabled.  Skipping.", allow_module_level=True)


@pytest.fixture
def room_name(request) -> str:
    return f"{request.function.__name__}-{request.node.callspec.id}"


@pytest_asyncio.fixture(loop_scope="session")
async def group_room(conversations: ConversationsApi, room_name: str):
    room = await conversations.create(ConversationType.group, room_name=room_name)
    yield room
    await room.delete()


@pytest_asyncio.fixture(loop_scope="session")
async def public_room(user_talk_api: TalkApi, room_name: str):
    room = await user_talk_api.conversations.create(
        ConversationType.public, room_name=room_name
    )
    await room.leave()
    yield room
    await room.delete()


_USER_DATA = {
    "user_id": "PytestUser",
    "display_name": "Pyest User Guy",
    "email": "pytestguy@example.com",
    "language": "en",
    "subadmin": [],
    "groups": [],
    "quota": None,
    "password": "MondayToFridayPlane",
}


@pytest_asyncio.fixture(loop_scope="session")
async def test_user(users_api: UsersApi):
    user = await users_api.create(**_USER_DATA)
    yield user
    await user.delete()


@pytest_asyncio.fixture(loop_scope="session")
async def user_talk_api(test_user: User, users_api: UsersApi):
    try:
        from nextcloud_async.provider.httpx import HttpXBasicAuth

        client = NextcloudClient(
            ENDPOINT,
            users_api.driver.client.http_client,
            auth=HttpXBasicAuth(test_user.id, _USER_DATA["password"]),
            user_agent=USER_AGENT,
        )
    except ImportError:
        try:
            from nextcloud_async.provider.aiohttp import AioHttpBasicAuth

            client = NextcloudClient(
                ENDPOINT,
                users_api.driver.client.http_client,
                auth=AioHttpBasicAuth(test_user.id, _USER_DATA["password"]),
                user_agent=USER_AGENT,
            )
        except ImportError:
            raise RuntimeError("Could not find httpx or aiohttp.")

    return talk_api(client)


# @pytest.mark.vcr
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

    async def test_list_open(self, conversations: ConversationsApi, public_room):
        public_rooms = await conversations.list_open()
        assert [room for room in public_rooms if room == public_room]
