# noqa: D400 D415
"""Nextcloud Users API.

https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_users.html
"""

import asyncio
import logging
from collections.abc import Awaitable
from typing import Any

from nextcloud_async.api.mixins import NextcloudDataObject
from nextcloud_async.api.modules import NextcloudModule, password_confirmation_required
from nextcloud_async.api.ocs.groups import Group, GroupsApi
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsDriver

log = logging.getLogger("nextcloud_async.api")


class User(NextcloudDataObject):
    self_api: "UsersApi"

    def __eq__(self, other: "User") -> bool:
        return self.id == other.id

    def __str__(self) -> str:
        return f'<Nextcloud User "{self.id}">'

    def refresh_function(self) -> Awaitable:
        """Define how to refresh this object."""
        log.debug("Refreshing User.")
        return self.self_api.get(self.id)

    async def update(self, new_data: dict[str, Any]) -> None:
        """Update this user.

        Args:
            new_data:
                Dictionary describing new attributes.

        """
        await self.self_api.update(self.id, new_data)
        await self._refresh()

    async def disable(self) -> None:
        """Disable this user."""
        await self.self_api.disable(self.id)
        self.enabled = False

    async def enable(self) -> None:
        """Enable this user."""
        await self.self_api.enable(self.id)
        self.enabled = True

    async def delete(self) -> None:
        """Delete this user."""
        await self.self_api.delete(self.id)
        self.data = {"id": "**deleted**"}

    async def get_groups(self) -> list[Group]:
        """Get list of groups this memeber is in."""
        return await self.self_api.get_group_membership(self.id)

    async def add_to_group(self, group: Group) -> None:
        """Add this user to the given group.

        Args:
            group:
                Group object

        """
        await self.self_api.add_to_group(self.id, group.id)
        await self._refresh()

    async def remove_from_group(self, group: Group) -> None:
        """Remove this user from the given Group.

        Args:
            group:
                Group object

        """
        await self.self_api.remove_from_group(self.id, group.id)
        await self._refresh()

    async def promote_to_group_subadmin(self, group: Group) -> None:
        """Promote this user to subadmin of the given Group.

        Args:
            group:
                Group object

        """
        await self.self_api.promote_to_group_subadmin(self.id, group.id)
        await self._refresh()

    async def demote_from_group_subadmin(self, group: Group) -> None:
        """Remove subadmin privileges from this user for the given group.

        Args:
            group:
                Group object

        """
        await self.self_api.demote_from_group_subadmin(self.id, group.id)
        await self._refresh()

    async def get_subadmin_groups(self) -> list[Group]:
        """Return list of groups of which this user is a subadmin.

        Returns:
            list[Group]

        """
        return await self.self_api.get_subadmin_groups(self.id)


