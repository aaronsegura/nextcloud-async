import pytest
import pytest_asyncio

import logging

from nextcloud_async.api import Group, GroupsApi, User, UsersApi
from nextcloud_async.exceptions import NextcloudError

log = logging.getLogger("nextcloud_async.tests.integration")

_nc_group = "PytestGroup"

_USER_DATA = {
    "user_id": "PytestUser",
    "display_name": "Pyest User Guy",
    "email": "pytestguy@example.com",
    "language": "en",
    "subadmin": [_nc_group],
    "groups": [_nc_group],
    "quota": None,
    "password": "FlibbyMcGiblets",
}


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def nc_group(groups_api: GroupsApi):
    group = await groups_api.create(_nc_group)
    yield group
    await group.delete()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def target_group(groups_api: GroupsApi):
    group = await groups_api.create("TargetGroup")
    yield group
    await group.delete()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def nc_user(users_api: UsersApi, nc_group: Group):
    # nc_group is not used here, but must exist to create the user
    assert nc_group

    user = await users_api.create(**_USER_DATA)

    yield user
    try:
        await user.delete()
    except NextcloudError:
        pass


@pytest.mark.integration
@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestUserDataObject:
    async def test_update(self, nc_user: User):
        _updated_user_data = {
            "displayname": "New Display Name",
            "email": "newemail@example.com",
        }
        await nc_user.update(_updated_user_data)
        assert nc_user.email == _updated_user_data["email"]
        assert nc_user.display_name == _updated_user_data["displayname"]

    async def test_disable_enable(self, nc_user: User):
        await nc_user.disable()
        assert nc_user.enabled is False
        await nc_user.enable()
        assert nc_user.enabled is True

    async def test_delete(self, users_api: UsersApi, nc_user: User):
        _id = nc_user.id
        await nc_user.delete()
        assert nc_user.id == "**deleted**"
        with pytest.raises(NextcloudError) as e:
            await users_api.get(_id)
        assert e.value.reason == "User does not exist"

    async def test_get_groups(self, nc_user: User, nc_group: Group):
        groups = await nc_user.get_groups()
        assert nc_group in groups

    async def test_add_to_group(self, nc_user: User, target_group: Group):
        await nc_user.add_to_group(target_group)
        assert target_group.id in nc_user.groups
        await target_group.delete()

    async def test_remove_from_group(self, nc_user: User, nc_group: Group):
        assert nc_group.id in nc_user.groups
        await nc_user.remove_from_group(nc_group)
        assert nc_group.id not in nc_user.groups

    async def test_promotion_demotion(self, nc_user: User, target_group: Group):
        await nc_user.promote_to_group_subadmin(target_group)
        assert target_group.id in nc_user.subadmin
        await nc_user.demote_from_group_subadmin(target_group)
        assert target_group.id not in nc_user.subadmin

    async def test_get_subadmin_groups(self, nc_user: User, nc_group: Group):
        groups = await nc_user.get_subadmin_groups()
        assert nc_group in groups

    async def test_dunders(self, nc_user: User):
        assert "Nextcloud User" in str(nc_user)
        assert nc_user == nc_user  # noqa: PLR0124


@pytest.mark.integration
@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestUsersApi:
    async def test_create(self, nc_user: User, nc_group: Group):
        assert nc_user.id == _USER_DATA["user_id"]
        assert nc_user.display_name == _USER_DATA["display_name"]
        assert nc_user.email == _USER_DATA["email"]
        assert nc_group.id in nc_user.subadmin
        assert nc_group.id in nc_user["groups"]
        assert nc_user.quota["quota"] == "none"

    async def test_get_editable_fields(self, users_api: UsersApi):
        fields = await users_api.get_editable_fields()
        assert isinstance(fields, list)

    async def test_resend_email(self, users_api: UsersApi, nc_user: User):
        await users_api.resend_welcome_email(nc_user.id)
