# noqa: D400 D415
"""https://github.com/nextcloud/notifications/blob/master/docs/ocs-endpoint-v2.md"""


class NotificationManager(object):
    """Manage user notifications on Nextcloud instance."""

    async def get_notifications(self):
        """Get user's notifications.

        Returns
        -------
            list: Notifications

        """
        return await self.ocs_query(
            method='GET',
            sub=r'/ocs/v2.php/apps/notifications/api/v2/notifications')

    async def get_notification(self, not_id: int):
        """Get a single notification.

        Args
        ----
            not_id (int): Notification ID

        Returns
        -------
            dict: Notification description

        """
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v2.php/apps/notifications/api/v2/notifications/{not_id}')

    async def remove_notifications(self):
        """Clear all of user's notifications.

        Returns
        -------
            Empty 200 Response

        """
        return await self.ocs_query(
            method='DELETE',
            sub=r'/ocs/v2.php/apps/notifications/api/v2/notifications')

    async def remove_notification(self, not_id: int):
        """Remove a single notification.

        Args
        ----
            not_id (int): Notification ID

        Returns
        -------
            Empty 200 Response

        """
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v2.php/apps/notifications/api/v2/notifications/{not_id}')
