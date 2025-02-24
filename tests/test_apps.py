import pytest
import pytest_asyncio

from nextcloud_async import NextcloudClient
from nextcloud_async.api import Apps, App

@pytest.fixture
def apps(nc: NextcloudClient) -> Apps:
    return Apps(nc)

@pytest_asyncio.fixture
async def ldap_app(apps: Apps) -> App:
    return await apps.get('user_ldap')

@pytest.mark.vcr
@pytest.mark.asyncio
class TestApps:
    _enabled_by_default = ['files', 'activity', 'dashboard']

    def test_apps_init(self, nc):
        apps = Apps(nc)
        assert isinstance(apps, Apps)

    async def test_app_enable_disable(self, apps: Apps):
        ldap_app = await apps.get('user_ldap')
        await ldap_app.enable()
        await ldap_app.disable()

    async def test_app_print(self, ldap_app: App):
        string = str(ldap_app)
        repr = ldap_app.__repr__()
        assert string != repr
        assert isinstance(string, str)
        assert isinstance(repr, str)
        assert ldap_app.id in string
        assert ldap_app.version in string

    async def test_apps_list(self, apps: Apps):
        response = await apps.list('enabled')
        assert isinstance(response, list)

    async def test_apps_list_enabled(self, apps: Apps):
        response = await apps.list_enabled()
        assert isinstance(response, list)
        for a in self._enabled_by_default:
            assert a in response

    async def test_apps_list_disabled(self, apps: Apps):
        response = await apps.list_disabled()
        assert isinstance(response, list)
        for a in self._enabled_by_default:
            assert a not in response

if __name__ == 'main':
    pytest.main()