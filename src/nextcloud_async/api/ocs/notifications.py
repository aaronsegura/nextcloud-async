"""Nextcloud Notifications API.

https://github.com/nextcloud/notifications/blob/master/docs/ocs-endpoint-v2.md
"""

from nextcloud_async.api.dataobject import NextcloudDataObject
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi


class Notification(NextcloudDataObject):
    self_api: "NotificationsApi"

    def __str__(self) -> str:
        return f'<Notification #{self.id} from "{self.app}">'

    def __eq__(self, other: "Notification") -> bool:
        return self.id == other.id

    @property
    def id(self) -> int:
        """Alias for self.notification_id."""
        return self.notification_id

    async def delete(self) -> None:
        """Delete this notification."""
        await self.self_api.delete(self.id)


class NotificationsApi(NextcloudModule):
    """Manage user notifications on Nextcloud instance."""

    def __init__(self, ocs_api: NextcloudOcsApi) -> None:
        self.api = ocs_api
        self.stub = "/apps/notifications/api/v2/notifications"

    async def get_all(self) -> list[Notification]:
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


def notifications_api(client: NextcloudClient) -> NotificationsApi:
    """NotificationsApi Factory."""
    ocs_api = NextcloudOcsApi(client, version="2")
    return NotificationsApi(ocs_api)
