from dataclasses import dataclass
from typing import TYPE_CHECKING, List
from urllib.parse import unquote

from nextcloud_async.driver import NextcloudIterator

from .base_file import BaseFile

if TYPE_CHECKING:
    from . import Files


class TrashFile(BaseFile):
    def __str__(self) -> str:
        return f'<Nextcloud Trash File #{self.fileid} "{unquote(self.href)}">'

    def __repr__(self) -> str:
        return f"<Nextcloud Trash File {self.data}>"

    @property
    def path(self) -> str:
        """File path relative to user data directory.

        Returns:
            File path
        """
        return "/{}".format("/".join(self.data["d:href"].split("/")[3:]))

    async def delete(self) -> None:
        """Delete this file."""
        return await self.files_api.delete_trash(self.path)

    async def restore(self) -> None:
        """Restore a trashbin file to former glory."""
        return await self.files_api.restore_trash(self.path)


@dataclass
class Trashbin(NextcloudIterator):
    """Class for making sense of Nextcloud Trashbins."""

    _files: List[TrashFile]
    files_api: "Files"

    def __post_init__(self) -> None:
        self.set_iterator(self._files, 1)

    @property
    def files(self) -> List[TrashFile]:
        """Filter out the trashbin object itself and return just trash files.

        Returns:
            List of Trash
        """
        user = self.files_api.api.client.user
        return [
            file
            for file in self._files
            if file.href != f"/remote.php/dav/trashbin/{user}/trash/"
        ]

    async def empty(self) -> None:
        """Empty the trashbin."""
        await self.files_api.empty_trashbin()
