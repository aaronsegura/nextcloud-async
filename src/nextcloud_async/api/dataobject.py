from abc import ABC, abstractmethod
from collections.abc import Awaitable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from nextcloud_async.driver import NextcloudModule


@dataclass
class NextcloudDataObject(ABC):
    data: dict[str, Any]
    self_api: NextcloudModule

    _refresh_fn: Awaitable | None = field(init=False, default=None)

    @abstractmethod
    def __str__(self) -> str: ...

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __repr__(self) -> str:
        return str(self.data)

    async def async_refresh(self) -> Coroutine[None, None, "NextcloudDataObject"]:
        """Define how this object is refreshed when calling self._refresh().

        For example: `return self.self_api.get(self.id)`
        """
        raise NotImplementedError

    async def _refresh(self) -> None:
        new_object = await self.async_refresh()
        self.data = new_object.data  # type: ignore
