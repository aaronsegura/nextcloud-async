
from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import (
    USER, ENDPOINT, PASSWORD, EMPTY_100)

import asyncio
import httpx

from unittest.mock import patch


class OCSAppsAPI(BaseTestCase):

    def test_get_app(self):
        APP = 'files'
        xml_response = bytes(
            '<?xml version="1.0"?>\n<ocs>\n <meta>\n  <status>ok</status>\n  '
            '<statuscode>100</statuscode>\n  <message>OK</message>\n  <totali'
            'tems></totalitems>\n  <itemsperpage></itemsperpage>\n </meta>\n '
            f'<data>\n  <id>{APP}</id>\n  <name>Files</name>\n  <summary>File '
            'Management</summary>\n  <description>File Management</descriptio'
            'n>\n  <version>1.18.0</version>\n  <licence>agpl</licence>\n  <a'
            'uthor>\n   <element>Robin Appelman</element>\n   <element>Vincen'
            't Petry</element>\n  </author>\n  <default_enable></default_enab'
            'le>\n  <types>\n   <element>filesystem</element>\n  </types>\n  '
            '<documentation>\n   <user>user-files</user>\n  </documentation>'
            '\n  <category>files</category>\n  <bugs>https://github.com/nextc'
            'loud/server/issues</bugs>\n  <dependencies>\n   <nextcloud/>\n  '
            '</dependencies>\n  <background-jobs>\n   <element>OCA\\Files\\Ba'
            'ckgroundJob\\ScanFiles</element>\n   <element>OCA\\Files\\Backgr'
            'oundJob\\DeleteOrphanedItems</element>\n   <element>OCA\\Files\\'
            'BackgroundJob\\CleanupFileLocks</element>\n   <element>OCA\\File'
            's\\BackgroundJob\\CleanupDirectEditingTokens</element>\n  </back'
            'ground-jobs>\n  <commands>\n   <element>OCA\\Files\\Command\\Sca'
            'n</element>\n   <element>OCA\\Files\\Command\\DeleteOrphanedFile'
            's</element>\n   <element>OCA\\Files\\Command\\TransferOwnership<'
            '/element>\n   <element>OCA\\Files\\Command\\ScanAppData</element'
            '>\n   <element>OCA\\Files\\Command\\RepairTree</element>\n  </co'
            'mmands>\n  <activity>\n   <settings>\n    <element>OCA\\Files\\A'
            'ctivity\\Settings\\FavoriteAction</element>\n    <element>OCA\\F'
            'iles\\Activity\\Settings\\FileChanged</element>\n    <element>OC'
            'A\\Files\\Activity\\Settings\\FileFavoriteChanged</element>\n   '
            '</settings>\n   <filters>\n    <element>OCA\\Files\\Activity\\Fi'
            'lter\\FileChanges</element>\n    <element>OCA\\Files\\Activity'
            '\\Filter\\Favorites</element>\n   </filters>\n   <providers>\n  '
            '  <element>OCA\\Files\\Activity\\FavoriteProvider</element>\n   '
            ' <element>OCA\\Files\\Activity\\Provider</element>\n   </provide'
            'rs>\n  </activity>\n  <navigations>\n   <navigation>\n    <eleme'
            'nt>\n     <name>Files</name>\n     <route>files.view.index</rout'
            'e>\n     <order>0</order>\n    </element>\n   </navigation>\n  <'
            '/navigations>\n  <settings>\n   <personal>\n    <element>OCA\\Fi'
            'les\\Settings\\PersonalSettings</element>\n   </personal>\n   <a'
            'dmin/>\n   <admin-section/>\n   <personal-section/>\n  </setting'
            's>\n  <info/>\n  <remote/>\n  <public/>\n  <repair-steps>\n   <i'
            'nstall/>\n   <pre-migration/>\n   <post-migration/>\n   <live-mi'
            'gration/>\n   <uninstall/>\n  </repair-steps>\n  <two-factor-pro'
            'viders/>\n </data>\n</ocs>\n', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_app(APP))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/apps/{APP}?',
                data=None,
                headers={'OCS-APIRequest': 'true'})

            match response:
                case {'id': APP}:
                    pass
                case _:
                    assert False

    def test_get_apps(self):
        APPS = [
            'workflow_script',
            'phonetrack',
            'epubreader',
            'previewgenerator',
            'unsplash',
            'serverinfo']
        xml_response = bytes(
            '<?xml version="1.0"?>\n<ocs>\n <meta>\n  <status>ok</status>\n  '
            '<statuscode>100</statuscode>\n  <message>OK</message>\n  <totali'
            'tems></totalitems>\n  <itemsperpage></itemsperpage>\n </meta>\n '
            '<data>\n  <apps>\n   <element>workflow_script</element>\n   <ele'
            'ment>phonetrack</element>\n   <element>epubreader</element>\n   '
            '<element>previewgenerator</element>\n   <element>unsplash</eleme'
            'nt>\n   <element>serverinfo</element>\n  </apps>\n </data>\n</oc'
            's>\n', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_apps())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/apps?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            for app in APPS:
                assert app in response['apps']

    def test_enable_app(self):
        APP = 'FavoriteThing'
        with patch(
            'httpx.AsyncClient.request',
            new_callable=AsyncMock,
            return_value=httpx.Response(
                status_code=100,
                content=EMPTY_100)) as mock:
            response = asyncio.run(self.ncc.enable_app(APP))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/apps/{APP}',
                data={},
                headers={'OCS-APIRequest': 'true'})
            assert response is None

    def test_disable_app(self):
        APP = 'FavoriteThing'
        with patch(
            'httpx.AsyncClient.request',
            new_callable=AsyncMock,
            return_value=httpx.Response(
                status_code=100,
                content=EMPTY_100)) as mock:
            response = asyncio.run(self.ncc.disable_app(APP))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/apps/{APP}',
                data={},
                headers={'OCS-APIRequest': 'true'})
            assert response is None
