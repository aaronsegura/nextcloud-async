from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import USER, ENDPOINT, PASSWORD, EMPTY_200

import asyncio
import httpx

from unittest.mock import patch
from importlib.metadata import version

VERSION = version('nextcloud_async')
TOKEN = 'qWPKzgQoCeV4Cvgc8Sl9ENJ8kXrGmijwWgA0eCNgOnP2bt'\
        'sWturgzFkdLGySmzMiheh746voMs5lpOB57MRm66KDV40G4n7V03cUnwznKX95k1'\
        'taNobxuGCNthK3I5me'


class LoginFlowV2(BaseTestCase):

    def test_login_flow_initiate(self):
        json_response = bytes(
            f'{{"poll":{{"token":"{TOKEN}","endpoint":"http:\\/\\/localhost:81'
            '81\\/login\\/v2\\/poll"},"login":"http:\\/\\/localhost:8181\\/l'
            'ogin\\/v2\\/flow\\/TtnMLxXHbxzkvubprdlowN0QoS7k9UVtOLf977xxVXsf'
            '9oUUsXGXjU9vSRi3axFUEZCyF2nC6WD8NERUwaeewCZC99NgN6IjGlCMWEHrS08'
            'I8GL1dChWpYqn78S1Zmk7"}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.login_flow_initiate())
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/index.php/login/v2',
                data={},
                headers={'user-agent': f'nextcloud_async/{VERSION}'})

    def test_login_flow_confirm(self):
        json_response = bytes(
            f'{{"server":"http:\\/\\/localhost:8181","loginName":"{USER}",'
            '"appPassword":"aoXMDFSBmFQhsqvuKuFXhW4s4Uj1GUJ3OZttYid7jbAxL'
            'XLZQDYOIywkW7kBLiroLyAik1Pf"}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.login_flow_wait_confirm(TOKEN, timeout=1))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/index.php/login/v2/poll',
                data={'token': TOKEN},
                headers={})

    def test_destroy_app_token(self):
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=EMPTY_200)) as mock:
            asyncio.run(self.ncc.destroy_login_token())
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/core/apppassword',
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
