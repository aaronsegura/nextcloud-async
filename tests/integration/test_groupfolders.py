import pytest
import pytest_asyncio

import logging
from collections.abc import AsyncGenerator

from nextcloud_async.api import (
    Group,
    GroupFolder,
    GroupFoldersApi,
    GroupFoldersPermissions,
    GroupsApi,
)
from nextcloud_async.exceptions import (
    NextcloudGenericServerError,
    NextcloudNotFoundError,
)

from .constants import REMOTE_BASE_DIR

log = logging.getLogger("nextcloud_async")


@pytest.fixture
def test_id(request: pytest.FixtureRequest) -> str:
    return request.node.callspec.id


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def group_folders(
    gf_api: GroupFoldersApi,
    remote_test_dir: str,
    test_id: str,
) -> AsyncGenerator[list[GroupFolder], None]:
    ret: list[GroupFolder] = []

    for i in range(0, 3):
        folder = await gf_api.create(f"{remote_test_dir}/groupfolder_{test_id}_{i}")
        ret.append(folder)

    yield ret

    for gf in ret:
        try:
            await gf.delete()
        except (NextcloudGenericServerError, NextcloudNotFoundError):
            pass


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_group(groups_api: GroupsApi, test_id: str) -> AsyncGenerator[Group, None]:
    group_id = f"groupfolders_test_{test_id}"
    group = await groups_api.create(group_id)

    yield group

    await group.delete()


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestGroupFoldersApi:
    async def test_create(self, group_folders: list[GroupFolder]):
        for folder in group_folders:
            assert folder.mount_point.startswith(f"{REMOTE_BASE_DIR}")

    async def test_get_all(
        self, gf_api: GroupFoldersApi, group_folders: list[GroupFolder]
    ):
        folder = group_folders[0]
        folder_list = await gf_api.list()
        assert folder in folder_list

    async def test_get_group_folder(
        self, gf_api: GroupFolder, group_folders: list[GroupFolder]
    ):
        folder = group_folders[0]
        get_folder = await gf_api.get(folder.id)
        assert get_folder == folder

    async def test_remove_group_folder(
        self, gf_api: GroupFoldersApi, group_folders: list[GroupFolder]
    ):
        folder = group_folders[0]
        folder_id = folder.id
        await folder.delete()
        # Prior to groupfolders 19 this returns a 500 error, we catch
        # NextcloudGenericServerError.
        with pytest.raises((NextcloudNotFoundError, NextcloudGenericServerError)):
            await gf_api.get(folder_id)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestGroupFolder:
    async def test_toggle_group_member(
        self, group_folders: list[GroupFolder], test_group: Group
    ):
        log.debug(f"FOLDER {group_folders[1]}")
        folder = group_folders[1]
        await folder.permit_group(test_group)
        assert test_group.id in folder.group_details
        await folder.deny_group(test_group)
        assert test_group.id not in folder.group_details

    async def test_toggle_advanced_permissions(self, group_folders: list[GroupFolder]):
        folder = group_folders[1]
        await folder.enable_advanced_permissions()
        assert folder.acl is True
        await folder.disable_advanced_permissions()
        assert folder.acl is False

    async def test_add_group_folder_advanced_permissions(
        self, group_folders: list[GroupFolder], test_group: Group
    ):
        folder = group_folders[1]
        await folder.enable_advanced_permissions()
        await folder.add_acl_manager(test_group)
        manage = {"type": "group", "id": test_group.id, "displayname": test_group.id}
        assert manage in folder.manage
        await folder.remove_acl_manager(test_group)
        assert manage not in folder.manage

    async def test_set_group_folder_permissions(
        self, group_folders: list[GroupFolder], test_group: Group
    ):
        folder = group_folders[1]
        await folder.enable_advanced_permissions()
        await folder.permit_group(test_group)
        await folder.set_acl(
            test_group, GroupFoldersPermissions.read | GroupFoldersPermissions.write
        )
        acl = {
            "displayName": test_group.id,
            "permissions": (
                GroupFoldersPermissions.read | GroupFoldersPermissions.write
            ).value,
            "type": "group",
        }
        assert test_group.id in folder.group_details
        assert folder.group_details[test_group.id] == acl

    async def test_set_group_folder_quota(self, group_folders: list[GroupFolder]):
        _some_quota = 5000
        _no_quota = -3
        folder = group_folders[1]
        await folder.set_quota(_some_quota)
        assert folder.quota == _some_quota
        await folder.set_quota(None)
        assert folder.quota == _no_quota

    async def test_rename_group_folder(
        self, remote_test_dir: str, group_folders: list[GroupFolder]
    ):
        folder = group_folders[2]
        new_name = f"{remote_test_dir}/SomeOtherFolder"
        await folder.rename(new_name)
        new_folder = await folder._api.get(folder.id)
        assert new_folder.mount_point == new_name
