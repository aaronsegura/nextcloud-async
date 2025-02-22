"""Implement Nextcloud Group Folders Interaction.

https://github.com/nextcloud/groupfolders#api
https://github.com/nextcloud/groupfolders/blob/master/openapi.json
"""

from enum import IntFlag, Enum
from dataclasses import dataclass

from typing import List, Dict, Any, Optional

from nextcloud_async.driver import NextcloudOcsApi, NextcloudModule
from nextcloud_async.client import NextcloudClient

class Permissions(IntFlag):
    """Groupfolders Permissions."""

    read = 1
    update = 2
    create = 4
    delete = 8
    share = 16
    all = 31


class AclManagerType(Enum):
    user = 'user'
    group = 'group'


@dataclass
class GroupFolder:
    data: Dict[str, Any]
    groupfolder_api: 'GroupFolders'

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<GroupFolder "{self.mount_point}">'

    def __repr__(self) -> str:
        return str(self.data)

    async def delete(self) -> None:
        """Delete this group folder."""
        await self.groupfolder_api.delete(self.id)
        self.data = {'mount_point': '**deleted**'}

    async def permit_group(self, group_id: str) -> None:
        """Give `group_id` access to this folder.

        Args:
            group_id: Group ID
        """
        await self.groupfolder_api.permit_group(
            folder_id=self.id,
            group_id=group_id)

    async def deny_group(self, group_id: str) -> None:
        """Remove `group_id` access from this group.

        Args:
            group_id: Group ID
        """
        await self.groupfolder_api.deny_group(folder_id=self.id, group_id=group_id)

    async def enable_advanced_permissions(self) -> None:
        """Enable advanced permissions."""
        return await self.groupfolder_api.enable_advanced_permissions(folder_id=self.id)

    async def disable_advanced_permissions(self) -> None:
        """Disable advanced permissios."""
        return await self.groupfolder_api.disable_advanced_permissions(folder_id=self.id)

    async def add_advanced_permission(
            self,
            object_id: str,
            object_type: AclManagerType) -> None:
        """Enable `object_id` as manager of advanced permissions.

        Args:
            object_id: Object ID

            object_type: AclManagerType
        """
        return await self.groupfolder_api.add_advanced_permissions(
            folder_id=self.id,
            object_id=object_id,
            object_type=object_type)

    async def remove_advanced_permission(
            self,
            object_id: str,
            object_type: AclManagerType) -> None:
        """Disable `object_id` as manager of advanced permissions.

        Args:
            object_id: Object ID

            object_type: AclManagerType
        """
        return await self.groupfolder_api.remove_advanced_permissions(
            folder_id=self.id,
            object_id=object_id,
            object_type=object_type)

    async def set_permissions(self, group_id: str, permissions: Permissions) -> None:
        """Set permissions a group has in this folder.

        Args:
            group_id: Group ID

            permissions: New permissions.
        """
        await self.groupfolder_api.set_permissions(
            folder_id=self.id,
            group_id=group_id,
            permissions=permissions)

    async def set_quota(self, quota: Optional[int]) -> None:
        """Set quota for group folder.

        Args:
            quota: Quota in bytes.  None for unlimited.
        """
        await self.groupfolder_api.set_quota(self.id, quota)

    async def rename(self, mount_point: str) -> None:
        """Rename a group folder.

        Args:
            folder_id: Folder ID

            mount_point: New mount point.
        """
        await self.groupfolder_api.rename(self.id, mount_point=mount_point)
        self.mount_point = mount_point


