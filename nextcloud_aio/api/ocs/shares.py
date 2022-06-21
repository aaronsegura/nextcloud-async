"""
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
"""

import asyncio

import datetime as dt

from enum import Enum, IntFlag
from typing import Any, Optional

from nextcloud_aio.exceptions import NextCloudAsyncException


class ShareType(Enum):
    user = 0
    group = 1
    public = 3
    federated = 6


class SharePermission(IntFlag):
    read = 1
    update = 2
    create = 4
    delete = 8
    share = 16


class OCSShareAPI(object):

    async def get_all_shares(self):
        """Return list of all shares."""
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v2.php/apps/files_sharing/api/v1/shares')

    async def get_file_shares(
            self,
            path: str,
            reshares: bool = False,
            subfiles: bool = False):
        """Return list of shares for given file/folder."""
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v2.php/apps/files_sharing/api/v1/shares',
            data={
                'path': path,
                'reshares': reshares,
                'subfiles': subfiles})

    async def get_share(self, share_id: int):
        """Return information about a known share."""
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}',
            data={'share_id': share_id})

    async def create_share(
            self,
            path: str,
            share_type: ShareType,
            permissions: SharePermission,
            share_with: Optional[str] = None,
            allow_public_upload: bool = False,
            password: Optional[str] = None,
            expire_date: Optional[str] = None,
            note: Optional[str] = None):
        """Create a new share."""
        try:
            expire_dt = dt.datetime.strptime(expire_date, r'%Y-%m-%d')
        except ValueError:
            raise NextCloudAsyncException('Invalid date.  Should be YYYY-MM-DD')
        else:
            now = dt.datetime.now()
            if expire_dt < now:
                raise NextCloudAsyncException('Invalid date.  Should be in the future.')

        return await self.ocs_query(
            method='POST',
            sub='/ocs/v2.php/apps/files_sharing/api/v1/shares',
            data={
                'path': path,
                'shareType': share_type.value,
                'shareWith': share_with,
                'permissions': permissions.value,
                'publicUpload': allow_public_upload,
                'password': password,
                'expireDate': expire_date,
                'note': note})

    async def delete_share(self, share_id: int):
        """Delete a share by share_id."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}',
            data={'share_id': share_id}
        )

    async def update_share(
            self,
            share_id: int,
            permissions: Optional[SharePermission] = None,
            password: Optional[str] = None,
            allow_public_upload: Optional[bool] = None,
            expire_date: Optional[str] = None,  # YYYY-MM-DD
            note: Optional[str] = None):
        """
        Update an existing share.

        Do fancy await stuff to update everyone in the same request.
        """
        reqs = []
        attrs = [
            ('permissions', permissions),
            ('password', password),
            ('publicUpload', allow_public_upload),
            ('expireDate', expire_date),
            ('note', note)]

        for a in attrs:
            if a[1]:
                reqs.append(self.__update_share(share_id, a[0], a[1]))

        return await asyncio.gather(*reqs)

    async def __update_share(self, share_id, key: str, value: Any):
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}',
            data={key: value})
