# noqa: D400 D415
"""https://github.com/nextcloud/notifications/blob/master/docs/ocs-endpoint-v2.md"""

from typing import List, Dict, Hashable, Any

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsApi, NextcloudModule


class Notifications(NextcloudModule):
    """Manage user notifications on Nextcloud instance."""

    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '2'):
        self.stub = f'/apps/notifications/api/v{api_version}/notifications'
        self.api = NextcloudOcsApi(client, ocs_version = '2')

    async def list(self) -> List[Dict[Hashable, Any]]:
        """Get user's notifications.

        Returns
        -------
            list: Notifications

        """
        return await self._get()

    async def get(self, id: int):
        """Get a single notification.

        Args
        ----
            id (int): Notification ID

        Returns
        -------
            dict: Notification description

        """
        return await self._get(path=f'/{id}')

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