class UsersApi(NextcloudModule):
    """Manage users on a Nextcloud instance."""

    def __init__(self, ocs_api: NextcloudOcsDriver) -> None:
        self.stub = "/cloud"
        self.api = ocs_api

    @password_confirmation_required
    async def create(
        self,
        user_id: str,
        display_name: str,
        email: str,
        language: str,
        quota: int | None = None,
        groups: list[str] = [],
        subadmin: list[str] = [],
        password: str | None = None,
    ) -> User:
        """Create a new Nextcloud user.

        Args:
            user_id:
                New user ID

            display_name:
                User display Name (eg. "Your Name")

            email:
                E-mail Address

            quota:
                User quota, in bytes.  "None" for unlimited.

            language:
                User language

            groups:
                Groups user should be added to.

            subadmin:
                Groups user should be admin for.

            password:
                User password.

        Returns:
            dict: New user

        """
        await self._post(
            path="/users",
            data={
                "userid": user_id,
                "displayName": display_name,
                "email": email,
                "groups": groups,
                "subadmin": subadmin,
                "language": language,
                "quota": str(quota) if quota else "none",
                "password": password,
            },
        )

        return await self.get(user_id)

    async def search(self, search: str, limit: int = 100, offset: int = 0) -> list[str]:
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
            path="/users", data={"search": search, "limit": limit, "offset": offset}
        )
        return response["users"]

    async def get(self, user_id: str) -> User:
        """Get a valid user.

        Args:
            user_id:
                User ID to get.

        Returns:
            User object.

        """
        response = await self._get(path=f"/users/{user_id}")
        return User(response, self)

    async def get_all(self) -> list[str]:
        """Return all user IDs.

        Admin required

        Returns:
            List: User IDs

        """
        response = await self._get(path="/users")
        return response["users"]

    # TODO: Move into another module and referene from here
    # async def user_autocomplete(
    #     self,
    #     search: str,
    #     item_type: str | None = None,
    #     item_id: str | None = None,
    #     sorter: str | None = None,
    #     share_types: list[ShareType] = [ShareType["user"]],
    #     limit: int = 25,
    # ) -> list[dict[str, str]]:
    #     """Search for a user using incomplete information.

    #     https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html#auto-complete-and-user-search

    #     https://github.com/nextcloud/server/blob/master/core/Controller/AutoCompleteController.php#L62

    #     Args:
    #         search:
    #             Search string

    #         item_type:
    #             Item type, `users` or `groups`. Used for sorting.

    #         item_id:
    #             Item id, used for sorting.  Defaults to None.

    #         sorter:
    #             Can be piped, top priority first, e.g.: "commenters|share-recipients"

    #         share_types:
    #             ShareType, defaults to ShareType['user']

    #         limit:
    #             Results per page. Defaults to 25.

    #     Returns:
    #         list: Potential matches

    #     """
    #     share_types_values = [x.value for x in share_types]
    #     return await self._get(
    #         path="/ocs/v2.php/core/autocomplete/get",
    #         data={
    #             "search": search,
    #             "itemType": item_type,
    #             "itemId": item_id,
    #             "sorter": sorter,
    #             "shareTypes[]": share_types_values,
    #             "limit": limit,
    #         },
    #     )

    @password_confirmation_required
    async def update(self, user_id: str, new_data: dict[str, Any]) -> None:
        """Update a user's information.

        Use async/await to update everything at once.

        Args:
            user_id:
                User ID

            new_data:
                New key/value pairs

        """
        reqs = []
        for k, v in new_data.items():
            reqs.append(self._update_user(user_id, k, v))

        await asyncio.gather(*reqs)

    async def _update_user(self, user_id: str, k: str, v: str | int) -> list[str]:
        return await self._put(path=f"/users/{user_id}", data={"key": k, "value": v})

    async def get_editable_fields(self) -> list[str]:
        """Get user-editable fields.

        Returns:
            list: User-editable fields

        """
        return await self._get(path="/user/fields")

    @password_confirmation_required
    async def disable(self, user_id: str) -> None:
        """Disable `user_id`.

        Must be admin.

        Args:
            user_id: User ID

        """
        await self._put(path=f"/users/{user_id}/disable")

    @password_confirmation_required
    async def enable(self, user_id: str) -> None:
        """Enable `user_id`.  Must be admin.

        Args:
            user_id: User ID

        """
        await self._put(path=f"/users/{user_id}/enable")

    @password_confirmation_required
    async def delete(self, user_id: str) -> None:
        """Remove existing `user_id`.

        Args:
            user_id: User ID

        """
        return await self._delete(path=f"/users/{user_id}")

    async def get_group_membership(self, user_id: str | None = None) -> list[Group]:
        """Get list of groups `user_id` belongs to.

        Args:
            user_id: User ID. Optional, defaults to current user.

        Returns:
            list: group ids

        """
        response = await self._get(
            path=f"/users/{user_id if user_id else self.api.client.user}/groups"
        )
        return [Group({"id": group_id}, self) for group_id in response["groups"]]

    @password_confirmation_required
    async def add_to_group(self, user_id: str, group_id: str) -> None:
        """Add `user_id` to `group_id`.

        Args:
            user_id:
                User ID

            group_id:
                Group ID

        """
        await self._post(path=f"/users/{user_id}/groups", data={"groupid": group_id})

    @password_confirmation_required
    async def remove_from_group(self, user_id: str, group_id: str) -> None:
        """Remove `user_id` from `group_id`.

        Args:
            user_id:
                User ID

            group_id:
                Group Id

        """
        await self._delete(path=f"/users/{user_id}/groups", data={"groupid": group_id})

    @password_confirmation_required
    async def promote_to_group_subadmin(self, user_id: str, group_id: str) -> None:
        """Make user_id a subadmin of group_id.

        Args:
            user_id:
                User ID

            group_id:
                Group ID

        """
        await self._post(path=f"/users/{user_id}/subadmins", data={"groupid": group_id})

    @password_confirmation_required
    async def demote_from_group_subadmin(self, user_id: str, group_id: str) -> None:
        """Demote `user_id` from subadmin of `group_id`.

        Args:
            user_id:
                User ID

            group_id:
                Group ID

        """
        return await self._delete(
            path=f"/users/{user_id}/subadmins", data={"groupid": group_id}
        )

    async def get_subadmin_groups(self, user_id: str) -> list[Group]:
        """Return list of groups of which `user_id` is subadmin.

        Args:
            user_id: User ID

        Returns:
            list: group ids

        """
        response = await self._get(path=f"/users/{user_id}/subadmins")
        return [
            Group({"id": group_id}, GroupsApi(self.api.client)) for group_id in response
        ]

    @password_confirmation_required
    async def resend_welcome_email(self, user_id: str) -> None:
        """Re-send initial welcome e-mail to user_id.

        Args:
            user_id: User ID

        """
        await self._post(path=f"/users/{user_id}/welcome")


def users_api(client: NextcloudClient) -> UsersApi:
    """UsersApi Factory."""
    ocs_api = NextcloudOcsDriver(client)
    return UsersApi(ocs_api)
