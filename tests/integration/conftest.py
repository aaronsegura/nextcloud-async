import pytest
import pytest_asyncio

import asyncio
import logging
import os
from importlib.util import find_spec

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
from nextcloud_async.provider.aiohttp import (
    AioHttpBasicAuth,
    AioHttpClientProvider,
    AioHttpResponseMock,
)
from nextcloud_async.provider.httpx import (
    HttpXBasicAuth,
    HttpXClientProvider,
    HttpXResponseMock,
)

from .constants import (
    APP_TOKEN,
    ENDPOINT,
    NEXTCLOUD_VERSION,
    PASSWORD,
    REMOTE_BASE_DIR,
    USER,
    USER_AGENT,
)

log = logging.getLogger("nextcloud_async")

if find_spec("httpx"):
    HTTP_TYPE = AioHttpClientProvider
    HTTP_AUTH_TYPE = AioHttpBasicAuth
elif find_spec("aiohttp"):
    HTTP_TYPE = HttpXClientProvider
    HTTP_AUTH_TYPE = HttpXBasicAuth
else:
    raise RuntimeError("Could not find httpx or aiohttp clients.")


_NETWORK_BLOCKED = False


"""
    Plugins Configuration
"""


@pytest.fixture
def vcr_config():
    return {
        # Add 'headers' to match_on defaults
        "match_on": [
            "method",
            "scheme",
            "host",
            "port",
            "path",
            "query",
            "headers",
        ],
        # cookies will change between sessions
        "filter_headers": [
            "cookie",
            "authorization",
        ],
        # Write plain text responses to cassettes
        "decode_compressed_response": True,
        "allow_playback_repeats": False,
    }


@pytest.fixture
def vcr_cassette_dir(request):
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


"""
    Session Startup/Teardown
"""


def nextcloud_client() -> NextcloudClient:
    """Generate a nextcloud client for setup/teardown."""
    nc = NextcloudClient(
        ENDPOINT,
        auth=HTTP_AUTH_TYPE(USER, PASSWORD),
        http_client=HTTP_TYPE(timeout=10),
        user_agent=USER_AGENT,
    )
    return nc


@pytest.mark.asyncio(autouse=True)
async def remote_base_dir(files_api: FilesApi):
    try:
        await files_api.mkdir(REMOTE_BASE_DIR)
    except NextcloudMethodNotAllowedError:
        await files_api.delete(REMOTE_BASE_DIR)
        await files_api.mkdir(REMOTE_BASE_DIR)
    dir = await files_api.get_all(REMOTE_BASE_DIR)
    yield dir
    await dir.delete()


def pytest_sessionstart(session: pytest.Session):
    # Prep the test environment

    if not session.config.getoption("--collect-only"):
        asyncio.run(async_sessionstart())


async def async_sessionstart():
    if _NETWORK_BLOCKED:
        return
    nc = nextcloud_client()
    files = files_api(nc)

    try:
        await files.mkdir(REMOTE_BASE_DIR)
    except NextcloudMethodNotAllowedError:
        await files.delete(REMOTE_BASE_DIR)
        await files.mkdir(REMOTE_BASE_DIR)
    log.debug("Session startup complete.")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    asyncio.run(async_sessionfinish(session, exitstatus))


async def async_sessionfinish(session: pytest.Session, exitstatus: int):
    if (
        exitstatus == 0
        and not _NETWORK_BLOCKED
        and "--collect-only" not in session.config.invocation_params.args
    ):
        nc = nextcloud_client()
        files = files_api(nc)
        await files.delete(REMOTE_BASE_DIR)


"""
    Fixtures
"""


@pytest_asyncio.fixture(loop_scope="session")
async def remote_test_dir(files_api: FilesApi, request: pytest.FixtureRequest):
    dir = (
        f"{REMOTE_BASE_DIR}"
        f"/{'.'.join(request.module.__name__.split('.')[2:])}"
        f"-{request.function.__name__}-{request.node.callspec.id}"
    )
    await files_api.mkdir(dir)
    return dir


