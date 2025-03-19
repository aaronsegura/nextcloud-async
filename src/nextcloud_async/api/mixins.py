import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from nextcloud_async.api.modules import NextcloudModule

log = logging.getLogger("nextcloud_async.api")


@dataclass
class NextcloudDataObject(ABC):
    data: dict[str, Any]
    _api: NextcloudModule

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

        For example: `return self._api.get(self.id)`
        """
        raise NotImplementedError

    async def _refresh(self) -> None:
        log.debug("Refreshing object.")
        new_object = await self.refresh_function()
        log.debug(f"Setting new data {new_object.data}")
        self.data = new_object.data


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
