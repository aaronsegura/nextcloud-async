# noqa: D400 D415
"""Nextcloud Users API.

https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_users.html
"""

import asyncio

from typing import Optional, List, Dict, Any

from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.client import NextcloudClient


class Users(NextcloudModule):
    """Manage users on a Nextcloud instance."""

    def __init__(
            self,
            client: NextcloudClient,
            ocs_version: str = '1') -> None:
        self.stub = r'/cloud/users'
        self.api = NextcloudOcsApi(client, ocs_version = ocs_version)

    async def create_user(
            self,
            user_id: str,
            display_name: str,
            email: str,
            quota: str,
            language: str,
            groups: List[str] = [],
            subadmin: List[str] = [],
            password: Optional[str] = None) -> Dict[str, str]:
        """Create a new Nextcloud user.

        Args:
            user_id (str): New user ID

            display_name (str): User display Name (eg. "Your Name")

            email (str): E-mail Address

            quota (str): User quota, in bytes.  "none" for unlimited.

            language (str): User language

            groups (List, optional): Groups user should be aded to. Defaults to [].

            subadmin (List, optional): Groups user should be admin for. Defaults to [].

            password (Optional[str], optional): User password. Defaults to None.

        Returns:
            dict: New user ID

            Example:

                { 'id': 'YourNewUser' }
        """
        return await self._post(
            data={
                'userid': user_id,
                'displayName': display_name,
                'email': email,
                'groups': groups,
                'subadmin': subadmin,
                'language': language,
                'quota': quota,
                'password': password})

    async def search(
            self,
            search: str,
            limit: int = 100,
            offset: int = 0) -> List[str]:
        """Search for users.

        Args:
            search:
                Search string

            limit:
                Results per request. Defaults to 100.

            offset:
                Paging offset. Defaults to 0.

        Returns:
            list: User ID matches
        """
        response = await self._get(
            data={
                'search': search,
                'limit': limit,
                'offset': offset})
        return response['users']

    async def get(self, user_id: str) -> Dict[str, str]:
        """Get a valid user.

        Args:
            user_id:
                User ID to get.

        Returns:
            dict: User description.
        """
        return await self._get(path=f'/{user_id}')

    async def list(self) -> List[str]:
        """Return all user IDs.

        Admin required

        Returns:
            List: User IDs
        """
        response = await self._get()
        return response['users']


    # TODO: Put into OCS-specific module, along with other TODOs
    # async def user_autocomplete(
    #         self,
    #         search: str,
    #         item_type: Optional[str] = None,
    #         item_id: Optional[str] = None,
    #         sorter: Optional[str] = None,
    #         share_types: Optional[List[ShareType]] = [ShareType['user']],
    #         limit: int = 25) -> List[Dict[str, str]]:
    #     """Search for a user using incomplete information.

    #     Reference:
    #         https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html#auto-complete-and-user-search

    #         https://github.com/nextcloud/server/blob/master/core/Controller/AutoCompleteController.php#L62

    #     Args
    #     ----
    #         search (str): Search string

    #         item_type (str, optional): Item type, `users` or `groups`. Used for sorting.
    #         Defaults to None.

    #         item_id (str, optional): Item id, used for sorting.  Defaults to None.

    #         sorter (str, optional): Can be piped, top priority first, e.g.:
    #         "commenters|share-recipients"

    #         share_types (ShareType, optional): ShareType, defaults to ShareType['user']

    #         limit (int, optional): Results per page. Defaults to 25.

    #     Returns
    #     -------
    #         list: Potential matches

    #     """
    #     share_types_values = [x.value for x in share_types]
    #     return await self._get(
    #         path='/ocs/v2.php/core/autocomplete/get',
    #         data={
    #             'search': search,
    #             'itemType': item_type,
    #             'itemId': item_id,
    #             'sorter': sorter,
    #             'shareTypes[]': share_types_values,
    #             'limit': limit})

    async def update_user(
            self,
            user_id: str,
            new_data: Dict[str, Any]) -> List[List[str]]:
        """Update a user's information.

        Use async/await to update everything at once.

        Args:
            user_id (str): User ID

            new_data (Dict): New key/value pairs

        Returns:
            list: Responses
        """
        reqs = []
        for k, v in new_data.items():
            reqs.append(self.__update_user(user_id, k, v))

        return await asyncio.gather(*reqs)

    async def __update_user(self, user_id: str, k: str, v: str | int) -> List[str]:
        return await self._put(
            path=f'/{user_id}',
            data={'key': k, 'value': v})

    async def get_editable_fields(self):
        """Get user-editable fields.

        Returns:
            list: User-editable fields
        """
        return await self._get(path=r'/fields')

    async def disable(self, user_id: str) -> List[str]:
        """Disable `user_id`.

        Must be admin.

        Args:
            user_id (str): User ID

        Returns:
            Empty 100 Response
        """
        return await self._put(path=f'/{user_id}/disable')

    async def enable(self, user_id: str) -> List[str]:
        """Enable `user_id`.  Must be admin.

        Args:
            user_id (str): User ID

        Returns:
            Empty 100 Response
        """
        return await self._put(path=f'/{user_id}/enable')

    async def delete(self, user_id: str) -> List[str]:
        """Remove existing `user_id`.

        Args:
            user_id (str): User ID

        Returns:
            Empty 100 Response
        """
        return await self._delete(path=f'/{user_id}')

    async def get_group_membership(self, user_id: str) -> List[str]:
        """Get list of groups `user_id` belongs to.

        Args:
            user_id (str, optional): User ID. Defaults to current user.

        Returns:
            list: group ids
        """
        response = await self._get(path=f'/{user_id }/groups')
        return response['groups']

    async def add_to_group(self, user_id: str, group_id: str) -> List[str]:
        """Add `user_id` to `group_id`.

        Args:
            user_id (str): User ID

            group_id (str): Group ID

        Returns:
            Empty 100 Response
        """
        return await self._post(
            path=f'/{user_id}/groups',
            data={'groupid': group_id})

    async def remove_from_group(self, user_id: str, group_id: str) -> List[str]:
        """Remove `user_id` from `group_id`.

        Args:
            user_id (str): User ID

            group_id (str): Group Id

        Returns:
            Empty 100 Response
        """
        return await self._delete(
            path=f'/{user_id}/groups',
            data={'groupid': group_id})

    async def promote_to_subadmin(self, user_id: str, group_id: str) -> List[str]:
        """Make `user_id` a subadmin of `group_id`.

        Args:
            user_id (str): User ID

            group_id (str): Group ID

        Returns:
            Empty 100 Response
        """
        return await self._post(
            path=f'/{user_id}/subadmins',
            data={'groupid': group_id})

    async def demote_from_subadmin(self, user_id: str, group_id: str) -> List[str]:
        """Demote `user_id` from subadmin of `group_id`.

        Args:
            user_id (str): User ID

            group_id (str): Group ID

        Returns:
            Empty 100 Response
        """
        return await self._delete(
            path=f'/{user_id}/subadmins',
            data={'groupid': group_id})

    async def get_subadmin_groups(self, user_id: str) -> List[str]:
        """Return list of groups of which `user_id` is subadmin.

        Args:
            user_id (str): User ID

        Returns:
            list: group ids
        """
        return await self._get(path=f'/{user_id}/subadmins')

    async def resend_welcome_email(self, user_id: str) -> List[str]:
        """Re-send initial welcome e-mail to `user_id`.

        Args:
            user_id (str): User ID

        Returns:
            Empty 100 Response
        """
        return await self._post(path=f'/{user_id}/welcome')
