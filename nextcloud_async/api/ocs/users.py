# noqa: D400 D415
"""https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/\
instruction_set_for_users.html"""

import asyncio

from typing import Optional, List, Dict
from nextcloud_async.api.ocs.shares import ShareType


class UserManager():
    """Manage users on a Nextcloud instance."""

    async def create_user(
            self,
            user_id: str,
            display_name: str,
            email: str,
            quota: str,
            language: str,
            groups: List = [],
            subadmin: List = [],
            password: Optional[str] = None) -> Dict[str, str]:
        """Create a new Nextcloud user.

        Args
        ----
            user_id (str): New user ID

            display_name (str): User display Name (eg. "Your Name")

            email (str): E-mail Address

            quota (str): User quota, in bytes.  -3 for unlimited.

            language (str): User language

            groups (List, optional): Groups user should be aded to. Defaults to [].

            subadmin (List, optional): Groups user should be admin for. Defaults to [].

            password (Optional[str], optional): User password. Defaults to None.

        Returns
        -------
            dict: New user ID

            Example:

                { 'id': 'YourNewUser' }

        """
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
            offset: int = 0) -> List[str]:
        """Search for users.

        Args
        ----
            search (str): Search string

            limit (int, optional): Results per request. Defaults to 100.

            offset (int, optional): Paging offset. Defaults to 0.

        Returns
        -------
            list: User ID matches

        """
        response = await self.ocs_query(
            method='GET',
            sub='/ocs/v1.php/cloud/users',
            data={
                'search': search,
                'limit': limit,
                'offset': offset})
        return response['users']

    async def get_user(self, user_id: str = None) -> Dict[str, str]:
        """Get a valid user.

        Args
        ----
            user_id (str, optional): User ID. Defaults to None (current user).

        Returns
        -------
            dict: User description.

        """
        if not user_id:
            user_id = self.user
        return await self.ocs_query(method='GET', sub=f'/ocs/v1.php/cloud/users/{user_id}')

    async def get_users(self) -> List[str]:
        """Return all user IDs.

        Admin required

        Returns
        -------
            List: User IDs

        """
        response = await self.ocs_query(method='GET', sub=r'/ocs/v1.php/cloud/users')
        return response['users']

    async def user_autocomplete(
            self,
            search: str,
            item_type: Optional[str] = None,
            item_id: Optional[str] = None,
            sorter: Optional[str] = None,
            share_types: Optional[List[ShareType]] = [ShareType['user']],
            limit: int = 25) -> List[Dict[str, str]]:
        """Search for a user using incomplete information.

        Reference:
            https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/\
            ocs-api-overview.html#auto-complete-and-user-search

            https://github.com/nextcloud/server/blob/master/core/Controller/\
            AutoCompleteController.php#L62

        Args
        ----
            search (str): Search string

            item_type (str, optional): Item type, `users` or `groups`. Used for sorting.
            Defaults to None.

            item_id (str, optional): Item id, used for sorting.  Defaults to None.

            sorter (str, optional): Can be piped, top priority first, e.g.:
            "commenters|share-recipients"

            share_types (ShareType, optional): ShareType, defaults to ShareType['user']

            limit (int, optional): Results per page. Defaults to 25.

        Returns
        -------
            list: Potential matches

        """
        share_types_values = [x.value for x in share_types]
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v2.php/core/autocomplete/get',
            data={
                'search': search,
                'itemType': item_type,
                'itemId': item_id,
                'sorter': sorter,
                'shareTypes[]': share_types_values,
                'limit': limit})

    async def update_user(
            self,
            user_id: str,
            new_data: Dict) -> List[List[str]]:
        """Update a user's information.

        Use async/await to update everything at once.

        Args
        ----
            user_id (str): User ID

            new_data (Dict): New key/value pairs

        Returns
        -------
            list: Responses

        """
        reqs = []
        for k, v in new_data.items():
            reqs.append(self.__update_user(user_id, k, v))

        return await asyncio.gather(*reqs)

    async def __update_user(self, user_id, k, v) -> List[str]:
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v1.php/cloud/users/{user_id}',
            data={'key': k, 'value': v})

    async def get_user_editable_fields(self):
        """Get user-editable fields.

        Returns
        -------
            list: User-editable fields

        """
        return await self.ocs_query(
            method='GET',
            sub=r'/ocs/v1.php/cloud/user/fields')

    async def disable_user(self, user_id: str) -> List[str]:
        """Disable `user_id`.

        Must be admin.

        Args
        ----
            user_id (str): User ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/disable')

    async def enable_user(self, user_id: str) -> List[str]:
        """Enable `user_id`.  Must be admin.

        Args
        ----
            user_id (str): User ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/enable')

    async def remove_user(self, user_id: str) -> List[str]:
        """Remove existing `user_id`.

        Args
        ----
            user_id (str): User ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/users/{user_id}')

    async def get_user_groups(self, user_id: Optional[str] = None) -> List[str]:
        """Get list of groups `user_id` belongs to.

        Args
        ----
            user_id (str, optional): User ID. Defaults to current user.

        Returns
        -------
            list: group ids

        """
        response = await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/users/{user_id or self.user}/groups')
        return response['groups']

    async def add_user_to_group(self, user_id: str, group_id: str) -> List[str]:
        """Add `user_id` to `group_id`.

        Args
        ----
            user_id (str): User ID

            group_id (str): Group ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='POST',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/groups',
            data={'groupid': group_id})

    async def remove_user_from_group(self, user_id: str, group_id: str) -> List[str]:
        """Remove `user_id` from `group_id`.

        Args
        ----
            user_id (str): User ID

            group_id (str): Group Id

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/groups',
            data={'groupid': group_id})

    async def promote_user_to_subadmin(self, user_id: str, group_id: str) -> List[str]:
        """Make `user_id` a subadmin of `group_id`.

        Args
        ----
            user_id (str): User ID

            group_id (str): Group ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='POST',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/subadmins',
            data={'groupid': group_id})

    async def demote_user_from_subadmin(self, user_id: str, group_id: str) -> List[str]:
        """Demote `user_id` from subadmin of `group_id`.

        Args
        ----
            user_id (str): User ID

            group_id (str): Group ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/subadmins',
            data={'groupid': group_id})

    async def get_user_subadmin_groups(self, user_id: str) -> List[str]:
        """Return list of groups of which `user_id` is subadmin.

        Args
        ----
            user_id (str): User ID

        Returns
        -------
            list: group ids

        """
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/subadmins')

    async def resend_welcome_email(self, user_id: str) -> List[str]:
        """Re-send initial welcome e-mail to `user_id`.

        Args
        ----
            user_id (str): User ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='POST',
            sub=f'/ocs/v1.php/cloud/users/{user_id}/welcome')
