import pytest
import pytest_asyncio

from typing import AsyncGenerator

from nextcloud_async.api import Apps, App


_test_app = "files_external"


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def test_app(apps: Apps) -> AsyncGenerator[App]:
    yield await apps.get(_test_app)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestApps:
    _enabled_by_default = ["files", "activity", "dashboard"]

    async def test_app_enable_disable(self, apps: Apps):
        test_app = await apps.get(_test_app)
        await test_app.enable()
        await test_app.disable()

    async def test_apps_list(self, apps: Apps):
        response = await apps.list("enabled")
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
