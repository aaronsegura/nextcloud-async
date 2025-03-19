"""Nextcloud DAV API for File Management.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
"""

import io
import json
import os
import re
import uuid
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import quote

import httpx
import platformdirs as pdir
from aiofile import async_open

from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudDavDriver
from nextcloud_async.exceptions import (
    NextcloudBadRequestError,
    NextcloudChunkedUploadError,
    NextcloudError,
)

from .trashbin import Trashbin, TrashFile
from .user_files import UserFile, UserPath
from .versions import Version, Versions


class FilesApi(NextcloudModule):
    """Interact with Nextcloud DAV Files Endpoint."""

    def __init__(self, dav_driver: NextcloudDavDriver) -> None:
        self.driver = dav_driver
        self.stub = ""

    def _namespace_favorites_properties(self, properties: list[str]) -> str:
        data: str = ""
        default_properties = ["oc:fileid", "d:resourcetype", "oc:favorite"]

        # if user passes in properties, they must be built into an Element
        # tree so they can be dumped to an XML document and then sent
        # as the query body
        root = ET.Element(
            "oc:filter-files",
            attrib={
                "xmlns:d": "DAV:",
                "xmlns:oc": "http://owncloud.org/ns",
                "xmlns:nc": "http://nextcloud.org/ns",
            },
        )
        filter_rules = ET.SubElement(root, "oc:filter-rules")
        ET.SubElement(filter_rules, "oc:favorite").text = "1"
        prop = ET.SubElement(root, "d:prop")
        for p in properties + default_properties:
            ET.SubElement(prop, p)

        tree = ET.ElementTree(root)
        # Write XML file to memory, then read it into `data`
        with io.BytesIO() as _mem:
            tree.write(_mem, xml_declaration=True)
            _mem.seek(0)
            data = _mem.read().decode("utf-8")

        return data

    def _namespace_properties(self, properties: list[str]) -> str:
        data: str = ""

        default_properties = ["oc:fileid", "d:resourcetype"]

        # if user passes in parameters, they must be built into an Element
        # tree so they can be dumped to an XML document and then sent
        # as the query body
        root = ET.Element(
            "d:propfind",
            attrib={
                "xmlns:d": "DAV:",
                "xmlns:oc": "http://owncloud.org/ns",
                "xmlns:nc": "http://nextcloud.org/ns",
            },
        )
        prop = ET.SubElement(root, "d:prop")
        for t in default_properties + properties:
            ET.SubElement(prop, t)

        tree = ET.ElementTree(root)

        # Write XML file to memory, then read it into `data`
        with io.BytesIO() as _mem:
            tree.write(_mem, xml_declaration=True)
            _mem.seek(0)
            data = _mem.read().decode("utf-8")

        return data

    async def get_all(
        self, path: str, properties: list[str] = [], directory_only: bool = False
    ) -> UserPath:
        """Return a list of files at `path`.

        Always return a list, even if path is a file.

        Args:
            path:
                Filesystem path

            properties:
                List of additional properties to return.

            directory_only:
                Return properties of a folder, not the contents
        Returns:
            list[File]

        """
        data = self._namespace_properties(properties)
        response: list[dict[str, Any]] | dict[str, Any] = await self._propfind(
            path=f"/files/{self.driver.client.user}/{path}",
            headers={"Depth": "0" if directory_only else ""},
            data=data,
        )

        if isinstance(response, list):
            return UserPath(path, [UserFile(data, self) for data in response])
        else:
            return UserPath(path, [UserFile(response, self)])

    async def download(self, path: str) -> bytes:
        """Download the file at `path`.

        Args:
            path (str): File path

        Returns:
            str: File content

        """
        return await self._get_raw(path=f"/files/{self.driver.client.user}/{path}")

    async def upload(self, local_path: str, remote_path: str) -> None:
        """Upload a file.

        Args:
            local_path (str): Local path

            remote_path (str): Desination path

        """
        async with async_open(local_path, "rb") as fp:
            await self._put(
                path=f"/files/{self.driver.client.user}/{remote_path}",
                data=await fp.read(),
            )

    async def mkdir(self, path: str, create_parents: bool = False) -> None:
        """Create a new folder/directory.

        Args:
            path (str): Filesystem path

            create_parents (bool): Create directory parents (mkdir -p)

        """
        if create_parents:
            await self.mkdir_with_parents(path)
            return

        await self._mkcol(path=f"/files/{self.driver.client.user}/{path}")

    async def delete(self, path: str) -> None:
        """Delete file or folder.

        Args:
            path: Filesystem path
            trash:

        """
        _path: str = f"/files/{self.driver.client.user}/{path}"
        await self._delete(path=_path)

    async def move(self, source: str, dest: str, overwrite: bool = False) -> None:
        """Move a file or folder.

        Args:
            source (str): Source path

            dest (str): Destination path

            overwrite (bool, optional): Overwrite destination if exists.
            Defaults to False.

        """
        await self._move(
            path=f"/files/{self.driver.client.user}/{source}",
            headers={
                "Destination": (
                    f"{self.driver.client.endpoint}/remote.php/dav/files/"
                    f"{self.driver.client.user}/{quote(dest)}"
                ),
                "Overwrite": "T" if overwrite else "F",
            },
        )

    async def copy(self, source: str, dest: str, overwrite: bool = False) -> None:
        """Copy a file or folder.

        Args:
            source (str): Source path

            dest (str): Destination path

            overwrite (bool, optional): Overwrite destination if exists.
            Defaults to False.

        """
        await self._copy(
            path=f"/files/{self.driver.client.user}/{source}",
            headers={
                "Destination": (
                    f"{self.driver.client.endpoint}/remote.php/dav/files/"
                    f"{self.driver.client.user}/{quote(dest)}"
                ),
                "Overwrite": "T" if overwrite else "F",
            },
        )

    async def _favorite(self, path: str, set: bool) -> dict[str, Any]:
        """Set file/folder as a favorite.

        Args:
            path (str): Filesystem path

            set (bool): Make favorite

        Returns:
            dict: file info

        """
        data = f"""<?xml version="1.0"?>
                <d:propertyupdate
                    xmlns:d="DAV:"
                    xmlns:oc="http://owncloud.org/ns">
                <d:set><d:prop>
                <oc:favorite>{1 if set else 0}</oc:favorite>
                </d:prop></d:set></d:propertyupdate>
        """

        return await self._proppatch(
            path=f"/files/{self.driver.client.user}/{path}", data=data
        )

    async def set_favorite(self, path: str) -> UserFile:
        """Set file/folder as a favorite.

        Args:
            path (str): Filesystem path

        Returns:
            dict: File info

        """
        response = await self._favorite(path, True)
        return UserFile(response, self.driver)

    async def unset_favorite(self, path: str) -> UserFile:
        """Remove file/folder as a favorite.

        Args:
            path (str): Filesystem path

        Returns:
            dict: File info

        """
        response = await self._favorite(path, False)
        return UserFile(response, self.driver)

    async def get_favorites(
        self, path: str = "", properties: list[str] = []
    ) -> list[UserFile]:
        """List favorites below given Path.

        Args:
            path: Filesystem path. Defaults to ''.
            properties: List of extra properties to get.

        Returns:
            list: list of favorites

        """
        data = self._namespace_favorites_properties(properties)
        response = await self._report(
            path=f"/files/{self.driver.client.user}/{path}", data=data
        )
        if isinstance(response, dict):
            return [UserFile(response, self.driver)]
        elif isinstance(response, list):
            return [UserFile(data, self.driver) for data in response]
        else:
            raise NextcloudError(status_code=500, reason="Unparseable response")

    async def get_trashbin(self) -> Trashbin:
        """Get items in the trash.

        Returns:
            files.Path

        """
        _properties = [
            "nc:trashbin-filename",
            "nc:trashbin-original-location",
            "nc:trashbin-deletion-time",
        ]
        data = self._namespace_properties(_properties)

        response = await self._propfind(
            path=f"/trashbin/{self.driver.client.user}/trash", data=data
        )
        if isinstance(response, list):
            return Trashbin([TrashFile(d, self) for d in response], self)
        if isinstance(response, dict):
            return Trashbin([TrashFile(response, self)], self)
        raise NextcloudError(
            status_code=500, reason="Unable to interpret server response."
        )

    async def delete_trash(self, path: str) -> None:
        """Permanently delete a file from the trash.

        Args:
            path (str): Trash path (without `/remote.php/dav/`)

        """
        if not path.startswith(f"/trashbin/{self.driver.client.user}/trash"):
            raise NextcloudBadRequestError(f"Path is not a trashfile: {path}")
        await self._delete(path=path)

    async def restore_trash(self, path: str) -> None:
        """Restore a file from the trash.

        Args:
            path (str): Trash path

        """
        await self._move(
            path=path,
            headers={
                "Destination": (
                    f"{self.driver.client.endpoint}/remote.php/dav/trashbin/"
                    f"{self.driver.client.user}/restore/file"
                )
            },
        )

    async def empty_trashbin(self) -> None:
        """Empty the trash."""
        await self._delete(path=f"/trashbin/{self.driver.client.user}/trash")

    async def get_versions(self, file_id: int) -> Versions:
        """List of file versions.

        Args:
            file_id (int): File ID

        Returns:
            list: File versions

        """
        response = await self._propfind(
            path=f"/versions/{self.driver.client.user}/versions/{file_id}"
        )
        return Versions([Version(data, self) for data in response], self)

    async def restore_version(self, path: str) -> None:
        """Restore an old file version.

        Args:
            path (str): File version path

        """
        await self._move(
            path=path,
            headers={
                "Destination": (
                    f"{self.driver.client.endpoint}/remote.php/dav/versions/"
                    f"{self.driver.client.user}/restore/file"
                )
            },
        )

    def _replace_slashes(self, string: str) -> str:
        """Replace path slashes with underscores."""
        return string.replace("/", "_").replace("\\", "_")

    async def mkdir_with_parents(self, path: str) -> None:
        """Create folder with parents (mkdir -p).

        Args:
            path (str): Path to folder

        Raises:
            NextcloudException: Errors from self.create_folder()

        """
        path_chunks = path.strip("/").split("/")
        for count in range(1, len(path_chunks) + 1):
            try:
                await self.mkdir("/".join(path_chunks[0:count]))
            except NextcloudError as e:
                if "already exists" not in str(e):
                    raise

    async def __upload_file_chunk(self, local_path: str, uuid_dir: str) -> httpx.Response:
        async with async_open(local_path, "rb") as fp:
            return await self._put(
                path=f"/uploads/{self.driver.client.user}/{uuid_dir}/{os.path.basename(local_path)}",
                data=await fp.read(),
            )

    async def __assemble_chunks(self, uuid_dir: str, remote_path: str) -> httpx.Response:
        return await self._move(
            path=f"/uploads/{self.driver.client.user}/{uuid_dir}/.file",
            headers={
                "Destination": f"{self.driver.client.endpoint}/remote.php/dav/files/"
                f"{self.driver.client.user}/{quote(remote_path.strip('/'))}",
                "Overwrite": "T",
            },
        )

    async def upload_file_chunked(
        self, local_path: str, remote_path: str, chunk_size: int
    ) -> None:
        """Upload a large file in chunks.

        https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/chunking.html

        Args:
            local_path (str): Local file to upload

            remote_path (str): Remote path for finished file

            chunk_size (int): Upload file this many bytes per chunk

        Raises:
            NextcloudChunkedCacheExists: When previous failed attempt is detected.

        """
        file_position = 0
        padding = len(str(os.stat(local_path).st_size))

        local_path_escaped = self._replace_slashes(local_path)
        remote_path_escaped = self._replace_slashes(remote_path)
        uuid_dir = str(uuid.uuid4())

        local_cache_dir = (
            f"{pdir.user_cache_dir('nextcloud-async')}"
            f"/chunked_uploads/{local_path_escaped}-{remote_path_escaped}"
        )

        try:
            os.makedirs(local_cache_dir)
        except OSError:
            # Cache maybe exists, read metadata and attempt to resume upload
            async with async_open(f"{local_cache_dir}/metadata.json", "r") as metadata_fp:
                metadata = json.loads(await metadata_fp.read())
                uuid_dir = metadata["uuid"]
        else:
            # Write metadata to file in case of error uploading
            async with async_open(f"{local_cache_dir}/metadata.json", "w") as metadata_fp:
                metadata = {"uuid": uuid_dir}
                await metadata_fp.write(json.dumps(metadata))

        resume_chunk = None
        for file in os.listdir(local_cache_dir):
            # Check for existing chunk, resume there and proceed with
            # rest of file.
            if span := re.match(r"[0-9]+-([0-9]+)$", file):
                if resume_chunk:
                    raise NextcloudChunkedUploadError()
                resume_chunk = file
                file_position = int(span[1])

        if resume_chunk:
            await self.__upload_file_chunk(f"{local_cache_dir}/{resume_chunk}", uuid_dir)
            os.remove(f"{local_cache_dir}/{resume_chunk}")
        else:
            # Make remote upload directory
            await self._mkcol(path=f"/uploads/{self.driver.client.user}/{uuid_dir}")

        async with async_open(local_path, "rb") as source_fp:
            source_fp.seek(file_position)
            while data := await source_fp.read(chunk_size):
                chunk_name = (
                    f"{file_position:0{padding}}-{(file_position + len(data)):0{padding}}"
                )
                async with async_open(
                    f"{local_cache_dir}/{chunk_name}", "wb"
                ) as chunk_fp:
                    await chunk_fp.write(data)
                file_position += len(data)
                await self.__upload_file_chunk(
                    f"{local_cache_dir}/{chunk_name}", uuid_dir
                )
                os.remove(f"{local_cache_dir}/{chunk_name}")

        # Assemble chunks.  Server takes care of directory removal.
        await self.__assemble_chunks(uuid_dir, remote_path.strip("/"))

        # Remove local cache directory
        for file in os.listdir(local_cache_dir):
            os.remove(f"{local_cache_dir}/{file}")
        os.rmdir(local_cache_dir)

    async def get_groupfolder_acl(
        self, path: str, inherited: bool = False
    ) -> list[dict[str, Any]]:
        """Return a list of groupfolder ACL rules set for `path`.

        Args:
            path (str): Filesystem path
            inherited (bool): Return inherited rules instead of normal rules

        Returns:
            list: ACL rules

        """
        data = None
        ruleprop = "nc:acl-list"
        if inherited:
            ruleprop = "nc:inherited-acl-list"

        root = ET.Element(
            "d:propfind",
            attrib={
                "xmlns:d": "DAV:",
                "xmlns:oc": "http://owncloud.org/ns",
                "xmlns:nc": "http://nextcloud.org/ns",
            },
        )
        prop = ET.SubElement(root, "d:prop")
        ET.SubElement(prop, ruleprop)

        tree = ET.ElementTree(root)

        # Write XML file to memory, then read it into `data`
        with io.BytesIO() as _mem:
            tree.write(_mem, xml_declaration=True)
            _mem.seek(0)
            data = _mem.read().decode("utf-8")

        result = await self._propfind(
            path=f"/files/{self.driver.client.user}/{path}", data=data
        )

        ret: list[dict[str, Any]] = []
        if result["d:propstat"]["d:prop"][ruleprop]:
            ret = result["d:propstat"]["d:prop"][ruleprop]["nc:acl"]
        else:
            ret = []

        if type(result) is not list:
            return [result]

        return ret

    async def set_groupfolder_acl(self, path: str, acls: list[dict[str, Any]]) -> None:
        """Apply a list of groupfolder ACL rules to `path`.

        Args:
            path (str): Filesystem path
            acls (list[dict[str, Any]]): List of ACL rule dicts

        """
        data = None

        root = ET.Element(
            "d:propertyupdate",
            attrib={
                "xmlns:d": "DAV:",
                "xmlns:oc": "http://owncloud.org/ns",
                "xmlns:nc": "http://nextcloud.org/ns",
            },
        )
        prop = ET.SubElement(root, "d:set")
        prop = ET.SubElement(prop, "d:prop")
        prop = ET.SubElement(prop, "nc:acl-list")
        for acl in acls:
            aclprop = ET.SubElement(prop, "nc:acl")
            for key, val in acl.items():
                child = ET.Element(key)
                child.text = str(val)
                aclprop.append(child)

        tree = ET.ElementTree(root)

        # Write XML file to memory, then read it into `data`
        with io.BytesIO() as _mem:
            tree.write(_mem, xml_declaration=True)
            _mem.seek(0)
            data = _mem.read().decode("utf-8")

        return await self._proppatch(
            path=f"/files/{self.driver.client.user}/{path}", data=data
        )


def files_api(client: NextcloudClient) -> FilesApi:
    """FilesApi Factory."""
    dav_driver = NextcloudDavDriver(client)
    return FilesApi(dav_driver)
