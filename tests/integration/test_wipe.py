"""Test Nextcloud Remote Wipe API.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html
"""

import pytest
import pytest_asyncio

from unittest.mock import AsyncMock

from nextcloud_async.api import WipeApi
from nextcloud_async.exceptions import NextcloudNotFoundError
from nextcloud_async.provider import HttpResponseMock


@pytest_asyncio.fixture
async def require_app_token(
    wipe_api: tuple[WipeApi, HttpResponseMock],
) -> None:
    api, _ = wipe_api
    if not api.driver.client.app_token:
        pytest.skip("Not valid for this test.")


@pytest.mark.integration
@pytest.mark.vcr
@pytest.mark.asyncio
class TestWipeApi:
    async def test_check_false_by_basic_auth(
        self, wipe_api: tuple[WipeApi, HttpResponseMock]
    ):
        api, _ = wipe_api
        if api.driver.client.app_token:
            pytest.skip("Not valid for this test.")

        assert await api.check() is False

    async def test_check_false_by_exception(
        self,
        require_app_token,  # noqa: ARG002
        wipe_api: tuple[WipeApi, HttpResponseMock],
    ):
        api, mock = wipe_api
        api.driver.client.http_client.request = AsyncMock(
            side_effect=NextcloudNotFoundError()
        )
        result = await api.check()
        assert result is False

    async def test_check_true_by_valid_response(
        self,
        require_app_token,  # noqa: ARG002
        wipe_api: tuple[WipeApi, HttpResponseMock],
    ):
        api, mock = wipe_api
        _response = mock(200, json={"wipe": True})  # type: ignore
        api.driver.client.http_client.request = AsyncMock(return_value=_response)
        result = await api.check()
        assert result is True
