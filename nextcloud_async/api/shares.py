"""Implement Nextcloud Shares/Sharee APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
https://github.com/nextcloud/server/blob/892c473b064af222570a0c7155d9603a229d7312/apps/files_sharing/openapi.json

Not Implemented:
    Federated share management
"""

import asyncio

import datetime as dt
from dataclasses import dataclass

from enum import Enum, IntFlag
from typing import Any, Optional, List, Dict, Hashable, Tuple

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.helpers import bool2str
from nextcloud_async.exceptions import NextcloudException


class ShareType(Enum):
    """Share types.

    Reference:
        https://github.com/nextcloud/server/blob/master/lib/public/Share/IShare.php
    """

    user = 0
    group = 1
    public_link = 3
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


@dataclass
class Share:
    data: Dict[Hashable, Any]
    shares_api: 'Shares'

    async def delete(self):
        await self.shares_api.delete(self.id) # type: ignore
        self.data = {}

    async def update(self, **kwargs):  # type: ignore
        await self.shares_api.update(share_id=self.id, **kwargs)  # type: ignore

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Nextcloud Share "{self.path}" by {self.owner}>'

    def __repr__(self):
        return str(self)


class Shares(NextcloudModule):
    """Manage local shares on Nextcloud instances."""
    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '1'):
        self.stub = f'/apps/files_sharing/api/v{api_version}/shares'
        self.api = NextcloudOcsApi(client, ocs_version = '2')

    async def list(self) -> List[Share]:
        """Return list of all shares.

        Returns
        -------
            list: Share descriptions
        """
        response = await self._get()
        return [Share(x, self) for x in response]

    async def get_file_shares(
            self,
            path: str,
            reshares: bool = False,
            subfiles: bool = False) -> List[Share]:
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
        response = await self._get(
            data={
                'path': path,
                'reshares': bool2str(reshares),
                'subfiles': bool2str(subfiles)})
        return [Share(x, self) for x in response]

    async def get(self, share_id: int) -> Share:
        """Return information about a known share.

        Args
        ----
            share_id (int): Share ID

        Returns
        -------
            dict: Share description

        """
        response = await self._get(
            path=f'/{share_id}',
            data={'share_id': share_id})
        return Share(response[0], self)

    async def create(
            self,
            path: str,
            share_type: ShareType,
            permissions: SharePermission,
            share_with: Optional[str] = None,
            allow_public_upload: bool = False,
            password: Optional[str] = None,
            expire_date: Optional[dt.datetime] = None,
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
            NextcloudException: Invalid expiration date or date in the past.

        Returns
        -------
            # TODO : fill me in

        """

        # Checks the expire_date argument exists before evaluation, otherwise continues.
        if expire_date:
            if expire_date < dt.datetime.now():
                raise NextcloudException(status_code=406, reason='Invalid expiration date.  Should be in the future.')

        response = await self._post(
            data={
                'path': path,
                'shareType': share_type.value,
                'shareWith': share_with,
                'permissions': permissions.value,
                'publicUpload': str(allow_public_upload).lower(),
                'password': password,
                'expireDate': expire_date.strftime(r'%Y-%m-%d') if expire_date else None,
                'note': note})
        return(Share(response, self))

    async def delete(self, share_id: int):
        """Delete an existing share.

        Args
        ----
            share_id (int): The Share ID to delete

        Returns
        -------
            Query results.

        """
        return await self._delete(
            path=f'/{share_id}',
            data={'share_id': share_id})

    async def update(
            self,
            share_id: int,
            permissions: Optional[SharePermission] = None,
            password: Optional[str] = None,
            allow_public_upload: Optional[bool] = None,
            expire_date: Optional[str] = None,  # YYYY-MM-DD
            note: Optional[str] = None) -> List[Dict[Hashable, Any]]:
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
        attrs: List[Tuple[str, Any]] = [
            ('permissions', permissions),
            ('password', password),
            ('publicUpload', str(allow_public_upload).lower()),
            ('expireDate', expire_date),
            ('note', note)]

        reqs = [self.__update_share(share_id, k, v) for k, v in attrs if v]
        return await asyncio.gather(*reqs)  # type: ignore

    async def __update_share(self, share_id: int, key: str, value: Any) -> Dict[Hashable, Any]:
        return await self._put(
            path=f'/{share_id}',
            data={key: value})
