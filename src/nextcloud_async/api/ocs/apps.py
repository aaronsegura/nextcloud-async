"""Nextcloud Application API.

Reference:
    https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_apps.html
"""

from typing import Dict, List, Optional

from nextcloud_async.api.dataobject import NextcloudDataObject
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.helpers import password_confirmation_required


class App(NextcloudDataObject):
    self_api: "Apps"

    def __str__(self) -> str:
        return f"<Nextcloud App {self.id} v{self.version}>"

    async def disable(self) -> None:
        """Disable this app."""
        await self.self_api.disable(app_id=self.id)

    async def enable(self) -> None:
        """Enable this app."""
        await self.self_api.enable(app_id=self.id)


class Apps(NextcloudModule):
    """Manage applications on a Nextcloud instance."""

    def __init__(self, client: NextcloudClient, ocs_version: str = "1") -> None:
        self.client = client
        self.api = NextcloudOcsApi(client, ocs_version=ocs_version)
        self.stub = "/cloud/apps"

    async def get(self, app_id: str) -> App:
        """Get application information.

        Args:
            app_id: Application id

        Returns:
            App object
        """
        response = await self._get(path=f"/{app_id}")
        return App(response, self)

    async def list(self, filter: Optional[str] = None) -> List[str]:
        """Get list of applications.

        Args:
            filter: "enabled" or "disabled". Defaults to None.

        Returns:
            list: List of application ids
        """
        data: Dict[str, str] = {}
        if filter:
            data = {"filter": filter.lower()}

        response = await self._get(data=data)
        return response["apps"]

    async def list_enabled(self) -> List[str]:
        """Get list of enabled applications."""
        return await self.list("enabled")

    async def list_disabled(self) -> List[str]:
        """Get list of disabled applications."""
        # Prior to Nextcloud 31, using filter=disabled on this call returns a dictionary
        # instead of a list.  This is fixed in commit 77114fb3...
        response = await self.list("disabled")
        if isinstance(response, dict):
            return list(response.values())
        else:
            return response

    @password_confirmation_required
    async def enable(self, app_id: str) -> None:
        """Enable Application.

        Requires admin privileges.

        Args:
            app_id (str): Application ID
        """
        return await self._post(path=f"/{app_id}")

    @password_confirmation_required
    async def disable(self, app_id: str) -> None:
        """Disable Application.

        Requires admin privileges.

        Args:
            app_id (str): Application ID
        """
        await self._delete(path=f"/{app_id}")
