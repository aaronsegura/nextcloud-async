import copy
from hashlib import sha1
from unittest.mock import AsyncMock, call

import pytest
from pytest_httpx import HTTPXMock

from nextcloud_async.api import (
    AclManagerType,
    Group,
    GroupFolder,
    GroupFoldersApi,
    GroupFoldersPermissions,
    GroupsApi,
    User,
)
from nextcloud_async.client.client import NextcloudClient

from .constants import (
    CAPABILITIES_RESPONSE,
    CAPABILITIES_URL,
    ENDPOINT,
    OCS_EMPTY_200,
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


class GroupFoldersMock(GroupFoldersApi):
    api: AsyncMock


class GroupFolderMock(GroupFolder):
    self_api: GroupFoldersMock


@pytest.fixture(name="gfs")
def _groupfolders(
    nc_basic_mocked: NextcloudClient, asyncmock: AsyncMock
) -> GroupFoldersMock:
    gfs = GroupFoldersMock(nc_basic_mocked)
    gfs.api = asyncmock
    return gfs


_STUB = "/index.php/apps/groupfolders/folders"


@pytest.mark.asyncio
class TestGroupFoldersApi:
    async def test_validate_capability(self, gfs: GroupFoldersMock):
        await gfs._validate_capability()
        expected = [call.require_capability("groupfolders")]
        gfs.api.assert_has_calls(expected)

    async def test_list(self, gfs: GroupFoldersMock):
        gfs.api.get.return_value = LIST_RESPONSE["ocs"]["data"]
        await gfs.list()
        expected = [
            call.require_capability("groupfolders"),
            call.get(path="/apps/groupfolders/folders", data=None, headers=None),
        ]
        gfs.api.assert_has_calls(expected)

    async def test_create(self, gfs: GroupFoldersMock):
        _folder = sha1().hexdigest()
        await gfs.create(_folder)
        expected = [
            call.require_capability("groupfolders"),
            call.post(
                path="/apps/groupfolders/folders",
                data={"mountpoint": _folder},
                headers=None,
            ),
        ]
        gfs.api.assert_has_calls(expected)

    async def test_get(self, gfs: GroupFoldersMock):
        folder_id = GET_RESPONSE["ocs"]["data"]["id"]
        folder = await gfs.get(folder_id)
        expected = [
            call.require_capability("groupfolders"),
            call.get(
                path=f"/apps/groupfolders/folders/{folder_id}", data=None, headers=None
            ),
        ]
        gfs.api.assert_has_calls(expected)
        assert isinstance(folder, GroupFolder)


@pytest.fixture(name="gf_old")
def _groupfolder(gfs: GroupFoldersMock):
    gf = GroupFolderMock(GET_RESPONSE["ocs"]["data"], gfs)
    gf._changes_require_refresh = AsyncMock(return_value=True)
    return gf


@pytest.fixture(name="group")
def _group(magicmock, nc_basic_mocked):
    group = Group({"id": "TestGroup"}, GroupsApi(nc_basic_mocked))
    return group


@pytest.fixture(name="user")
def _user(gfs: GroupFoldersMock):
    return User({"id": "TestUser"}, gfs)


@pytest.mark.asyncio
class TestGroupFolderObjectWithRefresh:
    async def test_delete(self, gf: GroupFolderMock):
        folder_id = GET_RESPONSE["ocs"]["data"]["id"]
        await gf.delete()
        expected = [
            call.require_capability("groupfolders"),
            call.delete(
                path=f"/apps/groupfolders/folders/{folder_id}", data=None, headers=None
            ),
        ]
        gf.self_api.api.assert_has_calls(expected)

    async def test_permit_group(self, gf_old: GroupFolderMock, group: Group):
        await gf_old.permit_group(group)
        expected = [
            call.require_capability("groupfolders"),
            call.post(
                path=f"/apps/groupfolders/folders/{gf_old.id}/groups",
                data={"group": group.id},
                headers=None,
            ),
            call.require_capability("groupfolders"),
            call.get(
                path=f"/apps/groupfolders/folders/{gf_old.id}", data=None, headers=None
            ),
        ]
        gf_old.self_api.api.assert_has_calls(expected)
        gf_old._changes_require_refresh.assert_has_calls([call()])

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
