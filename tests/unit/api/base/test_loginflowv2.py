from unittest.mock import AsyncMock, call

import pytest

from nextcloud_async import NextcloudClient
from nextcloud_async.api import LoginFlowV2
from nextcloud_async.exceptions import (
    NextcloudForbiddenError,
    NextcloudLoginFlowTimeoutError,
    NextcloudNotFoundError,
)

from ...constants import APP_TOKEN, ENDPOINT, PASSWORD, USER


@pytest.fixture
def loginflow(asyncmock: AsyncMock):
    nc = NextcloudClient(ENDPOINT, USER, PASSWORD, http_client=asyncmock)
    api = LoginFlowV2(nc)
    api.api = asyncmock
    return api


@pytest.mark.asyncio
class TestLoginFlowV2:
    async def test_initiate_flow(self, loginflow: LoginFlowV2):
        await loginflow.initiate()
        expected = [call.post(path="/login/v2", data=None, headers=None)]
        loginflow.api.assert_has_calls(expected)

    async def test_wait_confirm_timeout(self, loginflow: LoginFlowV2):
        loginflow.api.post.side_effect = NextcloudNotFoundError
        with pytest.raises(NextcloudLoginFlowTimeoutError):
            await loginflow.wait_confirm(token="[token]", timeout=1)
        expected = [
            call.post(path="/login/v2/poll", data={"token": "[token]"}, headers=None)
        ]
        loginflow.api.assert_has_calls(expected)

    async def test_wait_confirm_success(self, loginflow: LoginFlowV2):
        loginflow.api.post.return_value = {"key": "value"}
        response = await loginflow.wait_confirm(token="[token]", timeout=1)
        assert response == {"key": "value"}
        expected = [
            call.post(path="/login/v2/poll", data={"token": "[token]"}, headers=None)
        ]
        loginflow.api.assert_has_calls(expected)

    async def test_destroy_token_user_password(self, loginflow: LoginFlowV2):
        with pytest.raises(NextcloudForbiddenError):
            await loginflow.destroy_token()

    async def test_destroy_token_success(
        self, monkeypatch: pytest.MonkeyPatch, asyncmock: AsyncMock
    ):
        monkeypatch.setattr(
            "nextcloud_async.driver.ocs.NextcloudOcsApi.delete", asyncmock
        )
        nc = NextcloudClient(ENDPOINT, USER, app_token=APP_TOKEN, http_client=asyncmock)
        loginflow = LoginFlowV2(nc)
        await loginflow.destroy_token()
        expected = [call(path="/core/apppassword")]
        asyncmock.assert_has_calls(expected)
