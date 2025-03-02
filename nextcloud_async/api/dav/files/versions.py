from dataclasses import dataclass

from urllib.parse import unquote

from typing import List, TYPE_CHECKING

from .base_file import BaseFile

if TYPE_CHECKING:
    from . import Files


class Version(BaseFile):

    def __str__(self) -> str:
        return f'<Nextcloud File Version "{unquote(self.href)}">'

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
        self._index = 1
        self._len = len(self._files)
        return self

    def __next__(self) -> Version:
        if self._index >= self._len:
            raise StopIteration
        else:
            self._index += 1
            return self._files[self._index - 1]

    def __len__(self) -> int:
        return len(self._files) - 1

    def __getitem__(self, index: int) -> Version:
        return self._files[index+1]
