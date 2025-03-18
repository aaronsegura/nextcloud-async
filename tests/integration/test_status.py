import pytest
import pytest_asyncio
from vcr.cassette import Cassette

import datetime as dt
import json
from typing import AsyncGenerator

from dateutil.tz import tzlocal

from nextcloud_async.api import (
    MyStatus,
    PredefinedStatus,
    StatusApi,
    StatusType,
    User,
    UsersApi,
    UserStatus,
)
from nextcloud_async.exceptions import NextcloudBadRequestError

_CLEAR_AT_DT = dt.datetime.now(tz=tzlocal()) + dt.timedelta(seconds=300)


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def my_status(
    status_api: StatusApi, vcr: Cassette, network_blocked: bool
) -> MyStatus:
    if network_blocked:
        # Since we are sending/checking expiration time, which changes on every run
        # we pull the original request/response from the cassette and create a
        # MyStatus object with the response data.
        url = (
            f"{status_api.api.client.endpoint}{status_api.api.stub}{status_api.stub}"
            "/user_status/message/custom"
        )
        requests = [x for x in vcr.requests if x.uri == url and x.method == "PUT"]
        responses = []
        for request in requests:
            responses += vcr.responses_of(request)

        response = [x for x in responses if x["status"]["code"] == 200].pop()

        response_data = json.loads(response["body"]["string"])
        status = MyStatus(response_data["ocs"]["data"], status_api)
        status.data["clearAt"] = int(_CLEAR_AT_DT.timestamp())
        dt.datetime.fromtimestamp(status.clearAt, tz=tzlocal())
    else:
        status = await status_api.get()
        await status.set(StatusType.online)
        await status.set_message("Pytesting", status_icon="⌛", clear_at=_CLEAR_AT_DT)
    return status


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def predefined_statuses(status_api: StatusApi) -> list[PredefinedStatus]:
    return await status_api.get_predefined_statuses()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_user(network_blocked: bool, users_api: UsersApi) -> AsyncGenerator[User]:
    _test_user = {
        "user_id": "pytest_user",
        "display_name": "Pytest User Guy",
        "email": "pytest@example.com",
        "quota": None,
        "password": "MyCoolPassword",
        "language": "en",
    }

    if network_blocked:
        _test_user.update({"id": _test_user["user_id"]})
        test_user = User(_test_user, self_api=users_api)
    else:
        test_user = await users_api.create(**_test_user)

    yield test_user
    if not network_blocked:
        await test_user.delete()


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestStatus:
    async def test_get_status(self, my_status: MyStatus):
        assert isinstance(my_status, MyStatus)

    async def test_set_status(self, my_status: MyStatus):
        await my_status.set(StatusType.away)
        assert my_status.status == StatusType.away.value

    async def test_set_message(self, my_status: MyStatus):
        await my_status.set_message("Pytesting", status_icon="⌛", clear_at=_CLEAR_AT_DT)
        assert my_status.message == "Pytesting"
        assert my_status.icon == "⌛"

    async def test_set_message_expired(self, my_status: MyStatus):
        _clear_at = dt.datetime.now(tz=tzlocal()) - dt.timedelta(hours=1)
        with pytest.raises(NextcloudBadRequestError):
            await my_status.set_message("Pytesting", clear_at=_clear_at)

    async def test_get_predefined_statuses(self, status_api: StatusApi):
        statuses = await status_api.get_predefined_statuses()
        for status in statuses:
            assert isinstance(status, PredefinedStatus)

    async def test_set_predefined_status(
        self, my_status: MyStatus, predefined_statuses: list[PredefinedStatus]
    ):
        _status = predefined_statuses[0]
        await my_status.set_predefined_status(predefined_statuses[0])
        assert my_status.messageIsPredefined is True
        assert my_status.messageId == _status.id

    async def test_clear_status(self, my_status: MyStatus):
        await my_status.clear_message()
        assert my_status.message == ""

    async def test_get_all_user_statuses(self, status_api: StatusApi):
        await status_api.get_all_user_statuses()

    async def test_get_user_status(self, status_api: StatusApi):
        user_status = await status_api.get_user_status(status_api.api.client.user)
        assert isinstance(user_status, UserStatus)
