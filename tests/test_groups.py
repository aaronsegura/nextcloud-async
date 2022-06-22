
from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import (
    USER, ENDPOINT, PASSWORD, EMPTY_100, SIMPLE_100)

import asyncio
import httpx

from unittest.mock import patch


class OCSGroupsAPI(BaseTestCase):

    def test_search_groups(self):
        SEARCH = 'OK Go!'
        RESPONSE = 'OK_GROUP'
        xml_response = bytes(
            '<?xml version="1.0"?>\n<ocs>\n <meta>\n  <status>ok</status>\n  '
            '<statuscode>100</statuscode>\n  <message>OK</message>\n  <totali'
            'tems></totalitems>\n  <itemsperpage></itemsperpage>\n </meta>\n '
            f'<data>\n  <groups>\n   <element>{RESPONSE}</element>\n  </groups>'
            '\n </data>\n</ocs>\n', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.search_groups(SEARCH))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/groups?limit=100&offset=0&search=OK+Go%21',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert RESPONSE in response['groups']

    def test_create_group(self):
        GROUP = 'BobMouldFanClub'
        with patch(
            'httpx.AsyncClient.request',
            new_callable=AsyncMock,
            return_value=httpx.Response(
                status_code=100,
                content=EMPTY_100)) as mock:
            response = asyncio.run(self.ncc.create_group(GROUP))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/groups',
                data={'groupid': GROUP},
                headers={'OCS-APIRequest': 'true'})
            assert response is None

    def test_get_group_members(self):
        GROUP = 'FeelinAlright'
        GROUPUSER = 'JoeCocker'
        xml_response = bytes(SIMPLE_100.format(
            f'<users>\n   <element>{GROUPUSER}</element>\n  </users>\n'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_group_members(GROUP))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/groups/{GROUP}?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert GROUPUSER in response['users']

    def test_get_group_subadmins(self):
        GROUP = 'UMO'
        GROUPUSER = 'Ruban Nielson'
        xml_response = bytes(SIMPLE_100.format(
            f'<users>\n   <element>{GROUPUSER}</element>\n  </users>\n'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_group_subadmins(GROUP))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/groups/{GROUP}/subadmins?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert GROUPUSER in response['users']

    def test_remove_group(self):
        GROUP = 'BobMouldFanClub'
        with patch(
            'httpx.AsyncClient.request',
            new_callable=AsyncMock,
            return_value=httpx.Response(
                status_code=100,
                content=EMPTY_100)) as mock:
            response = asyncio.run(self.ncc.remove_group(GROUP))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/groups/{GROUP}',
                data={},
                headers={'OCS-APIRequest': 'true'})
            assert response is None
