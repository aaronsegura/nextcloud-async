"""Implement Nextcloud Group Folders Interaction.

https://github.com/nextcloud/groupfolders#api
"""

from enum import IntFlag

from typing import List, Dict, Hashable, Any

from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.client import NextcloudClient
from nextcloud_async.helpers import str2bool

class Permissions(IntFlag):
    """Groupfolders Permissions."""

    read = 1
    update = 2
    create = 4
    delete = 8
    share = 16
    all = 31


class GroupFolders(NextcloudModule):
    """Manage Group Folders.

    Must have Group Folders application enabled on server.  If groupfolders is not enabled,
    all requests will throw NextcloudNotFound exception.  You can check capabilities of the
    server before sending a request: self.get_capabilities('groupfolders')
    """

    def __init__(
            self,
            client: NextcloudClient):
        self.api = NextcloudOcsApi(client, stub='/index.php/apps')
        self.stub = 'groupfolders/folders'

    async def list(self) -> List[Dict[Hashable, Any]]:
        """Get list of all group folders.

        Returns
        -------
            list: List of group folders.

        """
        response = await self.api.get(path=self.stub)
        if isinstance(response, dict):
            return [response]
        return response

    async def add(self, path: str) -> Dict[Hashable, Any]:
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
        return await self.api.post(path=self.stub, data={'mountpoint': path})

    async def get(self, folder_id: int) -> Dict[Hashable, Any]:
        """Get group folder with id `folder_id`.

        Args
        ----
            folder_id (int): Group folder ID

        Returns
        -------
            dict: Group folder description.

        """
        return await self.api.get(path=f'{self.stub}/{folder_id}')

    async def delete(self, folder_id: int) -> bool:
        """Delete group folder with id `folder_id`.

        Args
        ----
            folder_id (int): Group folder ID

        Returns
        -------
            bool: success(True) or failure(False)

        """
        response = await self.api.delete(path=f'{self.stub}/{folder_id}')
        return str2bool(response['success'])

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
        response = await self.api.post(path=f'{self.stub}/{folder_id}/groups', data={'group': group_id})
        return str2bool(response['success'])

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
        response = await self.api.delete(path=f'/apps/groupfolders/folders/{folder_id}/groups/{group_id}')
        return str2bool(response['success'])

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

    async def disable_group_folder_advanced_permissions(self, folder_id: int):
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
        response = await self.api.post(
            path=f'{self.stub}/{folder_id}/acl',
            data={'acl': 1 if enable else 0})
        return str2bool(response['success'])


    async def add_advanced_permissions(
            self,
            folder_id: int,
            object_id: str,
            object_type: str):
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

    async def remove_group_folder_advanced_permissions(
            self,
            folder_id: int,
            object_id: str,
            object_type: str):
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
        response = await self.api.post(
            path=f'{self.stub}/{folder_id}/manageACL',
            data={
                'mappingId': object_id,
                'mappingType': object_type,
                'manageAcl': manage_acl})

        return str2bool(response['success'])


    async def set_group_folder_permissions(
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
        response = await self.api.post(
            path=f'{self.stub}/{folder_id}/groups/{group_id}',
            data={'permissions': permissions.value})
        return str2bool(response['success'])

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
        response = await self.api.post(
            path=f'{self.stub}/{folder_id}/quota',
            data={'quota': quota})
        return str2bool(response['successs'])

    async def rename(self, folder_id: int, mountpoint: str):
        """Rename a group folder.

        Args
        ----
            folder_id (int): Folder ID

            mountpoint (str): New mount point.

        Returns
        -------
            bool: success(True) or failure(False)

        """
        response = await self.api.post(
            path=f'{self.stub}/{folder_id}/mountpoint',
            data={'mountpoint': mountpoint})
        return str2bool(response['success'])
