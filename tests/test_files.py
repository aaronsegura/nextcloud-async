import pytest
import pytest_asyncio
import os
import asyncio
import httpx
import aiofile
from pathlib import Path

from nextcloud_async import NextcloudClient
from nextcloud_async.api import Files, File, Path
from nextcloud_async.exceptions import (
    NextcloudError,
    NextcloudNotFoundError,
    NextcloudPreconditionError,
    NextcloudConflictError,
    NextcloudMethodNotAllowedError)

from .constants import ENDPOINT, USER, PASSWORD

FILE_CONTENTS_ORIG = b'[File Contents]'
FILE_CONTENTS_NEW  = b'[Updated File Contents]'
REMOTE_TEST_DIR = '/.nextcloud-async-pytest'
REMOTE_TEST_FILE = f'{REMOTE_TEST_DIR}/Somefile.md'
REMOTE_TEST_FILE_DEST = f'{REMOTE_TEST_DIR}/Someotherfile.md'
REMOTE_TEST_COPY_DEST = f'{REMOTE_TEST_DIR}/copied_file'

def setup_module() -> None:
    asyncio.run(create_remote_test_dir())

def teardown_module() -> None:
    asyncio.run(remove_remote_test_dir())

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
async def local_test_file(class_tmp_path: Path):
    _file = f'{class_tmp_path}/file'
    async with aiofile.async_open(_file, 'wb') as fp:
        await fp.write(FILE_CONTENTS_ORIG)
        yield _file
    os.unlink(_file)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestFile:
    ...


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestFilesCreateFolder:

    async def test_create_folder(self, files_api: Files):
        _test_folder = f'{REMOTE_TEST_DIR}/created_folder'
        await files_api.mkdir(_test_folder)

    async def test_create_folder_no_parent(self, files_api: Files):
        _test_folder = f'{REMOTE_TEST_DIR}/.noexist/created_folder'
        try:
            await files_api.mkdir(_test_folder)
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
class TestFilesUploadDownload:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        _dir = f'{REMOTE_TEST_DIR}/upload'
        try:
            await files_api.mkdir(_dir)
        except NextcloudMethodNotAllowedError:
            await files_api.delete(_dir)
            await files_api.mkdir(_dir)
        return _dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_download_file(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> str:
        _file = f'{test_directory}/download.md'
        await files_api.upload(local_test_file, _file)
        return _file

    async def test_upload_file(
            self,
            files_api: Files,
            test_directory: str,
            local_test_file: str):
        await files_api.upload(local_test_file, f'{test_directory}/uploaded_file')

    async def test_download_file(self, files_api: Files, remote_download_file: str):
        file = await files_api.download(remote_download_file)
        assert file == FILE_CONTENTS_ORIG

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
class TestFilesList:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        _dir = f'{REMOTE_TEST_DIR}/list'
        try:
            await files_api.mkdir(_dir)
        except NextcloudMethodNotAllowedError:
            await files_api.delete(_dir)
            await files_api.mkdir(_dir)
        return _dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        await files_api.upload(local_test_file, f'{test_directory}/multi-file1.md')
        await files_api.upload(local_test_file, f'{test_directory}/multi-file2.md')
        return [f'{test_directory}/multi-file1.md', f'{test_directory}/multi-file2.md']

    async def test_list_single_file(
            self,
            files_api: Files,
            remote_test_files: list[str]) -> None:
        _props = ['oc:fileid', 'oc:size', 'nc:has-preview', 'nc:noexist']
        _remote_file = remote_test_files[0]

        path = await files_api.list(_remote_file, _props)
        assert isinstance(path, Path)
        assert len(path._files) == 1  # noqa: SLF001
        assert len(path.files) == 0
        assert path.is_file
        assert not path.is_dir

        file = path.file
        assert isinstance(file, File)
        assert hasattr(file, 'fileid')
        assert hasattr(file, 'size')
        assert hasattr(file, 'has-preview')
        assert 'Nextcloud File' in str(file)
        assert 'Nextcloud File' in file.__repr__()
        assert file.path == _remote_file
        assert not file.is_trash
        assert not file.is_version

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
        assert len(root_dir_only.files) == 0
        assert root_dir_only.dir.path.rstrip('/') == REMOTE_TEST_DIR.rstrip('/')

    async def test_list_directory_with_files(
            self,
            files_api: Files,
            test_directory: str,
            remote_test_files: list[str]):
        test_dir_with_files = await files_api.list(test_directory)
        assert len(test_dir_with_files.files) == len(remote_test_files)
        assert test_dir_with_files.dir.path.rstrip('/') == test_directory.rstrip('/')
        for file in remote_test_files:
            assert file in [f.path for f in test_dir_with_files.files]


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestFilesCopy:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        _dir = f'{REMOTE_TEST_DIR}/copy'
        try:
            await files_api.mkdir(_dir)
        except NextcloudMethodNotAllowedError:
            await files_api.delete(_dir)
            await files_api.mkdir(_dir)
        return _dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        await files_api.upload(local_test_file, f'{test_directory}/file1.md')
        await files_api.upload(local_test_file, f'{test_directory}/file2.md')
        return [f'{test_directory}/file1.md', f'{test_directory}/file2.md']

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
        _src_file = remote_test_files[0]
        try:
            await files_api.copy(
                _src_file,
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
        _src_file = remote_test_files[0]
        await files_api.copy(
            _src_file,
            f'{test_directory}/copy_test_success')

    async def test_copy_exists_no_overwrite(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        _src_file = remote_test_files[0]
        _dest_file = remote_test_files[1]
        try:
            await files_api.copy(
                _src_file,
                _dest_file)
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    async def test_copy_exists_with_overwrite(
            self,
            files_api: Files,
            remote_test_files: str):
        _src_file = remote_test_files[0]
        _dest_file = remote_test_files[1]
        await files_api.copy(
            _src_file,
            _dest_file,
            overwrite=True)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestFilesMove:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        _dir = f'{REMOTE_TEST_DIR}/move'
        try:
            await files_api.mkdir(_dir)
        except NextcloudMethodNotAllowedError:
            await files_api.delete(_dir)
            await files_api.mkdir(_dir)
        return _dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        ret = []
        for filenum in range(0,5):
            filename = f'{test_directory}/file{filenum}.md'
            await files_api.upload(local_test_file, filename)
            ret.append(filename)
        return ret

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
        _src_file = remote_test_files[0]
        try:
            await files_api.move(
                _src_file,
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
        _src_file = remote_test_files[0]
        await files_api.move(
            _src_file,
            f'{test_directory}/moved_file')

    async def test_move_exists_no_overwrite(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        _src_file = remote_test_files[1]
        _dest_file = remote_test_files[2]
        try:
            await files_api.move(_src_file, _dest_file)
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    async def test_move_exists_with_overwrite(
            self,
            files_api: Files,
            remote_test_files: list[str]):
        _src_file = remote_test_files[3]
        _dest_file = remote_test_files[4]
        await files_api.move(
            _src_file,
            _dest_file,
            overwrite=True)


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope='class')
class TestFilesDelete:

    @pytest_asyncio.fixture(loop_scope='class')
    async def test_directory(self, files_api: Files) -> str:
        _dir = f'{REMOTE_TEST_DIR}/delete'
        try:
            await files_api.mkdir(_dir)
        except NextcloudMethodNotAllowedError:
            await files_api.delete(_dir)
            await files_api.mkdir(_dir)
        return _dir

    @pytest_asyncio.fixture(loop_scope='class')
    async def remote_test_files(
            self,
            files_api: Files,
            local_test_file: str,
            test_directory: str) -> list[str]:
        ret = []
        for filenum in range(0,1):
            filename = f'{test_directory}/file{filenum}.md'
            await files_api.upload(local_test_file, filename)
            ret.append(filename)
        return ret

    async def test_delete(
            self,
            files_api: Files,
            remote_test_files: str):
        await files_api.delete(remote_test_files[0])

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


# @pytest.mark.vcr
# @pytest.mark.asyncio(loop_scope='class')
# class TestFilesFavorites:

#     async def test_set_favorite(
#             self,
#             files_api: Files,
#             remote_test_file: str):
#         await files_api.set_favorite(remote_test_file)

#     async def test_remove_favorite(
#             self,
#             files_api: Files,
#             remote_test_file: str):
#         await files_api.unset_favorite(remote_test_file)

#     async def test_get_single_favorite(
#             self,
#             files_api: Files,
#             single_favorite_file: str):
#         results = await files_api.get_favorites(REMOTE_TEST_DIR, ['oc:fileid'])
#         assert len(results) == 1


#     # def test_get_trashbin(self):  # noqa: D102
#     #     xml_response = bytes(
#     #         '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" '
#     #         'xmlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns" x'
#     #         'mlns:nc="http://nextcloud.org/ns"><d:response><d:href>/remote.php/da'
#     #         f'v/trashbin/{USER}/trash/</d:href><d:propstat><d:prop><d:resourcetyp'
#     #         'e><d:collection/></d:resourcetype></d:prop><d:status>HTTP/1.1 200 OK'
#     #         '</d:status></d:propstat></d:response><d:response><d:href>/remote.php'
#     #         f'/dav/trashbin/{USER}/trash/{FILE}.d1655760269</d:href><d:propstat><'
#     #         'd:prop><d:getlastmodified>Mon, 20 Jun 2022 21:24:29 GMT</d:getlastmo'
#     #         'dified><d:getcontentlength>0</d:getcontentlength><d:resourcetype/><d'
#     #         ':getetag>1655760269</d:getetag><d:getcontenttype>text/markdown</d:ge'
#     #         'tcontenttype></d:prop><d:status>HTTP/1.1 200 OK</d:status></d:propst'
#     #         'at><d:propstat><d:prop><d:quota-used-bytes/><d:quota-available-bytes'
#     #         '/></d:prop><d:status>HTTP/1.1 404 Not Found</d:status></d:propstat><'
#     #         '/d:response></d:multistatus>\n', 'utf-8')
#     #     with patch(
#     #             'httpx.AsyncClient.request',
#     #             new_callable=AsyncMock,
#     #             return_value=httpx.Response(
#     #                 status_code=200,
#     #                 content=xml_response)) as mock:
#     #         response = asyncio.run(self.ncc.get_trashbin())
#     #         mock.assert_called_with(
#     #             method='PROPFIND',
#     #             auth=(USER, PASSWORD),
#     #             url=f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash',
#     #             data={}, headers={})

#     #         assert {
#     #             'd:href': f'/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269',
#     #             'd:propstat': [
#     #                 {
#     #                     'd:prop': {
#     #                         'd:getlastmodified': 'Mon, 20 Jun 2022 21:24:29 GMT',
#     #                         'd:getcontentlength': '0',
#     #                         'd:resourcetype': None,
#     #                         'd:getetag': '1655760269',
#     #                         'd:getcontenttype': 'text/markdown'},
#     #                     'd:status': 'HTTP/1.1 200 OK'},
#     #                 {
#     #                     'd:prop': {
#     #                         'd:quota-used-bytes': None,
#     #                         'd:quota-available-bytes': None},
#     #                     'd:status': 'HTTP/1.1 404 Not Found'}]} in response

#     # def test_restore_from_trashbin(self):  # noqa: D102
#     #     TRASH_FILE = f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269'

#     #     with patch(
#     #             'httpx.AsyncClient.request',
#     #             new_callable=AsyncMock,
#     #             return_value=httpx.Response(
#     #                 status_code=200,
#     #                 content='')) as mock:
#     #         asyncio.run(self.ncc.restore_from_trashbin(
#     #             f'/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269'))

#     #         mock.assert_called_with(
#     #             method='MOVE',
#     #             auth=(USER, PASSWORD),
#     #             url=TRASH_FILE,
#     #             data={},
#     #             headers={
#     #                 'Destination': f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/restore/file'})

#     # def test_empty_trash(self):  # noqa: D102
#     #     with patch(
#     #             'httpx.AsyncClient.request',
#     #             new_callable=AsyncMock,
#     #             return_value=httpx.Response(
#     #                 status_code=200,
#     #                 content='')) as mock:
#     #         asyncio.run(self.ncc.empty_trashbin())

#     #         mock.assert_called_with(
#     #             method='DELETE',
#     #             auth=(USER, PASSWORD),
#     #             url=f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash',
#     #             data={},
#     #             headers={})

#     # def test_get_file_versions(self):  # noqa: D102
#     #     xml_response = bytes(
#     #         '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" x'
#     #         'mlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns'
#     #         '" xmlns:nc="http://nextcloud.org/ns"><d:response><d:href>/remote'
#     #         f'.php/dav/files/{USER}/{FILE}</d:href><d:propstat><d:prop><oc:fi'
#     #         'leid>2875527</oc:fileid></d:prop><d:status>HTTP/1.1 200 OK</d:st'
#     #         'atus></d:propstat></d:response></d:multistatus>\n', 'utf-8')
#     #     with patch(
#     #             'httpx.AsyncClient.request',
#     #             new_callable=AsyncMock,
#     #             return_value=httpx.Response(
#     #                 status_code=200,
#     #                 content=xml_response)) as mock:
#     #         asyncio.run(self.ncc.get_file_versions(FILE))

#     #         mock.assert_called_with(
#     #             method='PROPFIND',
#     #             auth=(USER, PASSWORD),
#     #             url=f'{ENDPOINT}/remote.php/dav/versions/{USER}/versions/2875527',
#     #             data={},
#     #             headers={})

#     # def test_restore_file_version(self):  # noqa: D102
#     #     xml_response = bytes('', 'utf-8')
#     #     VERSION = f'/remote.php/dav/versions/{USER}/versions/2875527/1655762900'
#     #     with patch(
#     #             'httpx.AsyncClient.request',
#     #             new_callable=AsyncMock,
#     #             return_value=httpx.Response(
#     #                 status_code=200,
#     #                 content=xml_response)) as mock:
#     #         asyncio.run(self.ncc.restore_file_version(VERSION))

#     #         mock.assert_called_with(
#     #             method='MOVE',
#     #             auth=(USER, PASSWORD),
#     #             url=f'{ENDPOINT}{VERSION}',
#     #             data={},
#     #             headers={
#     #                 'Destination':
#     #                     f'{ENDPOINT}/remote.php/dav/versions/{USER}/restore/file'})

#     # def test_upload_file_chunked(self):  # noqa: D102
#     #     # TODO: ^-this-v
#     #     pass
