"""Implement Nextcloud Group Folders Interaction.

https://github.com/nextcloud/groupfolders#api
https://github.com/nextcloud/groupfolders/blob/master/openapi.json
"""

from enum import IntFlag
from dataclasses import dataclass

from typing import List, Dict, Any

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

@dataclass
class GroupFolder:
    data: Dict[str, Any]
    groupfolder_api: 'GroupFolders'

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<GroupFolder "{self.mount_point}">'

    def __repr__(self):
        return str(self)

    async def delete(self):
        await self.groupfolder_api.delete(self.id)
        self.data = {'mount_point': '**deleted**'}

    async def permit_group(self, **kwargs):
        return await self.groupfolder_api.permit_group(folder_id=self.id, **kwargs)

    async def deny_group(self, **kwargs):
        return await self.groupfolder_api.deny_group(folder_id=self.id, **kwargs)

    async def enable_advanced_permissions(self, **kwargs):
        return await self.groupfolder_api.enable_advanced_permissions(folder_id=self.id, **kwargs)

    async def disable_advanced_permissions(self, **kwargs):
        return await self.groupfolder_api.disable_advanced_permissions(folder_id=self.id, **kwargs)

    async def add_advanced_permission(self, **kwargs):
        return await self.groupfolder_api.add_advanced_permissions(folder_id=self.id, **kwargs)

    async def remove_advanced_permission(self, **kwargs):
        return await self.groupfolder_api.remove_advanced_permissions(folder_id=self.id, **kwargs)

    async def set_permissions(self, **kwargs):
        return await self.groupfolder_api.set_permissions(folder_id=self.id, **kwargs)

    async def set_quota(self, **kwargs):
        return await self.groupfolder_api.set_quota(folder_id=self.id, **kwargs)

    async def rename(self, mount_point: str):
        if await self.groupfolder_api.rename(folder_id=self.id, mount_point=mount_point):
            self.mount_point = mount_point
            return True

        return False


class GroupFolders(NextcloudModule):
    """Manage Group Folders.

    Must have Group Folders application enabled on server.  If groupfolders is not enabled,
    all requests will throw NextcloudNotFound exception.  Check for 'groupfolders' in server
    capabilitites before using.
    """

    def __init__(
            self,
            client: NextcloudClient):
        self.stub = '/apps/groupfolders/folders'
        self.api = NextcloudOcsApi(client, ocs_stub='/index.php')

    # TODO: Fix when no groupfolders
    async def list(self) -> List[GroupFolder]:
        """Get list of all group folders.

        Returns
        -------
            list: List of group folders.

        """
        response = await self._get()
        return [GroupFolder(value, self) for _, value in response.items()]

    async def add(self, path: str) -> GroupFolder:
        """Create new group folder.

        Args
        ----
            path (str): Path of new group folder.

        Returns
        -------
            dict: New groupfolder id

            Example:

                { 'id': 1 }

        """
        response = await self._post(data={'mountpoint': path})
        return GroupFolder(response, self)

    async def get(self, folder_id: int) -> GroupFolder:
        """Get group folder with id `folder_id`.

        Args
        ----
            folder_id (int): Group folder ID

        Returns
        -------
            dict: Group folder description.

        """
        response = await self._get(path=f'/{folder_id}')
        return GroupFolder(response, self)

    async def delete(self, folder_id: int) -> bool:
        """Delete group folder with id `folder_id`.

        Args
        ----
            folder_id (int): Group folder ID

        Returns
        -------
            bool: success(True) or failure(False)

        """
        response = await self._delete(path=f'/{folder_id}')
        return response['success']

    async def permit_group(self, group_id: str, folder_id: int) -> bool:
        """Give `group_id` access to `folder_id`.

        Args
        ----
            group_id (str): Group ID

            folder_id (int): Folder ID

        Returns
        -------
            bool: success(True) or failure(False)

        """
        response = await self._post(path=f'/{folder_id}/groups', data={'group': group_id})
        return response['success']

    async def deny_group(self, group_id: str, folder_id: int) -> bool:
        """Remove `group_id` access from `folder_id`.

        Args
        ----
            group_id (str): Group ID

            folder_id (int): Folder ID

        Returns
        -------
            bool: success(True) or failure(False)

        """
        response = await self._delete(path=f'/apps/groupfolders/folders/{folder_id}/groups/{group_id}')
        return response['success']

    async def enable_advanced_permissions(self, folder_id: int) -> bool:
        """Enable advanced permissions on `folder_id`.

        Args
        ----
            folder_id (int): Folder ID

        Returns
        -------
            bool: success(True) or failure(False)

        """
        return await self.__advanced_permissions(folder_id, True)

    async def disable_advanced_permissions(self, folder_id: int):
        """Disable advanced permissions on `folder_id`.

        Args
        ----
            folder_id (int): Folder ID

        Returns
        -------
            bool: success(True) or failure(False)

        """
        return await self.__advanced_permissions(folder_id, False)

    async def __advanced_permissions(self, folder_id: int, enable: bool) -> bool:
        response = await self._post(
            path=f'/{folder_id}/acl',
            data={'acl': 1 if enable else 0})
        return response['success']

    async def add_advanced_permissions(
            self,
            folder_id: int,
            object_id: str,
            object_type: str) -> bool:
        """Enable `object_id` as manager of advanced permissions.

        Args
        ----
            folder_id (int): Folder ID

            object_id (str): Object ID

            object_type (str): either `user` or `group`

        Returns
        -------
            bool: success(True) or failure(False)

        """
        return await self.__advanced_permissions_admin(
            folder_id,
            object_id=object_id,
            object_type=object_type,
            manage_acl=True)

    async def remove_advanced_permissions(
            self,
            folder_id: int,
            object_id: str,
            object_type: str) -> bool:
        """Disable `object_id` as manager of advanced permissions.

        Args
        ----
            folder_id (int): Folder ID

            object_id (str): Object ID

            object_type (str): either `user` or `group`

        Returns
        -------
            bool: success(True) or failure(False)

        """
        return await self.__advanced_permissions_admin(
            folder_id,
            object_id=object_id,
            object_type=object_type,
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

        Args
        ----
            folder_id (int): Folder ID

            group_id (str): Group ID

            permissions (Permissions): New permissions.

        Returns
        -------
            bool: success(True) or failure(False)

        """
        response = await self._post(
            path=f'/{folder_id}/groups/{group_id}',
            data={'permissions': permissions.value})
        return response['success']

    async def set_quota(self, folder_id: int, quota: int) -> bool:
        """Set quota for group folder.

        Args
        ----
            folder_id (int): Folder ID

            quota (int): Quota in bytes.  -3 for unlimited.

        Returns
        -------
            bool: success(True) or failure(False)

        """
        response = await self._post(
            path=f'/{folder_id}/quota',
            data={'quota': quota})
        return response['successs']

    async def rename(self, folder_id: int, mount_point: str) -> bool:
        """Rename a group folder.

        Args
        ----
            folder_id (int): Folder ID

            mountpoint (str): New mount point.

        Returns
        -------
            bool: success(True) or failure(False)

        """
        response = await self._post(
            path=f'/{folder_id}/mountpoint',
            data={'mountpoint': mount_point})
        return response['success']
