import pytest
import pytest_asyncio
import aiofile
import os

import datetime as dt
from dateutil.tz import tzlocal

from pathlib import Path
from typing import AsyncGenerator

from nextcloud_async.api import (
    Users,
    Shares,
    Share,
    User,
    Files,
    SharePermission,
    ShareType,
)

from .helpers import create_clean_test_directory, create_remote_test_files
from .constants import REMOTE_TEST_DIR


_FILE_CONTENTS = b"[File Contents]"
_EXPIRATION = (dt.datetime.now(tz=tzlocal()) + dt.timedelta(days=1)).date()


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def test_directory(files_api: Files, network_blocked: bool) -> str:
    dir = f"{REMOTE_TEST_DIR}/shares"
    if not network_blocked:
        await create_clean_test_directory(files_api, dir)
    return dir


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def target_user(network_blocked: bool, users_api: Users) -> AsyncGenerator[User]:
    _test_user = {
        "user_id": "pytest_user",
        "display_name": "Pytest User Guy",
        "email": "pytest@example.com",
        "quota": None,
        "password": "MyCoolPassword",
        "language": "en",
    }

    if network_blocked:
        _test_user.update({"id": _test_user["user_id"]})
        test_user = User(_test_user, self_api=users_api)
    else:
        test_user = await users_api.create(**_test_user)

    yield test_user
    if not network_blocked:
        await test_user.delete()


@pytest.fixture(scope="module")
def class_tmp_path(tmp_path_factory: pytest.TempdirFactory) -> Path:
    """Create a class-scoped tmp_path fixture.

    https://stackoverflow.com/a/77584997"""
    return tmp_path_factory.mktemp(
        "nextcloud-async-pytest", numbered=True
    )  # type: ignore


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def local_test_file(
    class_tmp_path: Path, content=_FILE_CONTENTS
) -> AsyncGenerator[str]:
    file = f"{class_tmp_path}/file"
    async with aiofile.async_open(file, "wb") as fp:
        await fp.write(content)
        yield file
    os.unlink(file)


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def remote_test_files(
    files_api: Files, test_directory: str, local_test_file: str, network_blocked: bool
) -> list[str]:
    files = await create_remote_test_files(
        files_api,
        test_directory,
        local_test_file,
        num_files=2,
        network_blocked=network_blocked,
    )
    return files


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def shared_file(
    shares_api: Shares,
    target_user: User,
    remote_test_files: list[str],
):
    _path = remote_test_files[0]
    _shared_file_data = {
        "path": _path,
        "permissions": SharePermission.read,
        "share_type": ShareType.user,
        "share_with": target_user.id,
        "expire_date": _EXPIRATION,
    }
    shared_file = await shares_api.create(**_shared_file_data)
    return shared_file


@pytest.mark.asyncio(loop_scope="session")
class TestShares:

    async def test_get_all_shares(
        self,
        shares_api: Shares,
        shared_file: list[Share],
        remote_test_files: list[str],
    ):
        shares = await shares_api.get_file_shares()
        share = next(filter(lambda x: x.path == remote_test_files[0], shares))
        assert isinstance(share, Share)
        assert share.expiration == _EXPIRATION.strftime(r"%Y-%m-%d %H:%M:%S")
        assert shared_file in shares


#     def test_get_all_shares(self):  # noqa: D102
#         json_response = bytes(
#             '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},"'
#             'data":[{"id":"1","share_type":0,"uid_owner":"admin","displayname'
#             '_owner":"admin","permissions":19,"can_edit":true,"can_delete":tr'
#             'ue,"stime":1656094271,"parent":null,"expiration":null,"token":nu'
#             'll,"uid_file_owner":"admin","note":"","label":null,"displayname_'
#             'file_owner":"admin","path":"\\/Nextcloud Manual.pdf","item_type"'
#             ':"file","mimetype":"application\\/pdf","has_preview":false,"stor'
#             'age_id":"home::admin","storage":1,"item_source":30,"file_source"'
#             ':30,"file_parent":2,"file_target":"\\/Nextcloud Manual.pdf","sha'
#             're_with":"testuser","share_with_displayname":"Test User","share_'
#             'with_displayname_unique":"test@example.com","status":[],"mail_se'
#             'nd":0,"hide_download":0}]}}', 'utf-8')
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=200,
#                     content=json_response)) as mock:
#             asyncio.run(self.ncc.get_all_shares())
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v2.php/apps/files_sharing/api/v1/shares?format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})

#     def test_get_file_shares(self):  # noqa: D102
#         PATH = b''
#         RESHARES = 'True'
#         SUBFILES = 'True'
#         json_response = bytes(
#             '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},"'
#             'data":[{"id":"1","share_type":0,"uid_owner":"admin","displayname'
#             '_owner":"admin","permissions":19,"can_edit":true,"can_delete":tr'
#             'ue,"stime":1656094271,"parent":null,"expiration":null,"token":nu'
#             'll,"uid_file_owner":"admin","note":"","label":null,"displayname_'
#             'file_owner":"admin","path":"\\/Nextcloud Manual.pdf","item_type"'
#             ':"file","mimetype":"application\\/pdf","has_preview":false,"stor'
#             'age_id":"home::admin","storage":1,"item_source":30,"file_source"'
#             ':30,"file_parent":2,"file_target":"\\/Nextcloud Manual.pdf","sha'
#             're_with":"testuser","share_with_displayname":"Test User","share_'
#             'with_displayname_unique":"test@example.com","status":[],"mail_se'
#             'nd":0,"hide_download":0}]}}', 'utf-8')
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=200,
#                     content=json_response)) as mock:
#             urldata = recursive_urlencode({
#                 'path': PATH,
#                 'reshares': RESHARES,
#                 'subfiles': SUBFILES})
#             asyncio.run(self.ncc.get_file_shares(PATH, RESHARES, SUBFILES))
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v2.php/apps/files_sharing/api/v1/shares?'
#                     f'{urldata}&format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})

#     def test_get_share(self):  # noqa: D102
#         SHARE_ID = 1
#         json_response = bytes(
#             '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},"'
#             f'data":[{{"id":"{SHARE_ID}","share_type":0,"uid_owner":"admin","displayname'
#             '_owner":"admin","permissions":19,"can_edit":true,"can_delete":tr'
#             'ue,"stime":1656094271,"parent":null,"expiration":null,"token":nu'
#             'll,"uid_file_owner":"admin","note":"","label":null,"displayname_'
#             'file_owner":"admin","path":"\\/Nextcloud Manual.pdf","item_type"'
#             ':"file","mimetype":"application\\/pdf","has_preview":false,"stor'
#             'age_id":"home::admin","storage":1,"item_source":30,"file_source"'
#             ':30,"file_parent":2,"file_target":"\\/Nextcloud Manual.pdf","sha'
#             're_with":"testuser","share_with_displayname":"Test User","share_'
#             'with_displayname_unique":"test@example.com","status":[],"mail_se'
#             'nd":0,"hide_download":0}]}}', 'utf-8')
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=200,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.get_share(SHARE_ID))
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v2.php/apps/files_sharing/api'
#                     f'/v1/shares/{SHARE_ID}?share_id={SHARE_ID}&format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})
#             assert isinstance(response, dict)

# # TODO: Finish shares api tests
