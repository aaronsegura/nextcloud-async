# noqa: D400 D415
"""https://docs.nextcloud.com/server/latest/admin_manual/\
configuration_user/user_auth_ldap_api.html"""

from typing import Dict

from nextcloud_async.helpers import recursive_urlencode


class OCSLdapAPI(object):
    """Manage the LDAP configuration of a Nextcloud instance.

    Server must have LDAP user and group back-end enabled.
    """

    async def create_ldap_config(self):
        """Create a new LDAP configuration.

        Returns
        -------
            dict: New configuration ID, { "configID": ID }

        """
        return await self.ocs_query(
            method='POST',
            sub='/ocs/v2.php/apps/user_ldap/api/v1/config')

    async def remove_ldap_config(self, id: str):
        """Remove the given LDAP configuration.

        Args
        ----
            id (str): LDAP Configuration ID

        Returns
        -------
            Empty 200 Response

        """
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v2.php/apps/user_ldap/api/v1/config/{id}')

    async def get_ldap_config(self, id: str):
        """Get an LDAP configuration.

        Args
        ----
            id (str): LDAP Configuration ID

        Returns
        -------
            dict: LDAP configuration description

        """
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v2.php/apps/user_ldap/api/v1/config/{id}')

    async def set_ldap_config(self, id: str, config_data: Dict):
        """Set the properties of a given LDAP configuration.

        Args
        ----
            id (str): LDAP Configuration ID

            config_data (Dict): New values for configuration.

        Returns
        -------
            Empty 200 Response

        """
        if 'configData' not in config_data:
            # Attempt to fix improperly formatted dictionary
            config_data = {'configData': config_data}

        url_data = recursive_urlencode(config_data)
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v2.php/apps/user_ldap/api/v1/config/{id}?{url_data}')
