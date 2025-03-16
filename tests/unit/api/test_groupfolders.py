from hashlib import sha1
from unittest.mock import call

import pytest

from nextcloud_async.api import GroupFolder, GroupFolders, GroupFoldersPermissions
from nextcloud_async.exceptions import NextcloudForbiddenError


@pytest.fixture(name="gfs")
def _groupfolders(magicmock, asyncmock):
    gf = GroupFolders(magicmock)
    gf.api = asyncmock
    return gf


@pytest.mark.asyncio
class TestGroupFoldersApi:
    async def test_validate_capability(self, gfs):
        await gfs._validate_capability()
        expected = [call.require_capability("groupfolders")]
        gfs.api.assert_has_calls(expected)

    async def test_create(self, gfs):
        _folder = sha1().hexdigest()
        await gfs.create(_folder)
        expected = [
            call.require_capability("groupfolders"),
            call.post(
                path="/apps/groupfolders/folders",
                data={"mountpoint": _folder},
                headers=None,
            ),
        ]
        gfs.api.assert_has_calls(expected)
