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

    # TODO: Test get_notification(X)

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
