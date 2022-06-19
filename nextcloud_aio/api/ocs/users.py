"""
https://docs.nextcloud.com/server/22/admin_manual/configuration_user/instruction_set_for_users.html
"""

import asyncio

from typing import Optional, List, Dict


class UserManager():

    async def create_user(
            self,
            user_id: str,
            display_name: str,
            email: str,
            quota: str,
            language: str,
            groups: List = [],
            subadmin: List = [],
            password: Optional[str] = None):
        """Create a new Nextcloud user."""
        return await self.ocs_query(
            method='POST',
            sub='/ocs/v1.php/cloud/users',
            data={
                'userid': user_id,
                'displayName': display_name,
                'email': email,
                'groups': groups,
                'subadmin': subadmin,
                'language': language,
                'quota': quota,
                'password': password})

    async def search_users(
            self,
            search: str,
            limit: int = 100,
            offset: int = 0):
        """Search for users."""
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v1.php/cloud/users',
            data={
                'search': search,
                'limit': limit,
                'offset': offset})

    async def get_user(self, user_id: str = None) -> Dict:
        """Returns a valid user.  Defaults to current user."""
        if not user_id:
            user_id = self.user
        return await self.ocs_query(method='GET', sub=f'/ocs/v1.php/cloud/users/{user_id}')

    async def get_users(self) -> Dict:
        """Returns all user IDs.  Admin only."""
        return await self.ocs_query(method='GET', sub=r'/ocs/v1.php/cloud/users')

    async def user_autocomplete(
            self,
            search: str,
            item_type: Optional[str] = None,
            limit: int = 10):
        """Search for a user using incomplete information."""
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v2.php/core/autocomplete/get',
            data={
                'search': search,
                'itemType': item_type,
                'limit': limit})

    async def update_user(
            self,
            user_id: str,
            new_data: Dict):
        """
        Update a user's information.

        Use async/await to update everything at once.
        """
        reqs = []
        for k, v in new_data.items():
            reqs.append(self.__update_user(user_id, k, v))

        return await asyncio.gather(*reqs, )

    async def __update_user(self, user_id, k, v):
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v1.php/cloud/users/{user_id}',
            data={'key': k, 'value': v})

    async def get_user_editable_fields(self):
        """Which profile fields am I allowed to edit?"""
        return await self.ocs_query(
            method='GET',
            sub=r'/ocs/v1.php/cloud/user/fields')

    async def disable_user(self, user_id: str):
        """Disable `user_id`.  Must be admin."""
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/disable')

    async def enable_user(self, user_id: str):
        """Enable `user_id`.  Must be admin."""
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/enable')

    async def remove_user(self, user_id: str):
        """Remove existing `user_id`."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/users/{user_id}')

    async def get_user_groups(self, user_id: str):
        """Get list of groups `user_id` belongs to."""
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/groups')

    async def add_user_to_group(self, user_id: str, group_id: str):
        """Add `user_id` to `group_id`."""
        return await self.ocs_query(
            method='POST',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/groups',
            data={'groupid': group_id})

    async def remove_user_from_group(self, user_id: str, group_id: str):
        """Remove `user_id` from `group_id`."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/groups',
            data={'groupid': group_id})

    async def promote_user_to_subadmin(self, user_id: str, group_id: str):
        """Make `user_id` a subadmin of `group_id`."""
        return await self.ocs_query(
            method='POST',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/subadmins',
            data={'groupid': group_id})

    async def demote_user_from_subadmin(self, user_id: str, group_id: str):
        """Demote `user_id` from subadmin of `group_id`."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/subadmins',
            data={'groupid': group_id})

    async def get_user_subadmin_groups(self, user_id: str):
        """Return list of groups of which `user_id` is subadmin."""
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/subadmins')

    async def resend_welcome_email(self, user_id: str):
        """Re-send initial welcome e-mail to `user_id`."""
        return await self.ocs_query(
            method='POST',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/welcome')
