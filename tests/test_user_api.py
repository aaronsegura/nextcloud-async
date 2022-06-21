
from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import (
    USER, NAME, ENDPOINT, PASSWORD, EMAIL, EMPTY_100, SIMPLE_100)

from nextcloud_aio.exceptions import NextCloudAsyncException

import asyncio
import httpx

from unittest.mock import patch


class OCSUserAPI(BaseTestCase):

    def test_create_user(self):
        xml_response = bytes(SIMPLE_100.format(f'<id>{USER}</id>\n'), 'utf-8')
        QUOTA = '1G'
        LANG = 'en'

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.create_user(
                user_id=USER,
                email=EMAIL,
                display_name=NAME,
                password=PASSWORD,
                language=LANG,
                quota=QUOTA))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users',
                data={
                    'userid': USER,
                    'displayName': NAME,
                    'email': EMAIL,
                    'groups': [], 'subadmin': [],
                    'language': LANG,
                    'quota': QUOTA,
                    'password': PASSWORD},
                headers={'OCS-APIRequest': 'true'})
            assert response['id'] == USER

    def test_search_users(self):
        xml_response = bytes(SIMPLE_100.format(
            f'<users>\n<element>{USER}</element>\n  </users>\n'), 'utf-8')
        SEARCH = 'MUTEMATH'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.search_users(SEARCH))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users?search={SEARCH}&limit=100&offset=0',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert USER in response['users']['element']

    def test_get_user(self):
        xml_response = bytes(SIMPLE_100.format(
            f'<id>{USER}</id>\n <displayname>{NAME}</displayname>\n'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_user())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response['displayname'] == NAME and response['id'] == USER

    def test_get_users(self):
        TESTUSER = 'testuser'
        xml_response = bytes(SIMPLE_100.format(
            f'<users>\n   <element>{USER}</element>\n'
            f'<element>{TESTUSER}</element>\n </users>\n'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_users())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response['users']['element'] == [USER, TESTUSER]

    def test_user_autocomplete(self):
        xml_response = bytes(
            '<?xml version="1.0"?>\n<ocs>\n <meta>\n  <status>'
            'ok</status>\n  <statuscode>200</statuscode>\n  <message>OK</message>\n'
            f'</meta>\n <data>\n  <element>\n   <id>{USER}</id>\n   <label>{NAME}'
            '</label>\n   <icon>icon-user</icon>\n   <source>users</source>\n'
            '<status>\n    <status>online</status>\n    <message/>\n    <icon/>\n'
            '<clearAt/>\n   </status>\n   <subline></subline>\n  </element>\n'
            '</data>\n</ocs>\n', 'utf-8')
        SEARCH = 'dk'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            asyncio.run(self.ncc.user_autocomplete(SEARCH))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url='https://cloud.example.com/ocs/v2.php/core/autocomplete/get'
                    f'?search={SEARCH}&itemType=None&limit=10',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_update_user(self):
        WEBSITE = 'website'
        DISPLAYNAME = 'displayname'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=EMPTY_100)) as mock:
            asyncio.run(self.ncc.update_user(
                USER, {DISPLAYNAME: NAME, WEBSITE: ENDPOINT}))
            mock.assert_any_call(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}',
                data={'key': DISPLAYNAME, 'value': NAME},
                headers={'OCS-APIRequest': 'true'})
            mock.assert_any_call(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}',
                data={'key': WEBSITE, 'value': ENDPOINT},
                headers={'OCS-APIRequest': 'true'})
            assert mock.call_count == 2

    def test_get_user_editable_fields(self):
        FIELDS = ['displayname', 'email']
        xml_response = bytes(
            SIMPLE_100
            .format('<element>{}</element>\n   <element>{}</element>\n')
            .format(*FIELDS), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_user_editable_fields())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/user/fields?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            for field in FIELDS:
                assert field in response['element']

    def test_disable_user(self):
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=EMPTY_100)) as mock:
            asyncio.run(self.ncc.disable_user(USER))
            mock.assert_called_with(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/disable',
                data={},
                headers={'OCS-APIRequest': 'true'})

    def test_enable_user(self):
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=EMPTY_100)) as mock:
            asyncio.run(self.ncc.enable_user(USER))
            mock.assert_called_with(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/enable',
                data={},
                headers={'OCS-APIRequest': 'true'})

    def test_remove_user(self):
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=EMPTY_100)) as mock:
            asyncio.run(self.ncc.remove_user(user_id=USER))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}',
                data={},
                headers={'OCS-APIRequest': 'true'})

    def test_get_self_groups(self):
        xml_response = bytes(SIMPLE_100.format('<groups/>\n'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_user_groups())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/groups?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response['groups'] is None

    def test_get_user_groups(self):
        TESTUSER = 'testuser'
        xml_response = bytes(SIMPLE_100.format('<groups/>\n'), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_user_groups(TESTUSER))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{TESTUSER}/groups?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response['groups'] is None

    def test_add_user_to_group(self):
        GROUP = 'group'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=EMPTY_100)) as mock:
            asyncio.run(self.ncc.add_user_to_group(USER, GROUP))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/groups',
                data={'groupid': GROUP},
                headers={'OCS-APIRequest': 'true'})

    def test_add_user_to_nonexistent_group(self):
        GROUP = 'noexist_group'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock) as mock:
            mock.side_effect = NextCloudAsyncException('102: None')
            try:
                asyncio.run(self.ncc.add_user_to_group(USER, GROUP))
            except NextCloudAsyncException:
                pass
            finally:
                mock.assert_called_with(
                    method='POST',
                    auth=(USER, PASSWORD),
                    url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/groups',
                    data={'groupid': GROUP},
                    headers={'OCS-APIRequest': 'true'})
                self.assertRaises(NextCloudAsyncException)

    def test_remove_user_from_group(self):
        GROUP = 'group'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=EMPTY_100)) as mock:
            asyncio.run(self.ncc.remove_user_from_group(USER, GROUP))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/groups',
                data={'groupid': GROUP},
                headers={'OCS-APIRequest': 'true'})

    def test_promote_user_to_subadmin(self):
        GROUP = 'group'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=EMPTY_100)) as mock:
            asyncio.run(self.ncc.promote_user_to_subadmin(USER, GROUP))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/subadmins',
                data={'groupid': GROUP},
                headers={'OCS-APIRequest': 'true'})

    def test_demote_user_from_subadmin(self):
        GROUP = 'group'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=EMPTY_100)) as mock:
            asyncio.run(self.ncc.demote_user_from_subadmin(USER, GROUP))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/subadmins',
                data={'groupid': GROUP},
                headers={'OCS-APIRequest': 'true'})

    def test_get_user_subadmin_groups(self):
        TESTUSER = 'testuser'
        xml_response = EMPTY_100
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_user_subadmin_groups(TESTUSER))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{TESTUSER}/subadmins?',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response is None

    def test_resend_welcome_email(self):
        TESTUSER = 'testuser'
        xml_response = EMPTY_100
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=100,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.resend_welcome_email(TESTUSER))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{TESTUSER}/welcome',
                data={},
                headers={'OCS-APIRequest': 'true'})
            assert response is None
