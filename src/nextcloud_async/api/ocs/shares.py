"""Implement Nextcloud Shares/Sharee APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
https://github.com/nextcloud/server/blob/892c473b064af222570a0c7155d9603a229d7312/apps/files_sharing/openapi.json

Not Implemented:
    Federated share management
"""

import asyncio
import datetime as dt
import json
from collections.abc import Awaitable
from enum import Enum, IntFlag
from typing import Any, NotRequired, TypedDict, Unpack

from dateutil.tz import tzlocal

from nextcloud_async.api.mixins import NextcloudDataObject
from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsDriver
from nextcloud_async.exceptions import NextcloudError
from nextcloud_async.helpers import bool2str


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


class Share(NextcloudDataObject):
    _api: "SharesApi"

    def __str__(self) -> str:
        return f'<Nextcloud Share "{self.path}" by {self.displayname_owner}>'

    def __eq__(self, other: "Share") -> bool:
        return self.id == other.id

    def refresh_function(self) -> Awaitable:
        """Define how this object is refreshed."""
        return self._api.get(self.id)

    async def delete(self) -> None:
        """Delete this share."""
        await self._api.delete(self.id)
        self.data = {}

    class _ShareUpdateArgs(TypedDict):
        permissions: NotRequired[SharePermission]
        password: NotRequired[str]
        allow_public_upload: NotRequired[bool]
        expire_date: NotRequired[dt.date]
        attributes: NotRequired[str]
        send_mail: NotRequired[bool]
        note: NotRequired[str]

    async def update(self, **kwargs: Unpack[_ShareUpdateArgs]) -> None:  # noqa: D417
        """Update properties of this share.

        This function makes asynchronous calls to the __update_share function
        since the underlying API can only accept one modification per query.
        We launch one asynchronous request per given parameter.

        Args:
            permissions:
                New permissions.

            password:
                New password.

            allow_public_upload:
                Whether to allow public uploads to shared folder.

            expire_date:
                Expiration date (YYYY-MM-DD).

            note: \
                Note for this share.  Defaults to None.

            attributes: \
                serialized JSON string for share attributes (see docs)

            send_mail:
                send an email to the recipient. This will not send an email on its
                own. You will have to use the send-email endpoint to send the email.

        """
        await self._api.update(share_id=self.id, **kwargs)
        await self._refresh()

    async def send_email(self, password: str | None = None) -> None:
        """Re-send share e-mail to recipients.

        Args:
            password:
                Share password, if enabled

        """
        await self._api.send_email(self.id, password)


