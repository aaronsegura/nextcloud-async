import pytest

import json
from unittest.mock import AsyncMock

from nextcloud_async.api import Notification, NotificationsApi
from nextcloud_async.provider import HttpResponseMock


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
    def notification(
        self,
        notifications_api: tuple[NotificationsApi, HttpResponseMock],
    ) -> Notification:
        data = json.loads(self._single_response)
        return Notification(data["ocs"]["data"], notifications_api[0])

    async def test_get_notifications(
        self,
        notifications_api: tuple[NotificationsApi, HttpResponseMock],
    ):
        api, mock_response = notifications_api
        _response = mock_response(200, response=self._multi_response)  # type: ignore
        api.driver.client.http_client.request = AsyncMock(return_value=_response)
        notifications = await api.get_all()
        for notification in notifications:
            assert isinstance(notification, Notification)
            assert notification.id == 7

    async def test_get_notification(
        self,
        notifications_api: tuple[NotificationsApi, HttpResponseMock],
    ):
        api, mock_response = notifications_api
        _response = mock_response(200, response=self._single_response)  # type: ignore
        api.driver.client.http_client.request = AsyncMock(return_value=_response)

        notification = await api.get(7)
        assert isinstance(notification, Notification)
        assert notification.id == 7
        assert "updatenotification" in str(notification)

    async def test_clear_notifications(
        self,
        notifications_api: tuple[NotificationsApi, HttpResponseMock],
    ):
        api, mock_response = notifications_api
        _response = mock_response(200, response=self._empty_response)  # type: ignore
        api.driver.client.http_client.request = AsyncMock(return_value=_response)
        await api.clear()

    async def test_remove_notification(
        self,
        notifications_api: tuple[NotificationsApi, HttpResponseMock],
        notification: Notification,
    ):
        api, mock_response = notifications_api
        _response = mock_response(200, response=self._empty_response)  # type: ignore
        api.driver.client.http_client.request = AsyncMock(return_value=_response)
        await notification.delete()
        api.driver.client.http_client.request.assert_called_once()
