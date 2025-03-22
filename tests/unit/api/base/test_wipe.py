import pytest

from unittest.mock import AsyncMock, PropertyMock, call

from nextcloud_async.api import WipeApi
from nextcloud_async.exceptions import NextcloudMethodNotAllowedError

from .constants import APP_TOKEN, ENDPOINT


@pytest.fixture(name="wipe_api")
def _wipe_api() -> WipeApi:
    return WipeApi(AsyncMock())


@pytest.mark.asyncio
class TestWipe:
    async def test_check_no_app_token(self, wipe_api: WipeApi):
        wipe_api.driver.client = PropertyMock(app_token=None)
        with pytest.raises(NextcloudMethodNotAllowedError):
            await wipe_api.check()
        wipe_api.driver.assert_not_called()

    async def test_check_app_token(self, wipe_api: WipeApi):
        wipe_api.driver.client = PropertyMock(app_token=APP_TOKEN)
        result = await wipe_api.check()
        expected = [
            call.post(
                path="/index.php/core/wipe/check",
                data={"token": APP_TOKEN},
                headers=None,
            ),
            call.post().__contains__("wipe"),
        ]
        wipe_api.driver.assert_has_calls(expected)
        assert result is False

    async def test_notify_wiped(self, wipe_api: WipeApi):
        client_property = PropertyMock(
            endpoint=ENDPOINT, app_token=APP_TOKEN, http_client=AsyncMock()
        )
        wipe_api.driver.client = client_property
        await wipe_api.notify_wiped()
        expected = [
            call.post(
                url=f"{ENDPOINT}/index.php/core/wipe/success",
                data={"token": "[app token]"},
            )
        ]
        wipe_api.driver.client.http_client.assert_has_calls(expected)
