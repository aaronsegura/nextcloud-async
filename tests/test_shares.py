
from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import (
    USER, ENDPOINT, PASSWORD, EMPTY_100, SIMPLE_100)

import asyncio
import httpx

from unittest.mock import patch


class OCSGroupsAPI(BaseTestCase):

    def test_get_all_shares(self):
        xml_response = bytes(
            '<?xml version="1.0"?>\n<ocs>\n <meta>\n  <status>ok</status>\n  '
            '<statuscode>200</statuscode>\n  <message>OK</message>\n </meta>'
            '\n <data>\n  <element>\n   <id>1</id>\n   <share_type>0</share_t'
            'ype>\n   <uid_owner>admin</uid_owner>\n   <displayname_owner>adm'
            'in</displayname_owner>\n   <permissions>19</permissions>\n   <ca'
            'n_edit>1</can_edit>\n   <can_delete>1</can_delete>\n   <stime>16'
            '56094271</stime>\n   <parent/>\n   <expiration/>\n   <token/>\n '
            '  <uid_file_owner>admin</uid_file_owner>\n   <note></note>\n   <'
            'label/>\n   <displayname_file_owner>admin</displayname_file_owne'
            'r>\n   <path>/Nextcloud Manual.pdf</path>\n   <item_type>file</i'
            'tem_type>\n   <mimetype>application/pdf</mimetype>\n   <has_prev'
            'iew></has_preview>\n   <storage_id>home::admin</storage_id>\n   '
            '<storage>1</storage>\n   <item_source>30</item_source>\n   <file'
            '_source>30</file_source>\n   <file_parent>2</file_parent>\n   <f'
            'ile_target>/Nextcloud Manual.pdf</file_target>\n   <share_with>t'
            'estuser</share_with>\n   <share_with_displayname>Test User</shar'
            'e_with_displayname>\n   <share_with_displayname_unique>test@exam'
            'ple.com</share_with_displayname_unique>\n   <status/>\n   <mail_'
            'send>0</mail_send>\n   <hide_download>0</hide_download>\n  </ele'
            'ment>\n </data>\n</ocs>\n', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            asyncio.run(self.ncc.get_all_shares())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/files_sharing/api/v1/shares?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
