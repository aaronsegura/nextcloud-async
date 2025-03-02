import pytest
import pytest_asyncio
import os
import asyncio
import httpx
import aiofile
from pathlib import Path

from nextcloud_async import NextcloudClient
from nextcloud_async.api import (
    Files,
    UserFile,
    UserPath,
    TrashFile,
    Trashbin,
    Versions,
    Version)

from nextcloud_async.exceptions import (
    NextcloudError,
    NextcloudNotFoundError,
    NextcloudPreconditionError,
    NextcloudConflictError,
    NextcloudMethodNotAllowedError,
    NextcloudUnsupportedMediaType,
    NextcloudBadRequestError)

from .constants import ENDPOINT, USER, PASSWORD
from .helpers import (
    create_clean_test_directory,
    create_remote_test_files)

FILE_CONTENTS_ORIG = b'[File Contents]'
FILE_CONTENTS_NEW  = b'[Updated File Contents]'
REMOTE_TEST_DIR = '/.nextcloud-async-pytest'
REMOTE_TEST_FILE = f'{REMOTE_TEST_DIR}/Somefile.md'
REMOTE_TEST_FILE_DEST = f'{REMOTE_TEST_DIR}/Someotherfile.md'
REMOTE_TEST_COPY_DEST = f'{REMOTE_TEST_DIR}/copied_file'

def setup_module() -> None:
    asyncio.run(create_remote_test_dir())

async def create_remote_test_dir():
    # Prep the test environment
    # User-defined fixtures do not work here.
    nc = NextcloudClient(ENDPOINT, USER, PASSWORD, httpx.AsyncClient())
    files_api = Files(nc)

    try:
        await files_api.mkdir(REMOTE_TEST_DIR)
    except NextcloudError as e:
            if e == NextcloudMethodNotAllowedError:
                await files_api.delete(REMOTE_TEST_DIR)
                await files_api.mkdir(REMOTE_TEST_DIR)

def teardown_module() -> None:
    asyncio.run(remove_remote_test_dir())
    pass

async def remove_remote_test_dir():
    # Remove remote testing environment.
    nc = NextcloudClient(ENDPOINT, USER, PASSWORD, httpx.AsyncClient())
    files_api = Files(nc)
    try:
        await files_api.delete(REMOTE_TEST_DIR)
    except NextcloudError:
        pass

@pytest.fixture(scope='class')
def files_api(nc: NextcloudClient):
    return Files(nc)

@pytest.fixture(scope='class')
def class_tmp_path(tmp_path_factory: pytest.TempdirFactory) -> Path:
    """Create a class-scoped tmp_path fixture.

    https://stackoverflow.com/a/77584997"""
    return tmp_path_factory.mktemp(
        'nextcloud-async-pytest',
        numbered=True) # type: ignore

