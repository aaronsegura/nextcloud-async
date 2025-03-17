import httpx
import pytest
from pytest_httpx import HTTPXMock

from nextcloud_async import NextcloudClient
from nextcloud_async.api import Wipe
from nextcloud_async.exceptions import (
    NextcloudMethodNotAllowedError,
    NextcloudNotFoundError,
)

from ....constants import APP_TOKEN, EMPTY_RESPONSE, ENDPOINT, USER

FALSE_RESPONSE = r'{"wipe": false}'
TRUE_RESPONSE = b'{"wipe": true}'


@pytest.fixture
def wipe():
    client = NextcloudClient(
        ENDPOINT, USER, app_token=APP_TOKEN, http_client=httpx.AsyncClient()
    )
    return Wipe(client)


@pytest.mark.asyncio
class TestWipe:
    async def test_check_no_app_token(self, wipe: Wipe):
        wipe.api.client.app_token = None
        with pytest.raises(NextcloudMethodNotAllowedError):
            await wipe.check()

    async def test_check_no_wipe(self, wipe: Wipe, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200,
            text=FALSE_RESPONSE,
            url=f"{ENDPOINT}{wipe.api.stub}{wipe.stub}/check",
            method="POST",
        )
        result = await wipe.check()
        httpx_mock.assert_all_responses_sent()
        assert result is False

    async def test_check_not_found(self, wipe: Wipe, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(NextcloudNotFoundError(), method="POST")
        result = await wipe.check()
        assert result is False
        httpx_mock.assert_all_responses_sent()

    async def test_check_wipe(self, wipe: Wipe, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200,
            content=TRUE_RESPONSE,
            method="POST",
            url=f"{ENDPOINT}{wipe.api.stub}{wipe.stub}/check",
        )
        result = await wipe.check()
        httpx_mock.assert_all_responses_sent()
        assert result is True

    async def test_check_wipe_empty_response(self, wipe: Wipe, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200,
            content=EMPTY_RESPONSE,
            method="POST",
            url=f"{ENDPOINT}{wipe.api.stub}{wipe.stub}/check",
        )
        result = await wipe.check()
        httpx_mock.assert_all_responses_sent()
        assert result is False

    async def test_notify_wiped(self, wipe: Wipe, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200,
            content=EMPTY_RESPONSE,
            method="POST",
            url=f"{ENDPOINT}{wipe.stub}/success",
        )
        await wipe.notify_wiped()
        httpx_mock.assert_all_responses_sent()
