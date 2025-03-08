# import pytest
# import pytest_asyncio
# import asyncio

# from typing import AsyncGenerator

# from nextcloud_async import NextcloudClient
# from nextcloud_async.api import Apps
# from nextcloud_async.api import Ldap, LdapConfiguration
# from nextcloud_async.exceptions import NextcloudError

# from .constants import USER, PASSWORD, ENDPOINT
# from .conftest import _NETWORK_BLOCKED

# # pytest.skip('test', allow_module_level=True)

# def setup_module():
#     if not _NETWORK_BLOCKED:
#         asyncio.run(async_setup_module())

# async def async_setup_module():
#     nc = NextcloudClient(ENDPOINT, USER, PASSWORD)
#     apps = Apps(nc)
#     try:
#         await apps.enable("user_ldap")
#     except NextcloudError:
#         pytest.skip("LDAP Not enabled.", allow_module_level=True)


# @pytest_asyncio.fixture(scope='function', loop_scope='session')
# async def ldap_config(ldap_api: Ldap) -> AsyncGenerator[LdapConfiguration]:
#     print("1")
#     ldap_config = await ldap_api.create()
#     print("2")
#     yield ldap_config
#     print("3")
#     try:
#         await ldap_config.delete()
#         print("4")
#     except NextcloudError:
#         pass
#     print("5")


# #@pytest.mark.vcr
# @pytest.mark.asyncio(loop_scope='session')
# class TestLdap:

#     async def test_create_ldap_config(self, ldap_config: LdapConfiguration):
#         pass

#     @pytest.mark.skip
#     async def test_delete_ldap_config(self, ldap_config: LdapConfiguration):
#         await ldap_config.delete()

# # #     def test_remove_ldap_config(self):
# # #         CONFIG = 's01'
# # #         with patch(
# # #                 'httpx.AsyncClient.request',
# # #                 new_callable=AsyncMock,
# # #                 return_value=httpx.Response(
# # #                     status_code=200,
# # #                     content=EMPTY_200)) as mock:
# # #             response = asyncio.run(self.ncc.remove_ldap_config(CONFIG))
# # #             mock.assert_called_with(
# # #                 method='DELETE',
# # #                 auth=(USER, PASSWORD),
# # #                 url=f'{ENDPOINT}/ocs/v2.php/apps/user_ldap/api/v1/config/{CONFIG}',
# # #                 data={"format": "json"},
# # #                 headers={'OCS-APIRequest': 'true'})
# # #             assert response == []

# # #     def test_get_ldap_config(self):
# # #         CONFIG = 's01'
# # #         xml_response = bytes(
# # #             '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
# # #             '"data":{"ldapHost":"","ldapPort":"","ldapBackupHost":"","ldapBa'
# # #             'ckupPort":"","ldapBase":"","ldapBaseUsers":"","ldapBaseGroups":'
# # #             '"","ldapAgentName":"","ldapAgentPassword":"***","ldapTLS":"0","'
# # #             'turnOffCertCheck":"0","ldapIgnoreNamingRules":"","ldapUserDispl'
# # #             'ayName":"displayName","ldapUserDisplayName2":"","ldapUserAvatar'
# # #             'Rule":"default","ldapGidNumber":"gidNumber","ldapUserFilterObje'
# # #             'ctclass":"","ldapUserFilterGroups":"","ldapUserFilter":"","ldap'
# # #             'UserFilterMode":"0","ldapGroupFilter":"","ldapGroupFilterMode":'
# # #             '"0","ldapGroupFilterObjectclass":"","ldapGroupFilterGroups":"",'
# # #             '"ldapGroupDisplayName":"cn","ldapGroupMemberAssocAttr":"","ldap'
# # #             'LoginFilter":"","ldapLoginFilterMode":"0","ldapLoginFilterEmail'
# # #             '":"0","ldapLoginFilterUsername":"1","ldapLoginFilterAttributes"'
# # #             ':"","ldapQuotaAttribute":"","ldapQuotaDefault":"","ldapEmailAtt'
# # #             'ribute":"","ldapCacheTTL":"600","ldapUuidUserAttribute":"auto",'
# # #             '"ldapUuidGroupAttribute":"auto","ldapOverrideMainServer":"","ld'
# # #             'apConfigurationActive":"","ldapAttributesForUserSearch":"","lda'
# # #             'pAttributesForGroupSearch":"","ldapExperiencedAdmin":"0","homeF'
# # #             'olderNamingRule":"","hasMemberOfFilterSupport":"0","useMemberOf'
# # #             'ToDetectMembership":"1","ldapExpertUsernameAttr":"","ldapExpert'
# # #             'UUIDUserAttr":"","ldapExpertUUIDGroupAttr":"","lastJpegPhotoLoo'
# # #             'kup":"0","ldapNestedGroups":"0","ldapPagingSize":"500","turnOnP'
# # #             'asswordChange":"0","ldapDynamicGroupMemberURL":"","ldapDefaultP'
# # #             'PolicyDN":"","ldapExtStorageHomeAttribute":"","ldapMatchingRule'
# # #             r'InChainState":"unknown"}}}', 'utf-8')
# # #         with patch(
# # #                 'httpx.AsyncClient.request',
# # #                 new_callable=AsyncMock,
# # #                 return_value=httpx.Response(
# # #                     status_code=200,
# # #                     content=xml_response)) as mock:
# # #             asyncio.run(self.ncc.get_ldap_config(CONFIG))
# # #             mock.assert_called_with(
# # #                 method='GET',
# # #                 auth=(USER, PASSWORD),
# # #                 url=f'{ENDPOINT}/ocs/v2.php/apps/user_ldap/api/v1/config/{CONFIG}?format=json',
# # #                 data=None,
# # #                 headers={'OCS-APIRequest': 'true'})

# # #     def test_set_ldap_config(self):
# # #         CONFIG = 's01'
# # #         CONFIG_DATA = {
# # #             'configData':
# # #             {
# # #                 'ldapLoginFilter': 'Randall Carlson',
# # #                 'ldapGroupFilterMode': 'Graham Hancock'
# # #             }
# # #         }
# # #         URL_DATA = recursive_urlencode(CONFIG_DATA)
# # #         with patch(
# # #                 'httpx.AsyncClient.request',
# # #                 new_callable=AsyncMock,
# # #                 return_value=httpx.Response(
# # #                     status_code=200,
# # #                     content=EMPTY_200)) as mock:
# # #             asyncio.run(self.ncc.set_ldap_config(CONFIG, CONFIG_DATA))
# # #             mock.assert_called_with(
# # #                 method='PUT',
# # #                 auth=(USER, PASSWORD),
# # #                 url=f'{ENDPOINT}/ocs/v2.php/apps/user_ldap/api/v1/config/{CONFIG}?{URL_DATA}',
# # #                 data={"format": "json"},
# # #                 headers={'OCS-APIRequest': 'true'})
