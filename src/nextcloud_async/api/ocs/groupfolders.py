"""Implement Nextcloud Group Folders Interaction.

https://github.com/nextcloud/groupfolders#api
https://github.com/nextcloud/groupfolders/blob/master/openapi.json
"""

import logging
from enum import Enum, IntFlag
from typing import Awaitable

from semver import Version

from nextcloud_async.api.mixins import NextcloudDataObject
from nextcloud_async.api.modules import NextcloudModule, password_confirmation_required
from nextcloud_async.api.ocs.groups import Group
from nextcloud_async.api.ocs.users import User
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsDriver

log = logging.getLogger("nextcloud_async.api")


class GroupFoldersPermissions(IntFlag):
    """Groupfolders Permissions."""

    none = 0
    read = 1
    write = 2
    # create = 4  # Seemingly noop.  # noqa: ERA001
    delete = 8
    share = 16
    all = 31


class AclManagerType(Enum):
    user = "user"
    group = "group"


class GroupFolder(NextcloudDataObject):
    self_api: "GroupFoldersApi"

    def __str__(self) -> str:
        return f'<GroupFolder "{self.mount_point}">'

    def __eq__(self, other: "GroupFolder") -> bool:
        return self.mount_point == other.mount_point

    async def _changes_require_refresh(self) -> bool:
        """Whether or not object needs to be refreshed after changes.

        GroupFolders after commit 69200078 returns the changed folder with the
        response so we don't have to manually pull it again.

        https://github.com/nextcloud/groupfolders/commit/6920007850f430db4798993507b02950e45bac9d

        Returns:
            True or False

        """
        min_version = Version.parse("999.0.0")  # TODO: Update when commit released
        version = Version.parse(
            await self.self_api.api.get_capability("groupfolders.appVersion")
        )
        if version >= min_version:
            return False
        return True

    def refresh_function(self) -> Awaitable:
        """Define how to refresh this object."""
        log.debug("Providing refreshed object.")
        return self.self_api.get(self.id)

    async def delete(self) -> None:
        """Delete this group folder."""
        await self.self_api.delete(self.id)
        self.data = {"id": self.id, "mount_point": "**deleted**"}

    async def permit_group(self, group: Group) -> None:
        """Give `group_id` access to this folder.

        Args:
            group: Group object

        """
        await self.self_api.permit_group(folder_id=self.id, group_id=group.id)
        if await self._changes_require_refresh():
            await self._refresh()

    async def deny_group(self, group: Group) -> None:
        """Remove `group_id` access fom this group.

        Args:
            group: Group object

        """
        await self.self_api.deny_group(folder_id=self.id, group_id=group.id)
        if await self._changes_require_refresh():
            await self._refresh()

    async def enable_advanced_permissions(self) -> None:
        """Enable advanced permissions."""
        await self.self_api.enable_advanced_permissions(folder_id=self.id)
        if await self._changes_require_refresh():
            await self._refresh()

    async def disable_advanced_permissions(self) -> None:
        """Disable advanced permissios."""
        await self.self_api.disable_advanced_permissions(folder_id=self.id)
        if await self._changes_require_refresh():
            await self._refresh()

    async def add_acl_manager(self, object: Group | User) -> None:
        """Enable `object_id` as manager of advanced permissions.

        Args:
            object: User or Group object

        """
        if isinstance(object, User):
            object_type = AclManagerType.user
        elif isinstance(object, Group):
            object_type = AclManagerType.group

        await self.self_api.add_acl_manager(
            folder_id=self.id, object_id=object.id, object_type=object_type
        )
        if await self._changes_require_refresh():
            await self._refresh()

    async def remove_acl_manager(self, object: User | Group) -> None:
        """Disable `object_id` as manager of advanced permissions.

        Args:
            object: Object to remove from advanced permissions.

        """
        if isinstance(object, User):
            object_type = AclManagerType.user
        elif isinstance(object, Group):
            object_type = AclManagerType.group

        await self.self_api.remove_acl_manager(
            folder_id=self.id, object_id=object.id, object_type=object_type
        )
        if await self._changes_require_refresh():
            await self._refresh()

    async def set_acl(self, group: Group, permissions: GroupFoldersPermissions) -> None:
        """Set permissions a group has in this folder.

        Args:
            group: Group object

            permissions: New permissions.

        """
        await self.self_api.set_acl(
            folder_id=self.id, group_id=group.id, permissions=permissions
        )
        if await self._changes_require_refresh():
            await self._refresh()

    async def set_quota(self, quota: int | None) -> None:
        """Set quota for group folder.

        Args:
            quota: Quota in bytes.  None for unlimited.

        """
        await self.self_api.set_quota(self.id, quota)
        if await self._changes_require_refresh():
            await self._refresh()

    async def rename(self, mount_point: str) -> None:
        """Rename a group folder.

        Args:
            folder_id: Folder ID

            mount_point: New mount point.

        """
        await self.self_api.rename(self.id, mount_point=mount_point)
        self.mount_point = mount_point


