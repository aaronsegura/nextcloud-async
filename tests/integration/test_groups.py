import pytest
import pytest_asyncio

from collections.abc import AsyncGenerator

from nextcloud_async.api import Group, GroupsApi, User, UsersApi

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
async def test_groups(groups_api: GroupsApi) -> AsyncGenerator[list[Group], None]:
    ret: list[Group] = []

    for i in range(0, 2):
        group_name = f"{_TEST_GROUP_NAME}_{i}"
        test_group = await groups_api.create(group_name)
        ret.append(test_group)

    yield ret

    for i in range(0, 2):
        test_group = await groups_api.delete(f"{_TEST_GROUP_NAME}_{i}")


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_user(users_api: UsersApi) -> AsyncGenerator[User]:
    test_user = await users_api.create(**_TEST_USER)
    yield test_user
    await test_user.delete()


@pytest.mark.integration
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
