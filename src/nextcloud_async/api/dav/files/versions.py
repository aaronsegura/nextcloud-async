from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import unquote

from nextcloud_async.api.mixins import NextcloudIterator

from .base_file import BaseFile

if TYPE_CHECKING:
    from . import FilesApi


class Version(BaseFile):
    def __str__(self) -> str:
        return f'<Nextcloud File Version "{unquote(self.href)}">'

    def __repr__(self) -> str:
        return f"<Nextcloud File Version {self.data}>"

    @property
    def path(self) -> str:
        """File path relative to user data directory.

        Returns:
            File path

        """
        return "/{}".format("/".join(self.data["d:href"].split("/")[3:]))

    async def restore(self) -> None:
        """Restore a trashbin file to former glory."""
        return await self.files_api.restore_version(self.path)


@dataclass
class Versions(NextcloudIterator):
    """Class for making sense of Nextcloud Trashbins."""

    _files: list[Version]
    files_api: "FilesApi"

    def __post_init__(self) -> None:
        self.set_iterator(self._files, starting_index=1)

    def __getitem__(self, index: int) -> Version:
        return self._files[index + 1]
