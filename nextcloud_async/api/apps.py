"""Nextcloud Application API.

Reference:
    https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_apps.html
"""

from dataclasses import dataclass

from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.client import NextcloudClient

from typing import Optional, Dict, Any, List


@dataclass
class App:
    data: Dict[str, Any]
    apps_api: 'Apps'

    async def disable(self):
        await self.apps_api.disable(app_id=self.id)
        self.data = {}

    async def enable(self, **kwargs):
        await self.apps_api.enable(app_id=self.id)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Nextcloud App "{self.name}", {"enabled" if self.active else "disabled"}>'

    def __repr__(self):
        return str(self.data)



class Apps(NextcloudModule):
    """Manage applications on a Nextcloud instance."""

    def __init__(
            self,
            client: NextcloudClient,
            ocs_version: Optional[str] = '1'):
        self.client= client
        self.api = NextcloudOcsApi(client, ocs_version=ocs_version)
        self.stub = '/cloud/apps'

    async def get(self, app_id: str) -> App:
        """Get application information.

        Args
        ----
            app_id (str): Application id

        Returns
        -------
            dict: Application information

        """
        response = await self._get(path=f'/{app_id}')
        return App(response, self)

    async def list(self, filter: Optional[str] = None) -> List[str]:
        """Get list of applications.

        Args
        ----
            filter (str, optional): "enaled" or "disabled". Defaults to None.

        Returns
        -------
            list: List of application ids

        """
        data: Dict[str, str] = {}
        if filter:
            data = {'filter': filter}

        response = await self._get(data=data)
        return response['apps']

    async def enable(self, app_id: str) -> Dict[str, Any]:
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

    async def disable(self, app_id: str) -> Dict[str, Any]:
        """Disable Application.

        Requires admin privileges.

        Args
        ----
            app_id (str): Application ID

        Returns
        -------
            Empty 100 Response

        """
        return await self._delete(path=f'/{app_id}')