class SharesApi(NextcloudModule):
    """Manage local shares on Nextcloud instances."""

    def __init__(self, ocs_driver: NextcloudOcsDriver, api_version: str = "1") -> None:
        self.stub = f"/apps/files_sharing/api/v{api_version}/shares"
        self.api = ocs_driver

    async def get_file_shares(
        self,
        path: str | None = "",
        reshares: bool = False,
        subfiles: bool = False,
        shared_with_me: bool = False,
        include_tags: bool = False,
    ) -> list[Share]:
        """Return list of shares for given file/folder.

        Args:
            path:
                Path to file

            reshares:
                Also list reshares. Defaults to False.

            subfiles:
                List recursively if `path` is a folder. Defaults to False.

            shared_with_me:
                Only list files shared with the current user

            include_tags:
                Include tags with listing

        Returns:
            list[Share]

        """
        response = await self._get(
            data={
                "path": path,
                "reshares": bool2str(reshares),
                "subfiles": bool2str(subfiles),
                "shared_with_me": bool2str(shared_with_me),
                "include_tags": bool2str(include_tags),
            }
        )
        return [Share(x, self) for x in response]

    async def get(self, share_id: int) -> Share:
        """Return information about a known share.

        Args:
            share_id: Share ID

        Returns:
            Share object

        """
        response = await self._get(path=f"/{share_id}", data={"share_id": share_id})
        return Share(response[0], self)

    async def create(  # noqa: D417
        self,
        path: str,
        permissions: SharePermission,
        share_type: ShareType,
        share_with: dict[str, Any] | None = None,
        allow_public_upload: bool = False,
        password: str | None = None,
        send_password_by_talk: bool = False,
        expire_date: dt.date | None = None,
        note: str | None = None,
        label: str | None = None,
        send_mail: bool = False,
    ) -> Share:
        """Create a new share.

        Args:
            path:
                File to share

            share_type:
                See ShareType Enum

            permissions:
                See SharePermissions Enum

            share_with:
                Target of your sharing.

            allow_public_upload:
                Whether to allow public upload to shared folder. Defaults to False.

            password:
                Set a password on this share. Defaults to None.

            expire_date:
                Expiration datetime.date for this share.  Defaults to None.

            label:
                Adds a label for the share recipient.

            send_password_by_talk:
                Allows to set up a 'request password' room in Talk to distribute the
                password for this share.

            send_mail:
                Whether to send an e-mail to the recipient(s) after creation

            note: \
                Optional note to sharees. Defaults to None.

        Raises:
            NextcloudException: Date in the past.

        Returns:
            New Share object.

        """
        if expire_date:
            if expire_date <= dt.datetime.now(tz=tzlocal()).date():
                raise NextcloudError(
                    status_code=406,
                    reason="Invalid expiration date.  Should be in the future.",
                )

        response = await self._post(
            data={
                "path": path,
                "shareType": share_type.value,
                "shareWith": share_with,
                "permissions": permissions.value,
                "publicUpload": bool2str(allow_public_upload),
                "password": password,
                "expireDate": (
                    expire_date.strftime(r"%Y-%m-%d") if expire_date else None
                ),
                "note": note,
                "label": label,
                "sendPasswordByTalk": bool2str(send_password_by_talk),
                "sendMail": bool2str(send_mail),
            }
        )
        return Share(response, self)

    async def delete(self, share_id: int) -> None:
        """Delete an existing share.

        Args:
            share_id (int): The Share ID to delete

        Returns:
            Query results.

        """
        return await self._delete(path=f"/{share_id}", data={"share_id": share_id})

    #    This function makes asynchronous calls to the __update_share function
    #     since the underlying API can only accept one modification per query.
    #     We launch one asynchronous request per given parameter and return a
    #     list containing the results of all queries.

    async def update(
        self,
        share_id: int,
        permissions: SharePermission | None = None,  # noqa: ARG002
        password: str | None = None,  # noqa: ARG002
        allow_public_upload: bool | None = None,  # noqa: ARG002
        expire_date: dt.date | None = None,  # noqa: ARG002
        attributes: str | None = None,  # noqa: ARG002
        send_mail: bool | None = None,  # noqa: ARG002
        note: str | None = None,  # noqa: ARG002
    ) -> None:
        """Update properties of an existing share.

        This function makes asynchronous calls to the __update_share function
        since the underlying API can only accept one modification per query.
        We launch one asynchronous request per given parameter.

        Args:
            share_id:
                The share ID to update

            permissions:
                New permissions.

            password:
                New password.

            allow_public_upload:
                Whether to allow public uploads to shared folder.

            expire_date:
                Expiration date (YYYY-MM-DD).

            note: \
                Note for this share.  Defaults to None.

            attributes: \
                serialized JSON string for share attributes (see docs)

            send_mail:
                send an email to the recipient. This will not send an email on its
                own. You will have to use the send-email endpoint to send the email.

        """
        if attributes:
            attributes = json.dumps(attributes)

        # Translate from python arg names to nextcloud arg names
        if permissions:
            _permissions = permissions.value
        if allow_public_upload:
            _public_upload = bool2str(allow_public_upload)
        if send_mail:
            _send_mail = bool2str(send_mail)
        name_translations = [
            ("_permissions", "permissions"),
            ("password", "password"),
            ("_public_upload", "publicUpload"),
            ("expire_date", "expireDate"),
            ("note", "note"),
            ("attributes", "attributes"),
            ("_send_mail", "sendMail"),
        ]

        # Send requests as a batch
        updates = [(k[1], locals()[k[0]]) for k in name_translations if locals()[k[0]]]
        reqs = [self.__update_share(share_id, k, v) for k, v in updates]
        await asyncio.gather(*reqs)

    async def __update_share(self, share_id: int, key: str, value: Any) -> dict[str, Any]:
        return await self._put(path=f"/{share_id}", data={key: value})

    async def send_email(self, share_id: int, password: str | None = None) -> None:
        """Send an email to the recipients of a share.

        Args:
            share_id:
                Share ID

            password:
                The share password if enabled.

        """
        if password:
            data = {"password": password}
        else:
            data = None

        await self._post(path=f"/{share_id}/send-email", data=data)


def shares_api(client: NextcloudClient) -> SharesApi:
    """SharesApi Factory."""
    ocs_driver = NextcloudOcsDriver(client, version="2")
    return SharesApi(ocs_driver)
