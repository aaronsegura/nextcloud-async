import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from nextcloud_async.client import NextcloudClient
from nextcloud_async.exceptions import (
    NextcloudBadRequestError,
    NextcloudConflictError,
    NextcloudDeviceWipeRequestedError,
    NextcloudError,
    NextcloudFederationRemoteError,
    NextcloudForbiddenError,
    NextcloudGenericServerError,
    NextcloudMethodNotAllowedError,
    NextcloudNotCapableError,
    NextcloudNotFoundError,
    NextcloudNotSupportedError,
    NextcloudPreconditionError,
    NextcloudRequestTimeoutError,
    NextcloudServiceNotAvailableError,
    NextcloudTooManyRequestsError,
    NextcloudUnauthorizedError,
    NextcloudUnsupportedMediaTypeError,
    NextcloudUpgradeRequiredError,
)

_EXCEPTIONS = [
    NextcloudBadRequestError,
    NextcloudConflictError,
    NextcloudError,
    NextcloudForbiddenError,
    NextcloudMethodNotAllowedError,
    NextcloudNotCapableError,
    NextcloudNotFoundError,
    NextcloudPreconditionError,
    NextcloudTooManyRequestsError,
    NextcloudUnauthorizedError,
    NextcloudUnsupportedMediaTypeError,
    NextcloudFederationRemoteError,
    NextcloudUpgradeRequiredError,
    NextcloudServiceNotAvailableError,
    NextcloudNotSupportedError,
    NextcloudGenericServerError,
    NextcloudRequestTimeoutError,
]

log = logging.getLogger("nextcloud_async.driver")


