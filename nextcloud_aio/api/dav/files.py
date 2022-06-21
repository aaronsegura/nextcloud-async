import io

import xml.etree.ElementTree as etree

from typing import List, Optional, Union


class FileManager(object):
    async def list_files(self, path: str, properties: List[str] = []):
        """
        Return a list of files at `path`.

        If `properties` is passed, only those properties requested are
        returned.
        """
        data = None

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
        for t in properties:
            etree.SubElement(prop, t)

        tree = etree.ElementTree(root)

        # Write XML file to memory, then read it into `data`
        with io.BytesIO() as _mem:
            tree.write(_mem, xml_declaration=True)
            _mem.seek(0)
            data = _mem.read().decode('utf-8')

        return await self.dav_query(
            method='PROPFIND',
            sub=f'/remote.php/dav/files/{self.user}/{path}',
            data=data)

    async def download_file(self, path: str):
        """Download the file at `path`."""
        return (await self.request(
            method='GET',
            sub=f'/remote.php/dav/files/{self.user}/{path}',
            data={})).content

    async def upload_file(self, local_path: str, remote_path: str):
        """Upload a file."""
        with open(local_path, 'r') as fp:
            return await self.dav_query(
                method='PUT',
                sub=f'/remote.php/dav/files/{self.user}/{remote_path}',
                data=fp.read())

    async def create_folder(self, path: str):
        """Create a new folder/directory."""
        return await self.dav_query(
            method='MKCOL',
            sub=f'/remote.php/dav/files/{self.user}/{path}')

    async def delete(self, path: str):
        """Delete file or folder."""
        return await self.dav_query(
            method='DELETE',
            sub=f'/remote.php/dav/files/{self.user}/{path}')

    async def move(self, source: str, dest: str, overwrite: bool = False):
        """Move a file or folder."""
        return await self.dav_query(
            method='MOVE',
            sub=f'/remote.php/dav/files/{self.user}/{source}',
            headers={
                'Destination':
                    f'{self.endpoint}/remote.php/dav/files/{self.user}/{dest}',
                'Overwrite': 'T' if True else 'F'})

    async def copy(self, source: str, dest: str, overwrite: bool = False):
        """Move a file or folder."""
        return await self.dav_query(
            method='COPY',
            sub=f'/remote.php/dav/files/{self.user}/{source}',
            headers={
                'Destination':
                    f'{self.endpoint}/remote.php/dav/files/{self.user}/{dest}',
                'Overwrite': 'T' if overwrite else 'F'})

    async def __favorite(self, path: str, set: bool):
        """Set file/folder as a favorite."""
        data = f'''<?xml version="1.0"?>
                <d:propertyupdate
                    xmlns:d="DAV:"
                    xmlns:oc="http://owncloud.org/ns">
                <d:set><d:prop>
                <oc:favorite>{1 if set else 0}</oc:favorite>
                </d:prop></d:set></d:propertyupdate>
        '''

        return await self.dav_query(
            method='PROPPATCH',
            sub=f'/remote.php/dav/files/{self.user}/{path}',
            data=data)

    async def set_favorite(self, path: str):
        """Set file/folder as a favorite."""
        return await self.__favorite(path, True)

    async def remove_favorite(self, path: str):
        """Set file/folder as a favorite."""
        return await self.__favorite(path, False)

    async def get_favorites(self, path: Optional[str] = ''):
        """List favorites below given Path"""
        data = '''<?xml version="1.0"?><oc:filter-files  xmlns:d="DAV:"
        xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
        <oc:filter-rules><oc:favorite>1</oc:favorite></oc:filter-rules>
        </oc:filter-files>'''
        return await self.dav_query(
            method='REPORT',
            sub=f'/remote.php/dav/files/{self.user}/{path}',
            data=data)

    async def get_trashbin(self):
        """Return items in the trash."""
        return await self.dav_query(
            method='PROPFIND',
            sub=f'/remote.php/dav/trashbin/{self.user}/trash')

    async def restore_from_trashbin(self, path: str):
        """Restore a file from the trash."""
        return await self.dav_query(
            method='MOVE',
            sub=path,
            headers={
                'Destination':
                    f'{self.endpoint}/remote.php/dav/trashbin/{self.user}/restore/file'})

    async def empty_trashbin(self):
        """Empty the trash."""
        return await self.dav_query(
            method='DELETE',
            sub=f'/remote.php/dav/trashbin/{self.user}/trash')

    async def get_file_versions(self, file: Union[str, int]):
        """List of file versions."""
        file_id = file
        if isinstance(file, str):
            f = await self.list_files(file, properties=['oc:fileid'])
            file_id = f["d:propstat"]["d:prop"]["oc:fileid"]

        return await self.dav_query(
            method='PROPFIND',
            sub=f'/remote.php/dav/versions/{self.user}/versions/{file_id}')

    async def restore_file_version(self, path: str):
        """Restore an old file version."""
        return await self.dav_query(
            method='MOVE',
            sub=path,
            headers={
                'Destination':
                    f'{self.endpoint}/remote.php/dav/versions/{self.user}/restore/file'})

    async def upload_file_chunked(self, local_path: str, remote_path: str):
        """Upload a large file in chunks."""
        # TODO: write dav.upload_file_chunked
        pass
