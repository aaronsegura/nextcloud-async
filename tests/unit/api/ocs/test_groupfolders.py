import copy
from hashlib import sha1
from unittest.mock import AsyncMock, MagicMock, call

import httpx
import pytest
from pytest_httpx import HTTPXMock

from nextcloud_async import NextcloudClient
from nextcloud_async.api import (
    AclManagerType,
    Group,
    GroupFolder,
    GroupFolders,
    GroupFoldersPermissions,
    User,
)

from .constants import (
    CAPABILITIES_RESPONSE,
    CAPABILITIES_URL,
    ENDPOINT,
    OCS_EMPTY_200,
    PASSWORD,
    USER,
)

_LEGACY_SUCCESS_RESPONSE = copy.deepcopy(OCS_EMPTY_200)
_LEGACY_SUCCESS_RESPONSE["ocs"]["data"] = {"success": True}

GET_RESPONSE = {
    "ocs": {
        "meta": {
            "status": "ok",
            "statuscode": 100,
            "message": "OK",
            "totalitems": "",
            "itemsperpage": "",
        },
        "data": {
            "id": 972,
            "mount_point": "/.nextcloud-async-pytest/groupfolders/groupfolder_0",
            "groups": [],
            "quota": -3,
            "size": 0,
            "acl": False,
            "manage": [],
            "group_details": [],
        },
    }
}

_LATEST_SUCCESS_RESPONSE = copy.deepcopy(_LEGACY_SUCCESS_RESPONSE)
_LATEST_SUCCESS_RESPONSE["ocs"]["data"]["folder"] = GET_RESPONSE["ocs"]["data"]

LIST_RESPONSE = {
    "ocs": {
        "meta": {
            "status": "ok",
            "statuscode": 100,
            "message": "OK",
            "totalitems": "",
            "itemsperpage": "",
        },
        "data": {
            "938": {
                "id": 938,
                "mount_point": "test",
                "groups": [],
                "quota": -3,
                "size": 0,
                "acl": False,
                "manage": [],
                "group_details": [],
            },
            "1032": {
                "id": 1032,
                "mount_point": "/.nextcloud-async-pytest/groupfolders/groupfolder_0",
                "groups": [],
                "quota": -3,
                "size": 0,
                "acl": False,
                "manage": [],
                "group_details": [],
            },
            "1033": {
                "id": 1033,
                "mount_point": "/.nextcloud-async-pytest/groupfolders/groupfolder_1",
                "groups": [],
                "quota": -3,
                "size": 0,
                "acl": False,
                "manage": [],
                "group_details": [],
            },
            "1034": {
                "id": 1034,
                "mount_point": "/.nextcloud-async-pytest/groupfolders/groupfolder_2",
                "groups": [],
                "quota": -3,
                "size": 0,
                "acl": False,
                "manage": [],
                "group_details": [],
            },
        },
    }
}


@pytest.fixture(name="gfs")
def _groupfolders(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "nextcloud_async.api.ocs.groupfolders.GroupFolders._validate_capability",
        AsyncMock(),
    )
    nc = NextcloudClient(ENDPOINT, USER, PASSWORD, http_client=httpx.AsyncClient())
    gf = GroupFolders(nc)
    gf.api.destroy_capabilities()
    return gf


_STUB = "/index.php/apps/groupfolders/folders"


@pytest.mark.asyncio
class TestGroupFoldersApi:
    async def test_validate_capability(self, magicmock: MagicMock, asyncmock: AsyncMock):
        gfs = GroupFolders(magicmock)
        gfs.api = asyncmock
        await gfs._validate_capability()
        expected = [call.require_capability("groupfolders")]
        gfs.api.assert_has_calls(expected)

    async def test_list(self, gfs: GroupFolders, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200, json=LIST_RESPONSE, url=f"{ENDPOINT}{_STUB}?format=json", method="GET"
        )
        folders = await gfs.list()
        for folder in folders:
            assert isinstance(folder, GroupFolder)
        httpx_mock.assert_all_responses_sent()

    async def test_create(self, gfs: GroupFolders, httpx_mock: HTTPXMock):
        _folder = sha1().hexdigest()
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}",
            match_json={"mountpoint": _folder, "format": "json"},
            method="POST",
        )
        await gfs.create(_folder)
        httpx_mock.assert_all_responses_sent()

    async def test_get(self, gfs: GroupFolders, httpx_mock: HTTPXMock):
        folder_id = GET_RESPONSE["ocs"]["data"]["id"]
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{folder_id}?format=json",
            method="GET",
        )
        folder = await gfs.get(folder_id)
        assert isinstance(folder, GroupFolder)
        httpx_mock.assert_all_responses_sent()


