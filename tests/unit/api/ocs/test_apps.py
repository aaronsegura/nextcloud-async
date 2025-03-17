from hashlib import sha1
from random import choice
from string import ascii_letters
from unittest.mock import call

import pytest

from nextcloud_async.api import App, Apps
from nextcloud_async.exceptions import NextcloudForbiddenError


@pytest.fixture
def apps(magicmock, asyncmock):
    apps_api = Apps(magicmock)
    apps_api.api = asyncmock
    return apps_api


@pytest.fixture
def random():
    return sha1("".join(choice(ascii_letters)).encode("utf-8")).hexdigest()


@pytest.mark.asyncio
class TestAppsApi:
    async def test_init(self, magicmock):
        apps = Apps(magicmock, ocs_version="1")
        assert apps.client == magicmock

    async def test_get_app(self, apps, random):
        await apps.get(random)
        expected = [call.get(path=f"/cloud/apps/{random}", data=None, headers=None)]
        apps.api.assert_has_calls(expected)

    async def test_apps_list(self, apps):
        await apps.list()
        expected = [
            call.get(path="/cloud/apps", data={}, headers=None),
            call.get().__getitem__("apps"),
        ]
        apps.api.assert_has_calls(expected)

    async def test_list_filter(self, apps):
        await apps.list(filter="FILTER")
        expected = [
            call.get(path="/cloud/apps", data={"filter": "filter"}, headers=None),
            call.get().__getitem__("apps"),
        ]
        apps.api.assert_has_calls(expected)

    async def test_list_enabled(self, apps):
        await apps.list_enabled()
        expected = [
            call.get(path="/cloud/apps", data={"filter": "enabled"}, headers=None),
            call.get().__getitem__("apps"),
        ]
        apps.api.assert_has_calls(expected)

    async def test_list_disabled_pre_31(self, apps):
        apps.api.get.return_value = {"apps": {1: "app_1", 2: "app_2"}}
        response = await apps.list_disabled()
        assert isinstance(response, list)
        assert ["app_1", "app_2"] == response

        expected = [
            call.get(path="/cloud/apps", data={"filter": "disabled"}, headers=None),
        ]
        apps.api.assert_has_calls(expected)

    async def test_list_disabled_31_and_later(self, apps):
        apps.api.get.return_value = {"apps": ["app_1", "app_2"]}
        response = await apps.list_disabled()
        assert isinstance(response, list)
        assert ["app_1", "app_2"] == response

        expected = [
            call.get(path="/cloud/apps", data={"filter": "disabled"}, headers=None),
        ]
        apps.api.assert_has_calls(expected)

    async def test_enable_app(self, apps, random):
        await apps.enable(random)
        expected = [
            call.post(path=f"/cloud/apps/{random}", data=None, headers=None),
        ]
        apps.api.assert_has_calls(expected)

    async def test_enable_password_confirm(self, apps, random):
        apps.api.post.side_effect = NextcloudForbiddenError(
            "Password confirmation is required."
        )
        with pytest.raises(NextcloudForbiddenError):
            await apps.enable(random)

        expected = [
            call.post(path=f"/cloud/apps/{random}", data=None, headers=None),
            call.client.http_client.cookies.delete("oc_sessionPassphrase"),
            call.post(path=f"/cloud/apps/{random}", data=None, headers=None),
        ]
        apps.api.assert_has_calls(expected)

    async def test_disable_password_confirm(self, apps, random):
        apps.api.delete.side_effect = NextcloudForbiddenError(
            "Password confirmation is required."
        )
        with pytest.raises(NextcloudForbiddenError):
            await apps.disable(random)

        expected = [
            call.delete(path=f"/cloud/apps/{random}", data=None, headers=None),
            call.client.http_client.cookies.delete("oc_sessionPassphrase"),
            call.delete(path=f"/cloud/apps/{random}", data=None, headers=None),
        ]
        apps.api.assert_has_calls(expected)

    async def test_disable_app(self, apps):
        _app = sha1().hexdigest()
        await apps.disable(_app)
        expected = [
            call.delete(path=f"/cloud/apps/{_app}", data=None, headers=None),
        ]
        apps.api.assert_has_calls(expected)


@pytest.fixture
def app(asyncmock):
    _app_data = {"id": "app_id"}
    app = App(_app_data, asyncmock)
    return app


@pytest.mark.asyncio
class TestAppDataObject:
    async def test_disable(self, app):
        await app.disable()
        expected = [call.disable(app_id="app_id")]
        app.self_api.assert_has_calls(expected)

    async def test_enable(self, app):
        await app.enable()
        expected = [call.enable(app_id="app_id")]
        app.self_api.assert_has_calls(expected)