def nc_httpx_basic():
    nc = NextcloudClient(
        ENDPOINT,
        http_client=HttpXClientProvider(timeout=10),
        auth=HttpXBasicAuth(USER, PASSWORD),
        user_agent=USER_AGENT,
    )
    return nc


def nc_aiohttp_basic():
    nc = NextcloudClient(
        ENDPOINT,
        http_client=AioHttpClientProvider(timeout=10),
        auth=AioHttpBasicAuth(USER, PASSWORD),
        user_agent=USER_AGENT,
    )
    return nc


def nc_httpx_app_token():
    nc = NextcloudClient(
        ENDPOINT,
        http_client=HttpXClientProvider(timeout=10),
        user=USER,
        app_token=APP_TOKEN,
        user_agent=USER_AGENT,
    )
    return nc


def nc_aiohttp_app_token():
    nc = NextcloudClient(
        ENDPOINT,
        http_client=AioHttpClientProvider(timeout=10),
        user=USER,
        app_token=APP_TOKEN,
        user_agent=USER_AGENT,
    )
    return nc


@pytest_asyncio.fixture(
    params=[
        ("aiohttp_basic", AioHttpResponseMock),
        ("aiohttp_app_token", AioHttpResponseMock),
        ("httpx_basic", HttpXResponseMock),
        ("httpx_app_token", HttpXResponseMock),
    ],
    loop_scope="session",
    ids=["aiohttp_basic", "aiohttp_app_token", "httpx_basic", "httpx_app_token"],
)
async def nc(request) -> tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock]:
    match request.param[0]:
        case "httpx_app_token":
            # pytest.skip()
            return nc_httpx_app_token(), request.param[1]
        case "httpx_basic":
            # pytest.skip()
            return nc_httpx_basic(), request.param[1]
        case "aiohttp_app_token":
            # pytest.skip()
            return nc_aiohttp_app_token(), request.param[1]
        case "aiohttp_basic":
            #  pytest.skip()
            return nc_aiohttp_basic(), request.param[1]
        case _:
            raise RuntimeError("Unknown HTTP client type.")


@pytest.fixture(name="ldap_api")
def _ldap_api(nc: NextcloudClient) -> LdapApi:
    return ldap_api(nc[0])


@pytest.fixture(name="apps_api")
def _apps_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> AppsApi:
    return apps_api(nc[0])


@pytest.fixture(name="files_api")
def _files_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> FilesApi:
    return files_api(nc[0])


@pytest.fixture(name="gf_api")
def _gf_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> GroupFoldersApi:
    api = groupfolders_api(nc[0])
    api.driver.destroy_capabilities()
    return api


@pytest.fixture(name="groups_api")
def _groups_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> GroupsApi:
    return groups_api(nc[0])


@pytest.fixture(name="loginflowv2_api")
def _loginflowv2_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> tuple[LoginFlowV2Api, HttpXResponseMock | AioHttpResponseMock]:
    return loginflowv2_api(nc[0]), nc[1]


@pytest.fixture(name="maps_api")
def _maps_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> MapsApi:
    if nc[0].app_token:
        pytest.skip()
    return maps_api(nc[0])


@pytest.fixture(name="notifications_api")
def _notifications_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> tuple[NotificationsApi, HttpXResponseMock | AioHttpResponseMock]:
    return notifications_api(nc[0]), nc[1]


@pytest.fixture(name="shares_api")
def _shares_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> SharesApi:
    return shares_api(nc[0])


@pytest.fixture(name="sharees_api")
def _sharees_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> ShareesApi:
    return sharees_api(nc[0])


@pytest.fixture(name="users_api")
def _users_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> UsersApi:
    return users_api(nc[0])


@pytest.fixture(name="status_api")
def _status_api(
    nc: tuple[NextcloudClient, HttpXResponseMock | AioHttpResponseMock],
) -> StatusApi:
    return status_api(nc[0])
