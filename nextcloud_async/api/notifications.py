# noqa: D400 D415
"""https://github.com/nextcloud/notifications/blob/master/docs/ocs-endpoint-v2.md"""

from dataclasses import dataclass
from typing import List, Dict, Any

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi


@dataclass
class Notification:
    data: Dict[str, Any]
    notifications_api: 'Notifications'

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Notification #{self.id} from "{self.app}">'

    def __repr__(self):
        return str(self.data)


    @property
    def id(self):
        return self.notification_id

    async def delete(self):
        await self.notifications_api.delete(self.id)


class Notifications(NextcloudModule):
    """Manage user notifications on Nextcloud instance."""

    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '2'):
        self.stub = f'/apps/notifications/api/v{api_version}/notifications'
        self.api = NextcloudOcsApi(client, ocs_version = '2')

    async def list(self) -> List[Notification]:
        """Get user's notifications.

        Returns
        -------
            list: Notifications
        """
        response = await self._get()
        return [Notification(data, self) for data in response]

    async def get(self, id: int) -> Notification:
        """Get a single notification.

        Args
        ----
            id (int): Notification ID

        Returns
        -------
            Notification Object
        """
        response = await self._get(path=f'/{id}')
        return Notification(response, self)

    async def clear(self) -> None:
        """Clear all of user's notifications.

        Raises
        ------
            NextcloudException
        """
        return await self._delete()

    async def delete(self, id: int) -> None:
        """Remove a single notification.

        Args
        ----
            id (int): Notification ID

        Raises
        ------
            NextcloudException
        """
        return await self._delete(path=f'/{id}')
