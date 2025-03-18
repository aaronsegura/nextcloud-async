import asyncio
import os

import httpx
import pytest
import pytest_asyncio

from nextcloud_async import NextcloudClient
from nextcloud_async.api import (
    AppsApi,
    FilesApi,
    GroupFoldersApi,
    GroupsApi,
    LdapApi,
    LoginFlowV2Api,
    MapsApi,
    NotificationsApi,
    ShareesApi,
    SharesApi,
    StatusApi,
    UsersApi,
    apps_api,
    files_api,
    groupfolders_api,
    groups_api,
    ldap_api,
    loginflowv2_api,
    maps_api,
    notifications_api,
    sharees_api,
    shares_api,
    status_api,
    users_api,
)
from nextcloud_async.exceptions import NextcloudMethodNotAllowedError

from .constants import (
    APP_TOKEN,
    ENDPOINT,
    NEXTCLOUD_VERSION,
    PASSWORD,
    REMOTE_TEST_DIR,
    USER,
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
        ".".join(request.module.__name__.split(".")[2:]),
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
    files = files_api(nc)

    try:
        await files.mkdir(REMOTE_TEST_DIR)
    except NextcloudMethodNotAllowedError:
        await files.delete(REMOTE_TEST_DIR)
        await files.mkdir(REMOTE_TEST_DIR)


def pytest_sessionfinish(exitstatus: int):
    asyncio.run(async_sessionfinish(exitstatus))


async def async_sessionfinish(exitstatus: int):
    if exitstatus == 0 and not _NETWORK_BLOCKED:
        nc = NextcloudClient(ENDPOINT, USER, PASSWORD, http_client=httpx.AsyncClient())
        files = files_api(nc)
        await files.delete(REMOTE_TEST_DIR)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def nc():
    async with httpx.AsyncClient() as client:
        yield NextcloudClient(
            ENDPOINT, USER, app_token=APP_TOKEN, http_client=client, user_agent=USER_AGENT
        )


@pytest.fixture(scope="session", name="ldap_api")
def _ldap_api(nc: NextcloudClient) -> LdapApi:
    return ldap_api(nc)


@pytest.fixture(scope="session", name="apps_api")
def _apps_api(nc: NextcloudClient) -> AppsApi:
    return apps_api(nc)


@pytest.fixture(scope="session", name="files_api")
def _files_api(nc: NextcloudClient) -> FilesApi:
    return files_api(nc)


@pytest.fixture(scope="session")
def gf_api(nc: NextcloudClient) -> GroupFoldersApi:
    return groupfolders_api(nc)


@pytest.fixture(scope="session", name="groups_api")
def _groups_api(nc: NextcloudClient) -> GroupsApi:
    return groups_api(nc)


@pytest.fixture(scope="session", name="loginflowv2_api")
def _loginflowv2_api(nc: NextcloudClient) -> LoginFlowV2Api:
    return loginflowv2_api(nc)


@pytest.fixture(scope="session", name="maps_api")
def _maps_api(nc: NextcloudClient) -> MapsApi:
    return maps_api(nc)


@pytest.fixture(scope="session", name="notifications_api")
def _notifications_api(nc: NextcloudClient) -> NotificationsApi:
    return notifications_api(nc)


@pytest.fixture(scope="session", name="shares_api")
def _shares_api(nc: NextcloudClient) -> SharesApi:
    return shares_api(nc)


@pytest.fixture(scope="session", name="sharees_api")
def _sharees_api(nc: NextcloudClient) -> ShareesApi:
    return sharees_api(nc)


@pytest.fixture(scope="session", name="users_api")
def _users_api(nc: NextcloudClient) -> UsersApi:
    return users_api(nc)


@pytest.fixture(scope="session", name="status_api")
def _status_api(nc: NextcloudClient) -> StatusApi:
    return status_api(nc)