class NextcloudHttpApi(ABC):
    """Methods imported by different Nextcloud API drivers."""

    _capabilities_api: "NextcloudCapabilities"

    def __init__(self, client: NextcloudClient) -> None:
        self.client = client
        self._capabilities_api = NextcloudCapabilities(client)

    @abstractmethod
    async def request(
        self,
        method: str = "GET",
        path: str = "",
        data: Any = None,
        headers: dict[str, Any] | None = None,
        content: bytes | None = None,
        raw_response: bool = False,
    ) -> Any:
        """Subclasses must define how to request information from their endpoints."""
        ...

    def _path_args(self, data: dict[str, Any] | None = None, path: str = "") -> str:
        if not data:
            return path

        parts = []
        for k, v in data.items():
            if isinstance(v, bool):
                parts.append(f"{k}={str(v).lower()}")
            elif v is None:
                parts.append(f"{k}=")
            else:
                parts.append(f"{k}={v}")
        return f"{path}?{'&'.join(parts)}"

    def _munge_headers(
        self, headers: dict[str, Any] | None = None, extra: dict[str, Any] | None = {}
    ) -> dict[str, Any]:
        if headers:
            headers["User-Agent"] = self.client.user_agent
        else:
            headers = {"User-Agent": self.client.user_agent}

        if extra:
            headers.update(extra)

        if self.client.request_headers:
            headers.update(self.client.request_headers)

        return headers

    def _format_json(self, data: dict[str, Any] | None) -> dict[str, Any]:
        if data:
            data.update({"format": "json"})
        else:
            data = {"format": "json"}
        return data

    async def _wipe_requested(self) -> bool:
        from nextcloud_async.api import Wipe

        wipe = Wipe(self.client)
        return await wipe.check()

    async def has_capability(self, capability: str) -> bool:
        """Check if server has a capability.

        Args:
            capability:
                Dot-separated strings

                Example: `files.versioning`

        Returns:
            True or False
        """
        return await self._capabilities_api.supported(capability)

    async def get_capability(self, capability: str) -> Any:
        """Return value of capability.

        Args:
            capability:
                Dot-separated strings

                Example: `files.versioning`

        Returns:
            Value from server capabilities
        """
        return await self._capabilities_api.get_capability(capability)

    async def require_capability(self, capability: str) -> None:
        """Throw exception if server doesn't have a capability.

        Args:
            capability:
                Dot-separated strings

                Example: `files.versioning`

        Raises:
            NextcloudNotCapableError: When server doesn't support capability.
        """
        if not await self.has_capability(capability):
            raise NextcloudNotCapableError()

    def destroy_capabilities(self) -> None:
        """Force refresh of capabilities from server."""
        self._capabilities_api.destroy()

    async def _raise_response_exception(self, status_code: int, reason: str) -> None:
        """Optionally raise an exception based on response status_code.

        Args:
            status_code:
                Status code of response

            reason:
                Text string describing exception

        Raises:
            NextcloudError:
                Generic top-level exception to catch all exceptions.  See
                nextcloud_async.exceptions for all possible outcomes.

        """
        match status_code:
            case 401:
                if await self._wipe_requested():
                    raise NextcloudDeviceWipeRequestedError()
                else:
                    raise NextcloudUnauthorizedError(reason)
            case 403:
                if await self._wipe_requested():
                    raise NextcloudDeviceWipeRequestedError()
                else:
                    raise NextcloudForbiddenError(reason)
            case _:
                try:
                    exception = [
                        e for e in _EXCEPTIONS if e.status_code == status_code
                    ].pop()
                except IndexError:
                    if status_code >= 400:  # noqa: PLR2004
                        log.debug(f"Raising generic error. [{status_code}] {reason}")
                        raise NextcloudError(status_code=status_code, reason=str(reason))
                else:
                    raise exception(reason)

    async def get(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="GET"."""
        return await self.request(method="GET", path=path, data=data, headers=headers)

    async def get_raw(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="GET" and raw_response=True."""
        return await self.request(
            method="GET", path=path, data=data, headers=headers, raw_response=True
        )

    async def post(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="POST"."""
        return await self.request(method="POST", path=path, data=data, headers=headers)

    async def put(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="PUT"."""
        return await self.request(method="PUT", path=path, data=data, headers=headers)

    async def delete(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="DELETE"."""
        return await self.request(method="DELETE", path=path, data=data, headers=headers)

    async def propfind(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="PROPFIND"."""
        return await self.request(
            method="PROPFIND", path=path, data=data, headers=headers
        )

    async def mkcol(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="MKCOL"."""
        return await self.request(method="MKCOL", path=path, data=data, headers=headers)

    async def move(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="MOVE"."""
        return await self.request(method="MOVE", path=path, data=data, headers=headers)

    async def copy(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="COPY"."""
        return await self.request(method="COPY", path=path, data=data, headers=headers)

    async def proppatch(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="PROPPATCH"."""
        return await self.request(
            method="PROPPATCH", path=path, data=data, headers=headers
        )

    async def report(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Passthrough to self.request() with method="REPORT"."""
        return await self.request(method="REPORT", path=path, data=data, headers=headers)


class NextcloudModule(ABC):
    api: Any
    stub: str

    async def _get(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.get(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _get_raw(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.get_raw(
            path=f"{self.stub}{path}",
            data=data,
            headers=headers,
        )

    async def _post(
        self,
        data: Any | None = None,
        path: str = "",
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.post(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _put(
        self,
        data: Any | None = None,
        path: str = "",
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.put(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _delete(
        self,
        data: Any | None = None,
        path: str = "",
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.delete(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _propfind(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.propfind(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _mkcol(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.mkcol(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _move(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.move(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _copy(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.copy(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _proppatch(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.proppatch(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _report(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.report(
            path=f"{self.stub}{path}", data=data, headers=headers
        )


class NextcloudCapabilities:
    _instance: Optional["NextcloudCapabilities"] = None
    _capabilities: Dict[str, Any] = {}
    _version: Dict[str, Any] = {}

    client: NextcloudClient

    def __new__(cls, client: NextcloudClient) -> "NextcloudCapabilities":  # noqa: ARG004
        """Singleton pattern for Capabilities API."""
        if not cls._instance:
            log.debug("CREATING NEW CAPABILITIES OBJECT")
            cls._instance = super(NextcloudCapabilities, cls).__new__(cls)
        else:
            log.debug("RETURNING EXISTING CAPABILITIES OBJECT")
        return cls._instance

    def __init__(self, client: NextcloudClient) -> None:
        self.client = client

    @classmethod
    def destroy(cls) -> None:
        """Destroy singleton instance.

        This is useful for unit testing.
        """
        cls._instance = None

    async def _get_capabilities(self) -> Dict[str, Any]:
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


class NextcloudIterator:
    """Turn an object into an iterator.

    Inherit this object then use set_iterator to point to an internal list used for
    iteration.
    """

    def set_iterator(self, target: list, starting_index: int = 0) -> None:
        """Define the list over which this object will iterate.

        Args:
            target:
                local list

            starting_index:
                list index for first value.
        """
        self._iterator = target
        self._starting_index = starting_index

    def __iter__(self) -> Any:
        self._index = self._starting_index
        self._end = len(self._iterator)
        return self

    def __next__(self) -> Any:
        if self._index >= self._end:
            raise StopIteration
        else:
            self._index += 1
            return self._iterator[self._index - 1]

    def __len__(self) -> int:
        return len(self._iterator) - self._starting_index


class NextcloudIteratorModule(NextcloudModule): ...
