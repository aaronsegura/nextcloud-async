"""Test Nextcloud Remote Wipe API.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html
"""

from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import USER, ENDPOINT, PASSWORD, EMPTY_200

import asyncio
import httpx

from unittest.mock import patch


class OCSRemoteWipeAPI(BaseTestCase):  # noqa: D101

    def test_get_wipe_status(self):  # noqa: D102
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=bytes('[]', 'utf-8'))) as mock:
            asyncio.run(self.ncc.get_wipe_status())
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/index.php/core/wipe/check',
                data={'token': PASSWORD},
                headers={})

    def test_notify_wipe_status(self):  # noqa: D102
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=EMPTY_200)) as mock:
            asyncio.run(self.ncc.notify_wipe_status())
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/index.php/core/wipe/success',
                data={'token': PASSWORD},
                headers={})
