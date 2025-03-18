import json

import pytest
from pytest_httpx import HTTPXMock

from nextcloud_async.api import Notification, NotificationsApi


@pytest.mark.asyncio(loop_scope="session")
class TestNotifications:
    _multi_response = bytes(
        r'{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
        r'"data":[{"notification_id": 7,"app":"updatenotifi'
        r'cation","user":"admin","datetime":"2022-07-04T14:10:22+00:00","o'
        r'bject_type":"core","object_id":"24.0.2.1","subject":"Update to N'
        r'extcloud 24.0.2 is available.","message":"","link":"http:\\/\\/l'
        r'ocalhost:8181\\/settings\\/admin\\/overview#version","subjectRic'
        r'h":"","subjectRichParameters":[],"messageRich":"","messageRichPa'
        r'rameters":[],"icon":"http:\\/\\/localhost:8181\\/apps\\/updateno'
        r'tification\\/img\\/notification.svg","actions":[]}]}}',
        "utf-8",
    )

    _single_response = bytes(
        r'{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
        r'"data":{"notification_id": 7,"app":"updatenotifi'
        r'cation","user":"admin","datetime":"2022-07-04T14:10:22+00:00","o'
        r'bject_type":"core","object_id":"24.0.2.1","subject":"Update to N'
        r'extcloud 24.0.2 is available.","message":"","link":"http:\\/\\/l'
        r'ocalhost:8181\\/settings\\/admin\\/overview#version","subjectRic'
        r'h":"","subjectRichParameters":[],"messageRich":"","messageRichPa'
        r'rameters":[],"icon":"http:\\/\\/localhost:8181\\/apps\\/updateno'
        r'tification\\/img\\/notification.svg","actions":[]}}}',
        "utf-8",
    )

    _empty_response = bytes(
        r'{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
        r'"data":[]}}',
        "utf-8",
    )

    @pytest.fixture
    def notification(self, notifications_api: NotificationsApi) -> Notification:
        data = json.loads(self._single_response)
        return Notification(data["ocs"]["data"], notifications_api)

    async def test_get_notifications(
        self, notifications_api: NotificationsApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(200, content=self._multi_response)
        notifications = await notifications_api.get_all()
        for notification in notifications:
            assert isinstance(notification, Notification)
            assert notification.id == 7

        request = httpx_mock.get_request()
        assert_url = "".join(
            [
                notifications_api.api.client.endpoint,
                notifications_api.api.stub,
                notifications_api.stub,
                "?format=json",
            ]
        )
        assert str(request.url) == assert_url

    async def test_get_notification(
        self, notifications_api: NotificationsApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(200, content=self._single_response)

        notification = await notifications_api.get(7)
        assert isinstance(notification, Notification)
        assert notification.id == 7
        assert "updatenotification" in str(notification)

        request = httpx_mock.get_request()
        assert_url = "".join(
            [
                notifications_api.api.client.endpoint,
                notifications_api.api.stub,
                notifications_api.stub,
                "/7?format=json",
            ]
        )
        assert str(request.url) == assert_url
        assert request.method == "GET"

    async def test_clear_notifications(
        self, notifications_api: NotificationsApi, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(200, content=self._empty_response)
        await notifications_api.clear()

        request = httpx_mock.get_request()
        assert_url = "".join(
            [
                notifications_api.api.client.endpoint,
                notifications_api.api.stub,
                notifications_api.stub,
            ]
        )
        assert str(request.url) == assert_url
        assert request.method == "DELETE"

    async def test_remove_notification(
        self,
        notifications_api: NotificationsApi,
        notification: Notification,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(200, content=self._empty_response)
        await notification.delete()

        request = httpx_mock.get_request()
        assert_url = "".join(
            [
                notifications_api.api.client.endpoint,
                notifications_api.api.stub,
                notifications_api.stub,
                "/7",
            ]
        )
        assert str(request.url) == assert_url
        assert request.method == "DELETE"
