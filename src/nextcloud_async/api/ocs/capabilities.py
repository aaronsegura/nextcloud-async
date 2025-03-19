import logging
from typing import Any, Optional

from nextcloud_async import NextcloudClient
from nextcloud_async.exceptions import NextcloudNotCapableError

log = logging.getLogger("nextcloud_async.api")


class NextcloudCapabilities:
    _instance: Optional["NextcloudCapabilities"] = None
    _capabilities: dict[str, Any] = {}
    _version: dict[str, Any] = {}

    client: NextcloudClient

    def __new__(cls, client: NextcloudClient) -> "NextcloudCapabilities":  # noqa: ARG004
        """Singleton pattern for Capabilities API."""
        if not cls._instance:
            log.debug("Creating new Capabilities object.")
            cls._instance = super(NextcloudCapabilities, cls).__new__(cls)
        else:
            log.debug("Reusing existing Capabilities object.")
        return cls._instance

    def __init__(self, client: NextcloudClient) -> None:
        self.client = client

    @classmethod
    def destroy(cls) -> None:
        """Destroy singleton instance.

        This is useful for unit testing.
        """
        cls._instance = None

    async def _get_capabilities(self) -> dict[str, Any]:
        """Return capabilities for this server."""
        headers = {"OCS-APIRequest": "true"}
        headers.update(self.client.request_headers)

        response = await self.client.http_client.request(
            method="GET",
            auth=self.client.auth,
            url=f"{self.client.endpoint}/ocs/v1.php/cloud/capabilities?format=json",
            headers=headers,
        )
        return response.json()["ocs"]["data"]

    async def _pop_capabilities(self) -> None:
        """Populate local capabilties cache."""
        response = await self._get_capabilities()
        self._capabilities = response["capabilities"]
        self._version = response["version"]

    async def get_all(self) -> dict[str, Any]:
        """Return full dictionary of server capabilities."""
        if not self._capabilities:
            await self._pop_capabilities()
        return self._capabilities

    async def get_capability(self, capability: str) -> Any:
        """Return a specific capability.

        Args:
            capability:
                dot-separated strings

        Raises:
            NextcloudNotCapableError:
                When capability does not exist.

        Returns:
            Capability value

        """
        if not self._capabilities:
            await self._pop_capabilities()

        current_node = self._capabilities
        for item in capability.split("."):
            try:
                current_node = current_node[item]
            except TypeError:
                try:
                    if item not in current_node:
                        raise NextcloudNotCapableError
                except TypeError:
                    raise NextcloudNotCapableError
            except KeyError:
                try:
                    if item not in current_node:
                        raise NextcloudNotCapableError
                except TypeError:
                    raise NextcloudNotCapableError
        return current_node

    async def supported(self, capability: str) -> bool:
        """Check if capability is supported on server.

        Args:
            capability:
                dot-separated strings.

        Returns:
            True or False

        """
        if not self._capabilities:
            await self._pop_capabilities()

        current_node = self._capabilities
        for item in capability.split("."):
            try:
                current_node = current_node[item]
            except TypeError:
                try:
                    if item not in current_node:
                        return False
                except TypeError:
                    return False
            except KeyError:
                try:
                    if item not in current_node:
                        return False
                except TypeError:
                    return False

        # Some capabilities may exist with a "false" value, so we cannot
        # assume that just because it exists it is enabled.  It is assumed
        # that any capability with a non-false value is enabled.
        if current_node is not False:
            return True
        else:
            return False

    async def server_version(self) -> dict[str, str]:
        """Return the server version."""
        if not self._version:
            await self._pop_capabilities()
        return self._version
