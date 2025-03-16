from typing import Callable
from unittest.mock import AsyncMock, call

import pytest

from nextcloud_async import NextcloudClient
from nextcloud_async.driver import NextcloudHttpApi

ENDPOINT = "http://localhost"
USER = "USER"
PASS = "PASSWORD"

EMPTY_RESPONSE = b"[]"


class PytestDummyApi(NextcloudHttpApi):
    request = AsyncMock()


@pytest.fixture
def nc() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, PASS, http_client=AsyncMock)


@pytest.fixture
def nc_app_token() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, app_token=PASS)


@pytest.fixture
def api(nc) -> PytestDummyApi:
    return PytestDummyApi(nc)


@pytest.fixture
def api_app_token(nc_app_token) -> PytestDummyApi:
    return PytestDummyApi(nc_app_token)


@pytest.fixture
def path_args(api) -> Callable:
    return api._path_args


@pytest.fixture
def munge_headers(api) -> Callable:
    return api._munge_headers


class TestInit:
    def test_path_args_bool(self, path_args: Callable):
        result = path_args({"thing": True})
        assert result == "?thing=true"

    def test_path_args_none(self, path_args: Callable):
        result = path_args({"thing": None})
        assert result == "?thing="


class TestPathArgs:
    def test_path_args_key_value(self, path_args: Callable):
        result = path_args({"thing": "stuff"})
        assert result == "?thing=stuff"

    def test_path_args_all(self, path_args: Callable):
        result = path_args({"bool": True, "None": None, "key": "value"})
        assert result == "?bool=true&None=&key=value"


class TestMungeHeaders:
    def test_munge_headers_default(self, api: PytestDummyApi, munge_headers: Callable):
        result = munge_headers()
        assert result == {"User-Agent": api.client.user_agent}

    def test_munge_headers_with_headers(
        self, api: PytestDummyApi, munge_headers: Callable
    ):
        result = munge_headers({"TestHeader": "TestValue"})
        assert result == {"User-Agent": api.client.user_agent, "TestHeader": "TestValue"}

    def test_munge_headers_with_extras(
        self, api: PytestDummyApi, munge_headers: Callable
    ):
        result = munge_headers({"TestHeader": "TestValue"}, {"ExtraHeader": "ExtraValue"})
        assert result == {
            "User-Agent": api.client.user_agent,
            "TestHeader": "TestValue",
            "ExtraHeader": "ExtraValue",
        }

    def test_munge_headers_with_app_token_auth(self):
        nc = NextcloudClient("endpoint", "user", app_token="[app_token]")
        api = PytestDummyApi(nc)
        result = api._munge_headers({"TestHeader": "TestValue"})
        assert result == {
            "User-Agent": nc.user_agent,
            "TestHeader": "TestValue",
            "Authorization": "Bearer [app_token]",
        }


class TestFormatJson:
    def test_format_json(self, api: PytestDummyApi):
        result = api._format_json(None)
        assert result == {"format": "json"}

    def test_format_json_existing(self, api: PytestDummyApi):
        result = api._format_json({"TestKey": "TestValue"})
        assert result == {"TestKey": "TestValue", "format": "json"}


class TestCapabilityApi:
    def test_wipe_requested(self, api: PytestDummyApi): ...

    def test_has_capability(self, api: PytestDummyApi): ...

    def test_require_capability(self, api: PytestDummyApi): ...

    def test_raise_response_exception(self, api: PytestDummyApi): ...


class TestRequests:
    @pytest.mark.parametrize(
        "methods",
        [
            "get",
            "post",
            "put",
            "delete",
            "propfind",
            "mkcol",
            "move",
            "copy",
            "proppatch",
            "report",
        ],
    )
    @pytest.mark.asyncio
    async def test_request_methods(self, api: PytestDummyApi, methods: str):
        method_function = api.__getattribute__(f"{methods}")
        await method_function()

        expected = [call(method=f"{methods.upper()}", path="", data=None, headers=None)]
        api.request.assert_has_calls(expected)

    @pytest.mark.asyncio
    async def test_get_raw(self, api: PytestDummyApi):
        method_function = api.__getattribute__("get_raw")
        await method_function()

        expected = [
            call(method="GET", path="", data=None, headers=None, raw_response=True)
        ]
        api.request.assert_has_calls(expected)
