"""Nextcloud Group Management API.

https://docs.nextcloud.com/server/22/admin_manual/configuration_user/\
instruction_set_for_groups.html
"""

from typing import Optional


class GroupManager(object):
    """Manage groups on a Nextcloud instance."""

    async def search_groups(
            self,
            search: str,
            limit: Optional[int] = 100,
            offset: Optional[int] = 0):
        """Search groups.

        This is the way to 'get' a group.

        Args
        ----
            search (str): Search string

            limit (int, optional): Results per page. Defaults to 100.

            offset (int, optional): Page offset. Defaults to 0.

        Returns
        -------
            list: Group names.

        """
        response = await self.ocs_query(
            method='GET',
            sub='/ocs/v1.php/cloud/groups',
            data={
                'limit': limit,
                'offset': offset,
                'search': search})
        return response['groups']

    async def create_group(self, group_id: str):
        """Create a new group.

        Args
        ----
            group_id (str): Group name

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='POST',
            sub=r'/ocs/v1.php/cloud/groups',
            data={'groupid': group_id})

    async def get_group_members(self, group_id: str):
        """Get group members.

        Args
        ----
            group_id (str): _description_

        Returns
        -------
            list: Users belonging to `group_id`

        """
        response = await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/groups/{group_id}')
        return response['users']

    async def get_group_subadmins(self, group_id: str):
        """Get `group_id` subadmins.

        Args
        ----
            group_id (str): Group ID

        Returns
        -------
            list: Users who are subadmins of this group.

        """
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/groups/{group_id}/subadmins')

    async def remove_group(self, group_id: str):
        """Remove `group_id`.

        Args
        ----
            group_id (str): Group ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/groups/{group_id}')
