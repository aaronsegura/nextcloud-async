import pytest
import pytest_asyncio

import asyncio

from nextcloud_async import NextcloudClient
from nextcloud_async.api import (
    AppsApi,
    BreakoutRoom,
    ConversationType,
    ListableScope,
    TalkApi,
    User,
    UsersApi,
    talk_api,
)
from nextcloud_async.api.ocs.talk.conversations import ConversationsApi

from .constants import ENDPOINT, USER_AGENT


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def require_app_enabled(apps_api: AppsApi):
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
        ConversationType.group, room_name=room_name
    )
    await room.set_scope(ListableScope.everyone)
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
async def user_talk_api(test_user: User, request: pytest.FixtureRequest):
    client = None
    if "httpx" in request.node.callspec.id:
        try:
            from nextcloud_async.provider.httpx import HttpXBasicAuth, HttpXClientProvider

            client = NextcloudClient(
                ENDPOINT,
                http_client=HttpXClientProvider(timeout=30),
                auth=HttpXBasicAuth(test_user.id, _USER_DATA["password"]),
                user_agent=USER_AGENT,
            )
        except ImportError:
            pass

    if "aiohttp" in request.node.callspec.id:
        try:
            from nextcloud_async.provider.aiohttp import (
                AioHttpBasicAuth,
                AioHttpClientProvider,
            )

            client = NextcloudClient(
                ENDPOINT,
                http_client=AioHttpClientProvider(timeout=30),
                auth=AioHttpBasicAuth(test_user.id, _USER_DATA["password"]),
                user_agent=USER_AGENT,
            )
        except ImportError:
            pass

    if not client:
        raise RuntimeError(
            f"Could not find suitable client for {request.node.callspec.id}"
        )

    return talk_api(client)
