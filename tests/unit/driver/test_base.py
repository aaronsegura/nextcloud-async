import pytest
from httpx import ReadTimeout
from pytest_httpx import HTTPXMock

from nextcloud_async import NextcloudClient
from nextcloud_async.driver import NextcloudBaseApi
from nextcloud_async.exceptions import (
    NextcloudAsyncError,
    NextcloudRequestTimeoutError,
)

from .constants import EMPTY_RESPONSE, ENDPOINT, PASS, USER


@pytest.fixture
def nc() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, PASS)


@pytest.fixture
def nc_app_token() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, app_token=PASS)


@pytest.fixture
def base(nc) -> NextcloudBaseApi:
    return NextcloudBaseApi(nc)


@pytest.fixture
def base_app_token(nc_app_token) -> NextcloudBaseApi:
    return NextcloudBaseApi(nc_app_token)


class TestInit:
    def test_default(self, magicmock):
        base = NextcloudBaseApi(magicmock)
        assert base.stub == "/index.php"
        assert base.client == magicmock

    def test_stub(self, magicmock):
        base = NextcloudBaseApi(magicmock, api_stub="/this/path/now")
        assert base.stub == "/this/path/now"


@pytest.mark.asyncio
class TestRequest:
    async def test_default_get(self, base: NextcloudBaseApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=200,
            method="GET",
            content=EMPTY_RESPONSE,
            headers={"key": "value"},
            url=f"{ENDPOINT}{base.stub}",
        )

        http_response = await base.request()
        assert http_response == []

        httpx_mock.assert_all_responses_sent()

    async def test_request_readtimeout(
        self, base: NextcloudBaseApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_exception(ReadTimeout("Request Timed out"))
        with pytest.raises(NextcloudRequestTimeoutError):
            await base.request()

    async def test_malformed_response(
        self, base: NextcloudBaseApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(200, content=b"this is not json")
        with pytest.raises(NextcloudAsyncError):
            await base.request()
