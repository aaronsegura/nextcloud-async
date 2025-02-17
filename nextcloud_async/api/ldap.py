# noqa: D400 D415
"""
https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/user_auth_ldap_api.html
"""

from typing import Dict, Hashable, Any

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.helpers import recursive_urlencode


class Ldap(NextcloudModule):
    """Manage the LDAP configuration of a Nextcloud instance.

    Server must have LDAP user and group back-end enabled.
    """
    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '1'):
        self.stub = f'/apps/user_ldap/api/v{api_version}'
        self.api = NextcloudOcsApi(client, ocs_version = '2')

    async def add_config(self) -> Dict[Hashable, Any]:
        """Create a new LDAP configuration.

        Returns
        -------
            dict: New configuration ID, { "configID": ID }

        """
        return await self._post(path='/config')

    async def delete_config(self, id: str):
        """Remove the given LDAP configuration.

        Args
        ----
            id (str): LDAP Configuration ID

        """
        await self._delete(path=f'/config/{id}')

    async def get_config(self, id: str) -> Dict[Hashable, Any]:
        """Get an LDAP configuration.

        Args
        ----
            id (str): LDAP Configuration ID

        Returns
        -------
            dict: LDAP configuration description

        """
        return await self._get(path=f'/config/{id}')

    async def update_config(self, id: str, config_data: Dict[Hashable, Any]):
        """Update/set the properties of a given LDAP configuration.

        Args
        ----
            id (str): LDAP Configuration ID

            config_data (Dict): New values for configuration.
        """
        if 'configData' not in config_data:
            # Attempt to fix improperly formatted dictionary
            config_data = {'configData': config_data}

        url_data = recursive_urlencode(config_data)
        await self._put(path=f'/config/{id}?{url_data}')
