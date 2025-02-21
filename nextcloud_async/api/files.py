"""Implement Nextcloud DAV API for File Management.

    https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
"""
import io
import os
import uuid
import json
import re
import httpx

import platformdirs as pdir
import xml.etree.ElementTree as etree

from urllib.parse import quote

from dataclasses import dataclass

from typing import List, Optional, Any, Dict, ByteString

from nextcloud_async.driver import NextcloudModule, NextcloudDavApi
from nextcloud_async.client import NextcloudClient
from nextcloud_async.helpers import remove_key_prefix

from nextcloud_async.exceptions import (
    NextcloudChunkedUploadException,
    NextcloudException)

@dataclass
class File:
    data: Dict[str, Any]
    files_api: 'Files'

    def __post_init__(self):
        if isinstance(self.data['d:propstat'], list):
            for prop in self.data['d:propstat']:
                self.data.update(prop['d:prop'])
        elif isinstance(self.data['d:propstat'], dict):
            self.data.update(self.data['d:propstat'])

        self.data = remove_key_prefix(self.data)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Nextcloud File "{self.path}">'

    def __repr__(self):
        return f'<Nextcloud File {self.data}>'

    @property
    def path(self):
        return '/{}'.format('/'.join(self.href.split('/')[5:]))

    @property
    def _trash_path(self):
        if self.is_trash:
            return '/{}'.format('/'.join(self.href.split('/')[3:]))
        else:
            raise NextcloudException(status_code=400, reason='File is not a trashbin file.')

    @property
    def is_trash(self):
        return self.href.startswith('/remote.php/dav/trashbin/')

    @property
    def _version_path(self):
        if self.is_version:
            return '/{}'.format('/'.join(self.href.split('/')[3:]))
        else:
            raise NextcloudException(status_code=400, reason='File is not a version file.')

    @property
    def is_version(self):
        return self.href.startswith('/remote.php/dav/versions/')

    async def download(self):
        return await self.files_api.download(self.path)

    async def delete(self):
        return await self.files_api.delete(self.path)

    async def move(self, **kwargs):
        return await self.files_api.move(source=self.path, **kwargs)

    async def copy(self, **kwargs):
        return await self.files_api.copy(source=self.path, **kwargs)

    async def set_favorite(self):
        await self.files_api.set_favorite(self.path)
        self.favorite = True

    async def unset_favorite(self):
        return await self.files_api.unset_favorite(self.path)

    async def restore_trash(self):
        return await self.files_api.restore_trash(self._trash_path)

    # TODO: No errors, but also doesn't restore :/
    async def restore_version(self):
        print(f"restoring {self._version_path}")
        return await self.files_api.restore_version(self._version_path)


