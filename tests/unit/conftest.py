# import pytest

# from unittest.mock import AsyncMock, MagicMock

# from nextcloud_async import NextcloudClient
# from nextcloud_async.driver import (
#     NextcloudBaseDriver,
#     NextcloudDavDriver,
#     NextcloudOcsDriver,
# )

# from ..constants import APP_TOKEN, ENDPOINT, PASSWORD, USER, USER_AGENT


# @pytest.fixture
# def nc_basic_mocked() -> NextcloudClient:
#     return NextcloudClient(
#         ENDPOINT, AsyncMock(), , user_agent=USER_AGENT
#     )


# @pytest.fixture
# def nc_token_mocked() -> NextcloudClient:
#     return NextcloudClient(
#         ENDPOINT,
#         USER,
#         app_token=APP_TOKEN,
#         http_client=AsyncMock(),
#         user_agent=USER_AGENT,
#     )
