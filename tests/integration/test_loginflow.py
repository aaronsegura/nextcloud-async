import pytest

from unittest.mock import AsyncMock, call

from nextcloud_async.api import LoginFlowV2Api
from nextcloud_async.exceptions import (
    NextcloudLoginFlowTimeoutError,
)
from nextcloud_async.provider import HttpResponseMock

from .constants import APP_TOKEN, ENDPOINT, USER, USER_AGENT


@pytest.mark.asyncio(loop_scope="session")
class TestLoginFlowV2:
    """Must monkeypatch and mock this one since it requires user intervention."""

    async def test_login_flow_initiate(
        self,
        loginflowv2_api: tuple[LoginFlowV2Api, HttpResponseMock],
    ):
        api, response_mock = loginflowv2_api

        response_data = {
            "poll": {
                "token": "RandomString",
                "endpoint": f"{ENDPOINT}/login/v2/poll",
            },
            "login": f"{ENDPOINT}/login/v2/flow/AnotherRandomString",
        }

        _response = response_mock(200, json=response_data)  # type: ignore
        api.driver.client.http_client.request = AsyncMock(return_value=_response)
        response = await api.initiate()
        assert response["login"] == f"{ENDPOINT}/login/v2/flow/AnotherRandomString"
        assert response["poll"]["token"] == "RandomString"

    async def test_login_flow_confirm_success(
        self,
        loginflowv2_api: tuple[LoginFlowV2Api, HttpResponseMock],
    ):
        api, response_mock = loginflowv2_api

        response_data = {
            "server": ENDPOINT,
            "loginName": USER,
            "appPassword": "[app password]",
        }
        _response = response_mock(200, json=response_data)  # type: ignore
        api.driver.client.http_client.request = AsyncMock(return_value=_response)
        response = await api.wait_confirm("RandomStringToken", timeout=1)

        assert response["server"] == ENDPOINT
        assert response["loginName"] == USER
        assert response["appPassword"] == "[app password]"
        _auth = api.driver.client.auth if api.driver.client.auth else None
        _auth_headers = (
            {"Authorization": f"Bearer {APP_TOKEN}"}
            if api.driver.client.app_token
            else {}
        )
        expected = [
            call(
                method="POST",
                auth=_auth,
                url=f"{ENDPOINT}/index.php/login/v2/poll",
                data={"token": "RandomStringToken", "format": "json"},
                content=None,
                json=None,
                headers={"User-Agent": USER_AGENT, **_auth_headers},
            )
        ]
        api.driver.client.http_client.request.assert_has_calls(expected)

    async def test_login_flow_timeout(
        self,
        loginflowv2_api: tuple[LoginFlowV2Api, HttpResponseMock],
    ):
        api, response_mock = loginflowv2_api

        _response = response_mock(404, "")  # type: ignore
        api.driver.client.http_client.request = AsyncMock(return_value=_response)
        with pytest.raises(NextcloudLoginFlowTimeoutError):
            await api.wait_confirm("[TOKEN]", timeout=0, interval=1)

    # async def test_destroy_app_token_using_password(
    #     self, httpx_mock: HTTPXMock, loginflowv2_api: LoginFlowV2Api
    # ):
    #     _empty_200 = bytes(
    #         '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK",'
    #         '"totalitems":"","itemsperpage":""},"data":[]}}',
    #         "utf-8",
    #     )
    #     httpx_mock.add_response(status_code=200, content=_empty_200)
    #     with pytest.raises(NextcloudForbiddenError):
    #         await loginflowv2_api.destroy_token()

    # TODO: Move to another module ^^^ vvvv
    # async def test_destroy_app_token(
    #     self, httpx_mock: HTTPXMock, loginflowv2_api: LoginFlowV2Api
    # ):
    #     _empty_200 = bytes(
    #         '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK",'
    #         '"totalitems":"","itemsperpage":""},"data":[]}}',
    #         "utf-8",
    #     )
    #     loginflowv2_api.client.app_token = APP_TOKEN
    #     httpx_mock.add_response(status_code=200, content=_empty_200)
    #     await loginflowv2_api.destroy_token()
    #     httpx_mock.assert_all_responses_sent()
