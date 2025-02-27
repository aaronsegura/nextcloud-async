import pytest
import asyncio
import httpx

from nextcloud_async import NextcloudClient
from nextcloud_async.api import Files, File, Path
from nextcloud_async.exceptions import (
    NextcloudError,
    NextcloudNotFoundError,
    NextcloudPreconditionError,
    NextcloudConflictError,
    NextcloudMethodNotAllowedError)

from .constants import (
    FILE_CONTENTS_ORIG,
    FILE_CONTENTS_NEW,
    REMOTE_TEST_BASE_DIR,
    REMOTE_TEST_DIR_SRC,
    REMOTE_TEST_DIR_DEST,
    REMOTE_TEST_FILE_SRC,
    REMOTE_TEST_SUBDIRS,
    ENDPOINT, USER, PASSWORD)

@pytest.fixture
def files_api(nc: NextcloudClient):
    return Files(nc)

def setup_module() -> None:
    # Remove remote testing directory for test_files:
    asyncio.run(create_remote_test_dirs())

def teardown_module() -> None:
    asyncio.run(remove_remote_test_dir())

async def create_remote_test_dirs():
    # Prep the test environment
    # User-defined fixtures do not work here.
    nc = NextcloudClient(ENDPOINT, USER, PASSWORD, httpx.AsyncClient())
    files_api = Files(nc)

    for dir in [REMOTE_TEST_BASE_DIR, REMOTE_TEST_DIR_SRC, REMOTE_TEST_DIR_DEST]:
        try:
            await files_api.mkdir(dir)
        except NextcloudError as e:
                if e.status_code != 405:  # noqa: PLR2004
                    raise

async def remove_remote_test_dir():
    # Remove remote testing environment.
    nc = NextcloudClient(ENDPOINT, USER, PASSWORD, httpx.AsyncClient())
    files_api = Files(nc)
    try:
        await files_api.delete(REMOTE_TEST_BASE_DIR)
    except NextcloudError:
        pass


