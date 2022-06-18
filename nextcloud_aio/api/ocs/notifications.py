
class NotificationManager(object):

    async def get_notifications(self):
        """Get user's notification."""
        return await self.ocs_query(
            method='GET',
            sub=r'/ocs/v2.php/apps/notifications/api/v2/notifications')

    async def get_notification(self, not_id: int):
        """Get a single notification."""
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v2.php/apps/notifications/api/v2/notifications/{not_id}')

    async def remove_notifications(self):
        """Clear all of user's notification."""
        return await self.ocs_query(
            method='DELETE',
            sub=r'/ocs/v2.php/apps/notifications/api/v2/notifications')

    async def remove_notification(self, not_id: int):
        """Remove a single notification."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v2.php/apps/notifications/api/v2/notifications/{not_id}')
