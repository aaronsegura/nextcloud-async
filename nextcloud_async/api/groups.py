"""Nextcloud Group Management API.

https://docs.nextcloud.com/server/22/admin_manual/configuration_user/\
instruction_set_for_groups.html
"""

from typing import Optional, List, Dict, Hashable, Any

from nextcloud_async.driver import NextcloudOcsApi, NextcloudModule
from nextcloud_async.client import NextcloudClient


class Groups(NextcloudModule):
    """Manage groups on a Nextcloud instance."""

    def __init__(
            self,
            client: NextcloudClient):

        self.api = NextcloudOcsApi(client)
        self.stub = '/cloud/groups'

    async def search(
            self,
            search: Optional[str] = '',
            limit: Optional[int] = 100,
            offset: Optional[int] = 0) -> List[str]:
        """Search groups.

        This is the way to 'get' a group.

        Args
        ----
            search (str): Search string, empty string for all groups.

            limit (int, optional): Results per page. Defaults to 100.

            offset (int, optional): Page offset. Defaults to 0.

        Returns
        -------
            list: Group names.

        """
        response = await self._get(
            data={
                'limit': limit,
                'offset': offset,
                'search': search})
        return response['groups']

    async def add(self, group_name: str) -> Dict[Hashable, Any]:
        """Create a new group.

        Args
        ----
            group_name (str): Group name

        Returns
        -------
            Empty 100 Response

        """
        return await self.api.post(
            path=self.stub,
            data={'groupid': group_name})

    async def get_group_members(self, group_name: str) -> List[str]:
        """Get group members.

        Args
        ----
            group_id (str): _description_

        Returns
        -------
            list: Users belonging to `group_id`

        """
        response = await self.api.get(
            path=f'{self.stub}/{group_name}')
        return response['users']

    async def get_subadmins(self, group_name: str) -> List[str]:
        """Get `group_name` subadmins.

        Args
        ----
            group_name (str): Group ID

        Returns
        -------
            list: Users who are subadmins of this group.

        """
        return await self.api.get(
            path=f'{self.stub}/{group_name}/subadmins')

    async def delete(self, group_name: str):
        """Remove `group_id`.

        Args
        ----
            group_id (str): Group ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.api.delete(
            path=f'{self.stub}/{group_name}')