class GroupFoldersApi(NextcloudModule):
    """Manage Group Folders.

    Requires capability: groupfolders
    """

    api: NextcloudOcsDriver

    def __init__(self, ocs_api: NextcloudOcsDriver) -> None:
        self.stub = "/apps/groupfolders/folders"
        self.api = ocs_api

    async def _validate_capability(self) -> None:
        await self.api.require_capability("groupfolders")

    async def list(self) -> list[GroupFolder]:
        """Get list of all group folders.

        Returns:
            List of group folders.

        """
        await self._validate_capability()
        response = await self._get()
        if not response:
            return []
        return [GroupFolder(value, self) for _, value in response.items()]

    @password_confirmation_required
    async def create(self, path: str) -> GroupFolder:
        """Create new group folder.

        Args:
            path: Path of new group folder.

        Returns:
            New GroupFolder object

        """
        await self._validate_capability()
        response = await self._post(data={"mountpoint": path})
        return GroupFolder(response, self)

    async def get(self, folder_id: int) -> GroupFolder:
        """Get group folder with id `folder_id`.

        Args:
            folder_id (int): Group folder ID

        Returns:
            Groupfolder

        """
        await self._validate_capability()
        response = await self._get(path=f"/{folder_id}")
        return GroupFolder(response, self)

    @password_confirmation_required
    async def delete(self, folder_id: int) -> None:
        """Delete group folder with id `folder_id`.

        Args:
            folder_id (int): Group folder ID

        Returns:
            bool: success(True) or failure(False)

        """
        await self._validate_capability()
        await self._delete(path=f"/{folder_id}")

    @password_confirmation_required
    async def permit_group(self, group_id: str, folder_id: int) -> None:
        """Give `group_id` access to `folder_id`.

        Args:
            group_id: Group ID

            folder_id: Folder ID

        """
        await self._validate_capability()
        await self._post(path=f"/{folder_id}/groups", data={"group": group_id})

    @password_confirmation_required
    async def deny_group(self, group_id: str, folder_id: int) -> None:
        """Remove `group_id` access from `folder_id`.

        Args:
            group_id: Group ID

            folder_id: Folder ID

        """
        await self._validate_capability()
        await self._delete(path=f"/{folder_id}/groups/{group_id}")

    @password_confirmation_required
    async def enable_advanced_permissions(self, folder_id: int) -> None:
        """Enable advanced permissions on `folder_id`.

        Args:
            folder_id: Folder ID

        Returns:
            bool: success(True) or failure(False)

        """
        await self._validate_capability()
        await self._advanced_permissions(folder_id, True)

    @password_confirmation_required
    async def disable_advanced_permissions(self, folder_id: int) -> None:
        """Disable advanced permissions on `folder_id`.

        Args:
            folder_id: Folder ID

        """
        await self._validate_capability()
        await self._advanced_permissions(folder_id, False)

    async def _advanced_permissions(self, folder_id: int, enable: bool) -> None:
        await self._post(path=f"/{folder_id}/acl", data={"acl": 1 if enable else 0})

    @password_confirmation_required
    async def add_acl_manager(
        self, folder_id: int, object_id: str, object_type: AclManagerType
    ) -> None:
        """Enable `object_id` as manager of advanced permissions.

        Args:
            folder_id: Folder ID

            object_id: Object ID

            object_type: either `user` or `group`

        """
        await self._validate_capability()
        await self._advanced_permissions_admin(
            folder_id,
            object_id=object_id,
            object_type=object_type.value,
            manage_acl=True,
        )

    @password_confirmation_required
    async def remove_acl_manager(
        self, folder_id: int, object_id: str, object_type: AclManagerType
    ) -> None:
        """Disable `object_id` as manager of advanced permissions.

        Args:
            folder_id: Folder ID

            object_id: Object ID

            object_type: AclManagerType

        """
        await self._validate_capability()
        await self._advanced_permissions_admin(
            folder_id,
            object_id=object_id,
            object_type=object_type.value,
            manage_acl=False,
        )

    async def _advanced_permissions_admin(
        self, folder_id: int, object_id: str, object_type: str, manage_acl: bool
    ) -> bool:
        response = await self._post(
            path=f"/{folder_id}/manageACL",
            data={
                "mappingId": object_id,
                "mappingType": object_type,
                "manageAcl": manage_acl,
            },
        )

        return response["success"]

    @password_confirmation_required
    async def set_acl(
        self, folder_id: int, group_id: str, permissions: GroupFoldersPermissions
    ) -> bool:
        """Set permissions a group has in a folder.

        Args:
            folder_id: Folder ID

            group_id: Group ID

            permissions: New permissions.

        """
        await self._validate_capability()
        response = await self._post(
            path=f"/{folder_id}/groups/{group_id}",
            data={"permissions": permissions.value},
        )
        return response["success"]

    @password_confirmation_required
    async def set_quota(self, folder_id: int, quota: int | None) -> None:
        """Set quota for group folder.

        Args:
            folder_id : Folder ID

            quota: Quota in bytes.  None for unlimited.

        """
        await self._validate_capability()
        await self._post(
            path=f"/{folder_id}/quota", data={"quota": quota if quota else -3}
        )

    async def rename(self, folder_id: int, mount_point: str) -> None:
        """Rename a group folder.

        Args:
            folder_id: Folder ID

            mount_point: New mount point.

        """
        await self._validate_capability()
        await self._post(
            path=f"/{folder_id}/mountpoint", data={"mountpoint": mount_point}
        )


def groupfolders_api(client: NextcloudClient) -> GroupFoldersApi:
    """GroupFoldersApi Factory."""
    ocs_api = NextcloudOcsDriver(client, stub="/index.php")
    return GroupFoldersApi(ocs_api)
