import pytest
import pytest_asyncio

import logging

from nextcloud_async.api import Group, GroupsApi, User, UsersApi
from nextcloud_async.exceptions import NextcloudError

log = logging.getLogger("nextcloud_async.tests.integration")

_TEST_GROUP = "PytestGroup"

_USER_DATA = {
    "user_id": "PytestUser",
    "display_name": "Pyest User Guy",
    "email": "pytestguy@example.com",
    "language": "en",
    "subadmin": [_TEST_GROUP],
    "groups": [_TEST_GROUP],
    "quota": None,
    "password": "FlibbyMcGiblets",
}


_INSTANTIATED_USER = {
    "enabled": True,
    "storageLocation": "/var/www/html/data/PytestUser",
    "id": "PytestUser",
    "lastLogin": 0,
    "backend": "Database",
    "subadmin": ["PytestGroup"],
    "quota": {"quota": "none", "used": 0},
    "manager": "",
    "email": "pytestguy@example.com",
    "additional_mail": [],
    "displayname": "Pyest User Guy",
    "display-name": "Pyest User Guy",
    "phone": "",
    "address": "",
    "website": "",
    "twitter": "",
    "fediverse": "",
    "organisation": "",
    "role": "",
    "headline": "",
    "biography": "",
    "profile_enabled": "1",
    "groups": ["PytestGroup"],
    "language": "en",
    "locale": "",
    "notify_email": None,
    "backendCapabilities": {"setDisplayName": True, "setPassword": True},
}


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_group(groups_api: GroupsApi):
    group = await groups_api.create(_TEST_GROUP)
    yield group
    await group.delete()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def target_group(groups_api: GroupsApi):
    group = await groups_api.create("TargetGroup")
    yield group
    await group.delete()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_user(users_api: UsersApi, test_group: Group):
    # test_group is not used here, but must exist to create the user
    assert test_group

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
    async def test_update(self, test_user: User):
        _updated_user_data = {
            "displayname": "New Display Name",
            "email": "newemail@example.com",
        }
        await test_user.update(_updated_user_data)
        assert test_user.email == _updated_user_data["email"]
        assert test_user.display_name == _updated_user_data["displayname"]

    async def test_disable_enable(self, test_user: User):
        await test_user.disable()
        assert test_user.enabled is False
        await test_user.enable()
        assert test_user.enabled is True

    async def test_delete(self, users_api: UsersApi, test_user: User):
        _id = test_user.id
        await test_user.delete()
        assert test_user.id == "**deleted**"
        with pytest.raises(NextcloudError) as e:
            await users_api.get(_id)
        assert e.value.reason == "User does not exist"

    async def test_get_groups(self, test_user: User, test_group: Group):
        groups = await test_user.get_groups()
        assert test_group in groups

    async def test_add_to_group(self, test_user: User, target_group: Group):
        await test_user.add_to_group(target_group)
        assert target_group.id in test_user.groups
        await target_group.delete()

    async def test_remove_from_group(self, test_user: User, test_group: Group):
        assert test_group.id in test_user.groups
        await test_user.remove_from_group(test_group)
        assert test_group.id not in test_user.groups

    async def test_promotion_demotion(self, test_user: User, target_group: Group):
        await test_user.promote_to_group_subadmin(target_group)
        assert target_group.id in test_user.subadmin
        await test_user.demote_from_group_subadmin(target_group)
        assert target_group.id not in test_user.subadmin

    async def test_get_subadmin_groups(self, test_user: User, test_group: Group):
        groups = await test_user.get_subadmin_groups()
        assert test_group in groups

    async def test_dunders(self, test_user: User):
        assert "Nextcloud User" in str(test_user)
        assert test_user == test_user  # noqa: PLR0124


@pytest.mark.integration
@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestUsersApi:
    async def test_create(self, test_user: User, test_group: Group):
        assert test_user.id == _USER_DATA["user_id"]
        assert test_user.display_name == _USER_DATA["display_name"]
        assert test_user.email == _USER_DATA["email"]
        assert test_group.id in test_user.subadmin
        assert test_group.id in test_user["groups"]
        assert test_user.quota["quota"] == "none"

    async def test_get_editable_fields(self, users_api: UsersApi):
        fields = await users_api.get_editable_fields()
        assert isinstance(fields, list)

    async def test_resend_email(self, users_api: UsersApi, test_user: User):
        await users_api.resend_welcome_email(test_user.id)