@pytest.mark.asyncio
@pytest.mark.vcr
class TestFiles:

    @pytest.mark.order(1)
    async def test_create_folder(self, files_api: Files):
        _test_folder = f'{REMOTE_TEST_DIR_SRC}/created_folder'
        await files_api.mkdir(_test_folder)

    @pytest.mark.order(2)
    async def test_create_folder_exists(self, files_api:Files):
        try:
            await files_api.mkdir(f'{REMOTE_TEST_DIR_SRC}/created_folder')
        except NextcloudMethodNotAllowedError:
            assert True
        else:
            assert False

    @pytest.mark.order(2)
    async def test_upload_file(self, files_api: Files, temp_file: str):
        await files_api.upload(temp_file, f'{REMOTE_TEST_FILE_SRC}')

    @pytest.mark.order(3)
    async def test_upload_file_exists(self, files_api: Files, temp_file: str):
        await files_api.upload(temp_file, f'{REMOTE_TEST_FILE_SRC}')

    @pytest.mark.order(3)
    async def test_download_file(self, files_api: Files):
        file = await files_api.download(REMOTE_TEST_FILE_SRC)
        assert file == FILE_CONTENTS_ORIG

    @pytest.mark.order(3)
    async def test_list_single_file(self, files_api: Files):
        _props = ['oc:fileid', 'oc:size', 'nc:has-preview', 'nc:noexist']

        path = await files_api.list(REMOTE_TEST_FILE_SRC, _props)
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
        assert file.path == REMOTE_TEST_FILE_SRC
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
            assert not file.non_exist_key
        except KeyError:
            pass
        else:
            assert False

    async def test_list_no_exist(self, files_api: Files):
        try:
            await files_api.list(f'{REMOTE_TEST_BASE_DIR}/.noexist')
        except NextcloudNotFoundError:
            assert True
        else:
            assert False

    @pytest.mark.order(3)
    async def test_list_directory_only(self, files_api: Files):
        root_dir_only = await files_api.list(REMOTE_TEST_DIR_SRC, directory_only=True)

        assert root_dir_only.is_dir
        assert not root_dir_only.is_file
        assert len(root_dir_only.files) == 0
        assert root_dir_only.dir.path.rstrip('/') == REMOTE_TEST_DIR_SRC.rstrip('/')

    @pytest.mark.order(3)
    async def test_list_directory_with_files(self, files_api: Files):
        root_dir_with_files = await files_api.list(REMOTE_TEST_DIR_SRC)
        assert len(root_dir_with_files.files) > 0
        assert root_dir_with_files.dir.path.rstrip('/') == REMOTE_TEST_DIR_SRC.rstrip('/')

    @pytest.mark.order(3)
    async def test_copy_src_noexist(self, files_api: Files):
        try:
            await files_api.copy(
                f'{REMOTE_TEST_DIR_SRC}/.noexist',
                REMOTE_TEST_DIR_DEST)
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    @pytest.mark.order(3)
    async def test_copy_dest_dir_noexist(self, files_api: Files):
        try:
            await files_api.copy(
                REMOTE_TEST_FILE_SRC,
                f'{REMOTE_TEST_DIR_DEST}/.noexist/exception_raise')
        except NextcloudConflictError:
            assert True
        else:
            assert False

    @pytest.mark.order(3)
    async def test_copy_success(self, files_api: Files):
        # Test fresh copy
        await files_api.copy(
            REMOTE_TEST_FILE_SRC,
            f'{REMOTE_TEST_DIR_DEST}/copy_test')

    @pytest.mark.order(4)
    async def test_copy_exists_no_overwrite(self, files_api: Files):
        try:
            await files_api.copy(
                REMOTE_TEST_FILE_SRC,
                f'{REMOTE_TEST_DIR_DEST}/copy_test')
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    @pytest.mark.order(4)
    async def test_copy_exists_with_overwrite(self, files_api: Files):
        await files_api.copy(
            REMOTE_TEST_FILE_SRC,
            f'{REMOTE_TEST_DIR_DEST}/copy_test',
            overwrite=True)

    @pytest.mark.order(5)
    async def test_move_src_noexist(self, files_api: Files):
        try:
            await files_api.move(
                f'{REMOTE_TEST_DIR_SRC}/.noexist',
                f'{REMOTE_TEST_DIR_DEST}')
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    @pytest.mark.order(5)
    async def test_move_dir_noexist(self, files_api: Files):
        try:
            await files_api.move(
                REMOTE_TEST_FILE_SRC,
                f'{REMOTE_TEST_DIR_DEST}/.noexist/exception_raise')
        except NextcloudConflictError:
            assert True
        else:
            assert False

    @pytest.mark.order(5)
    async def test_move_success(self, files_api: Files):
        await files_api.move(
            REMOTE_TEST_FILE_SRC,
            f'{REMOTE_TEST_DIR_DEST}/Somefile.md')
        await files_api.move(
            f'{REMOTE_TEST_DIR_DEST}/Somefile.md',
            REMOTE_TEST_FILE_SRC)

    @pytest.mark.order(5)
    async def test_move_exists_no_overwrite(self, files_api: Files):
        try:
            await files_api.move(
                REMOTE_TEST_FILE_SRC,
                f'{REMOTE_TEST_DIR_DEST}/copy_test')
        except NextcloudPreconditionError:
            assert True
        else:
            assert False

    @pytest.mark.order(5)
    async def test_move_exists_with_overwrite(self, files_api: Files):
        await files_api.move(
            REMOTE_TEST_FILE_SRC,
            f'{REMOTE_TEST_DIR_DEST}/copy_test',
            overwrite=True)

    @pytest.mark.order(6)
    async def test_delete(self, files_api: Files):
        await files_api.delete(f'{REMOTE_TEST_DIR_DEST}/copy_test')

    @pytest.mark.order(6)
    async def test_delete_noexist(self, files_api: Files):
        try:
            await files_api.delete(f'{REMOTE_TEST_DIR_DEST}/.noexist')
        except NextcloudNotFoundError:
            assert True
        else:
            assert False


    # def test_remove_favorite(self):  # noqa: D102
    #     xml_response = bytes(
    #         '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" '
    #         'xmlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns" '
    #         'xmlns:nc="http://nextcloud.org/ns"><d:response>'
    #         f'<d:href>/remote.php/dav/files/{USER}/{FILE}</d:href><d:propstat>'
    #         '<d:prop><oc:favorite/></d:prop><d:status>HTTP/1.1 200 OK</d:status>'
    #         '</d:propstat></d:response></d:multistatus>', 'utf-8')
    #     with patch(
    #             'httpx.AsyncClient.request',
    #             new_callable=AsyncMock,
    #             return_value=httpx.Response(
    #                 status_code=200,
    #                 content=xml_response)) as mock:
    #         response = asyncio.run(self.ncc.remove_favorite(FILE))
    #         mock.assert_called_with(
    #             method='PROPPATCH',
    #             auth=(USER, PASSWORD),
    #             url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FILE}',
    #             data='<?xml version="1.0"?>\n                <d:propertyupdate\n'
    #                  '                    xmlns:d="DAV:"\n                    xm'
    #                  'lns:oc="http://owncloud.org/ns">\n                <d:set><'
    #                  'd:prop>\n                <oc:favorite>0</oc:favorite>\n   '
    #                  '             </d:prop></d:set></d:propertyupdate>\n        ',
    #             headers={})
    #         assert response == {
    #             'd:href': f'/remote.php/dav/files/{USER}/{FILE}',
    #             'd:propstat': {
    #                 'd:prop': {
    #                     'oc:favorite': None},
    #                 'd:status': 'HTTP/1.1 200 OK'}}

    # def test_set_favorite(self):  # noqa: D102
    #     xml_response = bytes(
    #         '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" '
    #         'xmlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns" '
    #         'xmlns:nc="http://nextcloud.org/ns"><d:response>'
    #         f'<d:href>/remote.php/dav/files/{USER}/{FILE}</d:href><d:propstat>'
    #         '<d:prop><oc:favorite/></d:prop><d:status>HTTP/1.1 200 OK</d:status>'
    #         '</d:propstat></d:response></d:multistatus>', 'utf-8')
    #     with patch(
    #             'httpx.AsyncClient.request',
    #             new_callable=AsyncMock,
    #             return_value=httpx.Response(
    #                 status_code=200,
    #                 content=xml_response)) as mock:
    #         response = asyncio.run(self.ncc.set_favorite(FILE))
    #         mock.assert_called_with(
    #             method='PROPPATCH',
    #             auth=(USER, PASSWORD),
    #             url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FILE}',
    #             data='<?xml version="1.0"?>\n'
    #                  '                <d:propertyupdate\n'
    #                  '                    xmlns:d="DAV:"\n'
    #                  '                    xmlns:oc="http://owncloud.org/ns">\n'
    #                  '                <d:set><d:prop>\n'
    #                  '                <oc:favorite>1</oc:favorite>\n'
    #                  '                </d:prop></d:set></d:propertyupdate>\n'
    #                  '        ',
    #             headers={})
    #         assert response == {
    #             'd:href': f'/remote.php/dav/files/{USER}/{FILE}',
    #             'd:propstat': {
    #                 'd:prop': {
    #                     'oc:favorite': None},
    #                 'd:status': 'HTTP/1.1 200 OK'}}

    # def test_get_favorites(self):  # noqa: D102
    #     xml_response = bytes(
    #         '<?xml version="1.0"?>\n'
    #         '<d:multistatus xmlns:d="DAV:" xmlns:s="http://sabredav.org/ns" xmlns:'
    #         'oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">\n <d:'
    #         'response>\n  <d:status>HTTP/1.1 200 OK</d:status>\n  <d:href>/remote.'
    #         f'php/dav/files/{FILE}</d:href>\n  <d:propstat>\n'
    #         '   <d:prop/>\n   <d:status>HTTP/1.1 418 I\'m a teapot</d:status>\n  <'
    #         '/d:propstat>\n </d:response>\n <d:response>\n  <d:status>HTTP/1.1 200'
    #         f' OK</d:status>\n  <d:href>/remote.php/dav/files/{USER}/{FILE}</d:href'
    #         '>\n  <d:propstat>\n   <d:prop/>\n   <d:status>HTTP/1.1 418 I\'m a tea'
    #         'pot</d:status>\n  </d:propstat>\n </d:response>\n</d:multistatus>\n',
    #         'utf-8')
    #     with patch(
    #             'httpx.AsyncClient.request',
    #             new_callable=AsyncMock,
    #             return_value=httpx.Response(
    #                 status_code=200,
    #                 content=xml_response)) as mock:
    #         response = asyncio.run(self.ncc.get_favorites())
    #         mock.assert_called_with(
    #             method='REPORT',
    #             auth=(USER, PASSWORD),
    #             url=f'{ENDPOINT}/remote.php/dav/files/{USER}/',
    #             data='<?xml version="1.0"?><oc:filter-files  xmlns:d="DAV:"\n'
    #                 '        xmlns:oc="http://owncloud.org/ns" xmlns:nc="http'
    #                 '://nextcloud.org/ns">\n        <oc:filter-rules><oc:favo'
    #                 'rite>1</oc:favorite></oc:filter-rules>\n        </oc:fil'
    #                 'ter-files>', headers={})
    #         assert {
    #             'd:status': 'HTTP/1.1 200 OK',
    #             'd:href': f'/remote.php/dav/files/{USER}/{FILE}',
    #             'd:propstat': {
    #                 'd:prop': None,
    #                 'd:status': "HTTP/1.1 418 I'm a teapot"}} in response

    # def test_get_trashbin(self):  # noqa: D102
    #     xml_response = bytes(
    #         '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" '
    #         'xmlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns" x'
    #         'mlns:nc="http://nextcloud.org/ns"><d:response><d:href>/remote.php/da'
    #         f'v/trashbin/{USER}/trash/</d:href><d:propstat><d:prop><d:resourcetyp'
    #         'e><d:collection/></d:resourcetype></d:prop><d:status>HTTP/1.1 200 OK'
    #         '</d:status></d:propstat></d:response><d:response><d:href>/remote.php'
    #         f'/dav/trashbin/{USER}/trash/{FILE}.d1655760269</d:href><d:propstat><'
    #         'd:prop><d:getlastmodified>Mon, 20 Jun 2022 21:24:29 GMT</d:getlastmo'
    #         'dified><d:getcontentlength>0</d:getcontentlength><d:resourcetype/><d'
    #         ':getetag>1655760269</d:getetag><d:getcontenttype>text/markdown</d:ge'
    #         'tcontenttype></d:prop><d:status>HTTP/1.1 200 OK</d:status></d:propst'
    #         'at><d:propstat><d:prop><d:quota-used-bytes/><d:quota-available-bytes'
    #         '/></d:prop><d:status>HTTP/1.1 404 Not Found</d:status></d:propstat><'
    #         '/d:response></d:multistatus>\n', 'utf-8')
    #     with patch(
    #             'httpx.AsyncClient.request',
    #             new_callable=AsyncMock,
    #             return_value=httpx.Response(
    #                 status_code=200,
    #                 content=xml_response)) as mock:
    #         response = asyncio.run(self.ncc.get_trashbin())
    #         mock.assert_called_with(
    #             method='PROPFIND',
    #             auth=(USER, PASSWORD),
    #             url=f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash',
    #             data={}, headers={})

    #         assert {
    #             'd:href': f'/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269',
    #             'd:propstat': [
    #                 {
    #                     'd:prop': {
    #                         'd:getlastmodified': 'Mon, 20 Jun 2022 21:24:29 GMT',
    #                         'd:getcontentlength': '0',
    #                         'd:resourcetype': None,
    #                         'd:getetag': '1655760269',
    #                         'd:getcontenttype': 'text/markdown'},
    #                     'd:status': 'HTTP/1.1 200 OK'},
    #                 {
    #                     'd:prop': {
    #                         'd:quota-used-bytes': None,
    #                         'd:quota-available-bytes': None},
    #                     'd:status': 'HTTP/1.1 404 Not Found'}]} in response

    # def test_restore_from_trashbin(self):  # noqa: D102
    #     TRASH_FILE = f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269'

    #     with patch(
    #             'httpx.AsyncClient.request',
    #             new_callable=AsyncMock,
    #             return_value=httpx.Response(
    #                 status_code=200,
    #                 content='')) as mock:
    #         asyncio.run(self.ncc.restore_from_trashbin(
    #             f'/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269'))

    #         mock.assert_called_with(
    #             method='MOVE',
    #             auth=(USER, PASSWORD),
    #             url=TRASH_FILE,
    #             data={},
    #             headers={
    #                 'Destination': f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/restore/file'})

    # def test_empty_trash(self):  # noqa: D102
    #     with patch(
    #             'httpx.AsyncClient.request',
    #             new_callable=AsyncMock,
    #             return_value=httpx.Response(
    #                 status_code=200,
    #                 content='')) as mock:
    #         asyncio.run(self.ncc.empty_trashbin())

    #         mock.assert_called_with(
    #             method='DELETE',
    #             auth=(USER, PASSWORD),
    #             url=f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash',
    #             data={},
    #             headers={})

    # def test_get_file_versions(self):  # noqa: D102
    #     xml_response = bytes(
    #         '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" x'
    #         'mlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns'
    #         '" xmlns:nc="http://nextcloud.org/ns"><d:response><d:href>/remote'
    #         f'.php/dav/files/{USER}/{FILE}</d:href><d:propstat><d:prop><oc:fi'
    #         'leid>2875527</oc:fileid></d:prop><d:status>HTTP/1.1 200 OK</d:st'
    #         'atus></d:propstat></d:response></d:multistatus>\n', 'utf-8')
    #     with patch(
    #             'httpx.AsyncClient.request',
    #             new_callable=AsyncMock,
    #             return_value=httpx.Response(
    #                 status_code=200,
    #                 content=xml_response)) as mock:
    #         asyncio.run(self.ncc.get_file_versions(FILE))

    #         mock.assert_called_with(
    #             method='PROPFIND',
    #             auth=(USER, PASSWORD),
    #             url=f'{ENDPOINT}/remote.php/dav/versions/{USER}/versions/2875527',
    #             data={},
    #             headers={})

    # def test_restore_file_version(self):  # noqa: D102
    #     xml_response = bytes('', 'utf-8')
    #     VERSION = f'/remote.php/dav/versions/{USER}/versions/2875527/1655762900'
    #     with patch(
    #             'httpx.AsyncClient.request',
    #             new_callable=AsyncMock,
    #             return_value=httpx.Response(
    #                 status_code=200,
    #                 content=xml_response)) as mock:
    #         asyncio.run(self.ncc.restore_file_version(VERSION))

    #         mock.assert_called_with(
    #             method='MOVE',
    #             auth=(USER, PASSWORD),
    #             url=f'{ENDPOINT}{VERSION}',
    #             data={},
    #             headers={
    #                 'Destination':
    #                     f'{ENDPOINT}/remote.php/dav/versions/{USER}/restore/file'})

    # def test_upload_file_chunked(self):  # noqa: D102
    #     # TODO: ^-this-v
    #     pass
