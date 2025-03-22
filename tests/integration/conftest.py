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
    TalkApi,
    UsersApi,
    WipeApi,
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
    talk_api,
    users_api,
    wipe_api,
)
from nextcloud_async.exceptions import NextcloudMethodNotAllowedError
from nextcloud_async.provider import HttpResponseMock

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

    if find_spec("httpx"):
        from nextcloud_async.provider import httpx

        _http_type = httpx.HttpXClientProvider
        _http_auth_type = httpx.HttpXBasicAuth
    elif find_spec("aiohttp"):
        from nextcloud_async.provider import aiohttp

        _http_type = aiohttp.AioHttpClientProvider
        _http_auth_type = aiohttp.AioHttpBasicAuth
    else:
        raise RuntimeError("Could not find httpx or aiohttp clients.")

    nc = NextcloudClient(
        ENDPOINT,
        auth=_http_auth_type(USER, PASSWORD),
        http_client=_http_type(timeout=10),
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
    pytest.importorskip("httpx")
    from nextcloud_async.provider.httpx import (
        HttpXBasicAuth,
        HttpXClientProvider,
    )

    nc = NextcloudClient(
        ENDPOINT,
        http_client=HttpXClientProvider(timeout=10),
        auth=HttpXBasicAuth(USER, PASSWORD),
        user_agent=USER_AGENT,
    )
    return nc


def nc_aiohttp_basic():
    pytest.importorskip("aiohttp")
    from nextcloud_async.provider.aiohttp import (
        AioHttpBasicAuth,
        AioHttpClientProvider,
    )

    nc = NextcloudClient(
        ENDPOINT,
        http_client=AioHttpClientProvider(timeout=10),
        auth=AioHttpBasicAuth(USER, PASSWORD),
        user_agent=USER_AGENT,
    )
    return nc


def nc_httpx_app_token():
    pytest.importorskip("httpx")
    from nextcloud_async.provider.httpx import (
        HttpXClientProvider,
    )

    nc = NextcloudClient(
        ENDPOINT,
        http_client=HttpXClientProvider(timeout=10),
        user=USER,
        app_token=APP_TOKEN,
        user_agent=USER_AGENT,
    )
    return nc


def nc_aiohttp_app_token():
    pytest.importorskip("aiohttp")
    from nextcloud_async.provider.aiohttp import (
        AioHttpClientProvider,
    )

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
        "aiohttp_basic",
        "aiohttp_app_token",
        "httpx_basic",
        "httpx_app_token",
    ],
    loop_scope="session",
)
async def nc(
    request,
) -> tuple[NextcloudClient, HttpResponseMock]:
    match request.param:
        case "httpx_app_token":
            try:
                from nextcloud_async.provider.httpx import HttpXResponseMock
            except ImportError:
                pytest.skip("HTTPX not installed.")

            return nc_httpx_app_token(), HttpXResponseMock  # type: ignore
        case "httpx_basic":
            try:
                from nextcloud_async.provider.httpx import HttpXResponseMock
            except ImportError:
                pytest.skip("HTTPX not installed.")

            return nc_httpx_basic(), HttpXResponseMock  # type: ignore
        case "aiohttp_app_token":
            try:
                from nextcloud_async.provider.aiohttp import AioHttpResponseMock
            except ImportError:
                pytest.skip("AioHTTP not installed.")

            return nc_aiohttp_app_token(), AioHttpResponseMock  # type: ignore
        case "aiohttp_basic":
            try:
                from nextcloud_async.provider.aiohttp import AioHttpResponseMock
            except ImportError:
                pytest.skip("AioHTTP not installed.")

            return nc_aiohttp_basic(), AioHttpResponseMock  # type: ignore
        case _:
            raise RuntimeError("Unknown HTTP client type.")


@pytest.fixture(name="ldap_api")
def _ldap_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> LdapApi:
    return ldap_api(nc[0])


@pytest.fixture(name="apps_api")
def _apps_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> AppsApi:
    return apps_api(nc[0])


@pytest.fixture(name="files_api")
def _files_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> FilesApi:
    return files_api(nc[0])


@pytest.fixture(name="gf_api")
def _gf_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> GroupFoldersApi:
    api = groupfolders_api(nc[0])
    api.driver.destroy_capabilities()
    return api


@pytest.fixture(name="groups_api")
def _groups_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> GroupsApi:
    return groups_api(nc[0])


@pytest.fixture(name="loginflowv2_api")
def _loginflowv2_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> tuple[LoginFlowV2Api, HttpResponseMock]:
    return loginflowv2_api(nc[0]), nc[1]


@pytest.fixture(name="maps_api")
def _maps_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> MapsApi:
    if nc[0].app_token:
        pytest.skip("Maps app does not support app_token authentication.")
    return maps_api(nc[0])


@pytest.fixture(name="notifications_api")
def _notifications_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> tuple[NotificationsApi, HttpResponseMock]:
    return notifications_api(nc[0]), nc[1]


@pytest.fixture(name="shares_api")
def _shares_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> SharesApi:
    return shares_api(nc[0])


@pytest.fixture(name="sharees_api")
def _sharees_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> ShareesApi:
    return sharees_api(nc[0])


@pytest.fixture(name="users_api")
def _users_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> UsersApi:
    return users_api(nc[0])


@pytest.fixture(name="status_api")
def _status_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> StatusApi:
    return status_api(nc[0])


@pytest.fixture(name="wipe_api")
def _wipe_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> tuple[WipeApi, HttpResponseMock]:
    return wipe_api(nc[0]), nc[1]


@pytest.fixture(name="talk_api")
def _talk_api(
    nc: tuple[NextcloudClient, HttpResponseMock],
) -> tuple[TalkApi, HttpResponseMock]:
    return talk_api(nc[0]), nc[1]


@pytest.fixture(name="conversations")
def _conversations(talk_api: tuple[TalkApi, HttpResponseMock]):
    api, mock = talk_api
    return api.conversations
