# noqa: D100

from nextcloud_async.helpers import recursive_urlencode
from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import USER, ENDPOINT, PASSWORD

import asyncio
import httpx

from unittest.mock import patch


class OCSShareAPI(BaseTestCase):  # noqa: D101

    def test_get_all_shares(self):  # noqa: D102
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},"'
            'data":[{"id":"1","share_type":0,"uid_owner":"admin","displayname'
            '_owner":"admin","permissions":19,"can_edit":true,"can_delete":tr'
            'ue,"stime":1656094271,"parent":null,"expiration":null,"token":nu'
            'll,"uid_file_owner":"admin","note":"","label":null,"displayname_'
            'file_owner":"admin","path":"\\/Nextcloud Manual.pdf","item_type"'
            ':"file","mimetype":"application\\/pdf","has_preview":false,"stor'
            'age_id":"home::admin","storage":1,"item_source":30,"file_source"'
            ':30,"file_parent":2,"file_target":"\\/Nextcloud Manual.pdf","sha'
            're_with":"testuser","share_with_displayname":"Test User","share_'
            'with_displayname_unique":"test@example.com","status":[],"mail_se'
            'nd":0,"hide_download":0}]}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.get_all_shares())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/files_sharing/api/v1/shares?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_get_file_shares(self):  # noqa: D102
        PATH = b''
        RESHARES = 'True'
        SUBFILES = 'True'
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},"'
            'data":[{"id":"1","share_type":0,"uid_owner":"admin","displayname'
            '_owner":"admin","permissions":19,"can_edit":true,"can_delete":tr'
            'ue,"stime":1656094271,"parent":null,"expiration":null,"token":nu'
            'll,"uid_file_owner":"admin","note":"","label":null,"displayname_'
            'file_owner":"admin","path":"\\/Nextcloud Manual.pdf","item_type"'
            ':"file","mimetype":"application\\/pdf","has_preview":false,"stor'
            'age_id":"home::admin","storage":1,"item_source":30,"file_source"'
            ':30,"file_parent":2,"file_target":"\\/Nextcloud Manual.pdf","sha'
            're_with":"testuser","share_with_displayname":"Test User","share_'
            'with_displayname_unique":"test@example.com","status":[],"mail_se'
            'nd":0,"hide_download":0}]}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            urldata = recursive_urlencode({
                'path': PATH,
                'reshares': RESHARES,
                'subfiles': SUBFILES})
            asyncio.run(self.ncc.get_file_shares(PATH, RESHARES, SUBFILES))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/files_sharing/api/v1/shares?'
                    f'{urldata}&format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_get_share(self):  # noqa: D102
        SHARE_ID = 1
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},"'
            f'data":[{{"id":"{SHARE_ID}","share_type":0,"uid_owner":"admin","displayname'
            '_owner":"admin","permissions":19,"can_edit":true,"can_delete":tr'
            'ue,"stime":1656094271,"parent":null,"expiration":null,"token":nu'
            'll,"uid_file_owner":"admin","note":"","label":null,"displayname_'
            'file_owner":"admin","path":"\\/Nextcloud Manual.pdf","item_type"'
            ':"file","mimetype":"application\\/pdf","has_preview":false,"stor'
            'age_id":"home::admin","storage":1,"item_source":30,"file_source"'
            ':30,"file_parent":2,"file_target":"\\/Nextcloud Manual.pdf","sha'
            're_with":"testuser","share_with_displayname":"Test User","share_'
            'with_displayname_unique":"test@example.com","status":[],"mail_se'
            'nd":0,"hide_download":0}]}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_share(SHARE_ID))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/files_sharing/api'
                    f'/v1/shares/{SHARE_ID}?share_id={SHARE_ID}&format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert isinstance(response, dict)

# TODO: Finish shares api tests
