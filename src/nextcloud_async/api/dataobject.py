import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from nextcloud_async.driver import NextcloudModule

log = logging.getLogger("nextcloud_async.api")


@dataclass
class NextcloudDataObject(ABC):
    data: dict[str, Any]
    self_api: NextcloudModule

    _refresh_fn: Awaitable | None = field(init=False, default=None)

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __eq__(self, other: "NextcloudDataObject") -> bool: ...

    def __getitem__(self, k: str) -> Any:
        return self.data[k]

    def __getattr__(self, k: str) -> Any:
        # Nextcloud likes to use dashes in keys.  We translate them to underscores.
        translated_key = k.replace("_", "-")
        for key in self.data.keys():
            if key in (translated_key, k):
                # Translate string'd integers
                if isinstance(self.data[key], str):
                    try:
                        return int(self.data[key])
                    except (ValueError, TypeError):
                        return self.data[key]
                else:
                    return self.data[key]

        return self.data[k]

    def __repr__(self) -> str:
        return f"<{__class__.__name__} data={str(self.data)}>"

    def refresh_function(self) -> Coroutine[None, None, "NextcloudDataObject"]:
        """Define how this object is refreshed when calling self._refresh().

        For example: `return self.self_api.get(self.id)`
        """
        raise NotImplementedError

    async def _refresh(self) -> None:
        log.debug("Refreshing object.")
        new_object = await self.refresh_function()
        log.debug(f"Setting new data {new_object.data}")
        self.data = new_object.data
