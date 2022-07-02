
from urllib.parse import urlencode
from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import (
    USER, ENDPOINT, PASSWORD, EMPTY_100, SIMPLE_100)

import asyncio
import httpx

from unittest.mock import patch


class OCSGroupsAPI(BaseTestCase):

    def test_search_groups(self):
        SEARCH = 'OK Go'
        RESPONSE = 'OK_GROUP'
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":100,"message":"OK","t'
            'otalitems":"","itemsperpage":""},"data":{"groups":['
            f'"{RESPONSE}"'
            ']}}}', 'utf-8')
        search_encoded = urlencode({'search': SEARCH})
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.search_groups(SEARCH))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/groups?'
                    f'limit=100&offset=0&{search_encoded}&format=json',
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
                data={'groupid': GROUP, 'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
            assert response == []

    def test_get_group_members(self):
        GROUP = 'FeelinAlright'
        GROUPUSER = 'JoeCocker'
        json_response = bytes(SIMPLE_100.format(
            r'{"users":["'
            f'{GROUPUSER}'
            r'"]}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_group_members(GROUP))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/groups/{GROUP}?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert GROUPUSER in response['users']

    def test_get_group_subadmins(self):
        GROUP = 'UMO'
        GROUPUSER = 'Ruban Nielson'
        json_response = bytes(SIMPLE_100.format(
            r'{"users":["'
            f'{GROUPUSER}'
            r'"]}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_group_subadmins(GROUP))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/groups/{GROUP}/subadmins?format=json',
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
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
            assert response == []
