# import pytest

# from typing import Callable
# from unittest.mock import AsyncMock, call

# from pytest_httpx import HTTPXMock

# from nextcloud_async import NextcloudClient
# from nextcloud_async.driver import NextcloudHttpDriver
# from nextcloud_async.exceptions import NextcloudNotCapableError

# from .constants import (
#     APP_TOKEN,
#     CAPABILITIES_RESPONSE,
#     EMPTY_RESPONSE,
#     ENDPOINT,
#     PASSWORD,
#     USER,
#     USER_AGENT,
# )


# class PytestDummyApi(NextcloudHttpDriver):
#     request: AsyncMock = AsyncMock()


# @pytest.fixture
# def nc() -> NextcloudClient:
#     return NextcloudClient(ENDPOINT, USER, PASSWORD, user_agent=USER_AGENT)


# @pytest.fixture
# def nc_app_token() -> NextcloudClient:
#     return NextcloudClient(ENDPOINT, USER, app_token=APP_TOKEN, user_agent=USER_AGENT)


# @pytest.fixture
# def api(nc) -> PytestDummyApi:
#     api = PytestDummyApi(nc)
#     api._capabilities_api.destroy()
#     return api


# @pytest.fixture
# def api_app_token(nc_app_token) -> PytestDummyApi:
#     return PytestDummyApi(nc_app_token)


# @pytest.fixture
# def path_args(api) -> Callable:
#     return api._path_args


# @pytest.fixture
# def munge_headers(api) -> Callable:
#     return api._munge_headers


# class TestPathArgs:
#     def test_path_args_bool(self, path_args: Callable):
#         result = path_args({"thing": True})
#         assert result == "?thing=true"

#     def test_path_args_none(self, path_args: Callable):
#         result = path_args({"thing": None})
#         assert result == "?thing="

#     def test_path_args_key_value(self, path_args: Callable):
#         result = path_args({"thing": "stuff"})
#         assert result == "?thing=stuff"

#     def test_path_args_all(self, path_args: Callable):
#         result = path_args({"bool": True, "None": None, "key": "value"})
#         assert result.startswith("?")
#         parts = result[1:].split("&")
#         assert "bool=true" in parts
#         assert "None=" in parts
#         assert "key=value" in parts


# class TestMungeHeaders:
#     def test_munge_headers_default(self, api: PytestDummyApi, munge_headers: Callable):
#         result = munge_headers()
#         assert result == {"User-Agent": api.client.user_agent}

#     def test_munge_headers_with_headers(
#         self, api: PytestDummyApi, munge_headers: Callable
#     ):
#         result = munge_headers({"TestHeader": "TestValue"})
#         assert result == {"User-Agent": api.client.user_agent, "TestHeader": "TestValue"}

#     def test_munge_headers_with_extras(
#         self, api: PytestDummyApi, munge_headers: Callable
#     ):
#         result = munge_headers({"TestHeader": "TestValue"}, {"ExtraHeader": "ExtraValue"})
#         assert result == {
#             "User-Agent": api.client.user_agent,
#             "TestHeader": "TestValue",
#             "ExtraHeader": "ExtraValue",
#         }

#     def test_munge_headers_with_app_token_auth(self, api_app_token):
#         result = api_app_token._munge_headers({"TestHeader": "TestValue"})
#         assert result == {
#             "User-Agent": USER_AGENT,
#             "TestHeader": "TestValue",
#             "Authorization": f"Bearer {APP_TOKEN}",
#         }


# class TestFormatJson:
#     def test_format_json(self, api: PytestDummyApi):
#         result = api._format_json(None)
#         assert result == {"format": "json"}

#     def test_format_json_existing(self, api: PytestDummyApi):
#         result = api._format_json({"TestKey": "TestValue"})
#         assert result == {"TestKey": "TestValue", "format": "json"}


# @pytest.mark.asyncio
# class TestCapabilities:
#     async def test_has_capability(self, api: PytestDummyApi, httpx_mock: HTTPXMock):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         assert await api.has_capability("files")

#     async def test_has_capability_noexist(
#         self, api: PytestDummyApi, httpx_mock: HTTPXMock
#     ):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         assert not await api.has_capability("noexist")

#     async def test_require_capability(self, api: PytestDummyApi, httpx_mock: HTTPXMock):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         await api.require_capability("files")

#     async def test_raise_response_exception(
#         self, api: PytestDummyApi, httpx_mock: HTTPXMock
#     ):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         with pytest.raises(NextcloudNotCapableError):
#             await api.require_capability("noexist")

#     async def test_get_capability(self, api: PytestDummyApi, httpx_mock: HTTPXMock):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         result = await api._capabilities_api.get_capability("core")
#         assert result == CAPABILITIES_RESPONSE["ocs"]["data"]["capabilities"]["core"]

#     async def test_get_capability_deep(self, api: PytestDummyApi, httpx_mock: HTTPXMock):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         result = await api._capabilities_api.get_capability("spreed.features")

#         assert (
#             result
#             == CAPABILITIES_RESPONSE["ocs"]["data"]["capabilities"]["spreed"]["features"]
#         )

#     async def test_get_capability_deep_noexist(
#         self, api: PytestDummyApi, httpx_mock: HTTPXMock
#     ):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         with pytest.raises(NextcloudNotCapableError):
#             await api._capabilities_api.get_capability("spreed.features.noexist")

#     async def test_get_capability_noexist(
#         self, api: PytestDummyApi, httpx_mock: HTTPXMock
#     ):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         with pytest.raises(NextcloudNotCapableError):
#             await api._capabilities_api.get_capability("noexist")

#     async def test_server_version(self, api: PytestDummyApi, httpx_mock: HTTPXMock):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         result = await api._capabilities_api.server_version()
#         assert result == CAPABILITIES_RESPONSE["ocs"]["data"]["version"]

#     async def test_get_all(self, api: PytestDummyApi, httpx_mock: HTTPXMock):
#         httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
#         result = await api._capabilities_api.get_all()
#         assert result == CAPABILITIES_RESPONSE["ocs"]["data"]["capabilities"]


# class TestRequests:
#     @pytest.mark.parametrize(
#         "methods",
#         [
#             "get",
#             "post",
#             "put",
#             "delete",
#             "propfind",
#             "mkcol",
#             "move",
#             "copy",
#             "proppatch",
#             "report",
#         ],
#     )
#     @pytest.mark.asyncio
#     async def test_request_methods(self, api: PytestDummyApi, methods: str):
#         method_function = api.__getattribute__(f"{methods}")
#         await method_function()

#         expected = [call(method=f"{methods.upper()}", path="", data=None, headers=None)]
#         api.request.assert_has_calls(expected)

#     @pytest.mark.asyncio
#     async def test_get_raw(self, api: PytestDummyApi):
#         method_function = api.__getattribute__("get_raw")
#         await method_function()

#         expected = [
#             call(method="GET", path="", data=None, headers=None, raw_response=True)
#         ]
#         api.request.assert_has_calls(expected)


# @pytest.mark.asyncio
# async def test_wipe_requested(api: PytestDummyApi, httpx_mock: HTTPXMock):
#     httpx_mock.add_response(404, json=EMPTY_RESPONSE)
#     api.client.app_token = APP_TOKEN
#     assert await api._wipe_requested() is False
