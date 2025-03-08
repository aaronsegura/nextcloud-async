"""Nextcloud Notifications API.

https://github.com/nextcloud/notifications/blob/master/docs/ocs-endpoint-v2.md
"""

from typing import List

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.api.dataobject import NextcloudDataObject


class Notification(NextcloudDataObject):
    self_api: "Notifications"

    def __str__(self) -> str:
        return f'<Notification #{self.id} from "{self.app}">'

    def async_refresh(self) -> None:
        """No need to refresh this object."""
        ...

    @property
    def id(self) -> int:
        """Alias for self.notification_id."""
        return self.notification_id

    async def delete(self) -> None:
        """Delete this notification."""
        await self.self_api.delete(self.id)


class Notifications(NextcloudModule):
    """Manage user notifications on Nextcloud instance."""

    def __init__(self, client: NextcloudClient, api_version: str = "2") -> None:
        self.stub = f"/apps/notifications/api/v{api_version}/notifications"
        self.api = NextcloudOcsApi(client, ocs_version="2")

    async def list(self) -> List[Notification]:
        """Get user's notifications.

        Returns:
            List of Notification
        """
        response = await self._get()
        return [Notification(data, self) for data in response]

    async def get(self, id: int) -> Notification:
        """Get a single notification.

        Args:
            id (int): Notification ID

        Returns:
            Notification
        """
        response = await self._get(path=f"/{id}")
        return Notification(response, self)

    async def clear(self) -> None:
        """Clear all of user's notifications."""
        return await self._delete()

    async def delete(self, id: int) -> None:
        """Remove a single notification.

        Args:
            id (int): Notification ID
        """
        return await self._delete(path=f"/{id}")