@pytest_asyncio.fixture(loop_scope='class')
async def local_test_file(
    class_tmp_path: Path,
    content=FILE_CONTENTS_ORIG):
    file = f'{class_tmp_path}/file'
    async with aiofile.async_open(file, 'wb') as fp:
        await fp.write(content)
        yield file
    os.unlink(file)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestCreateFolder:

    async def test_create_folder(self, files_api: Files):
        test_folder = f'{REMOTE_TEST_DIR}/created_folder'
        await files_api.mkdir(test_folder)

    async def test_create_folder_no_parent(self, files_api: Files):
        test_folder = f'{REMOTE_TEST_DIR}/.noexist/created_folder'
        try:
            await files_api.mkdir(test_folder)
        except NextcloudConflictError:
            assert True
        else:
            assert False

    async def test_create_folder_exists(self, files_api:Files):
        try:
            await files_api.mkdir(f'{REMOTE_TEST_DIR}')
        except NextcloudMethodNotAllowedError:
            assert True
        else:
            assert False


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestUploadDownload:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        dir = f'{REMOTE_TEST_DIR}/upload'
        await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_download_file(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> str:
        file = f'{test_directory}/download.md'
        await files_api.upload(local_test_file, file)
        return file

    async def test_upload_file(
            self,
            files_api: Files,
            test_directory: str,
            local_test_file: str):
        await files_api.upload(local_test_file, f'{test_directory}/uploaded_file')

    async def test_download_file(self, files_api: Files, remote_download_file: str):
        file = await files_api.list(remote_download_file)
        contents = await file.download()
        assert contents == FILE_CONTENTS_ORIG

    async def test_download_file_noexist(
            self,
            files_api: Files,
            test_directory: str):
        try:
            await files_api.download(f'{test_directory}/.noexist')
        except NextcloudNotFoundError:
            assert True
        else:
            assert False


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestList:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        dir = f'{REMOTE_TEST_DIR}/list'
        await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=2)

    async def test_list_single_file(
            self,
            files_api: Files,
            remote_test_files: list[str]) -> None:
        props = ['oc:fileid', 'oc:size', 'nc:has-preview', 'nc:noexist']
        remote_file = remote_test_files[0]

        path = await files_api.list(remote_file, props)
        assert isinstance(path, UserPath)
        assert len(path._files) == 1  # noqa: SLF001
        assert path.is_file
        assert not path.is_dir

        file = path._file
        assert isinstance(file, UserFile)
        assert hasattr(file, 'fileid')
        assert hasattr(file, 'size')
        assert hasattr(file, 'has-preview')
        assert 'Nextcloud File' in str(file)
        assert 'Nextcloud File' in file.__repr__()
        assert file.path == remote_file

        try:
            hasattr(file, 'noexist')
            hasattr(file, 'nc:noexist')
        except KeyError:
            assert True
        else:
            assert False

        try:
            file.has_preview
        except KeyError:
            assert False

        try:
            assert not file.key_noexist
        except KeyError:
            pass
        else:
            assert False

    async def test_list_no_exist(self, files_api: Files):
        try:
            await files_api.list(f'{REMOTE_TEST_DIR}/.noexist')
        except NextcloudNotFoundError:
            assert True
        else:
            assert False

    async def test_list_directory_only(self, files_api: Files):
        root_dir_only = await files_api.list(REMOTE_TEST_DIR, directory_only=True)

        assert root_dir_only.is_dir
        assert not root_dir_only.is_file
        assert root_dir_only._dir.path.rstrip('/') == REMOTE_TEST_DIR.rstrip('/')

    async def test_list_directory_with_files(
            self,
            files_api: Files,
            test_directory: str,
            remote_test_files: list[str]):
        test_dir_with_files = await files_api.list(test_directory)
        assert len(test_dir_with_files) == len(remote_test_files)
        assert test_dir_with_files._dir.path.rstrip('/') == test_directory.rstrip('/')  # noqa: SLF001
        for file in remote_test_files:
            assert file in [f.path for f in test_dir_with_files]


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestCopy:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        dir = f'{REMOTE_TEST_DIR}/copy'
        await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=2)

    async def test_copy_src_noexist(
            self,
            files_api: Files,
            test_directory: str):
        try:
            await files_api.copy(
                f'{test_directory}/.noexist',
                test_directory)
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    async def test_copy_dest_dir_noexist(
            self,
            files_api: Files,
            test_directory: str,
            remote_test_files: str):
        src_file = remote_test_files[0]
        try:
            await files_api.copy(
                src_file,
                f'{test_directory}/.noexist/exception_raise')
        except NextcloudConflictError:
            assert True
        else:
            assert False

    async def test_copy_success(
            self,
            files_api: Files,
            test_directory: str,
            remote_test_files: list[str]):
        # Test fresh copy
        src_file = await files_api.list(remote_test_files[0])
        await src_file.copy(f'{test_directory}/copy_test_success')

    async def test_copy_exists_no_overwrite(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        src_file = await files_api.list(remote_test_files[0])
        dest_file = remote_test_files[1]
        try:
            await src_file.copy(dest_file)
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    async def test_copy_exists_with_overwrite(
            self,
            files_api: Files,
            remote_test_files: str):
        src_file = await files_api.list(remote_test_files[0])
        dest_file = remote_test_files[1]
        await src_file.copy(dest_file, overwrite=True)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestMove:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        dir = f'{REMOTE_TEST_DIR}/move'
        await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
         return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=5)

    async def test_move_src_noexist(
            self,
            files_api: Files,
            test_directory: str):
        try:
            await files_api.move(
                f'{test_directory}/.noexist',
                test_directory)
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    async def test_move_dest_dir_noexist(
            self,
            files_api: Files,
            test_directory: str,
            remote_test_files: list[str]):
        src_file = await files_api.list(remote_test_files[0])
        try:
            await src_file.move(
                f'{test_directory}/.noexist/exception_raise')
        except NextcloudConflictError:
            assert True
        else:
            assert False

    async def test_move_success(
            self,
            files_api: Files,
            test_directory: str,
            remote_test_files: list[str]):
        src_file = await files_api.list(remote_test_files[0])
        await src_file.move(f'{test_directory}/moved_file')

    async def test_move_exists_no_overwrite(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        src_file = await files_api.list(remote_test_files[1])
        dest_file = remote_test_files[2]
        try:
            await src_file.move(dest_file)
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    async def test_move_exists_with_overwrite(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        src_file = await files_api.list(remote_test_files[3])
        dest_file = remote_test_files[4]
        await src_file.move(dest_file, overwrite=True)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestDelete:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        dir = f'{REMOTE_TEST_DIR}/delete'
        await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=1)

    async def test_delete(
            self,
            files_api: Files,
            remote_test_files: str):
        file = await files_api.list(remote_test_files[0])
        await file.delete()
        try:
            await files_api.list(remote_test_files[0])
        except NextcloudNotFoundError:
            assert True
        else:
            assert False

    async def test_delete_noexist(
            self,
            files_api: Files,
            test_directory: str):
        try:
            await files_api.delete(f'{test_directory}/.noexist')
        except NextcloudNotFoundError:
            assert True
        else:
            assert False


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestFavorites:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        dir = f'{REMOTE_TEST_DIR}/favorites'
        await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=1)

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_favorited_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        ret = []
        for filenum in range(0,2):
            filename = f'{test_directory}/favorited{filenum}.md'
            await files_api.upload(local_test_file, filename)
            await files_api.set_favorite(filename)
            ret.append(filename)
        return ret

    async def test_set_favorite(
            self,
            files_api: Files,
            remote_test_files: str):
        file = await files_api.list(remote_test_files[0])
        await file.set_favorite()
        favorites = await files_api.get_favorites()
        assert [f for f in favorites if f.path == remote_test_files[0]]

    async def test_remove_favorite(
            self,
            files_api: Files,
            remote_favorited_files: list[str]):
        file = await files_api.list(remote_favorited_files[0])
        await file.unset_favorite()
        favorites = await files_api.get_favorites()
        assert not [f for f in favorites if f.path == remote_favorited_files[0]]

    async def test_get_file(
            self,
            files_api: Files,
            remote_favorited_files: list[str]):
        try:
             await files_api.get_favorites(remote_favorited_files[1])
        except NextcloudUnsupportedMediaType:
            assert True
        else:
            assert False

    async def test_get_multiple_favorites(
            self,
            files_api: Files,
            test_directory: str,
            remote_favorited_files: list[str]):
        results = await files_api.get_favorites(test_directory)
        assert len(results) == len(remote_favorited_files)

