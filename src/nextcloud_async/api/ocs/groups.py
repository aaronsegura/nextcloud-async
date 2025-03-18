"""Nextcloud Group Management API.

This interface allows you to manage groups and group membership on a Nextcloud instance.
If you want to promote a user to subadmin or remove subadmin privileges, see the Users
API.

https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_groups.html
"""

from typing import List

from nextcloud_async.api.dataobject import NextcloudDataObject
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.helpers import password_confirmation_required


class Group(NextcloudDataObject):
    self_api: "GroupsApi"
    self_type = "Group"

    def __eq__(self, other: "Group") -> bool:
        return self.id == other.id

    def __str__(self) -> str:
        return f'<Nextcloud Group "{self.id}">'

    def refresh_function(self) -> None:
        """No reason to refresh this object."""
        ...

    async def get_members(self) -> list[str]:
        """Get group members.

        Returns:
            list: Users belonging to `group_id`

        """
        return await self.self_api.get_members(self.id)

    async def get_subadmins(self) -> list[str]:
        """Get `group_id` subadmins.

        Args:
            group_id (str): Group ID

        Returns:
            list: Users who are subadmins of this group.

        """
        return await self.self_api.get_subadmins(self.id)

    async def delete(self) -> None:
        """Delete this group."""
        await self.self_api.delete(self.id)
        self.id = "<deleted>"


class GroupsApi(NextcloudModule):
    """Manage groups on a Nextcloud instance."""

    def __init__(self, ocs_api: NextcloudOcsApi) -> None:
        self.api = ocs_api
        self.stub = "/cloud/groups"

    async def search(
        self, search: str = "", limit: int = 100, offset: int = 0
    ) -> list[Group]:
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
            data={"limit": limit, "offset": offset, "search": search}
        )
        return [Group(data, self) for data in response["groups"]]

    @password_confirmation_required
    async def create(self, group_id: str) -> Group:
        """Create a new group.

        Args:
            group_id (str): Group name

        Returns:
            New Group

        """
        await self._post(data={"groupid": group_id})
        return Group({"id": group_id}, self)

    async def get_members(self, group_id: str) -> list[str]:
        """Get group members.

        Args:
            group_id (str): _description_

        Returns:
            list: Users belonging to `group_id`

        """
        response = await self._get(path=f"/{group_id}")
        return response["users"]

    @password_confirmation_required
    async def get_subadmins(self, group_id: str) -> list[str]:
        """Get `group_id` subadmins.

        Args:
            group_id (str): Group ID

        Returns:
            list: Users who are subadmins of this group.

        """
        return await self._get(path=f"/{group_id}/subadmins")

    @password_confirmation_required
    async def delete(self, group_id: str) -> None:
        """Remove `group_id`.

        Args:
            group_id (str): Group ID

        """
        return await self._delete(path=f"/{group_id}")


def groups_api(client: NextcloudClient) -> GroupsApi:
    """GroupsApi Factory."""
    ocs_api = NextcloudOcsApi(client)
    return GroupsApi(ocs_api)