class GroupFolders(NextcloudModule):
    """Manage Group Folders.

    Requires capability: groupfolders
    """

    api: NextcloudOcsApi

    def __init__(
            self,
            client: NextcloudClient) -> None:
        self.stub = '/apps/groupfolders/folders'
        self.api = NextcloudOcsApi(client, ocs_stub='/index.php')

    async def _validate_capability(self) -> None:
        await self.api.require_capability('groupfolders')

    # TODO: Fix when no groupfolders
    async def list(self) -> List[GroupFolder]:
        """Get list of all group folders.

        Returns:
            List of group folders.
        """
        await self._validate_capability()
        response = await self._get()
        return [GroupFolder(value, self) for _, value in response.items()]

    async def add(self, path: str) -> GroupFolder:
        """Create new group folder.

        Args:
            path: Path of new group folder.

        Returns:
            New GroupFolder object
        """
        await self._validate_capability()
        response = await self._post(data={'mountpoint': path})
        return GroupFolder(response, self)

    async def get(self, folder_id: int) -> GroupFolder:
        """Get group folder with id `folder_id`.

        Args:
            folder_id (int): Group folder ID

        Returns:
            Groupfolder
        """
        await self._validate_capability()
        response = await self._get(path=f'/{folder_id}')
        return GroupFolder(response, self)

    async def delete(self, folder_id: int) -> None:
        """Delete group folder with id `folder_id`.

        Args:
            folder_id (int): Group folder ID

        Returns:
            bool: success(True) or failure(False)
        """
        await self._validate_capability()
        await self._delete(path=f'/{folder_id}')

    async def permit_group(self, group_id: str, folder_id: int) -> None:
        """Give `group_id` access to `folder_id`.

        Args:
            group_id: Group ID

            folder_id: Folder ID
        """
        await self._validate_capability()
        await self._post(path=f'/{folder_id}/groups', data={'group': group_id})

    async def deny_group(self, group_id: str, folder_id: int) -> None:
        """Remove `group_id` access from `folder_id`.

        Args:
            group_id: Group ID

            folder_id: Folder ID
        """
        await self._validate_capability()
        await self._delete(
            path=f'/apps/groupfolders/folders/{folder_id}/groups/{group_id}')

    async def enable_advanced_permissions(self, folder_id: int) -> None:
        """Enable advanced permissions on `folder_id`.

        Args:
            folder_id: Folder ID

        Returns:
            bool: success(True) or failure(False)
        """
        await self._validate_capability()
        await self.__advanced_permissions(folder_id, True)

    async def disable_advanced_permissions(self, folder_id: int) -> None:
        """Disable advanced permissions on `folder_id`.

        Args:
            folder_id: Folder ID
        """
        await self._validate_capability()
        await self.__advanced_permissions(folder_id, False)

    async def __advanced_permissions(self, folder_id: int, enable: bool) -> None:
        await self._post(
            path=f'/{folder_id}/acl',
            data={'acl': 1 if enable else 0})

    async def add_advanced_permissions(
            self,
            folder_id: int,
            object_id: str,
            object_type: AclManagerType) -> None:
        """Enable `object_id` as manager of advanced permissions.

        Args:
            folder_id: Folder ID

            object_id: Object ID

            object_type: either `user` or `group`
        """
        await self._validate_capability()
        await self.__advanced_permissions_admin(
            folder_id,
            object_id=object_id,
            object_type=object_type.value,
            manage_acl=True)

    async def remove_advanced_permissions(
            self,
            folder_id: int,
            object_id: str,
            object_type: AclManagerType) -> None:
        """Disable `object_id` as manager of advanced permissions.

        Args:
            folder_id: Folder ID

            object_id: Object ID

            object_type: AclManagerType
        """
        await self._validate_capability()
        await self.__advanced_permissions_admin(
            folder_id,
            object_id=object_id,
            object_type=object_type.value,
            manage_acl=False)

    async def __advanced_permissions_admin(
            self,
            folder_id: int,
            object_id: str,
            object_type: str,
            manage_acl: bool) -> bool:
        response = await self._post(
            path=f'/{folder_id}/manageACL',
            data={
                'mappingId': object_id,
                'mappingType': object_type,
                'manageAcl': manage_acl})

        return response['success']

    async def set_permissions(
            self,
            folder_id: int,
            group_id: str,
            permissions: Permissions) -> bool:
        """Set permissions a group has in a folder.

        Args:
            folder_id: Folder ID

            group_id: Group ID

            permissions: New permissions.
        """
        await self._validate_capability()
        response = await self._post(
            path=f'/{folder_id}/groups/{group_id}',
            data={'permissions': permissions.value})
        return response['success']

    async def set_quota(self, folder_id: int, quota: Optional[int]) -> None:
        """Set quota for group folder.

        Args:
            folder_id : Folder ID

            quota: Quota in bytes.  None for unlimited.
        """
        await self._validate_capability()
        await self._post(
            path=f'/{folder_id}/quota',
            data={'quota': quota if quota else "none"})

    async def rename(self, folder_id: int, mount_point: str) -> None:
        """Rename a group folder.

        Args:
            folder_id: Folder ID

            mount_point: New mount point.
        """
        await self._validate_capability()
        response = await self._post(
            path=f'/{folder_id}/mountpoint',
            data={'mountpoint': mount_point})
        return response['success']