@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestTrashbin:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        dir = f'{REMOTE_TEST_DIR}/trashbin'
        await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=3)

    @pytest_asyncio.fixture(loop_scope='class')
    async def deleted_file(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        file = remote_test_files[0]
        await files_api.delete(file)
        return file

    async def test_get_trashbin(
            self,
            files_api: Files):
        trash = await files_api.get_trashbin()
        assert isinstance(trash, Trashbin)
        for f in trash:
            assert isinstance(f, TrashFile)

    async def test_restore_from_trashbin(
            self,
            files_api: Files,
            deleted_file: str):
        trash = await files_api.get_trashbin()
        for f in trash:
            if f.trashbin_original_location == deleted_file:
                await f.restore()
                try:
                    await files_api.list(deleted_file)
                except NextcloudNotFoundError:
                    assert False
                else:
                    assert True

    async def test_delete_trash_regular_file(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        try:
            await files_api.delete_trash(remote_test_files[1])
        except NextcloudBadRequestError:
            assert True
        else:
            assert False

    async def test_delete_trash_file(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        file = await files_api.list(remote_test_files[2])
        await file.delete()
        trashbin = await files_api.get_trashbin()
        for trash in trashbin:
            if trash.trashbin_original_location == file.path:
                await trash.delete()

    async def test_empty_trash(
            self,
            files_api: Files):
        trash = await files_api.get_trashbin()
        await trash.empty()
        trash = await files_api.get_trashbin()
        assert len(trash) == 0


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestVersions:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        dir = f'{REMOTE_TEST_DIR}/versions'
        await create_clean_test_directory(files_api, dir)
        return dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        return await create_remote_test_files(
            files_api,
            test_directory,
            local_test_file,
            num_files=1)

    @pytest_asyncio.fixture(loop_scope='class')
    async def versioned_file(
            self,
            files_api: Files,
            remote_test_files: list[str],
            tmp_path: Path) -> str:
        updated_file = tmp_path / 'updated_file'
        async with aiofile.async_open(updated_file, 'wb') as fp:
            await fp.write(FILE_CONTENTS_NEW)
        remote_file = remote_test_files[0]
        await files_api.upload(str(updated_file), remote_file)
        return remote_file

    async def test_get_file_versions(
            self,
            files_api: Files,
            versioned_file: str):
        file = await files_api.list(versioned_file)
        versions = await file.get_versions()
        assert isinstance(versions, Versions)
        for version in versions:
            assert isinstance(version, Version)
            assert len(versions) == 1

    async def test_restore_file_version(
            self,
            files_api: Files,
            versioned_file: str):
        file = await files_api.list(versioned_file)
        versions = await file.get_versions()
        version = versions[0]
        await version.restore()
        restored_file = await files_api.download(file.path)
        assert restored_file == FILE_CONTENTS_ORIG

# TODO: Test chunked uploads
