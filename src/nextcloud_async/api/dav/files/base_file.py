from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .files import FilesApi


@dataclass
class BaseFile(ABC):
    data: dict[str, Any]
    files_api: "FilesApi"

    def __post_init__(self) -> None:
        """Do some translation.

        d:propstat could contain multiple dicts in a list if any requested properties
        could not be found.  In this case, we disregard any 404 properties and only
        populate our local data['_properties'] with successfully retrieved properties.
        """
        if isinstance(self.data["d:propstat"], list):
            for propdict in self.data["d:propstat"]:
                if "200 OK" in propdict["d:status"]:
                    self.data["_properties"] = propdict["d:prop"]

        if isinstance(self.data["d:propstat"], dict):
            if "200 OK" in self.data["d:propstat"]["d:status"]:
                self.data["_properties"] = self.data["d:propstat"]["d:prop"]

    def __getattr__(self, k: str) -> Any:
        """Return a property of a given file.

        Our local data is populated with the results of all the properties
        retrieved from the server.  Unfortunately, the keys are all namespaced
        (eg, 'oc:fileid', 'nc:has-preview'), and some of them potentially have
        a dash ("-") in the name, which is an illegal character in a python class
        attribute.  In order to facilitate easy retrieval of these values, this
        __getattr__ will translate underscores to dashes and search for key names
        without the namespace prefix.

        For example, these will both work if ['oc:fileid', 'nc:has-preview'] are
        passed in as properties:

            file.fileid
            file.has_preview

        Args:
            k:
                The property key

        Raises:
            KeyError: When property cannot be found

        Returns:
            Property value
        """
        translated_key = k.replace("_", "-")

        keys = self.data.keys()
        for key in keys:
            if key.endswith(f":{translated_key}") or key == k:
                try:
                    return int(self.data[key])
                except (ValueError, TypeError):
                    return self.data[key]

        keys = self.data["_properties"].keys()
        for key in keys:
            if key.endswith(f":{translated_key}") or key == k:
                try:
                    return int(self.data["_properties"][key])
                except (ValueError, TypeError):
                    return self.data["_properties"][key]

        raise KeyError

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __repr__(self) -> str: ...
