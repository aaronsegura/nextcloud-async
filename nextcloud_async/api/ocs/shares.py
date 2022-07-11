"""Implement Nextcloud Shares/Sharee APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-sharee-api.html

Not Implemented:
    Federated share management
"""

import asyncio

import datetime as dt

from enum import Enum, IntFlag
from typing import Any, Optional, List

from nextcloud_async.exceptions import NextCloudException


class ShareType(Enum):
    """Share types.

    Reference:
        https://github.com/nextcloud/server/blob/master/lib/public/Share/IShare.php
    """

    user = 0
    group = 1
    public = 3
    email = 4
    federated = 6
    circle = 7
    guest = 8
    remote_group = 9
    room = 10
    deck = 12
    deck_user = 13


class SharePermission(IntFlag):
    """Share Permissions."""

    read = 1
    update = 2
    create = 4
    delete = 8
    share = 16
    all = 31


class OCSShareAPI(object):
    """Manage local shares on Nextcloud instances."""

    async def get_all_shares(self):
        """Return list of all shares.

        Returns
        -------
            list: Share descriptions

        """
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v2.php/apps/files_sharing/api/v1/shares')

    async def get_file_shares(
            self,
            path: str,
            reshares: bool = False,
            subfiles: bool = False):
        """Return list of shares for given file/folder.

        Args
        ----
            path (str): Path to file

            reshares (bool, optional): Also list reshares. Defaults to False.

            subfiles (bool, optional): List recursively if `path` is a folder. Defaults to
            False.

        Returns
        -------
            list: File share descriptions

        """
        return await self.ocs_query(
            method='GET',
            sub='/ocs/v2.php/apps/files_sharing/api/v1/shares',
            data={
                'path': path,
                'reshares': reshares,
                'subfiles': subfiles})

    async def get_share(self, share_id: int):
        """Return information about a known share.

        Args
        ----
            share_id (int): Share ID

        Returns
        -------
            dict: Share description

        """
        return (await self.ocs_query(
            method='GET',
            sub=f'/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}',
            data={'share_id': share_id}))[0]

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
        """Create a new share.

        Args
        ----
            path (str): File to share

            share_type (ShareType): See ShareType Enum

            permissions (SharePermission): See SharePermissions Enum

            share_with (str, optional): Target of your sharing. Defaults to None.

            allow_public_upload (bool, optional): Whether to allow public upload to shared
            folder. Defaults to False.

            password (str, optional): Set a password on this share. Defaults to None.

            expire_date (str, optional): Expiration date (YYYY-MM-DD) for this share.
            Defaults to None.

            note (str, optional): Optional note to sharees. Defaults to None.

        Raises
        ------
            NextCloudException: Invalid expiration date or date in the past.

        Returns
        -------
            # TODO : fill me in

        """
        try:
            expire_dt = dt.datetime.strptime(expire_date, r'%Y-%m-%d')
        except ValueError:
            raise NextCloudException('Invalid date.  Should be YYYY-MM-DD')
        else:
            now = dt.datetime.now()
            if expire_dt < now:
                raise NextCloudException('Invalid date.  Should be in the future.')

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
        """Delete an existing share.

        Args
        ----
            share_id (int): The Share ID to delete

        Returns
        -------
            Query results.

        """
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
            note: Optional[str] = None) -> List:
        """Update properties of an existing share.

        This function makes asynchronous calls to the __update_share function
        since the underlying API can only accept one modification per query.
        We launch one asynchronous request per given parameter and return a
        list containing the results of all queries.

        Args
        ----
            share_id (int): The share ID to update

            permissions (SharePermission, optional): New permissions.
            Defaults to None.

            password (str, optional): New password. Defaults to None.

            allow_public_upload bool, optional): Whether to allow
            public uploads to shared folder. Defaults to None.

            expire_date str, optional): Expiration date (YYYY-MM-DD).
            Defaults to None.

            note (str): Note for this share.  Defaults to None.

        Returns
        -------
            List: responses from update queries

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
                reqs.append(self.__update_share(share_id, *a))

        return await asyncio.gather(*reqs)

    async def __update_share(self, share_id, key: str, value: Any):
        return await self.ocs_query(
            method='PUT',
            sub=f'/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}',
            data={key: value})

    async def search_sharees(
            self,
            item_type: str,
            lookup: bool = False,
            limit: int = 200,
            page: int = 1,
            search: str = None):
        """Search for people or groups to share things with.

        Args
        ----
            item_type (str): Item type (`file`, `folder`, `calendar`, etc...)

            lookup (bool, optional): Whether to use global Nextcloud lookup service.
            Defaults to False.

            limit (int, optional): How many results to return per request. Defaults to 200.

            page (int, optional): Return this page of results. Defaults to 1.

            search (str, optional): Search term. Defaults to None.

        Returns
        -------
            Dictionary of exact and potential matches.

        """
