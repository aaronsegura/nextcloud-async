"""
https://docs.nextcloud.com/server/22/admin_manual/configuration_user/instruction_set_for_groups.html
"""

from typing import Optional


class GroupManager(object):

    async def search_groups(
            self,
            search: str,
            limit: Optional[int] = 100,
            offset: Optional[int] = 0):
        """Search groups.  This is the way to 'get' a group."""
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v1.php/cloud/groups',
            data={
                'limit': limit,
                'offset': offset,
                'search': search})

    async def create_group(self, group_id: str):
        """Create a new group."""
        return await self.ocs_query(
            method='POST',
            sub=r'/ocs/v1.php/cloud/groups',
            data={'groupid': group_id})

    async def get_group_members(self, group_id: str):
        """Get group members."""
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/groups/{group_id}')

    async def get_group_subadmins(self, group_id: str):
        """Get `group_id` subadmins."""
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/groups/{group_id}/subadmins')

    async def remove_group(self, group_id: str):
        """Remove `group_id`."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/groups/{group_id}')
