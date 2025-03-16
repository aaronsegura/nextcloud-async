from unittest.mock import AsyncMock

import pytest
from httpx import ReadTimeout, Response
from pytest_httpx import HTTPXMock

from nextcloud_async import NextcloudClient
from nextcloud_async.driver import NextcloudOcsApi
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

ENDPOINT = "http://localhost"
USER = "USER"
PASS = "PASSWORD"

EMPTY_200 = (
    b'{"ocs": {"meta": {"status": "ok", "statuscode": 200, "message": "OK"}, "data": []}}'
)

EXCEPTION_RESPONSE = (
    b'{"ocs": {'
    b'"meta": {"status": "failure", "statuscode": {status_code}, "message": "Excepted"}, '
    b'"data": []}}'
)


@pytest.fixture
def nc() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, PASS)


@pytest.fixture
def nc_app_token() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, app_token=PASS)


@pytest.fixture
def ocs(nc) -> NextcloudOcsApi:
    return NextcloudOcsApi(nc)


@pytest.fixture
def ocs_app_token(nc_app_token) -> NextcloudOcsApi:
    return NextcloudOcsApi(nc_app_token)


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
        ocs: NextcloudOcsApi,
        asyncmock: AsyncMock,
        status_code: int,
        exception: BaseException,
    ):
        response = Response(
            status_code,
            content=bytes(
                EXCEPTION_RESPONSE.decode().replace("{status_code}", str(status_code)),
                "utf-8",
            ),
        )
        asyncmock.return_value = False
        ocs._wipe_requested = asyncmock
        with pytest.raises(exception):  # type: ignore
            await ocs.raise_response_exception(response)

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
        ocs: NextcloudOcsApi,
        asyncmock: AsyncMock,
        status_code: int,
        exception: BaseException,
    ):
        response = Response(
            200,
            content=bytes(
                EXCEPTION_RESPONSE.decode().replace("{status_code}", str(status_code)),
                "utf-8",
            ),
        )
        asyncmock.return_value = False
        ocs._wipe_requested = asyncmock
        with pytest.raises(exception):  # type: ignore
            await ocs.raise_response_exception(response)

    @pytest.mark.parametrize(
        "status_code",
        [401, 403],
    )
    @pytest.mark.asyncio
    async def test_raise_wipe_requested(
        self,
        ocs: NextcloudOcsApi,
        asyncmock: AsyncMock,
        status_code: int,
    ):
        response = Response(
            status_code,
            content=bytes(
                EXCEPTION_RESPONSE.decode().replace("{status_code}", str(status_code)),
                "utf-8",
            ),
        )
        asyncmock.return_value = True
        ocs._wipe_requested = asyncmock
        with pytest.raises(NextcloudDeviceWipeRequestedError):
            await ocs.raise_response_exception(response)


class TestInit:
    def test_default(self, magicmock):
        ocs = NextcloudOcsApi(magicmock)
        assert ocs.stub == "/ocs/v1.php"
        assert ocs.client == magicmock

    def test_version(self, magicmock):
        ocs = NextcloudOcsApi(magicmock, ocs_version="2")
        assert ocs.ocs_version == "2"
        assert ocs.stub == "/ocs/v2.php"

    def test_stub(self, magicmock):
        ocs = NextcloudOcsApi(magicmock, ocs_stub="/this/path/now")
        assert ocs.stub == "/this/path/now"


@pytest.mark.asyncio
class TestRequest:
    async def test_default_get(self, ocs: NextcloudOcsApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=200,
            method="GET",
            content=EMPTY_200,
            headers={"key": "value"},
            url=f"{ENDPOINT}{ocs.stub}?format=json",
        )

        http_response = await ocs.request()
        assert http_response == []

        httpx_mock.assert_all_responses_sent()

    async def test_request_readtimeout(self, ocs: NextcloudOcsApi, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(ReadTimeout("Request Timed out"))
        with pytest.raises(NextcloudRequestTimeoutError):
            await ocs.request()

    async def test_malformed_response(self, ocs: NextcloudOcsApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(200, content=b"this is not json")
        with pytest.raises(NextcloudAsyncError):
            await ocs.request()

    async def test_raw_response(self, ocs: NextcloudOcsApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(100, content=EMPTY_200)
        response = await ocs.request(raw_response=True)
        assert response == EMPTY_200
