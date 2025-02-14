"""Nextcloud Application API.

Reference:
    https://docs.nextcloud.com/server/22/admin_manual/\
configuration_user/instruction_set_for_apps.html
"""

from nextcloud_async.api.ocs import NextcloudOcsApi
from nextcloud_async.client import NextcloudClient

from typing import Optional, Dict, Hashable, Any, List


class AppManager:
    """Manage applications on a Nextcloud instance."""

    def __init__(
            self,
            client: NextcloudClient):
        self.api = NextcloudOcsApi(client)

    async def get_app(self, app_id: str) -> Dict[Hashable, Any]:
        """Get application information.

        Args
        ----
            app_id (str): Application id

        Returns
        -------
            dict: Application information

        """
        return await self.api.get(sub=f'/ocs/v1.php/cloud/apps/{app_id}')

    async def list_apps(self, filter: Optional[str] = None) -> List[int]:
        """Get list of applications.

        Args
        ----
            filter (str, optional): _description_. Defaults to None.

        Returns
        -------
            list: List of application ids

        """
        data: Dict[Hashable, str] = {}
        if filter:
            data = {'filter': filter}

        response = await self.api.get(
            sub=r'/ocs/v1.php/cloud/apps',
            data=data)
        return response['apps']

    async def enable_app(self, app_id: str) -> Dict[Hashable, Any]:
        """Enable Application.

        Requires admin privileges.

        Args
        ----
            app_id (str): Application ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.api.post(sub=f'/ocs/v1.php/cloud/apps/{app_id}')

    async def disable_app(self, app_id: str) -> Dict[Hashable, Any]:
        """Disable Application.

        Requires admin privileges.

        Args
        ----
            app_id (str): Application ID

        Returns
        -------
            Empty 100 Response

        """
        return await self.api.delete(sub=f'/ocs/v1.php/cloud/apps/{app_id}')
