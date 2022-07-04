from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import USER, ENDPOINT, PASSWORD, SIMPLE_100

from nextcloud_aio.api.ocs.groupfolders import Permissions as GP

import asyncio
import httpx

from unittest.mock import patch

FOLDER = 'GROUPFOLDER'
FOLDERID = 2
GROUP = 'somegroup'
TESTUSER = 'testuser'


class OCSGroupFoldersAPI(BaseTestCase):

    def test_get_all_group_folders(self):
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":100,"message":"OK",'
            f'"totalitems":"","itemsperpage":""}},"data":{{"{FOLDERID}":{{"id"'
            f':{FOLDERID},"mount_point":"{FOLDER}","groups":[],"quota":-3,"si'
            'ze":0,"acl":false,"manage":[]}}}}', 'utf-8')
        with patch(
            'httpx.AsyncClient.request',
            new_callable=AsyncMock,
            return_value=httpx.Response(
                status_code=100,
                content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_all_group_folders())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response[str(FOLDERID)]['id'] == FOLDERID

    def test_create_group_folder(self):
        json_response = bytes(SIMPLE_100.format(f'{{"id":{FOLDERID}}}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.create_group_folder(FOLDER))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders',
                data={'mountpoint': FOLDER, 'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
            assert response['id'] == FOLDERID

    def test_get_group_folder(self):
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":100,"message":"OK",'
            f'"totalitems":"","itemsperpage":""}},"data":{{"id":{FOLDERID},'
            f'"mount_point":"{FOLDER}","groups":[],"quota":-3,"size":0,"acl'
            '":false,"manage":[]}}}', 'utf-8')
        with patch(
            'httpx.AsyncClient.request',
            new_callable=AsyncMock,
            return_value=httpx.Response(
                status_code=100,
                content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_group_folder(FOLDERID))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response['id'] == FOLDERID

    def test_remove_group_folder(self):
        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.remove_group_folder(FOLDERID))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}',
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_add_group_to_group_folder(self):
        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.add_group_to_group_folder(GROUP, FOLDERID))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/groups',
                data={'format': 'json', 'group': GROUP},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_remove_group_from_group_folder(self):
        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.remove_group_from_group_folder(GROUP, FOLDERID))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/groups/{GROUP}',
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_enable_advanced_permissions(self):
        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(
                self.ncc.enable_group_folder_advanced_permissions(FOLDERID))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/acl',
                data={'format': 'json', 'acl': 1},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_disable_advanced_permissions(self):
        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(
                self.ncc.disable_group_folder_advanced_permissions(FOLDERID))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/acl',
                data={'format': 'json', 'acl': 0},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_add_group_folder_advanced_permissions(self):
        TYPE = 'user'
        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(
                self.ncc.add_group_folder_advanced_permissions(FOLDERID, TESTUSER, TYPE))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/manageACL',
                data={
                    'format': 'json',
                    'mappingId': TESTUSER,
                    'mappingType': TYPE,
                    'manageAcl': True},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_remove_group_folder_advanced_permissions(self):
        TYPE = 'user'
        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(
                self.ncc.remove_group_folder_advanced_permissions(FOLDERID, TESTUSER, TYPE))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/manageACL',
                data={
                    'format': 'json',
                    'mappingId': TESTUSER,
                    'mappingType': TYPE,
                    'manageAcl': False},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_set_group_folder_permissions(self):
        PERM = GP['create']|GP['delete']

        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(
                self.ncc.set_group_folder_permissions(FOLDERID, GROUP, PERM))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/groups/{GROUP}',
                data={
                    'format': 'json',
                    'permissions': PERM.value},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_set_group_folder_quota(self):
        QUOTA = -3

        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(
                self.ncc.set_group_folder_quota(FOLDERID, QUOTA))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/quota',
                data={
                    'format': 'json',
                    'quota': QUOTA},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True

    def test_rename_group_folder(self):
        NEWNAME = 'TakeFive'

        json_response = bytes(SIMPLE_100.format('{"success":true}'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(
                self.ncc.rename_group_folder(FOLDERID, NEWNAME))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/apps/groupfolders/folders/{FOLDERID}/mountpoint',
                data={
                    'format': 'json',
                    'mountpoint': NEWNAME},
                headers={'OCS-APIRequest': 'true'})
            assert response['success'] is True
