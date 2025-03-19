import pytest
import pytest_asyncio

from typing import AsyncGenerator

from nextcloud_async.api import Group, GroupsApi, User, UsersApi
from nextcloud_async.exceptions import NextcloudForbiddenError

_TEST_GROUP_NAME = "pytest_group"
_TEST_USER = {
    "user_id": "pytest_user",
    "display_name": "Pytest User Guy",
    "email": "pytest@example.com",
    "quota": None,
    "password": "MyCoolPassword",
    "language": "en",
}


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_groups(
    network_blocked: bool, groups_api: GroupsApi
) -> AsyncGenerator[list[Group]]:
    ret: list[Group] = []

    for i in range(0, 2):
        group_name = f"{_TEST_GROUP_NAME}_{i}"
        if network_blocked:
            test_group = Group({"id": group_name}, groups_api)
        else:
            test_group = await groups_api.create(group_name)
        ret.append(test_group)

    yield ret

    for i in range(0, 2):
        if not network_blocked:
            try:
                test_group = await groups_api.delete(f"{_TEST_GROUP_NAME}_{i}")
            except NextcloudForbiddenError:
                pass


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_user(network_blocked: bool, users_api: UsersApi) -> AsyncGenerator[User]:
    if network_blocked:
        _TEST_USER.update({"id": _TEST_USER["user_id"]})
        test_user = User(_TEST_USER, users_api)
    else:
        test_user = await users_api.create(**_TEST_USER)

    yield test_user
    if not network_blocked:
        await test_user.delete()


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestGroups:
    async def test_search_groups(self, groups_api: GroupsApi, test_groups: list[Group]):
        group = test_groups[0]
        groups = await groups_api.search(group.id)
        assert len(groups) == 1

    async def test_create_group(self, test_groups: list[Group]):
        group = test_groups[0]
        assert isinstance(group, Group)
        assert group.id == f"{_TEST_GROUP_NAME}_0"

    async def test_set_get_group_members(self, test_groups: list[Group], test_user: User):
        group = test_groups[0]
        await test_user.add_to_group(group)
        members = await group.get_members()
        assert test_user.id in members

    async def test_set_get_group_subadmins(
        self, test_groups: list[Group], test_user: User
    ):
        group = test_groups[0]
        await test_user.promote_to_group_subadmin(group)
        subadmins = await group.get_subadmins()
        assert test_user.id in subadmins

    async def test_remove_group(self, groups_api: GroupsApi, test_groups: list[Group]):
        group = test_groups[1]
        id = group.id
        await group.delete()
        response = await groups_api.search(id)
        assert response == []
