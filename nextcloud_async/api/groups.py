"""Nextcloud Group Management API.

https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_groups.html
"""

from dataclasses import dataclass

from typing import List, Any

from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.client import NextcloudClient


@dataclass
class Group:
    data: str
    groups_api: 'Groups'

    def __post_init__(self) -> None:
        self._data = {'name': self.data}

    def __getattr__(self, k: str) -> Any:
        return self._data[k]

    def __str__(self) -> str:
        return f'<Nextcloud Group "{self.name}">'

    def __repr__(self) -> str:
        return f'<Nextcloud Group {self.data}>'

    async def get_members(self) -> List[str]:
        """Get group members.

        Returns:
            list: Users belonging to `group_id`
        """
        return await self.groups_api.get_members(self.name)

    async def get_subadmins(self) -> List[str]:
        """Get `group_id` subadmins.

        Args:
            group_id (str): Group ID

        Returns:
            list: Users who are subadmins of this group.
        """
        return await self.groups_api.get_subadmins(self.name)

    async def delete(self) -> None:
        """Delete this group."""
        await self.groups_api.delete(self.name)
        self._data['name'] = '<deleted>'


class Groups(NextcloudModule):
    """Manage groups on a Nextcloud instance."""

    def __init__(
            self,
            client: NextcloudClient) -> None:

        self.api = NextcloudOcsApi(client)
        self.stub = '/cloud/groups'

    async def search(
            self,
            search: str = '',
            limit: int = 100,
            offset: int = 0) -> List[Group]:
        """Search groups.

        This is the way to 'get' a group.

        Args:
            search:
                Search string, empty string for all groups.

            limit:
                Results per page. Defaults to 100.

            offset:
                Page offset. Defaults to 0.

        Returns:
            List of Groups
        """
        response = await self._get(
            data={
                'limit': limit,
                'offset': offset,
                'search': search})
        return [Group(data, self) for data in response['groups']]

    async def add(self, group_id: str) -> Group:
        """Create a new group.

        Args:
            group_id (str): Group name

        Returns:
            New Group
        """
        await self._post(data={'groupid': group_id})
        return Group(group_id, self)

    async def get_members(self, group_id: str) -> List[str]:
        """Get group members.

        Args:
            group_id (str): _description_

        Returns:
            list: Users belonging to `group_id`
        """
        response = await self._get(
            path=f'/{group_id}')
        return response['users']

    async def get_subadmins(self, group_id: str) -> List[str]:
        """Get `group_id` subadmins.

        Args:
            group_id (str): Group ID

        Returns:
            list: Users who are subadmins of this group.
        """
        return await self._get(path=f'/{group_id}/subadmins')

    async def delete(self, group_id: str) -> None:
        """Remove `group_id`.

        Args:
            group_id (str): Group ID
        """
        return await self._delete(
            path=f'/{group_id}')
