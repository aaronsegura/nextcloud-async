"""Nextcloud LDAP Interface.

https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/user_auth_ldap_api.html
"""

from typing import Any, Awaitable

from nextcloud_async.api.mixins import NextcloudDataObject
from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsDriver
from nextcloud_async.helpers import bool2int, recursive_urlencode


class LdapConfiguration(NextcloudDataObject):
    _api: "LdapApi"

    def __str__(self) -> str:
        return f"<Nextcloud Ldap Config {self.id}>"

    def __eq__(self, other: "LdapConfiguration") -> bool:
        return self.id == other.id

    @property
    def id(self) -> str:
        """Alias for self.data['configID]."""
        return self.configID

    def refresh_function(self) -> Awaitable:
        """Set up object refresh."""
        return self._api.get(self.id)

    async def delete(self) -> None:
        """Delete this configuration."""
        await self._api.delete(self.configID)
        self.data["configID"] = "**deleted**"

    async def update(self, config_data: dict[str, Any]) -> None:
        """Update/set the properties of this LDAP configuration.

        Args:
            config_data (Dict): New values for configuration.

        """
        await self._api.update(self.id, config_data)
        await self._refresh()


class LdapApi(NextcloudModule):
    """Manage the LDAP configuration of a Nextcloud instance.

    Server must have LDAP user and group back-end enabled.
    """

    def __init__(self, ocs_driver: NextcloudOcsDriver, api_version: str = "1") -> None:
        self.driver = ocs_driver
        self.stub = f"/apps/user_ldap/api/v{api_version}"

    async def create(self) -> LdapConfiguration:
        """Create a new LDAP configuration.

        Returns:
            dict: New configuration ID, { "configID": ID }

        """
        response = await self._post(path="/config")
        return LdapConfiguration(response, self)

    async def delete(self, id: str) -> None:
        """Remove the given LDAP configuration.

        Args:
            id (str): LDAP Configuration ID

        """
        await self._delete(path=f"/config/{id}")

    async def get(self, id: str, show_password: bool = False) -> LdapConfiguration:
        """Get an LDAP configuration.

        Args:
            id:
                LDAP Configuration ID

            show_password:
                Whether to include the ldapAgentPassword in results.

        Returns:
            dict: LDAP configuration description

        """
        response = await self._get(
            path=f"/config/{id}", json={"showPassword": bool2int(show_password)}
        )
        # Endpoint does not return configID in results.
        response["configID"] = id
        return LdapConfiguration(response, self)

    async def update(self, id: str, config_data: dict[str, Any]) -> None:
        """Update/set the properties of a given LDAP configuration.

        Args:
            id (str): LDAP Configuration ID

            config_data (Dict): New values for configuration.

        """
        if "configData" not in config_data:
            # Attempt to fix improperly formatted dictionary
            config_data = {"configData": config_data}

        url_data = recursive_urlencode(config_data)
        await self._put(path=f"/config/{id}?{url_data}")


def ldap_api(client: NextcloudClient) -> LdapApi:
    """LdapApi Factory."""
    ocs_driver = NextcloudOcsDriver(client, version="2")
    return LdapApi(ocs_driver)
