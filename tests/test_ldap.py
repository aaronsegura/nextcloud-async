
from nextcloud_aio.helpers import recursive_urlencode
from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import (
    USER, ENDPOINT, PASSWORD, EMPTY_100, SIMPLE_100, EMPTY_200)

import asyncio
import httpx

from unittest.mock import patch


class OCSLdapAPI(BaseTestCase):

    def test_create_ldap_config(self):
        NEW_CONFIG = 's01'
        xml_response = bytes(SIMPLE_100.format(f'<configID>{NEW_CONFIG}</configID>\n '), 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.create_ldap_config())
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_ldap/api/v1/config',
                data={},
                headers={'OCS-APIRequest': 'true'})
            assert NEW_CONFIG in response['configID']

    def test_remove_ldap_config(self):
        CONFIG = 's01'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=bytes(EMPTY_100, 'utf-8'))) as mock:
            response = asyncio.run(self.ncc.remove_ldap_config(CONFIG))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_ldap/api/v1/config/{CONFIG}',
                data={},
                headers={'OCS-APIRequest': 'true'})
            assert response is None

    def test_get_ldap_config(self):
        CONFIG = 's01'
        xml_response = bytes(
            '<?xml version="1.0"?>\n<ocs>\n <meta>\n  <status>ok</status>\n  '
            '<statuscode>200</statuscode>\n  <message>OK</message>\n </meta>'
            '\n <data>\n  <ldapHost></ldapHost>\n  <ldapPort></ldapPort>\n  '
            '<ldapBackupHost></ldapBackupHost>\n  <ldapBackupPort></ldapBack'
            'upPort>\n  <ldapBase></ldapBase>\n  <ldapBaseUsers></ldapBaseUs'
            'ers>\n  <ldapBaseGroups></ldapBaseGroups>\n  <ldapAgentName></l'
            'dapAgentName>\n  <ldapAgentPassword>***</ldapAgentPassword>\n  '
            '<ldapTLS>0</ldapTLS>\n  <turnOffCertCheck>0</turnOffCertCheck>'
            '\n  <ldapIgnoreNamingRules></ldapIgnoreNamingRules>\n  <ldapUse'
            'rDisplayName>displayName</ldapUserDisplayName>\n  <ldapUserDisp'
            'layName2></ldapUserDisplayName2>\n  <ldapUserAvatarRule>default'
            '</ldapUserAvatarRule>\n  <ldapGidNumber>gidNumber</ldapGidNumbe'
            'r>\n  <ldapUserFilterObjectclass></ldapUserFilterObjectclass>\n'
            '  <ldapUserFilterGroups></ldapUserFilterGroups>\n  <ldapUserFil'
            'ter></ldapUserFilter>\n  <ldapUserFilterMode>0</ldapUserFilterM'
            'ode>\n  <ldapGroupFilter></ldapGroupFilter>\n  <ldapGroupFilter'
            'Mode>XXX</ldapGroupFilterMode>\n  <ldapGroupFilterObjectclass><'
            '/ldapGroupFilterObjectclass>\n  <ldapGroupFilterGroups></ldapGr'
            'oupFilterGroups>\n  <ldapGroupDisplayName>cn</ldapGroupDisplayN'
            'ame>\n  <ldapGroupMemberAssocAttr></ldapGroupMemberAssocAttr>\n'
            '  <ldapLoginFilter>XXX</ldapLoginFilter>\n  <ldapLoginFilterMod'
            'e>0</ldapLoginFilterMode>\n  <ldapLoginFilterEmail>0</ldapLogin'
            'FilterEmail>\n  <ldapLoginFilterUsername>1</ldapLoginFilterUser'
            'name>\n  <ldapLoginFilterAttributes></ldapLoginFilterAttributes'
            '>\n  <ldapQuotaAttribute></ldapQuotaAttribute>\n  <ldapQuotaDef'
            'ault></ldapQuotaDefault>\n  <ldapEmailAttribute></ldapEmailAttr'
            'ibute>\n  <ldapCacheTTL>600</ldapCacheTTL>\n  <ldapUuidUserAttr'
            'ibute>auto</ldapUuidUserAttribute>\n  <ldapUuidGroupAttribute>a'
            'uto</ldapUuidGroupAttribute>\n  <ldapOverrideMainServer></ldapO'
            'verrideMainServer>\n  <ldapConfigurationActive></ldapConfigurat'
            'ionActive>\n  <ldapAttributesForUserSearch></ldapAttributesForU'
            'serSearch>\n  <ldapAttributesForGroupSearch></ldapAttributesFor'
            'GroupSearch>\n  <ldapExperiencedAdmin>0</ldapExperiencedAdmin>'
            '\n  <homeFolderNamingRule></homeFolderNamingRule>\n  <hasMember'
            'OfFilterSupport>0</hasMemberOfFilterSupport>\n  <useMemberOfToD'
            'etectMembership>1</useMemberOfToDetectMembership>\n  <ldapExper'
            'tUsernameAttr></ldapExpertUsernameAttr>\n  <ldapExpertUUIDUserA'
            'ttr></ldapExpertUUIDUserAttr>\n  <ldapExpertUUIDGroupAttr></lda'
            'pExpertUUIDGroupAttr>\n  <lastJpegPhotoLookup>0</lastJpegPhotoL'
            'ookup>\n  <ldapNestedGroups>0</ldapNestedGroups>\n  <ldapPaging'
            'Size>500</ldapPagingSize>\n  <turnOnPasswordChange>0</turnOnPas'
            'swordChange>\n  <ldapDynamicGroupMemberURL></ldapDynamicGroupMe'
            'mberURL>\n  <ldapDefaultPPolicyDN></ldapDefaultPPolicyDN>\n  <l'
            'dapExtStorageHomeAttribute></ldapExtStorageHomeAttribute>\n  <l'
            'dapMatchingRuleInChainState>unknown</ldapMatchingRuleInChainSta'
            'te>\n </data>\n</ocs>\n', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            asyncio.run(self.ncc.get_ldap_config(CONFIG))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_ldap/api/v1/config/{CONFIG}?',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_set_ldap_config(self):
        CONFIG='s01'
        CONFIG_DATA = {
            'configData':
            {
                'ldapLoginFilter': 'Randall Carlson',
                'ldapGroupFilterMode': 'Graham Hancock'
            }
        }
        URL_DATA = recursive_urlencode(CONFIG_DATA)
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=EMPTY_200)) as mock:
            asyncio.run(self.ncc.set_ldap_config(CONFIG, CONFIG_DATA))
            mock.assert_called_with(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_ldap/api/v1/config/{CONFIG}?{URL_DATA}',
                data={},
                headers={'OCS-APIRequest': 'true'})
