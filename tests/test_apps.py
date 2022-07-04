
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
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":100,"message":"OK","t'
            'otalitems":"","itemsperpage":""},"data":{"id":"files","name":'
            f'"{APP}","summary":"File Management","description":"File Managem'
            'ent","version":"1.19.0","licence":"agpl","author":["Robin Appelm'
            'an","Vincent Petry"],"default_enable":"","types":["filesystem"],'
            '"documentation":{"user":"user-files"},"category":"files","bugs":'
            '"https:\\/\\/github.com\\/nextcloud\\/server\\/issues","dependen'
            'cies":{"nextcloud":{"@attributes":{"min-version":"24","max-versi'
            r'on":"24"}}},"background-jobs":["OCA\\\\Files\\\\BackgroundJob'
            '\\\\ScanFiles","OCA\\\\Files\\\\BackgroundJob\\\\DeleteOrphanedI'
            'tems","OCA\\\\Files\\\\BackgroundJob\\\\CleanupFileLocks","OCA'
            '\\\\Files\\\\BackgroundJob\\\\CleanupDirectEditingTokens"],"comm'
            'ands":["OCA\\\\Files\\\\Command\\\\Scan","OCA\\\\Files\\\\Comman'
            'd\\\\DeleteOrphanedFiles","OCA\\\\Files\\\\Command\\\\TransferOw'
            'nership","OCA\\\\Files\\\\Command\\\\ScanAppData","OCA\\\\Files'
            '\\\\Command\\\\RepairTree"],"activity":{"settings":["OCA\\\\Fil'
            'es\\\\Activity\\\\Settings\\\\FavoriteAction","OCA\\\\Files\\\\'
            'Activity\\\\Settings\\\\FileChanged","OCA\\\\Files\\\\Activity'
            '\\\\Settings\\\\FileFavoriteChanged"],"filters":["OCA\\\\Files'
            '\\\\Activity\\\\Filter\\\\FileChanges","OCA\\\\Files\\\\Activity'
            '\\\\Filter\\\\Favorites"],"providers":["OCA\\\\Files\\\\Activity'
            '\\\\FavoriteProvider","OCA\\\\Files\\\\Activity\\\\Provider"]},"'
            'navigations":{"navigation":[{"name":"Files","route":"files.view.'
            'index","order":"0"}]},"settings":{"personal":["OCA\\\\Files\\\\S'
            'ettings\\\\PersonalSettings"],"admin":[],"admin-section":[],"per'
            'sonal-section":[]},"info":[],"remote":[],"public":[],"repair-ste'
            'ps":{"install":[],"pre-migration":[],"post-migration":[],"live-m'
            'igration":[],"uninstall":[]},"two-factor-providers":[]}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_app(APP))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/apps/{APP}?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})

            match response:
                case {'id': APP}:
                    pass
                case _:
                    assert False

    def test_get_apps(self):
        APPS = [
            'serverinfo',
            'files_trashbin',
            'weather_status',
            'systemtags',
            'files_external',
            'encryption',
            'spreed']
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":100,"message":"OK",'
            '"totalitems":"","itemsperpage":""},"data":{"apps":["serverinfo'
            '","files_trashbin","weather_status","systemtags","files_extern'
            'al","encryption","spreed"]}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_apps())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/apps?format=json',
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
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
            assert response == []

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
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})
            assert response == []
