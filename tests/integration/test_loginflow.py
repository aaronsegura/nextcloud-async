import json

import pytest
from pytest_httpx import HTTPXMock

from nextcloud_async.api import LoginFlowV2Api, loginflowv2_api
from nextcloud_async.exceptions import (
    NextcloudForbiddenError,
    NextcloudLoginFlowTimeoutError,
)

from .constants import APP_TOKEN, USER

TOKEN = (
    "qWPKzgQoCeV4Cvgc8Sl9ENJ8kXrGmijwWgA0eCNgOnP2bt"
    "sWturgzFkdLGySmzMiheh746voMs5lpOB57MRm66KDV40G4n7V03cUnwznKX95k1"
    "taNobxuGCNthK3I5me"
)


@pytest.mark.asyncio(loop_scope="session")
class TestLoginFlowV2:
    """Must monkeypatch and mock this one since it requires user intervention."""

    async def test_login_flow_initiate(
        self, httpx_mock: HTTPXMock, loginflowv2_api: LoginFlowV2Api
    ):
        json_response = bytes(
            f'{{"poll":{{"token":"{TOKEN}","endpoint":"http:\\/\\/localhost:81'
            '81\\/login\\/v2\\/poll"},"login":"http:\\/\\/localhost:8181\\/l'
            "ogin\\/v2\\/flow\\/TtnMLxXHbxzkvubprdlowN0QoS7k9UVtOLf977xxVXsf"
            "9oUUsXGXjU9vSRi3axFUEZCyF2nC6WD8NERUwaeewCZC99NgN6IjGlCMWEHrS08"
            'I8GL1dChWpYqn78S1Zmk7"}',
            "utf-8",
        )
        httpx_mock.add_response(status_code=200, content=json_response)
        await loginflowv2_api.initiate()
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url == f"{loginflowv2_api.api.client.endpoint}/index.php/login/v2"

    async def test_login_flow_confirm_success(
        self, httpx_mock: HTTPXMock, loginflowv2_api: LoginFlowV2Api
    ):
        response = bytes(
            f'{{"server":"http:\\/\\/localhost:8181","loginName":"{USER}",'
            '"appPassword":"aoXMDFSBmFQhsqvuKuFXhW4s4Uj1GUJ3OZttYid7jbAxL'
            'XLZQDYOIywkW7kBLiroLyAik1Pf"}',
            "utf-8",
        )
        httpx_mock.add_response(status_code=200, content=response)
        await loginflowv2_api.wait_confirm(TOKEN, timeout=3)
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert (
            request.url == f"{loginflowv2_api.api.client.endpoint}"
            "/index.php/login/v2/poll"
        )
        request_token = json.loads(request.content)
        assert request_token == {"token": TOKEN}

    async def test_login_flow_timeout(
        self, httpx_mock: HTTPXMock, loginflowv2_api: LoginFlowV2Api
    ):
        httpx_mock.add_response(status_code=404, is_reusable=True)
        with pytest.raises(NextcloudLoginFlowTimeoutError):
            await loginflowv2_api.wait_confirm(TOKEN, timeout=1)

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
