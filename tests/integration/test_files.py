import os
from pathlib import Path

import aiofile
import pytest
import pytest_asyncio

from nextcloud_async.api import (
    FilesApi,
    Trashbin,
    TrashFile,
    UserFile,
    UserPath,
    Version,
    Versions,
)
from nextcloud_async.exceptions import (
    NextcloudBadRequestError,
    NextcloudConflictError,
    NextcloudMethodNotAllowedError,
    NextcloudNotFoundError,
    NextcloudPreconditionError,
    NextcloudUnsupportedMediaTypeError,
)

from .constants import REMOTE_TEST_DIR
from .helpers import create_clean_test_directory, create_remote_test_files

FILE_CONTENTS_ORIG = b"[File Contents]"
FILE_CONTENTS_NEW = b"[Updated File Contents]"
REMOTE_TEST_FILE = f"{REMOTE_TEST_DIR}/Somefile.md"
REMOTE_TEST_FILE_DEST = f"{REMOTE_TEST_DIR}/Someotherfile.md"
REMOTE_TEST_COPY_DEST = f"{REMOTE_TEST_DIR}/copied_file"


@pytest.fixture(scope="module")
def class_tmp_path(tmp_path_factory: pytest.TempdirFactory) -> Path:
    """Create a class-scoped tmp_path fixture.

    https://stackoverflow.com/a/77584997"""
    return tmp_path_factory.mktemp("nextcloud-async-pytest", numbered=True)  # type: ignore


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def local_test_file(class_tmp_path: Path, content=FILE_CONTENTS_ORIG):
    file = f"{class_tmp_path}/file"
    async with aiofile.async_open(file, "wb") as fp:
        await fp.write(content)
        yield file
    os.unlink(file)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestUploadDownload:
    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def test_directory(self, files_api: FilesApi, network_blocked: bool) -> str:
        dir = f"{REMOTE_TEST_DIR}/upload"
        if not network_blocked:
            await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_download_file(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked: bool,
    ) -> str:
        file = f"{test_directory}/download.md"
        if not network_blocked:
            await files_api.upload(local_test_file, file)
        return file

    async def test_upload_file(
        self, files_api: FilesApi, test_directory: str, local_test_file: str
    ):
        await files_api.upload(local_test_file, f"{test_directory}/uploaded_file")

    async def test_download_file(self, files_api: FilesApi, remote_download_file: str):
        file = await files_api.list(remote_download_file)
        contents = await file.download()
        assert contents == FILE_CONTENTS_ORIG

    async def test_download_file_noexist(self, files_api: FilesApi, test_directory: str):
        with pytest.raises(NextcloudNotFoundError):
            await files_api.download(f"{test_directory}/.noexist")


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestList:
    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def test_directory(self, files_api: FilesApi, network_blocked: bool) -> str:
        dir = f"{REMOTE_TEST_DIR}/list"
        if not network_blocked:
            await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_test_files(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked,
    ) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=2,
            network_blocked=network_blocked,
        )

    async def test_list_single_file(
        self, files_api: FilesApi, remote_test_files: list[str]
    ) -> None:
        props = ["oc:fileid", "oc:size", "nc:has-preview", "nc:noexist"]
        remote_file = remote_test_files[0]

        path = await files_api.list(remote_file, props)
        assert isinstance(path, UserPath)
        assert len(path._files) == 1  # noqa: SLF001
        assert path.is_file
        assert not path.is_dir

        file = path._file  # noqa: SLF001
        assert isinstance(file, UserFile)
        assert hasattr(file, "fileid")
        assert hasattr(file, "size")
        assert hasattr(file, "has-preview")
        assert "Nextcloud File" in str(file)
        assert "Nextcloud File" in file.__repr__()
        assert file.path == remote_file

        with pytest.raises(KeyError):
            hasattr(file, "noexist")

        with pytest.raises(KeyError):
            hasattr(file, "nc:noexist")

        try:
            file.has_preview
        except KeyError:
            pytest.fail("Expected attribute not present.")

        with pytest.raises(KeyError):
            assert not file.key_noexist

    async def test_list_no_exist(self, files_api: FilesApi):
        with pytest.raises(NextcloudNotFoundError):
            await files_api.list(f"{REMOTE_TEST_DIR}/.noexist")

    async def test_list_directory_only(self, files_api: FilesApi):
        root_dir_only = await files_api.list(REMOTE_TEST_DIR, directory_only=True)

        assert root_dir_only.is_dir
        assert not root_dir_only.is_file
        this_path = root_dir_only._dir.path.rstrip("/")
        assert this_path == REMOTE_TEST_DIR.rstrip("/")

    async def test_list_directory_with_files(
        self, files_api: FilesApi, test_directory: str, remote_test_files: list[str]
    ):
        test_dir_with_files = await files_api.list(test_directory)
        assert len(test_dir_with_files) == len(remote_test_files)
        assert test_dir_with_files._dir.path.rstrip("/") == test_directory.rstrip("/")
        for file in remote_test_files:
            assert file in [f.path for f in test_dir_with_files]


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestCopy:
    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def test_directory(self, files_api: FilesApi, network_blocked: bool) -> str:
        dir = f"{REMOTE_TEST_DIR}/copy"
        if not network_blocked:
            await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_test_files(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked: bool,
    ) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=2,
            network_blocked=network_blocked,
        )

    async def test_copy_src_noexist(self, files_api: FilesApi, test_directory: str):
        with pytest.raises(NextcloudPreconditionError):
            await files_api.copy(f"{test_directory}/.noexist", test_directory)

    async def test_copy_dest_dir_noexist(
        self, files_api: FilesApi, test_directory: str, remote_test_files: str
    ):
        src_file = remote_test_files[0]
        with pytest.raises(NextcloudConflictError):
            await files_api.copy(src_file, f"{test_directory}/.noexist/exception_raise")

    async def test_copy_success(
        self, files_api: FilesApi, test_directory: str, remote_test_files: list[str]
    ):
        # Test fresh copy
        src_file = await files_api.list(remote_test_files[0])
        await src_file.copy(f"{test_directory}/copy_test_success")

    async def test_copy_exists_no_overwrite(
        self, files_api: FilesApi, remote_test_files: list[str]
    ):
        src_file = await files_api.list(remote_test_files[0])
        dest_file = remote_test_files[1]
        with pytest.raises(NextcloudPreconditionError):
            await src_file.copy(dest_file)

    async def test_copy_exists_with_overwrite(
        self, files_api: FilesApi, remote_test_files: str
    ):
        src_file = await files_api.list(remote_test_files[0])
        dest_file = remote_test_files[1]
        await src_file.copy(dest_file, overwrite=True)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestMove:
    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def test_directory(self, files_api: FilesApi, network_blocked: bool) -> str:
        dir = f"{REMOTE_TEST_DIR}/move"
        if not network_blocked:
            await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_test_files(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked: bool,
    ) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=5,
            network_blocked=network_blocked,
        )

    async def test_move_src_noexist(self, files_api: FilesApi, test_directory: str):
        with pytest.raises(NextcloudPreconditionError):
            await files_api.move(f"{test_directory}/.noexist", test_directory)

    async def test_move_dest_dir_noexist(
        self, files_api: FilesApi, test_directory: str, remote_test_files: list[str]
    ):
        src_file = await files_api.list(remote_test_files[0])
        with pytest.raises(NextcloudConflictError):
            await src_file.move(f"{test_directory}/.noexist/exception_raise")

    async def test_move_success(
        self, files_api: FilesApi, test_directory: str, remote_test_files: list[str]
    ):
        src_file = await files_api.list(remote_test_files[0])
        await src_file.move(f"{test_directory}/moved_file")

    async def test_move_exists_no_overwrite(
        self, files_api: FilesApi, remote_test_files: list[str]
    ):
        src_file = await files_api.list(remote_test_files[1])
        dest_file = remote_test_files[2]
        with pytest.raises(NextcloudPreconditionError):
            await src_file.move(dest_file)

    async def test_move_exists_with_overwrite(
        self, files_api: FilesApi, remote_test_files: list[str]
    ):
        src_file = await files_api.list(remote_test_files[3])
        dest_file = remote_test_files[4]
        await src_file.move(dest_file, overwrite=True)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestDelete:
    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def test_directory(self, files_api: FilesApi, network_blocked: bool) -> str:
        dir = f"{REMOTE_TEST_DIR}/delete"
        if not network_blocked:
            await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_test_files(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked: bool,
    ) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=1,
            network_blocked=network_blocked,
        )

    async def test_delete(self, files_api: FilesApi, remote_test_files: str):
        file = await files_api.list(remote_test_files[0])
        await file.delete()
        with pytest.raises(NextcloudNotFoundError):
            await files_api.list(remote_test_files[0])

    async def test_delete_noexist(self, files_api: FilesApi, test_directory: str):
        with pytest.raises(NextcloudNotFoundError):
            await files_api.delete(f"{test_directory}/.noexist")


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestFavorites:
    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def test_directory(self, files_api: FilesApi, network_blocked: bool) -> str:
        dir = f"{REMOTE_TEST_DIR}/favorites"
        if not network_blocked:
            await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_test_files(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked: bool,
    ) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=1,
            network_blocked=network_blocked,
        )

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_favorited_files(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked: bool,
    ) -> list[str]:
        ret = []
        for filenum in range(0, 2):
            filename = f"{test_directory}/favorited{filenum}.md"
            if not network_blocked:
                await files_api.upload(local_test_file, filename)
                await files_api.set_favorite(filename)
            ret.append(filename)
        return ret

    async def test_set_favorite(self, files_api: FilesApi, remote_test_files: str):
        file = await files_api.list(remote_test_files[0])
        await file.set_favorite()
        favorites = await files_api.get_favorites()
        assert [f for f in favorites if f.path == remote_test_files[0]]

    async def test_remove_favorite(
        self, files_api: FilesApi, remote_favorited_files: list[str]
    ):
        file = await files_api.list(remote_favorited_files[0])
        await file.unset_favorite()
        favorites = await files_api.get_favorites()
        assert not [f for f in favorites if f.path == remote_favorited_files[0]]

    async def test_get_file(self, files_api: FilesApi, remote_favorited_files: list[str]):
        with pytest.raises(NextcloudUnsupportedMediaTypeError):
            await files_api.get_favorites(remote_favorited_files[1])

    async def test_get_multiple_favorites(
        self, files_api: FilesApi, test_directory: str, remote_favorited_files: list[str]
    ):
        results = await files_api.get_favorites(test_directory)
        assert len(results) == len(remote_favorited_files)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestTrashbin:
    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def test_directory(self, files_api: FilesApi, network_blocked: bool) -> str:
        dir = f"{REMOTE_TEST_DIR}/trashbin"
        if not network_blocked:
            await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_test_files(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked: bool,
    ) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=3,
            network_blocked=network_blocked,
        )

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def deleted_file(
        self, files_api: FilesApi, remote_test_files: list[str], network_blocked: bool
    ):
        file = remote_test_files[0]
        if not network_blocked:
            await files_api.delete(file)
        return file

    async def test_get_trashbin(self, files_api: FilesApi):
        trash = await files_api.get_trashbin()
        assert isinstance(trash, Trashbin)
        for f in trash:
            assert isinstance(f, TrashFile)

    async def test_restore_from_trashbin(self, files_api: FilesApi, deleted_file: str):
        trash = await files_api.get_trashbin()
        for f in trash:
            if f.trashbin_original_location == deleted_file:
                await f.restore()
                with pytest.raises(NextcloudNotFoundError):
                    await files_api.list(deleted_file)

    async def test_delete_trash_regular_file(
        self, files_api: FilesApi, remote_test_files: list[str]
    ):
        with pytest.raises(NextcloudBadRequestError):
            await files_api.delete_trash(remote_test_files[1])

    async def test_delete_trash_file(
        self, files_api: FilesApi, remote_test_files: list[str]
    ):
        file = await files_api.list(remote_test_files[2])
        await file.delete()
        trashbin = await files_api.get_trashbin()
        for trash in trashbin:
            if trash.trashbin_original_location == file.path:
                await trash.delete()

    async def test_empty_trash(self, files_api: FilesApi):
        trash = await files_api.get_trashbin()
        await trash.empty()
        trash = await files_api.get_trashbin()
        assert len(trash) == 0


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestVersions:
    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def test_directory(self, files_api: FilesApi, network_blocked: bool) -> str:
        dir = f"{REMOTE_TEST_DIR}/versions"
        if not network_blocked:
            await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def remote_test_files(
        self,
        files_api: FilesApi,
        local_test_file: str,
        test_directory: str,
        network_blocked: bool,
    ) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=1,
            network_blocked=network_blocked,
        )

    @pytest_asyncio.fixture(scope="class", loop_scope="session")
    async def versioned_file(
        self,
        files_api: FilesApi,
        remote_test_files: list[str],
        class_tmp_path: Path,
        network_blocked: bool,
    ) -> str:
        updated_file = class_tmp_path / "updated_file"
        async with aiofile.async_open(updated_file, "wb") as fp:
            await fp.write(FILE_CONTENTS_NEW)
        remote_file = remote_test_files[0]
        if not network_blocked:
            await files_api.upload(str(updated_file), remote_file)
        return remote_file

    async def test_get_file_versions(self, files_api: FilesApi, versioned_file: str):
        file = await files_api.list(versioned_file)
        versions = await file.get_versions()
        assert isinstance(versions, Versions)
        for version in versions:
            assert isinstance(version, Version)
            assert len(versions) == 1

    async def test_restore_file_version(self, files_api: FilesApi, versioned_file: str):
        file = await files_api.list(versioned_file)
        versions = await file.get_versions()
        version = versions[0]
        await version.restore()
        restored_file = await files_api.download(file.path)
        assert restored_file == FILE_CONTENTS_ORIG


# TODO: Test chunked uploads


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestCreateFolder:
    async def test_create_folder(self, files_api: FilesApi):
        test_folder = f"{REMOTE_TEST_DIR}/created_folder"
        await files_api.mkdir(test_folder)

    async def test_create_folder_no_parent(self, files_api: FilesApi):
        test_folder = f"{REMOTE_TEST_DIR}/.noexist/created_folder"
        with pytest.raises(NextcloudConflictError):
            await files_api.mkdir(test_folder)

    async def test_create_folder_exists(self, files_api: FilesApi):
        with pytest.raises(NextcloudMethodNotAllowedError):
            await files_api.mkdir(f"{REMOTE_TEST_DIR}")
