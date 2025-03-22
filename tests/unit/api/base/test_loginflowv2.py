import pytest

from unittest.mock import AsyncMock, call

from nextcloud_async import NextcloudClient
from nextcloud_async.api import LoginFlowV2Api, loginflowv2_api
from nextcloud_async.driver import NextcloudBaseDriver
from nextcloud_async.exceptions import (
    NextcloudLoginFlowTimeoutError,
    NextcloudNotFoundError,
)


@pytest.fixture
def loginflow() -> LoginFlowV2Api:
    api = LoginFlowV2Api(AsyncMock())
    return api


class TestFactory:
    def test_init(self, nc_basic_mocked: AsyncMock):
        lf_api = loginflowv2_api(nc_basic_mocked)
        assert lf_api.driver.client == nc_basic_mocked
        assert isinstance(lf_api.driver, NextcloudBaseDriver)
        assert isinstance(lf_api.driver.client, NextcloudClient)


@pytest.mark.asyncio
class TestLoginFlowV2:
    async def test_initiate_flow(self, loginflow: LoginFlowV2Api):
        await loginflow.initiate()
        expected = [call.post(path="/login/v2", data=None, headers=None)]
        loginflow.driver.assert_has_calls(expected)

    async def test_wait_confirm_timeout(self, loginflow: LoginFlowV2Api):
        loginflow.driver.post.side_effect = NextcloudNotFoundError
        with pytest.raises(NextcloudLoginFlowTimeoutError):
            await loginflow.wait_confirm(token="[token]", timeout=1)
        expected = [
            call.post(path="/login/v2/poll", data={"token": "[token]"}, headers=None)
        ]
        loginflow.driver.assert_has_calls(expected)

    async def test_wait_confirm_success(self, loginflow: LoginFlowV2Api):
        loginflow.driver.post.return_value = {"key": "value"}
        response = await loginflow.wait_confirm(token="[token]", timeout=1)
        assert response == {"key": "value"}
        expected = [
            call.post(path="/login/v2/poll", data={"token": "[token]"}, headers=None)
        ]
        loginflow.driver.assert_has_calls(expected)
