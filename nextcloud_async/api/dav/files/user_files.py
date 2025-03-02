
from dataclasses import dataclass

from typing import List, Optional, Any

from urllib.parse import unquote

from .base_file import BaseFile
from .versions import Versions

class UserFile(BaseFile):

    def __str__(self) -> str:
        return f'<Nextcloud File #{self.fileid} "{unquote(self.path)}">'

    def __repr__(self) -> str:
        return f'<Nextcloud File {self.data}>'

    @property
    def path(self) -> str:
        """File path relative to user data directory.

        Returns:
            File path
        """
        return '/{}'.format('/'.join(self.data['d:href'].split('/')[5:]))

    async def download(self) -> bytes:
        """Download this file."""
        return await self.files_api.download(self.path)

    async def delete(self) -> None:
        """Delete this file."""
        return await self.files_api.delete(self.path)

    async def move(self, dest: str, overwrite: bool = False) -> None:
        """Move this file.

        Args:
            dest:
                Destination path

            overwrite:
                Overwrite destination if it exists
        """
        return await self.files_api.move(
            source=self.path,
            dest=dest,
            overwrite=overwrite)

    async def copy(self, dest: str, overwrite: bool= False) -> None:
        """Copy file.

        Args:
            dest:
                Copy destination relative to user root

            overwrite:
                Overwrite destination if it exists
        """
        await self.files_api.copy(
            source=self.path,
            dest=dest,
            overwrite=overwrite)

    async def set_favorite(self) -> None:
        """Mark this file as a favorite."""
        await self.files_api.set_favorite(self.path)
        self.favorite = True

    async def unset_favorite(self) -> None:
        """Remove this file from favorites."""
        await self.files_api.unset_favorite(self.path)

    async def get_versions(self) -> Versions:
        """List older versions of this file."""
        return await self.files_api.get_versions(self.fileid)


@dataclass
class UserPath:
    """Class for making sense of Nextcloud directories.

    The Files.list() API returns this object.  If the original request
    to Files.list() was for a directory, the File object representing the
    directory can be found at Path.dir and the files contained within the
    directory can be found at Path.files.

    If the original request to Files.list() was for a specific file, that
    file can be found at Path.file.

    This object can be interrogated as to whether it represents a file or a
    directory using the Path.is_file and Path.is_dir properties.
    """
    _path: str
    _files: List[UserFile]

    def __iter__(self) -> 'UserPath':
        self._index = 0
        self._len = len(self._files)
        return self

    def __next__(self) -> UserFile:
        if self._index >= self._len:
            raise StopIteration
        else:
            self._index += 1
            return self._files[self._index - 1]

    def __len__(self) -> int:
        if self.is_dir:
            return len(self._files) - 1
        if self.is_file:
            return 1
        return 0

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
            KeyError: When this is a directory listing.

        Returns:
            Property value
        """
        translated_key = k.replace('_', '-')

        if self.is_file:
            try:
                return self._file.__getattribute__(k)
            except AttributeError:
                pass

        if self.is_dir:
            try:
                return self._dir.__getattribute__(k)
            except AttributeError:
                pass

        keys = self._self.data.keys()
        for key in keys:
            if key.endswith(f':{translated_key}') or key == k:
                try:
                    return int(self._self.data[key])
                except (ValueError, TypeError):
                    return self._self.data[key]

        keys = self._self.data['_properties'].keys()
        for key in keys:
            if key.endswith(f':{translated_key}') or key == k:
                try:
                    return int(self._self.data['_properties'][key])
                except (ValueError, TypeError):
                    return self._self.data['_properties'][key]

        raise KeyError

    def __getitem__(self, index):
        return self._files[index]

    @property
    def _self(self) -> UserFile:
        return [file for file in self._files
            if self._path.rstrip('/') == file.path.rstrip('/')].pop()

    @property
    def is_dir(self) -> bool:
        """Return True if this object represents a irectory."""
        if self._self.resourcetype:
            if 'd:collection' in self._self.resourcetype:
                return True
        return False

    @property
    def is_file(self) -> bool:
        """Return True if this object represents a single file."""
        return not self.is_dir

    @property
    def _file(self) -> Optional[UserFile]:
        return self._self

    @property
    def _dir(self) -> Optional[UserFile]:
        if self.is_dir:
            return self._self
