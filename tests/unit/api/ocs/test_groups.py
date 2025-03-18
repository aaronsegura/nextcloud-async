from unittest.mock import AsyncMock, call

import pytest

from nextcloud_async import NextcloudClient
from nextcloud_async.api import Group, GroupsApi

SEARCH_RESPONSE = {
    "ocs": {
        "meta": {
            "status": "ok",
            "statuscode": 100,
            "message": "OK",
            "totalitems": "",
            "itemsperpage": "",
        },
        "data": {"groups": ["pytest_group_0"]},
    }
}

CREATE_RESPONSE = {
    "ocs": {
        "meta": {
            "status": "ok",
            "statuscode": 100,
            "message": "OK",
            "totalitems": "",
            "itemsperpage": "",
        },
        "data": [],
    }
}


@pytest.fixture(name="groups")
def _groups(nc_basic_mocked: NextcloudClient, asyncmock: AsyncMock):
    groups = GroupsApi(nc_basic_mocked)
    groups.api = asyncmock
    return groups


@pytest.fixture(name="group")
def _mocked_group(groups: GroupsApi):
    group = Group({"id": "TestGroup"}, groups)
    return group


@pytest.mark.asyncio
class TestGroupsApi:
    async def test_search(self, groups: GroupsApi, group: Group):
        await groups.search(group.id, limit=100, offset=0)
        expected = [
            call.get(
                path="/cloud/groups",
                data={"limit": 100, "offset": 0, "search": "TestGroup"},
                headers=None,
            ),
            call.get().__getitem__("groups"),
            call.get().__getitem__().__iter__(),
        ]
        groups.api.assert_has_calls(expected)

    async def test_create(self, groups: GroupsApi):
        new_group = await groups.create("TestGroup")
        expected = [
            call.post(path="/cloud/groups", data={"groupid": "TestGroup"}, headers=None)
        ]
        groups.api.assert_has_calls(expected)
        assert isinstance(new_group, Group)


@pytest.mark.asyncio
class TestGroupObject:
    async def test_get_members(self, group: Group):
        await group.get_members()
        expected = [
            call.get(path="/cloud/groups/TestGroup", data=None, headers=None),
            call.get().__getitem__("users"),
        ]
        group.self_api.api.assert_has_calls(expected)

    async def test_get_subadmin(self, group: Group):
        await group.get_subadmins()
        expected = [
            call.get(
                path="/cloud/groups/TestGroup/subadmins",
                data=None,
                headers=None,
            )
        ]
        group.self_api.api.assert_has_calls(expected)

    async def test_delete(self, group: Group):
        await group.delete()
        expected = [call.delete(path="/cloud/groups/TestGroup", data=None, headers=None)]
        group.self_api.api.assert_has_calls(expected)

    async def test_string(self, group: Group):
        assert str(group) == f'<Nextcloud Group "{group.id}">'
