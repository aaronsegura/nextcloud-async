from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ReadTimeout, Response
from pytest_httpx import HTTPXMock

from nextcloud_async import NextcloudClient
from nextcloud_async.driver import NextcloudDavApi
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

EXCEPTION_RESPONSE = (
    b'<?xml version="1.0" encoding="utf-8"?>\n<d:error xmlns:d="DAV:" '
    b'xmlns:s="http://sabredav.org/ns">\n\t<s:exception>Internal Server Error'
    b"</s:exception>\n\t<s:message>\n\t\tThe server was unable to complete your request."
    b"\t\tIf this happens again, please send the technical details below to the server"
    b"administrator.\t\tMore details can be found in the server log.\t\t\t</s:message>"
    b"\n\n\t<s:technical-details>\n\t\t<s:remote-address>172.19.0.1</s:remote-address>"
    b"\n\t\t<s:request-id>wYmY8sidCWoJU7YVYt0d</s:request-id>\n\n\t\t"
    b"</s:technical-details>\n</d:error>\n"
)

EMPTY_RESPONSE = (
    b'<?xml version="1.0"?>'
    b'<d:multistatus xmlns:d="DAV:" xmlns:s="http://sabredav.org/ns" '
    b'xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">'
    b"<d:response></d:response></d:multistatus>"
)


@pytest.fixture
def nc() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, PASS)


@pytest.fixture
def nc_app_token() -> NextcloudClient:
    return NextcloudClient(ENDPOINT, USER, app_token=PASS)


@pytest.fixture
def dav(nc) -> NextcloudDavApi:
    return NextcloudDavApi(nc)


@pytest.fixture
def dav_app_token(nc_app_token) -> NextcloudDavApi:
    return NextcloudDavApi(nc_app_token)


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
        dav: NextcloudDavApi,
        asyncmock: AsyncMock,
        status_code: int,
        exception: BaseException,
    ):
        response = Response(
            status_code,
            content=EXCEPTION_RESPONSE,
        )
        asyncmock.return_value = False
        dav._wipe_requested = asyncmock
        with pytest.raises(exception):  # type: ignore
            await dav.raise_response_exception(response)

    @pytest.mark.parametrize(
        "status_code",
        [401, 403],
    )
    @pytest.mark.asyncio
    async def test_raise_wipe_requested(
        self,
        dav: NextcloudDavApi,
        asyncmock: AsyncMock,
        status_code: int,
    ):
        response = Response(status_code, content=EXCEPTION_RESPONSE)
        asyncmock.return_value = True
        dav._wipe_requested = asyncmock
        with pytest.raises(NextcloudDeviceWipeRequestedError):
            await dav.raise_response_exception(response)


class TestInit:
    def test_default(self, magicmock: MagicMock):
        dav = NextcloudDavApi(magicmock)
        assert dav.stub == "/remote.php/dav"
        assert dav.client == magicmock
        magicmock.assert_not_called()

    def test_stub(self, magicmock):
        dav = NextcloudDavApi(magicmock, api_stub="/this/path/now")
        assert dav.stub == "/this/path/now"


@pytest.mark.asyncio
class TestRequest:
    async def test_default_get(self, dav: NextcloudDavApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=200,
            method="GET",
            content=EMPTY_RESPONSE,
            headers={"key": "value"},
            url=f"{ENDPOINT}{dav.stub}",
        )

        http_response = await dav.request()
        assert http_response == None

        httpx_mock.assert_all_responses_sent()

    async def test_request_readtimeout(self, dav: NextcloudDavApi, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(ReadTimeout("Request Timed out"))
        with pytest.raises(NextcloudRequestTimeoutError):
            await dav.request()

    async def test_malformed_response(self, dav: NextcloudDavApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(200, content=b"this is not xml")
        with pytest.raises(NextcloudAsyncError):
            await dav.request()

    async def test_raw_response(self, dav: NextcloudDavApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(200, content=EMPTY_RESPONSE)
        response = await dav.request(raw_response=True)
        assert response == EMPTY_RESPONSE

    async def test_no_data(self, dav: NextcloudDavApi, httpx_mock: HTTPXMock):
        httpx_mock.add_response(200, content=None)
        response = await dav.request()
        assert response == {}
