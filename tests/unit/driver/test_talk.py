from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ReadTimeout, Response
from pytest_httpx import HTTPXMock

from nextcloud_async import NextcloudClient
from nextcloud_async.driver import NextcloudTalkApi
from nextcloud_async.exceptions import (
    NextcloudAsyncError,
    NextcloudBadRequestError,
    NextcloudConflictError,
    NextcloudDeviceWipeRequestedError,
    NextcloudError,
    NextcloudFederationRemoteError,
    NextcloudForbiddenError,
    NextcloudGenericServerError,
    NextcloudMethodNotAllowedError,
    NextcloudNotCapableError,
    NextcloudNotFoundError,
    NextcloudNotSupportedError,
    NextcloudPreconditionError,
    NextcloudRequestTimeoutError,
    NextcloudServiceNotAvailableError,
    NextcloudTooManyRequestsError,
    NextcloudUnauthorizedError,
    NextcloudUnsupportedMediaTypeError,
    NextcloudUpgradeRequiredError,
)

from .constants import (
    CAPABILITIES_RESPONSE,
    ENDPOINT,
    OCS_EMPTY_200,
    OCS_EXCEPTION_RESPONSE,
    PASSWORD,
    USER,
)


@pytest.fixture
def nc() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, PASSWORD)


@pytest.fixture
def nc_app_token() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, app_token=PASSWORD)


@pytest.fixture
def talk(nc: NextcloudClient) -> NextcloudTalkApi:
    return NextcloudTalkApi(nc)


@pytest.fixture
def talk_app_token(nc_app_token: NextcloudClient) -> NextcloudTalkApi:
    return NextcloudTalkApi(nc_app_token)


class TestHelpers:
    @pytest.mark.parametrize(
        ("status_code", "exception"),
        [
            (400, NextcloudBadRequestError),
            (401, NextcloudUnauthorizedError),
            (403, NextcloudForbiddenError),
            (404, NextcloudNotFoundError),
            (405, NextcloudMethodNotAllowedError),
            (406, NextcloudNotSupportedError),
            (408, NextcloudRequestTimeoutError),
            (409, NextcloudConflictError),
            (412, NextcloudPreconditionError),
            (415, NextcloudUnsupportedMediaTypeError),
            (422, NextcloudFederationRemoteError),
            (426, NextcloudUpgradeRequiredError),
            (429, NextcloudTooManyRequestsError),
            (499, NextcloudNotCapableError),
            (500, NextcloudGenericServerError),
            (503, NextcloudServiceNotAvailableError),
            (69420, NextcloudError),
        ],
    )
    @pytest.mark.asyncio
    async def test_raise_response_exception_by_status_code(
        self,
        talk: NextcloudTalkApi,
        asyncmock: AsyncMock,
        status_code: int,
        exception: BaseException,
    ):
        ocs_exception = OCS_EXCEPTION_RESPONSE.copy()
        ocs_exception["ocs"]["meta"]["statuscode"] = status_code
        response = Response(status_code, json=ocs_exception)
        asyncmock.return_value = False
        talk._wipe_requested = asyncmock
        with pytest.raises(exception):  # type: ignore
            await talk.raise_response_exception(response)

    @pytest.mark.parametrize(
        ("status_code", "exception"),
        [
            (400, NextcloudBadRequestError),
            (401, NextcloudUnauthorizedError),
            (403, NextcloudForbiddenError),
            (404, NextcloudNotFoundError),
            (405, NextcloudMethodNotAllowedError),
            (406, NextcloudNotSupportedError),
            (408, NextcloudRequestTimeoutError),
            (409, NextcloudConflictError),
            (412, NextcloudPreconditionError),
            (415, NextcloudUnsupportedMediaTypeError),
            (422, NextcloudFederationRemoteError),
            (426, NextcloudUpgradeRequiredError),
            (429, NextcloudTooManyRequestsError),
            (499, NextcloudNotCapableError),
            (500, NextcloudGenericServerError),
            (503, NextcloudServiceNotAvailableError),
            (69420, NextcloudError),
        ],
    )
    @pytest.mark.asyncio
    async def test_raise_response_exception_by_metadata(
        self,
        talk: NextcloudTalkApi,
        asyncmock: AsyncMock,
        status_code: int,
        exception: BaseException,
    ):
        ocs_exception = OCS_EXCEPTION_RESPONSE.copy()
        ocs_exception["ocs"]["meta"]["statuscode"] = status_code
        response = Response(200, json=ocs_exception)
        asyncmock.return_value = False
        talk._wipe_requested = asyncmock
        with pytest.raises(exception):  # type: ignore
            await talk.raise_response_exception(response)

    @pytest.mark.parametrize(
        "status_code",
        [401, 403],
    )
    @pytest.mark.asyncio
    async def test_raise_wipe_requested(
        self,
        talk: NextcloudTalkApi,
        asyncmock: AsyncMock,
        status_code: int,
    ):
        ocs_exception = OCS_EXCEPTION_RESPONSE.copy()
        ocs_exception["ocs"]["meta"]["statuscode"] = status_code
        response = Response(status_code, json=ocs_exception)
        asyncmock.return_value = True
        talk._wipe_requested = asyncmock
        with pytest.raises(NextcloudDeviceWipeRequestedError):
            await talk.raise_response_exception(response)


class TestInit:
    def test_default(self, magicmock: MagicMock):
        talk = NextcloudTalkApi(magicmock)
        assert talk.stub == "/ocs/v2.php"
        assert talk.client == magicmock

    def test_version(self, magicmock: MagicMock):
        talk = NextcloudTalkApi(magicmock, ocs_version="3")
        assert talk.ocs_version == "3"
        assert talk.stub == "/ocs/v3.php"

    def test_stub(self, magicmock: MagicMock):
        talk = NextcloudTalkApi(magicmock, stub="/this/path/now")
        assert talk.stub == "/this/path/now"


@pytest.mark.asyncio
class TestRequest:
    async def test_default_get(self, talk: NextcloudTalkApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=200,
            method="GET",
            json=OCS_EMPTY_200,
            headers={"key": "value"},
            url=f"{ENDPOINT}{talk.stub}?format=json",
        )

        response_data, response_headers = await talk.request()
        assert response_data == []
        assert "key" in response_headers
        assert response_headers["key"] == "value"

        httpx_mock.assert_all_responses_sent()

    async def test_request_readtimeout(
        self, talk: NextcloudTalkApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_exception(ReadTimeout("Request Timed out"))
        with pytest.raises(NextcloudRequestTimeoutError):
            await talk.request()

    async def test_malformed_response(
        self, talk: NextcloudTalkApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(200, content=b"this is not json")
        with pytest.raises(NextcloudAsyncError):
            await talk.request()

    @pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
    async def test_has_talk_feature(self, talk: NextcloudTalkApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
        assert await talk.has_feature("chat-v2")

    @pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
    async def test_require_talk_feature_noexist(
        self, talk: NextcloudTalkApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
        with pytest.raises(NextcloudNotCapableError):
            await talk.require_feature("noexist")

    @pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
    async def test_require_talk_feature(
        self, talk: NextcloudTalkApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(200, json=CAPABILITIES_RESPONSE)
        await talk.require_feature("chat-v2")
