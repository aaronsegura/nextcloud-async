from unittest.mock import AsyncMock, MagicMock

import pytest

from nextcloud_async import NextcloudClient
from nextcloud_async.driver import NextcloudBaseApi, NextcloudDavApi, NextcloudOcsApi

from ..constants import APP_TOKEN, ENDPOINT, PASSWORD, USER, USER_AGENT


@pytest.fixture
def nc_basic_mocked() -> NextcloudClient:
    return NextcloudClient(
        ENDPOINT, USER, PASSWORD, http_client=AsyncMock(), user_agent=USER_AGENT
    )


@pytest.fixture
def nc_token_mocked() -> NextcloudClient:
    return NextcloudClient(
        ENDPOINT,
        USER,
        app_token=APP_TOKEN,
        http_client=AsyncMock(),
        user_agent=USER_AGENT,
    )
