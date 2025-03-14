import logging

from httpx import BasicAuth

from abc import ABC, abstractmethod

from typing import Dict, Any, Optional

from nextcloud_async.client import NextcloudClient

from nextcloud_async.exceptions import (
    NextcloudBadRequestError,
    NextcloudForbiddenError,
    NextcloudNotModifiedError,
    NextcloudUnauthorizedError,
    NextcloudDeviceWipeRequestedError,
    NextcloudNotFoundError,
    NextcloudTooManyRequestsError,
    NextcloudConflictError,
    NextcloudPreconditionError,
    NextcloudNotCapableError,
    NextcloudError,
    NextcloudUnsupportedMediaTypeError,
    NextcloudMethodNotAllowedError,
)

log = logging.getLogger(__name__)


class NextcloudHttpApi(ABC):
    """Methods imported by different Nextcloud API drivers."""

    capabilities_api: "NextcloudCapabilities"

    def __init__(self, client: NextcloudClient) -> None:
        self.client = client

    @abstractmethod
    async def request(
        self,
        method: str = "GET",
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any: ...

    @abstractmethod
    async def raise_response_exception(self, status_code: int, reason: str): ...

    async def raw_request(
        self,
        method: str = "GET",
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any: ...

    def _munge_path_data(self, data: Optional[dict[str, Any]] = None, path: str = ""):
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

    async def _wipe_requested(self) -> bool:
        from nextcloud_async.api import Wipe

        wipe = Wipe(self.client)
        return await wipe.check()

    async def has_capability(self, capability: str) -> bool:
        return await self.capabilities_api.supported(capability)

    async def require_capability(self, capability: str) -> None:
        if not await self.has_capability(capability):
            raise NextcloudNotCapableError()

    async def _raise_response_exception(self, status_code: int, reason: str):
        match status_code:
            case 304:
                raise NextcloudNotModifiedError()
            case 400:
                raise NextcloudBadRequestError(reason)
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
            case 404:
                raise NextcloudNotFoundError(reason)
            case 405:
                raise NextcloudMethodNotAllowedError(reason)
            case 415:
                raise NextcloudUnsupportedMediaTypeError(reason)
            case 429:
                raise NextcloudTooManyRequestsError()
            case 409:
                raise NextcloudConflictError(reason)
            case 412:
                raise NextcloudPreconditionError(reason)
            case 499:
                raise NextcloudNotCapableError(reason)
            case _:
                pass

        if status_code >= 400:
            raise NextcloudError(status_code=status_code, reason=str(reason))

    async def get(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(method="GET", path=path, data=data, headers=headers)

    async def get_raw(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.raw_request(method="GET", path=path, data=data, headers=headers)

    async def post(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(method="POST", path=path, data=data, headers=headers)

    async def put(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(method="PUT", path=path, data=data, headers=headers)

    async def delete(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(method="DELETE", path=path, data=data, headers=headers)

    async def propfind(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(
            method="PROPFIND", path=path, data=data, headers=headers
        )

    async def mkcol(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(method="MKCOL", path=path, data=data, headers=headers)

    async def move(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(method="MOVE", path=path, data=data, headers=headers)

    async def copy(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(method="COPY", path=path, data=data, headers=headers)

    async def proppatch(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(
            method="PROPPATCH", path=path, data=data, headers=headers
        )

    async def report(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.request(method="REPORT", path=path, data=data, headers=headers)


class NextcloudModule(ABC):
    api: Any
    stub: str

    async def _get(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.get(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _get_raw(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.get_raw(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _post(
        self,
        data: Optional[Any] = None,
        path: str = "",
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.post(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _put(
        self,
        data: Optional[Any] = None,
        path: str = "",
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.put(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _delete(
        self,
        data: Optional[Any] = None,
        path: str = "",
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.delete(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _propfind(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.propfind(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _mkcol(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.mkcol(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _move(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.move(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _copy(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.copy(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _proppatch(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.proppatch(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _report(
        self,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.api.report(
            path=f"{self.stub}{path}", data=data, headers=headers
        )


class NextcloudCapabilities:
    _instance: Optional["NextcloudCapabilities"] = None
    _capabilities: Dict[str, Any] = {}
    _version: Dict[str, Any] = {}

    client: NextcloudClient

    def __new__(cls, client: NextcloudClient):
        if not cls._instance:
            cls._instance = super(NextcloudCapabilities, cls).__new__(cls)
        return cls._instance

    def __init__(self, client: NextcloudClient):
        self.client = client

    async def _get_capabilities(self) -> Dict[str, Any]:
        """Populate local capabilities cache for this server."""
        headers = {"OCS-APIRequest": "true"}
        if self.client.app_token:
            auth = None
            headers["Authorization"] = f"Bearer {self.client.app_token}"
        elif self.client.password:
            auth = BasicAuth(self.client.user, self.client.password)

        response = await self.client.http_client.request(
            method="GET",
            auth=auth,
            url=f"{self.client.endpoint}/ocs/v1.php/cloud/capabilities?format=json",
            headers=headers,
        )
        return response.json()["ocs"]["data"]

    async def _pop_capabilities(self):
        response = await self._get_capabilities()
        self._capabilities = response["capabilities"]
        self._version = response["version"]

    async def get_all(self) -> dict[str, Any]:
        if not self._capabilities:
            await self._pop_capabilities()
        return self._capabilities

    async def supported(self, capability: str) -> bool:
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

        return True

    async def server_version(self) -> dict[str, str]:
        if not self._version:
            await self._pop_capabilities()
        return self._version


class NextcloudIterator:
    def set_iterator(self, target: list, starting_index: int = 0):
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
