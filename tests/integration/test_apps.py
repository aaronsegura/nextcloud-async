import pytest

from nextcloud_async.api import AppsApi

_test_app = "files_external"


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestAppsApi:
    _enabled_by_default = ["files", "activity", "dashboard"]

    async def test_app_enable_disable(self, apps_api: AppsApi):
        test_app = await apps_api.get(_test_app)
        await test_app.enable()
        await test_app.disable()

    async def test_apps_list(self, apps_api: AppsApi):
        response = await apps_api.get_all("enabled")
        assert isinstance(response, list)

    async def test_apps_list_enabled(self, apps_api: AppsApi):
        response = await apps_api.list_enabled()
        assert isinstance(response, list)
        for a in self._enabled_by_default:
            assert a in response

    async def test_apps_list_disabled(self, apps_api: AppsApi):
        response = await apps_api.list_disabled()
        assert isinstance(response, list)
        for a in self._enabled_by_default:
            assert a not in response
