"""
https://docs.nextcloud.com/server/22/admin_manual/configuration_user/instruction_set_for_apps.html
"""

from typing import Optional


class AppManager(object):

    async def get_app(self, app_id: str):
        """Get application information."""
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/apps/{app_id}')

    async def get_apps(self, filter: Optional[str] = None):
        """Get list of applications."""
        data = {}
        if filter:
            data = {'filter': filter}
        return await self.ocs_query(
            method='GET',
            sub=r'/ocs/v1.php/cloud/apps',
            data=data)

    async def enable_app(self, app_id: str):
        """Enable Application."""
        return await self.ocs_query(
            method='POST',
            sub=f'/ocs/v1.php/cloud/apps/{app_id}')

    async def disable_app(self, app_id: str):
        """Enable Application."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/apps/{app_id}')
