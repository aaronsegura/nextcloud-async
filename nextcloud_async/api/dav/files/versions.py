from dataclasses import dataclass

from urllib.parse import unquote

from typing import List, TYPE_CHECKING

from .base_file import BaseFile

if TYPE_CHECKING:
    from . import Files


class Version(BaseFile):

    def __str__(self) -> str:
        return f'<Nextcloud File Version #{self.fileid} "{unquote(self.href)}">'

    def __repr__(self) -> str:
        return f'<Nextcloud File Version {self.data}>'

    @property
    def path(self) -> str:
        """File path relative to user data directory.

        Returns:
            File path
        """
        return '/{}'.format('/'.join(self.data['d:href'].split('/')[3:]))

    async def restore(self) -> None:
        """Restore a trashbin file to former glory."""
        return await self.files_api.restore_version(self.path)


@dataclass
class Versions:
    """Class for making sense of Nextcloud Trashbins."""
    _files: List[Version]
    files_api: 'Files'

    def __iter__(self) -> 'Versions':
        self._index = 0
        self._len = len(self._files)
        return self

    def __next__(self) -> Version:
        if self._index >= self._len:
            raise StopIteration
        else:
            self._index += 1
            return self._files[self._index - 1]

    @property
    def files(self) -> List[Version]:
        """Filter out the trashbin object itself and return just trash files.

        Returns:
            List of Version
        """
        user = self.files_api.api.client.user
        return [
            file for file in self._files
            if file.href != f'/remote.php/dav/trashbin/{user}/trash/']
