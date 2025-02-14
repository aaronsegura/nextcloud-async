"""Nextcloud Application API.

Reference:
    https://docs.nextcloud.com/server/lastest/admin_manual/configuration_user/instruction_set_for_apps.html
"""

from nextcloud_async.api import NextcloudModule
from nextcloud_async.api.ocs import NextcloudOcsApi
from nextcloud_async.client import NextcloudClient

from typing import Optional, Dict, Hashable, Any, List


class Apps(NextcloudModule):
    """Manage applications on a Nextcloud instance."""

    def __init__(
            self,
            client: NextcloudClient,
            ocs_version: Optional[str] = '1'):
        self.client= client
        self.api = NextcloudOcsApi(client, ocs_version=ocs_version)
        self.stub = '/cloud/apps'

    async def get(self, app_id: str) -> Dict[Hashable, Any]:
        """Get application information.

        Args
        ----
            app_id (str): Application id

        Returns
        -------
            dict: Application information

        """
        return await self._get(path=f'/{app_id}')

    async def list(self, filter: Optional[str] = None) -> List[int]:
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

        response = await self._get(data=data)
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
        return await self._post(path=f'/{app_id}')

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
        return await self.api.delete(path=f'/{app_id}')