class Files(NextcloudModule):
    """Interact with Nextcloud DAV Files Endpoint."""
    def __init__(
            self,
            client: NextcloudClient):
        self.client= client
        self.api = NextcloudDavApi(client)
        self.stub = ''

    def _namespace_properties(self, properties: List[str]):
        data: str = ''

        default_properties = [
            'd:getlastmodified',
            'd:getetag',
            'd:getcontenttype',
            'd:resourcetype',
            'd:getcontentlength',
            'oc:fileid']

        # if user passes in parameters, they must be built into an Element
        # tree so they can be dumped to an XML document and then sent
        # as the query body
        root = etree.Element(
            "d:propfind",
            attrib={
                'xmlns:d': 'DAV:',
                'xmlns:oc': 'http://owncloud.org/ns',
                'xmlns:nc': 'http://nextcloud.org/ns'})
        prop = etree.SubElement(root, 'd:prop')
        for t in default_properties + properties:
            etree.SubElement(prop, t)

        tree = etree.ElementTree(root)

        # Write XML file to memory, then read it into `data`
        with io.BytesIO() as _mem:
            tree.write(_mem, xml_declaration=True)
            _mem.seek(0)
            data = _mem.read().decode('utf-8')

        return data

    async def list(self, path: str, properties: List[str] = []) -> List[File]:
        """Return a list of files at `path`.

        If `properties` is passed, only those properties requested are
        returned.

        Always return a list, even if path is a file.

        Args
        ----
            path (str): Filesystem path

            properties (list, optional): List of properties to return. Defaults to [].

        Returns
        -------
            list: Files
        """
        data = self._namespace_properties(properties)
        response: List[Dict[str, Any]] | Dict[str, Any] = await self._propfind(
            path=f'/files/{self.client.user}/{path}',
            data=data)

        if isinstance(response, list):
            return [File(data, self) for data in response]
        else:
            return [File(response, self)]

    async def download(self, path: str) -> ByteString:
        """Download the file at `path`.

        Args
        ----
            path (str): File path

        Returns
        -------
            str: File content
        """
        return await self._get_raw(
            path=f'/files/{self.client.user}/{path}')

    async def upload(self, local_path: str, remote_path: str) -> None:
        """Upload a file.

        Args
        ----
            local_path (str): Local path

            remote_path (str): Desination path
        """
        with open(local_path, 'rb') as fp:
            await self._put(
                path=f'/files/{self.client.user}/{remote_path}',
                data=fp.read())

    async def mkdir(self, path: str, create_parents: bool = False) -> None:
        """Create a new folder/directory.

        Args
        ----
            path (str): Filesystem path

            create_parents (bool): Create directory parents (mkdir -p)
        """
        if create_parents:
            await self.mkdir_with_parents(path)
            return

        await self._mkcol(path=f'/files/{self.client.user}/{path}')

    async def delete(self, path: str) -> None:
        """Delete file or folder.

        Args
        ----
            path (str): Filesystem path
        """
        await self._delete(path=f'/files/{self.client.user}/{path}')

    async def move(self, source: str, dest: str, overwrite: bool = False) -> None:
        """Move a file or folder.

        Args
        ----
            source (str): Source path

            dest (str): Destination path

            overwrite (bool, optional): Overwrite destination if exists. Defaults to False.
        """
        return await self._move(
            path=f'/files/{self.client.user}/{source}',
            headers={
                'Destination':
                    f'{self.client.endpoint}/remote.php/dav/files/{self.client.user}/{quote(dest)}',
                'Overwrite': 'T' if overwrite else 'F'})

    async def copy(self, source: str, dest: str, overwrite: bool = False) -> None:
        """Copy a file or folder.

        Args
        ----
            source (str): Source path

            dest (str): Destination path

            overwrite (bool, optional): Overwrite destination if exists. Defaults to False.
        """
        await self._copy(
            path=f'/files/{self.client.user}/{source}',
            headers={
                'Destination':
                    f'{self.client.endpoint}/remote.php/dav/files/{self.client.user}/{quote(dest)}',
                'Overwrite': 'T' if overwrite else 'F'})

    async def __favorite(self, path: str, set: bool) -> Dict[str, Any]:
        """Set file/folder as a favorite.

        Args
        ----
            path (str): Filesystem path

            set (bool): Make favorite

        Returns
        -------
            dict: file info
        """
        data = f'''<?xml version="1.0"?>
                <d:propertyupdate
                    xmlns:d="DAV:"
                    xmlns:oc="http://owncloud.org/ns">
                <d:set><d:prop>
                <oc:favorite>{1 if set else 0}</oc:favorite>
                </d:prop></d:set></d:propertyupdate>
        '''

        return await self._proppatch(
            path=f'/files/{self.client.user}/{path}',
            data=data)

    async def set_favorite(self, path: str) -> File:
        """Set file/folder as a favorite.

        Args
        ----
            path (str): Filesystem path

        Returns
        -------
            dict: File info
        """
        response = await self.__favorite(path, True)
        return File(response, self.api)

    async def unset_favorite(self, path: str) -> File:
        """Remove file/folder as a favorite.

        Args
        ----
            path (str): Filesystem path

        Returns
        -------
            dict: File info
        """
        response = await self.__favorite(path, False)
        return File(response, self.api)

    async def get_favorites(self, path: Optional[str] = '') -> List[File]:
        """List favorites below given Path.

        Args
        ----
            path (str, optional): Filesystem path. Defaults to ''.

        Returns
        -------
            list: list of favorites
        """
        data = '''<?xml version="1.0"?><oc:filter-files  xmlns:d="DAV:"
        xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
        <oc:filter-rules><oc:favorite>1</oc:favorite></oc:filter-rules>
        </oc:filter-files>'''
        response =  await self._report(
            path=f'/files/{self.client.user}/{path}',
            data=data)
        return [File(data, self.api) for data in response]

    async def list_trash(self) -> List[File]:
        """Get items in the trash.

        Returns
        -------
            list: Trashed items
        """
        response = await self._propfind(path=f'/trashbin/{self.client.user}/trash')
        return [File(data, self) for data in response]

    async def restore_trash(self, path: str) -> None:
        """Restore a file from the trash.

        Args
        ----
            path (str): Trash path
        """
        await self._move(
            path=path,
            headers={
                'Destination':
                    f'{self.client.endpoint}/remote.php/dav/trashbin/{self.client.user}/restore/file'})

    async def empty_trashbin(self) -> None:
        """Empty the trash."""
        await self._delete(path=f'/trashbin/{self.client.user}/trash')

    async def list_versions(self, file_id: int) -> List[File]:
        """List of file versions.

        Args
        ----
            file_id (int): File ID

        Returns
        -------
            list: File versions
        """
        response = await self._propfind(path=f'/versions/{self.client.user}/versions/{file_id}')
        return [File(data, self) for data in response]

    async def restore_version(self, path: str) -> None:
        """Restore an old file version.

        Args
        ----
            path (str): File version path
        """
        await self._move(
            path=path,
            headers={
                'Destination':
                    f'{self.client.endpoint}/remote.php/dav/versions/{self.client.user}/restore/file'})

    def __replace_slashes(self, string: str):
        """Replace path slashes with underscores."""
        return string.replace('/', '_').replace('\\', '_')

    async def mkdir_with_parents(self, path: str) -> None:
        """Create folder with parents (mkdir -p).

        Args
        ----
            path (str): Path to folder

        Raises
        ------
            NextcloudException: Errors from self.create_folder()
        """
        path_chunks = path.strip('/').split('/')
        for count in range(1, len(path_chunks) + 1):
            try:
                await self.mkdir("/".join(path_chunks[0:count]))
            except NextcloudException as e:
                if 'already exists' not in str(e):
                    raise

    async def __upload_file_chunk(self, local_path: str, uuid_dir: str) -> httpx.Response:
        with open(local_path, 'rb') as fp:
            return await self._put(
                path=f'/uploads/{self.client.user}/{uuid_dir}/{os.path.basename(local_path)}',
                data=fp.read())

    async def __assemble_chunks(
            self,
            uuid_dir: str,
            remote_path: str) -> httpx.Response:
        return await self._move(
            path=f'/uploads/{self.client.user}/{uuid_dir}/.file',
            headers={
                'Destination':
                    f'{self.client.endpoint}/remote.php/dav/files/'
                    f'{self.client.user}/{quote(remote_path.strip("/"))}',
                'Overwrite': 'T'})

    async def upload_file_chunked(
            self,
            local_path: str,
            remote_path: str,
            chunk_size: int):
        """Upload a large file in chunks.

        https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/chunking.html

        Args
        ----
            local_path (str): Local file to upload

            remote_path (str): Remote path for finished file

            chunk_size (int): Upload file this many bytes per chunk

        Raises
        ------
            NextcloudChunkedCacheExists: When previous failed attempt is detected.
        """
        file_position = 0
        padding = len(str(os.stat(local_path).st_size))

        local_path_escaped = self.__replace_slashes(local_path)
        remote_path_escaped = self.__replace_slashes(remote_path)
        uuid_dir = str(uuid.uuid4())

        local_cache_dir = \
            f'{pdir.user_cache_dir("nextcloud-async")}' \
            f'/chunked_uploads/{local_path_escaped}-{remote_path_escaped}'

        try:
            os.makedirs(local_cache_dir)
        except OSError:
            # Cache maybe exists, read metadata and attempt to resume upload
            with open(f'{local_cache_dir}/metadata.json', 'r') as metadata_fp:
                metadata = json.loads(metadata_fp.read())
                uuid_dir = metadata['uuid']
        else:
            # Write metadata to file in case of error uploading
            with open(f'{local_cache_dir}/metadata.json', 'w') as metadata_fp:
                metadata = {'uuid': uuid_dir}
                metadata_fp.write(json.dumps(metadata))

        resume_chunk = None
        for file in os.listdir(local_cache_dir):
            # Check for existing chunk, resume there and proceed with
            # rest of file.
            if (span := re.match(r'[0-9]+-([0-9]+)$', file)):
                if resume_chunk:
                    raise NextcloudChunkedUploadException()
                resume_chunk = file
                file_position = int(span[1])

        if resume_chunk:
            await self.__upload_file_chunk(f'{local_cache_dir}/{resume_chunk}', uuid_dir)
            os.remove(f'{local_cache_dir}/{resume_chunk}')
        else:
            # Make remote upload directory
            await self._mkcol(
                path=f'/uploads/{self.client.user}/{uuid_dir}')

        with open(local_path, 'rb') as source_fp:
            source_fp.seek(file_position)
            while (data := source_fp.read(chunk_size)):
                chunk_name = \
                    f'{file_position:0{padding}}-{(file_position + len(data)):0{padding}}'
                with open(f'{local_cache_dir}/{chunk_name}', 'wb') as chunk_fp:
                    chunk_fp.write(data)
                file_position += len(data)
                await self.__upload_file_chunk(f'{local_cache_dir}/{chunk_name}', uuid_dir)
                os.remove(f'{local_cache_dir}/{chunk_name}')

        # Assemble chunks.  Server takes care of directory removal.
        await self.__assemble_chunks(uuid_dir, remote_path.strip('/'))

        # Remove local cache directory
        for file in os.listdir(local_cache_dir):
            os.remove(f'{local_cache_dir}/{file}')
        os.rmdir(local_cache_dir)

    async def get_groupfolder_acl(self, path: str, inherited: bool=False) -> List[Dict[str, Any]]:
        """Return a list of groupfolder ACL rules set for `path`.

        Args
        ----
            path (str): Filesystem path
            inherited (bool): Return inherited rules instead of normal rules

        Returns
        -------
            list: ACL rules
        """
        data = None
        ruleprop = 'nc:acl-list'
        if inherited:
            ruleprop = 'nc:inherited-acl-list'

        root = etree.Element(
            "d:propfind",
            attrib={
                'xmlns:d': 'DAV:',
                'xmlns:oc': 'http://owncloud.org/ns',
                'xmlns:nc': 'http://nextcloud.org/ns'})
        prop = etree.SubElement(root, 'd:prop')
        etree.SubElement(prop, ruleprop)

        tree = etree.ElementTree(root)

        # Write XML file to memory, then read it into `data`
        with io.BytesIO() as _mem:
            tree.write(_mem, xml_declaration=True)
            _mem.seek(0)
            data = _mem.read().decode('utf-8')

        result = await self._propfind(
            path=f'/files/{self.client.user}/{path}',
            data=data)

        ret: List[Dict[str, Any]] = []
        if result['d:propstat']['d:prop'][ruleprop]:
            ret = result['d:propstat']['d:prop'][ruleprop]['nc:acl']
        else:
            ret = []

        if type(result) is not list:
            return [result]

        return ret

    async def set_groupfolder_acl(self, path: str, acls: List[Dict[str, Any]]):
        """Apply a list of groupfolder ACL rules to `path`.

        Args
        ----
            path (str): Filesystem path
            acls (List[Dict[str, Any]]): List of ACL rule dicts

        Returns
        -------
            Empty 200 Response
        """
        data = None

        root = etree.Element(
            "d:propertyupdate",
            attrib={
                'xmlns:d': 'DAV:',
                'xmlns:oc': 'http://owncloud.org/ns',
                'xmlns:nc': 'http://nextcloud.org/ns'})
        prop = etree.SubElement(root, 'd:set')
        prop = etree.SubElement(prop, 'd:prop')
        prop = etree.SubElement(prop, 'nc:acl-list')
        for acl in acls:
            aclprop = etree.SubElement(prop, 'nc:acl')
            for key, val in acl.items():
                child = etree.Element(key)
                child.text = str(val)
                aclprop.append(child)

        tree = etree.ElementTree(root)

        # Write XML file to memory, then read it into `data`
        with io.BytesIO() as _mem:
            tree.write(_mem, xml_declaration=True)
            _mem.seek(0)
            data = _mem.read().decode('utf-8')

        return (await self._proppatch(
            path=f'/files/{self.client.user}/{path}',
            data=data))
