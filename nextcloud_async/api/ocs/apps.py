"""Nextcloud Application API.

Reference:
    https://docs.nextcloud.com/server/22/admin_manual/\
configuration_user/instruction_set_for_apps.html
"""

from typing import Optional


class AppManager(object):
    """Manage applications on a Nextcloud instance."""

    async def get_app(self, app_id: str):
        """Get application information.

        Args
        ----
            app_id (str): Application id

        Returns
        -------
            dict: Application information

        """
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v1.php/cloud/apps/{app_id}')

    async def get_apps(self, filter: Optional[str] = None):
        """Get list of applications.

        Args
        ----
            filter (str, optional): _description_. Defaults to None.

        Returns
        -------
            list: List of application ids

        """
        data = {}
        if filter:
            data = {'filter': filter}
        response = await self.ocs_query(
            method='GET',
            sub=r'/ocs/v1.php/cloud/apps',
            data=data)
        return response['apps']

    async def enable_app(self, app_id: str):
        """Enable Application.

        Requires admin privileges.

        Args
        ----
            app_id (str): Application ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='POST',
            sub=f'/ocs/v1.php/cloud/apps/{app_id}')

    async def disable_app(self, app_id: str):
        """Disable Application.

        Requires admin privileges.

        Args
        ----
            app_id (str): Application ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v1.php/cloud/apps/{app_id}')
