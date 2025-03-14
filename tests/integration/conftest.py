import httpx
import os
import asyncio
import pytest
import pytest_asyncio

from nextcloud_async import NextcloudClient
from nextcloud_async.api import (
    Files,
    Ldap,
    Apps,
    Groups,
    GroupFolders,
    LoginFlowV2,
    Maps,
    Notifications,
    Shares,
    Sharees,
    Status,
    Users,
)
from nextcloud_async.exceptions import NextcloudMethodNotAllowedError

from .constants import (
    NEXTCLOUD_VERSION,
    USER,
    PASSWORD,
    ENDPOINT,
    REMOTE_TEST_DIR,
    USER_AGENT,
)

_NETWORK_BLOCKED = False


@pytest.fixture
def vcr_config():
    return {
        # Add 'headers' to match_on defaults
        "match_on": ["method", "scheme", "host", "port", "path", "query", "headers"],
        # cookies will change between sessions
        "filter_headers": ["cookie", "authorization"],
        # Write plain text responses to cassettes
        "decode_compressed_response": True,
    }


@pytest.fixture
def vcr_cassette_dir(request):
    # Put all cassettes in cassettes/nextcloud-{version}/{module}/{test}.yaml
    return os.path.join(
        f"tests/integration/cassettes/nextcloud-{NEXTCLOUD_VERSION}",
        ".".join(request.module.__name__.split(".")[1:]),
    )


@pytest.fixture(scope="session")
def network_blocked(pytestconfig: pytest.Config) -> bool:
    if pytestconfig.getoption("--block-network"):
        return True
    else:
        return False


def pytest_configure(config: pytest.Config):
    if config.getoption("--block-network"):
        globals()["_NETWORK_BLOCKED"] = True


def pytest_sessionstart():
    # Prep the test environment
    # User-defined fixtures do not work here.
    asyncio.run(async_sessionstart())


async def async_sessionstart():
    if _NETWORK_BLOCKED:
        return

    nc = NextcloudClient(
        ENDPOINT,
        USER,
        PASSWORD,
        http_client=httpx.AsyncClient(timeout=30),
        user_agent=USER_AGENT,
    )
    files_api = Files(nc)

    try:
        await files_api.mkdir(REMOTE_TEST_DIR)
    except NextcloudMethodNotAllowedError:
        await files_api.delete(REMOTE_TEST_DIR)
        await files_api.mkdir(REMOTE_TEST_DIR)


def pytest_sessionfinish(exitstatus: int):
    asyncio.run(async_sessionfinish(exitstatus))


async def async_sessionfinish(exitstatus: int):
    if exitstatus == 0 and not _NETWORK_BLOCKED:
        nc = NextcloudClient(ENDPOINT, USER, PASSWORD, http_client=httpx.AsyncClient())
        files_api = Files(nc)
        await files_api.delete(REMOTE_TEST_DIR)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def nc():
    async with httpx.AsyncClient() as client:
        yield NextcloudClient(
            ENDPOINT, USER, PASSWORD, http_client=client, user_agent=USER_AGENT
        )


@pytest.fixture(scope="session")
def ldap_api(nc: NextcloudClient):
    return Ldap(nc)


@pytest.fixture(scope="session")
def apps(nc: NextcloudClient) -> Apps:
    return Apps(nc)


@pytest.fixture(scope="session")
def files_api(nc: NextcloudClient):
    return Files(nc)


@pytest.fixture(scope="session")
def gf_api(nc: NextcloudClient) -> GroupFolders:
    return GroupFolders(nc)


@pytest.fixture(scope="session")
def groups_api(nc: NextcloudClient) -> Groups:
    return Groups(nc)


@pytest.fixture(scope="session")
def loginflowv2_api(nc: NextcloudClient) -> LoginFlowV2:
    return LoginFlowV2(nc)


@pytest.fixture(scope="session")
def maps_api(nc: NextcloudClient) -> Maps:
    return Maps(nc)


@pytest.fixture(scope="session")
def notifications_api(nc: NextcloudClient) -> Notifications:
    return Notifications(nc)


@pytest.fixture(scope="session")
def shares_api(nc: NextcloudClient) -> Shares:
    return Shares(nc)


@pytest.fixture(scope="session")
def sharees_api(nc: NextcloudClient) -> Sharees:
    return Sharees(nc)


@pytest.fixture(scope="session")
def users_api(nc: NextcloudClient) -> Users:
    return Users(nc)


@pytest.fixture(scope="session")
def status_api(nc: NextcloudClient) -> Status:
    return Status(nc)