@pytest.fixture(name="gf")
def _groupfolder(gfs: GroupFolders):
    return GroupFolder(GET_RESPONSE["ocs"]["data"], gfs)


@pytest.fixture(name="group")
def _group(asyncmock: AsyncMock):
    return Group({"id": "TestGroup"}, asyncmock)


@pytest.fixture(name="user")
def _user(asyncmock: AsyncMock):
    return User({"id": "TestUser"}, asyncmock)


@pytest.mark.asyncio
class TestGroupFolderObjectLegacy:
    async def test_delete(self, gf: GroupFolder, httpx_mock: HTTPXMock):
        folder_id = GET_RESPONSE["ocs"]["data"]["id"]
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{folder_id}",
            match_json={"format": "json"},
            method="DELETE",
        )
        await gf.delete()
        httpx_mock.assert_all_responses_sent()

    async def test_permit_group(
        self, gf: GroupFolder, group: Group, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/groups",
            match_json={"group": group.id, "format": "json"},
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.permit_group(group)
        httpx_mock.assert_all_responses_sent()

    async def test_deny_group(self, gf: GroupFolder, group: Group, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/groups/{group.id}",
            match_json={"format": "json"},
            method="DELETE",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.deny_group(group)
        httpx_mock.assert_all_responses_sent()

    async def test_enable_advanced_permissions(
        self, gf: GroupFolder, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/acl",
            match_json={"acl": 1, "format": "json"},
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.enable_advanced_permissions()
        httpx_mock.assert_all_responses_sent()

    async def test_disable_advanced_permissions(
        self, gf: GroupFolder, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/acl",
            match_json={"acl": 0, "format": "json"},
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.disable_advanced_permissions()
        httpx_mock.assert_all_responses_sent()

    async def test_add_acl_manager_user(
        self, gf: GroupFolder, user: User, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/manageACL",
            match_json={
                "mappingId": user.id,
                "mappingType": AclManagerType.user.value,
                "manageAcl": True,
                "format": "json",
            },
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.add_acl_manager(user)
        httpx_mock.assert_all_responses_sent()

    async def test_add_acl_manager_group(
        self, gf: GroupFolder, group: Group, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/manageACL",
            match_json={
                "mappingId": group.id,
                "mappingType": AclManagerType.group.value,
                "manageAcl": True,
                "format": "json",
            },
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.add_acl_manager(group)
        httpx_mock.assert_all_responses_sent()

    async def test_remove_acl_manager_user(
        self, gf: GroupFolder, user: User, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/manageACL",
            match_json={
                "mappingId": user.id,
                "mappingType": AclManagerType.user.value,
                "manageAcl": False,
                "format": "json",
            },
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.remove_acl_manager(user)
        httpx_mock.assert_all_responses_sent()

    async def test_remove_acl_manager_group(
        self, gf: GroupFolder, group: Group, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/manageACL",
            match_json={
                "mappingId": group.id,
                "mappingType": AclManagerType.group.value,
                "manageAcl": False,
                "format": "json",
            },
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.remove_acl_manager(group)
        httpx_mock.assert_all_responses_sent()

    async def test_set_acl(self, gf: GroupFolder, group: Group, httpx_mock: HTTPXMock):
        permissions = GroupFoldersPermissions.read | GroupFoldersPermissions.write
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/groups/{group.id}",
            match_json={
                "permissions": permissions.value,
                "format": "json",
            },
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.set_acl(group, permissions)
        httpx_mock.assert_all_responses_sent()

    async def test_set_quota(self, gf: GroupFolder, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/quota",
            match_json={
                "quota": 1000,
                "format": "json",
            },
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.set_quota(1000)
        httpx_mock.assert_all_responses_sent()

    async def test_set_quota_unlimited(self, gf: GroupFolder, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200, json=CAPABILITIES_RESPONSE, url=CAPABILITIES_URL, method="GET"
        )
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/quota",
            match_json={
                "quota": -3,  # Magic value for "unlimited" :/
                "format": "json",
            },
            method="POST",
        )
        httpx_mock.add_response(
            200,
            json=GET_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}?format=json",
            method="GET",
        )
        await gf.set_quota(None)
        httpx_mock.assert_all_responses_sent()

    async def test_rename(self, gf: GroupFolder, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200,
            json=_LEGACY_SUCCESS_RESPONSE,
            url=f"{ENDPOINT}{_STUB}/{gf.id}/mountpoint",
            match_json={
                "mountpoint": "/NewMountPoint",
                "format": "json",
            },
            method="POST",
        )
        await gf.rename("/NewMountPoint")
        httpx_mock.assert_all_responses_sent()
