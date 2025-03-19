"""Nextcloud Application API.

Reference:
    https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_apps.html
"""

from nextcloud_async.api.mixins import NextcloudDataObject
from nextcloud_async.api.modules import NextcloudModule, password_confirmation_required
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsDriver


class App(NextcloudDataObject):
    _api: "AppsApi"

    def __str__(self) -> str:
        return f"<Nextcloud App {self.id} v{self.version}>"

    def __eq__(self, other: "App") -> bool:
        return (self.id, self.version) == (other.id, other.version)

    async def disable(self) -> None:
        """Disable this app."""
        await self._api.disable(app_id=self.id)

    async def enable(self) -> None:
        """Enable this app."""
        await self._api.enable(app_id=self.id)


class AppsApi(NextcloudModule):
    """Manage applications on a Nextcloud instance."""

    def __init__(self, ocs_driver: NextcloudOcsDriver) -> None:
        self.driver = ocs_driver
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

    async def get_all(self, filter: str | None = None) -> list[str]:
        """Get list of applications.

        Args:
            filter: "enabled" or "disabled". Defaults to None.

        Returns:
            list: List of application ids

        """
        data: dict[str, str] = {}
        if filter:
            data = {"filter": filter.lower()}

        response = await self._get(data=data)
        return response["apps"]

    async def list_enabled(self) -> list[str]:
        """Get list of enabled applications."""
        return await self.get_all("enabled")

    async def list_disabled(self) -> list[str]:
        """Get list of disabled applications."""
        # Prior to Nextcloud 31, using filter=disabled on this call returns a dictionary
        # instead of a list.  This is fixed in commit 77114fb3...
        response = await self.get_all("disabled")
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


def apps_api(client: NextcloudClient) -> AppsApi:
    """AppsApi Factory."""
    ocs_driver = NextcloudOcsDriver(client, version="1")
    return AppsApi(ocs_driver)
