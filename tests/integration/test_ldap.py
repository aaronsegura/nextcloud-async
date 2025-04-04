import pytest
import pytest_asyncio

from nextcloud_async.api import AppsApi, LdapApi, LdapConfiguration
from nextcloud_async.exceptions import NextcloudNotFoundError


@pytest_asyncio.fixture(scope="function", loop_scope="session", autouse=True)
async def check_maps_enabled(apps_api: AppsApi):
    app_list = await apps_api.get_all("enabled")
    if "user_ldap" not in app_list:
        pytest.skip("user_ldap app is not enabled.  Skipping.", allow_module_level=True)


@pytest_asyncio.fixture(loop_scope="session")
async def ldap_config(ldap_api: LdapApi):
    ldap_config = await ldap_api.create()
    yield ldap_config

    try:
        await ldap_config.delete()
    except NextcloudNotFoundError:
        pass


@pytest.mark.integration
@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestLdapApi:
    async def test_create(self, ldap_config: LdapConfiguration):
        assert isinstance(ldap_config, LdapConfiguration)

    async def test_get(self, ldap_api: LdapApi, ldap_config: LdapConfiguration):
        got_config = await ldap_api.get(ldap_config.id)
        assert got_config == ldap_config

    async def test_get_with_password(
        self, ldap_api: LdapApi, ldap_config: LdapConfiguration
    ):
        await ldap_config.update({"configData": {"ldapAgentPassword": "Secrets!"}})
        got_config = await ldap_api.get(ldap_config.id, show_password=True)
        assert got_config.ldapAgentPassword == "Secrets!"


@pytest.mark.integration
@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestLdapConfigurationObject:
    async def test_delete(self, ldap_api: LdapApi, ldap_config: LdapConfiguration):
        _id = ldap_config.id
        await ldap_config.delete()
        with pytest.raises(NextcloudNotFoundError):
            await ldap_api.get(_id)

    async def test_update(self, ldap_config: LdapConfiguration):
        _new_data = {
            "configData": {"ldapHost": "ldap.example.com", "ldapBase": "LdapBase"}
        }
        await ldap_config.update(_new_data)
        assert ldap_config.ldapHost == "ldap.example.com"
        assert ldap_config.ldapBase == "LdapBase"

    async def test_update_malformed_configdata(self, ldap_config: LdapConfiguration):
        _new_data = {"ldapHost": "ldap.example.com", "ldapBase": "LdapBase"}
        await ldap_config.update(_new_data)
        assert ldap_config.ldapHost == "ldap.example.com"
        assert ldap_config.ldapBase == "LdapBase"
