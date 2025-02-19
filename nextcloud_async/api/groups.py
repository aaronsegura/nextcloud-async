"""Nextcloud Group Management API.

https://docs.nextcloud.com/server/22/admin_manual/configuration_user/\
instruction_set_for_groups.html
"""

from dataclasses import dataclass

from typing import Optional, List, Any

from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.client import NextcloudClient


@dataclass
class Group:
    data: str
    groups_api: 'Groups'

    def __post_init__(self):
        self._data = {'name': self.data}

    def __getattr__(self, k: str) -> Any:
        return self._data[k]

    def __str__(self):
        return f'<Nextcloud Group "{self.name}">'

    def __repr__(self):
        return str(self.data)


    async def get_members(self):
        return await self.groups_api.get_members(self.name)

    async def get_subadmins(self):
        return await self.groups_api.get_subadmins(self.name)

    async def delete(self) -> None:
        await self.groups_api.delete(self.name)
        self._data['name'] = '<deleted>'


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
            offset: Optional[int] = 0) -> List[Group]:
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
        return [Group(data, self) for data in response['groups']]

    async def add(self, group_name: str) -> Group:
        """Create a new group.

        Args
        ----
            group_name (str): Group name

        """
        await self._post(data={'groupid': group_name})
        return Group(group_name, self)

    async def get_members(self, group_name: str) -> List[str]:
        """Get group members.

        Args
        ----
            group_id (str): _description_

        Returns
        -------
            list: Users belonging to `group_id`

        """
        response = await self._get(
            path=f'/{group_name}')
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
        return await self._get(path=f'/{group_name}/subadmins')

    async def delete(self, group_name: str) -> None:
        """Remove `group_id`.

        Args
        ----
            group_id (str): Group ID

        Returns
        -------
            Empty 100 Response

        """
        return await self._delete(
            path=f'/{group_name}')
