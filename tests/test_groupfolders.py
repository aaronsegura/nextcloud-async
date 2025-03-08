import pytest
import pytest_asyncio

from typing import AsyncGenerator

from nextcloud_async import NextcloudClient
from nextcloud_async.api import (
    GroupFolders,
    Files,
    GroupFolder,
    Groups,
    Group,
    GroupFoldersPermissions,
)
from nextcloud_async.exceptions import (
    NextcloudError,
    NextcloudNotFoundError,
    NextcloudGenericServerError,
)

from .constants import REMOTE_TEST_DIR
from .helpers import create_clean_test_directory

# pytest.skip('test', allow_module_level=True)


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def test_directory(files_api: Files, network_blocked: bool) -> str:
    dir = f"{REMOTE_TEST_DIR}/groupfolders"
    if not network_blocked:
        await create_clean_test_directory(files_api, dir)
    return dir


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def group_folders(
    gf_api: GroupFolders,
    test_directory: str,
) -> AsyncGenerator[list[GroupFolder]]:
    ret: list[GroupFolder] = []

    for i in range(0, 3):
        folder = await gf_api.create(f"{test_directory}/groupfolder_{i}")
        ret.append(folder)

    yield ret

    for gf in ret:
        try:
            await gf.delete()
        except NextcloudNotFoundError:
            pass


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_group(
    groups_api: Groups, network_blocked: bool
) -> AsyncGenerator[Group]:
    group_id = "groupfolders_test"
    if network_blocked:
        group = Group({"id": group_id}, groups_api)
    else:
        group = await groups_api.create(group_id)

    yield group

    if not network_blocked:
        await group.delete()


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestGroupFolders:

    async def test_create(self, group_folders: list[GroupFolder]):
        for folder in group_folders:
            assert folder.mount_point.startswith(f"{REMOTE_TEST_DIR}/groupfolders")

    async def test_get_all(
        self, gf_api: GroupFolders, group_folders: list[GroupFolder]
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
        self, gf_api: GroupFolders, group_folders: list[GroupFolder]
    ):
        folder = group_folders[0]
        folder_id = folder.id
        await folder.delete()
        try:
            await gf_api.get(folder_id)
        except NextcloudNotFoundError:
            assert True
        except NextcloudError as e:
            # Prior to groupfolders commit 54022df a call to get a
            # non-existant folder would return a server 500 error.
            if e.status_code == NextcloudGenericServerError.status_code:
                assert True
        else:
            assert False

    async def test_toggle_group_member(
        self, group_folders: list[GroupFolder], test_group: Group
    ):
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
        await folder.add_advanced_permission(test_group)
        manage = {"type": "group", "id": test_group.id, "displayname": test_group.id}
        assert manage in folder.manage
        await folder.remove_advanced_permission(test_group)
        assert manage not in folder.manage

    async def test_set_group_folder_permissions(
        self, group_folders: list[GroupFolder], test_group: Group
    ):
        folder = group_folders[1]
        await folder.enable_advanced_permissions()
        await folder.permit_group(test_group)
        await folder.set_advanced_permissions(
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
        self, test_directory: str, group_folders: list[GroupFolder]
    ):
        folder = group_folders[2]
        new_name = f"{test_directory}/SomeOtherFolder"
        await folder.rename(new_name)
        new_folder = await folder.groupfolder_api.get(folder.id)
        assert new_folder.mount_point == new_name
