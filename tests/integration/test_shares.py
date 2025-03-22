import pytest
import pytest_asyncio

import datetime as dt
import os
from collections.abc import AsyncGenerator
from pathlib import Path

import aiofile
from dateutil.tz import tzlocal

from nextcloud_async.api import (
    FilesApi,
    Share,
    ShareesApi,
    SharePermission,
    SharesApi,
    ShareType,
    User,
    UsersApi,
)
from nextcloud_async.exceptions import NextcloudNotFoundError

from .helpers import create_remote_test_files

_FILE_CONTENTS = b"[File Contents]"
_EXPIRATION = (dt.datetime.now(tz=tzlocal()) + dt.timedelta(days=1)).date()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def target_user(users_api: UsersApi) -> AsyncGenerator[User, None]:
    _test_user = {
        "user_id": "pytest_user",
        "display_name": "Pytest User Guy",
        "email": "pytest@example.com",
        "quota": None,
        "password": "MyCoolPassword",
        "language": "en",
    }
    test_user = await users_api.create(**_test_user)
    yield test_user
    await test_user.delete()


@pytest.fixture(scope="module")
def class_tmp_path(tmp_path_factory: pytest.TempdirFactory) -> Path:
    """Create a class-scoped tmp_path fixture.

    https://stackoverflow.com/a/77584997"""
    return tmp_path_factory.mktemp("nextcloud-async-pytest", numbered=True)  # type: ignore


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def local_test_file(
    class_tmp_path: Path, content=_FILE_CONTENTS
) -> AsyncGenerator[str, None]:
    file = f"{class_tmp_path}/file"
    async with aiofile.async_open(file, "wb") as fp:
        await fp.write(content)
        yield file
    os.unlink(file)


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def remote_test_files(
    files_api: FilesApi,
    remote_test_dir: str,
    local_test_file: str,
) -> list[str]:
    files = await create_remote_test_files(
        files_api,
        remote_test_dir,
        local_test_file,
        num_files=2,
    )
    return files


@pytest_asyncio.fixture(scope="function", loop_scope="session")
# @pytest.mark.vcr(filter_post_data_parameters={"expire_date": _EXPIRATION})
async def shared_file(
    shares_api: SharesApi,
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
    _share = await shares_api.create(**_shared_file_data)
    return _share


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestShares:
    @pytest.mark.vcr(filter_post_data_parameters={"expire_date": _EXPIRATION})
    async def test_get_all_shares(
        self,
        shares_api: SharesApi,
        shared_file: list[Share],
        remote_test_files: list[str],
    ):
        _shared_file = remote_test_files[0]
        shares = await shares_api.get_file_shares()
        share = [x for x in shares if x.path == _shared_file].pop()
        assert isinstance(share, Share)
        assert shared_file in shares

    async def test_get_share_info(self, shares_api: SharesApi, shared_file: Share):
        response = await shares_api.get(shared_file.id)
        assert response == shared_file

    async def test_delete_share(self, shares_api: SharesApi, shared_file: Share):
        _id = shared_file.id
        await shared_file.delete()
        with pytest.raises(NextcloudNotFoundError):
            await shares_api.get(_id)

    async def test_update_share(
        self,
        shared_file: Share,
    ):
        await shared_file.update(
            allow_public_upload=True,
            permissions=SharePermission.update | SharePermission.read,
            send_mail=True,
        )

    async def test_send_email(self, shared_file: Share):
        await shared_file.send_email()


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestSharees:
    async def test_get_sharees(self, sharees_api: ShareesApi, target_user: User):
        response = await sharees_api.search_sharees(target_user.id)
        match = [
            x
            for x in response["exact"]["users"]  # type: ignore
            if x["value"]["shareWith"] == target_user.id  # type: ignore
        ].pop()
        assert match

    async def test_get_recommended_sharees(self, sharees_api: ShareesApi):
        await sharees_api.sharee_recommendations()
