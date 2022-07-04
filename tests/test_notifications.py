"""Test Nextcloud Notifications API.

https://github.com/nextcloud/notifications/blob/master/docs/ocs-endpoint-v2.md
"""

from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import (
    USER, ENDPOINT, PASSWORD, EMPTY_200)

import asyncio
import httpx

from unittest.mock import patch


class OCSNotificationAPI(BaseTestCase):
    """Interact with Nextcloud Notifications API.

    Get user notifications, mark them read.  What more could you ever need?
    """

    def test_get_notifications(self):  # noqa: D102
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=EMPTY_200)) as mock:
            asyncio.run(self.ncc.get_notifications())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/notifications/api/v2/notifications?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_get_notification(self):  # noqa: D102
        NOT_ID = 7
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            f'"data":{{"notification_id":{NOT_ID},"app":"updatenotifi'
            'cation","user":"admin","datetime":"2022-07-04T14:10:22+00:00","o'
            'bject_type":"core","object_id":"24.0.2.1","subject":"Update to N'
            'extcloud 24.0.2 is available.","message":"","link":"http:\\/\\/l'
            'ocalhost:8181\\/settings\\/admin\\/overview#version","subjectRic'
            'h":"","subjectRichParameters":[],"messageRich":"","messageRichPa'
            'rameters":[],"icon":"http:\\/\\/localhost:8181\\/apps\\/updateno'
            'tification\\/img\\/notification.svg","actions":[]}}}', 'utf-8')

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_notification(NOT_ID))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/notifications/api/v2/notifications/{NOT_ID}?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response['notification_id'] == NOT_ID

    def test_remove_notifications(self):  # noqa: D102
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=EMPTY_200)) as mock:
            asyncio.run(self.ncc.remove_notifications())
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/notifications/api/v2/notifications',
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})

    def test_remove_notification(self):  # noqa: D102
        NOTIFICATION = 'xxxx'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=EMPTY_200)) as mock:
            asyncio.run(self.ncc.remove_notification(NOTIFICATION))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/notifications/api/'
                    f'v2/notifications/{NOTIFICATION}',
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
