import asyncio
import json
import logging
import warnings
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
import datetime as dt

import xmltodict
import httpx

from nextcloud_async import NextcloudClient
from nextcloud_async.api import (
    apps_api,
    files_api,
    groupfolders_api,
    groups_api,
    ldap_api,
    loginflowv2_api,
    maps_api,
    notifications_api,
    sharees_api,
    shares_api,
    status_api,
    talk_api,
    users_api,
    wipe_api,
)
from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.api.ocs.groupfolders import AclManagerType, GroupFoldersPermissions
from nextcloud_async.api.ocs.shares import SharePermission, ShareType
from nextcloud_async.api.ocs.status import PredefinedStatus, StatusType
from nextcloud_async.api.ocs.talk import TalkApi
from nextcloud_async.api.ocs.talk.chat import ChatFileShareMetadata
from nextcloud_async.api.ocs.talk.constants import (
    CallNotificationLevel,
    ConversationNotificationLevel,
    ConversationPermissionMode,
    ConversationReadOnlyState,
    ConversationType,
    ListableScope,
    ObjectSources,
    ParticipantPermissions,
    PermissionAction,
    SharedItemType,
)
from nextcloud_async.api.ocs.talk.rich_objects import NextcloudTalkRichObject
from nextcloud_async.exceptions import (
    NextcloudBadRequestError,
    NextcloudError,
    NextcloudForbiddenError,
    NextcloudNotFoundError,
    NextcloudRequestTimeoutError,
    NextcloudTooManyRequestsError,
    NextcloudUnauthorizedError,
)
from nextcloud_async.provider import HttpClientException
from nextcloud_async.provider.httpx import HttpXBasicAuth, HttpXClientProvider
from nextcloud_async.version import VERSION as __VERSION__

# Legacy Talk mixin named this Permissions.
Permissions = ParticipantPermissions

log = logging.getLogger("nextcloud_async")


@dataclass
class _NextcloudApis:
    apps: NextcloudModule
    files: NextcloudModule
    groupfolders: NextcloudModule
    groups: NextcloudModule
    ldap: NextcloudModule
    loginflow: NextcloudModule
    maps: NextcloudModule
    notifications: NextcloudModule
    sharees: NextcloudModule
    shares: NextcloudModule
    status: NextcloudModule
    talk: TalkApi
    users: NextcloudModule
    wipe: NextcloudModule


class NextCloudAsync:
    _apis: _NextcloudApis

    def __init__(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        user: str = "",
        password: str = "",
    ) -> None:
        """Construct a compatibility client (legacy NextCloudBaseAPI shape).

        Args:
            client: Raw ``httpx.AsyncClient`` instance.
            endpoint: Nextcloud base URL.
            user: Username (empty string allowed).
            password: Password or Nextcloud app password.

        """
        self.client = client
        self.endpoint = endpoint
        self.user = user
        self.password = password

        provider = HttpXClientProvider(client=client)
        basic_auth = HttpXBasicAuth(user, password)
        self._nc = NextcloudClient(
            endpoint=endpoint,
            http_client=provider,
            auth=basic_auth,
            user=user or None,
        )

        log.warning(
            (
                "NextCloudAsync is deprecated and will be removed in the future.  "
                "See https://github.com/aaronsegura/nextcloud_async for more info."
            ),
        )
        warnings.warn(
            (
                "NextCloudAsync is deprecated and will be removed in the future.  "
                "See https://github.com/aaronsegura/nextcloud_async for more info."
            ),
            DeprecationWarning,
            stacklevel=3,
        )

        self._apis = _NextcloudApis(
            apps=apps_api(self._nc),
            files=files_api(self._nc),
            groupfolders=groupfolders_api(self._nc),
            groups=groups_api(self._nc),
            ldap=ldap_api(self._nc),
            loginflow=loginflowv2_api(self._nc),
            maps=maps_api(self._nc),
            notifications=notifications_api(self._nc),
            sharees=sharees_api(self._nc),
            shares=shares_api(self._nc),
            status=status_api(self._nc),
            talk=talk_api(self._nc),
            users=users_api(self._nc),
            wipe=wipe_api(self._nc),
        )

        self._legacy_capabilities = None

    def _merge_request_headers(self, headers: dict[str, Any] | None) -> dict[str, Any]:
        hdrs = dict(headers or {})
        if self._nc.user_agent:
            hdrs.setdefault("User-Agent", self._nc.user_agent)
        if self._nc.request_headers:
            for key, value in self._nc.request_headers.items():
                hdrs.setdefault(key, value)
        return hdrs

    async def request(
        self,
        method: str = "GET",
        url: str | None = None,
        sub: str = "",
        data: dict[str, Any] = {},
        headers: dict[str, Any] = {},
    ) -> Any:
        """Send a request to the Nextcloud endpoint.

        Legacy signature (including mutable defaults) is preserved.
        Returns a response-like object from the modular HTTP provider.
        """
        payload: Any = data
        content: bytes | None = None
        if method.lower() == "get":
            sub = f"{sub}?{urlencode(data or {}, True)}"
            payload = None
        elif isinstance(data, (bytes, bytearray)):
            content = bytes(data)
            payload = None
        elif isinstance(data, str):
            content = data.encode("utf-8")
            payload = None

        hdrs = self._merge_request_headers(headers)
        target = f"{url}{sub}" if url else f"{self.endpoint}{sub}"
        try:
            response = await self._nc.http_client.request(
                method=method,
                auth=self._nc.auth,
                url=target,
                data=payload,
                content=content,
                headers=hdrs,
            )
        except HttpClientException as exc:
            reason = str(exc).lower()
            if "timeout" in reason or "timed out" in reason:
                raise NextcloudRequestTimeoutError() from exc
            raise

        match getattr(response, "status_code", None):
            case 304:
                raise NextcloudError(status_code=304, reason="Not Modified")
            case 400:
                raise NextcloudBadRequestError()
            case 401:
                raise NextcloudUnauthorizedError()
            case 403:
                raise NextcloudForbiddenError()
            case 404:
                raise NextcloudNotFoundError()
            case 429:
                raise NextcloudTooManyRequestsError()

        return response

    async def ocs_query(  # noqa: PLR0917
        self,
        method: str = "GET",
        url: str | None = None,
        sub: str = "",
        data: dict[str, Any] = {},
        headers: dict[str, Any] = {},
        include_headers: list = [],
    ) -> Any:
        """Submit an OCS-type query (legacy NextCloudOCSAPI.ocs_query)."""
        headers = dict(headers or {})
        data = dict(data or {})
        headers.update({"OCS-APIRequest": "true"})
        data.update({"format": "json"})

        response = await self.request(
            method, url=url, sub=sub, data=data, headers=headers
        )

        if response.content:
            response_content = json.loads(response.content.decode("utf-8"))
            ocs_meta = response_content["ocs"]["meta"]
            if ocs_meta["status"] != "ok":
                raise NextcloudError(
                    status_code=ocs_meta["statuscode"],
                    reason=ocs_meta["message"],
                )
            response_data = response_content["ocs"]["data"]
            if include_headers:
                response_headers = {}
                for header in include_headers:
                    response_headers.setdefault(
                        header, response.headers.get(header, None)
                    )
                return response_data, response_headers
            return response_data
        return None

    async def dav_query(
        self,
        method: str,
        url: str | None = None,
        sub: str = "",
        data: dict[str, Any] = {},
        headers: dict[str, Any] = {},
    ) -> Any:
        """Send a query to the Nextcloud DAV endpoint (legacy NextCloudDAVAPI)."""
        response = await self.request(
            method, url=url, sub=sub, data=data, headers=headers
        )
        if response.content:
            response_data = json.loads(json.dumps(xmltodict.parse(response.content)))
            if "d:error" in response_data:
                err = response_data["d:error"]
                raise NextcloudError(
                    f"{err['s:exception']}: {err['s:message']}".replace("\n", "")
                )
            return response_data["d:multistatus"]["d:response"]
        return None

    async def get_capabilities(self, capability: str | None = None) -> dict:
        """Return capabilities for this server (legacy NextCloudOCSAPI)."""
        if not self._legacy_capabilities:
            self._legacy_capabilities = await self.ocs_query(
                method="GET",
                sub="/ocs/v1.php/cloud/capabilities",
            )
        ret = self._legacy_capabilities
        if capability:
            if isinstance(capability, str):
                for item in capability.split("."):
                    if item in ret:
                        try:
                            ret = ret[item]
                        except TypeError as exc:
                            raise NextcloudError(
                                status_code=404,
                                reason=f"Capability not found: {item}",
                            ) from exc
                    else:
                        raise NextcloudError(
                            status_code=404,
                            reason=f"Capability not found: {item}",
                        )
            else:
                raise NextcloudError(
                    status_code=400, reason="`capability` must be a string."
                )
        return ret

    async def get_activity(
        self,
        since: int = 0,
        object_id: str | None = None,
        object_type: str | None = None,
        sort: str = "desc",
        limit: int = 50,
    ) -> Any:
        """Get recent activity for the current user.

        Legacy always requested activity headers, so this returns
        ``(data, headers)``.
        """
        data: dict[str, Any] = {}
        filt = ""
        if object_id and object_type:
            filt = "/filter"
            data.update({"object_type": object_type, "object_id": object_id})
        elif object_id or object_type:
            raise NextcloudError(
                "filter_object_type and filter_object are both required."
            )

        data.update({"limit": limit, "sort": sort, "since": since})
        return await self.ocs_query(
            method="GET",
            sub=f"/ocs/v2.php/apps/activity/api/v2/activity{filt}",
            data=data,
            include_headers=["X-Activity-First-Known", "X-Activity-Last-Given"],
        )

    async def get_file_guest_link(self, file_id: int) -> str:
        """Generate a generic sharable link for a file (expires in 8 hours)."""
        result = await self.ocs_query(
            method="POST",
            sub="/ocs/v2.php/apps/dav/api/v1/direct",
            data={"fileId": file_id},
        )
        return result["url"]

    # Legacy Apps API
    async def get_app(self, app_id: str) -> dict[str, Any]:
        """Get information about a specific app.

        Args:
            app_id: The app id

        Returns:
            App information

        """
        app = await self._apis.apps.get(app_id)
        return app.data

    async def get_apps(self, filter: str | None = None) -> list[str]:
        """Get a list of applications.

        Args:
            filter: Optional ``enabled`` / ``disabled`` filter.

        Returns:
            List of application ids (legacy ``response['apps']``).

        """
        return await self._apis.apps.get_all(filter)

    async def enable_app(self, app_id: str) -> dict[str, Any]:
        """Enable an app.

        Args:
            app_id: The app id

        Returns:
            Response data

        """
        result = await self._apis.apps.enable(app_id)
        return result.data

    async def disable_app(self, app_id: str) -> dict[str, Any]:
        """Disable an app.

        Args:
            app_id: The app id

        Returns:
            Response data

        """
        result = await self._apis.apps.disable(app_id)
        return result.data

    # Legacy GroupManager API
    async def search_groups(
        self, search: str, limit: int = 100, offset: int = 0
    ) -> list[str]:
        """Search for groups.

        Args:
            search: Search string
            limit: Results per page. Defaults to 100.
            offset: Page offset. Defaults to 0.

        Returns:
            List of group names.

        """
        groups = await self._apis.groups.search(search, limit, offset)
        return [g.id if hasattr(g, "id") else g for g in groups]

    async def create_group(self, group_id: str) -> list[str] | None:
        """Create a group.

        Args:
            group_id: The group name / id

        Returns:
            Empty OCS 100 response (list-like) like legacy ``ocs_query``.

        """
        await self._apis.groups.create(group_id)
        return []

    async def get_group_members(self, group_id: str) -> list[dict]:
        """Get members of a group.

        Args:
            group_id: The group id

        Returns:
            List of members

        """
        return await self._apis.groups.get_members(group_id)

    async def get_group_subadmins(self, group_id: str) -> list[str]:
        """Get subadmins of a group.

        Args:
            group_id: The group id

        Returns:
            List of subadmin user ids

        """
        return await self._apis.groups.get_subadmins(group_id)

    async def remove_group(self, group_id: str) -> dict[str, bool]:
        """Remove ``group_id``.

        Args:
            group_id: Group ID

        Returns:
            Success dict.

        """
        await self._apis.groups.delete(group_id)
        return {"success": True}

    # Legacy GroupFolderManager API
    @staticmethod
    def _groupfolders_permissions(
        permissions: GroupFoldersPermissions | int,
    ) -> GroupFoldersPermissions:
        if isinstance(permissions, GroupFoldersPermissions):
            return permissions
        return GroupFoldersPermissions(permissions)

    @staticmethod
    def _acl_manager_type(object_type: AclManagerType | str) -> AclManagerType:
        if isinstance(object_type, AclManagerType):
            return object_type
        return AclManagerType(object_type)

    async def get_all_group_folders(self) -> list[dict[str, Any]]:
        """Get list of all group folders."""
        folders = await self._apis.groupfolders.list()
        return [folder.data for folder in folders]

    async def create_group_folder(self, path: str) -> dict[str, Any]:
        """Create new group folder.

        Args:
            path: Path / mount point of the new group folder.

        """
        folder = await self._apis.groupfolders.create(path)
        return folder.data

    async def get_group_folder(self, folder_id: int) -> dict[str, Any]:
        """Get group folder with id ``folder_id``."""
        folder = await self._apis.groupfolders.get(folder_id)
        return folder.data

    async def remove_group_folder(self, folder_id: int) -> dict[str, bool]:
        """Delete group folder with id ``folder_id``."""
        await self._apis.groupfolders.delete(folder_id)
        return {"success": True}

    async def add_group_to_group_folder(
        self, group_id: str, folder_id: int
    ) -> dict[str, bool]:
        """Give ``group_id`` access to ``folder_id``.

        Arg order matches legacy: ``(group_id, folder_id)``.
        """
        await self._apis.groupfolders.permit_group(group_id, folder_id)
        return {"success": True}

    async def remove_group_from_group_folder(
        self, group_id: str, folder_id: int
    ) -> dict[str, bool]:
        """Remove ``group_id`` access from ``folder_id``.

        Arg order matches legacy: ``(group_id, folder_id)``.
        """
        await self._apis.groupfolders.deny_group(group_id, folder_id)
        return {"success": True}

    async def enable_group_folder_advanced_permissions(
        self, folder_id: int
    ) -> dict[str, bool]:
        """Enable advanced permissions on ``folder_id``."""
        await self._apis.groupfolders.enable_advanced_permissions(folder_id)
        return {"success": True}

    async def disable_group_folder_advanced_permissions(
        self, folder_id: int
    ) -> dict[str, bool]:
        """Disable advanced permissions on ``folder_id``."""
        await self._apis.groupfolders.disable_advanced_permissions(folder_id)
        return {"success": True}

    async def add_group_folder_advanced_permissions(
        self,
        folder_id: int,
        object_id: str,
        object_type: AclManagerType | str,
    ) -> dict[str, bool]:
        """Enable ``object_id`` as manager of advanced permissions."""
        await self._apis.groupfolders.add_acl_manager(
            folder_id,
            object_id,
            self._acl_manager_type(object_type),
        )
        return {"success": True}

    async def remove_group_folder_advanced_permissions(
        self,
        folder_id: int,
        object_id: str,
        object_type: AclManagerType | str,
    ) -> dict[str, bool]:
        """Disable ``object_id`` as manager of advanced permissions."""
        await self._apis.groupfolders.remove_acl_manager(
            folder_id,
            object_id,
            self._acl_manager_type(object_type),
        )
        return {"success": True}

    async def set_group_folder_permissions(
        self,
        folder_id: int,
        group_id: str,
        permissions: GroupFoldersPermissions | int,
    ) -> dict[str, bool]:
        """Set permissions a group has in a folder."""
        ok = await self._apis.groupfolders.set_acl(
            folder_id,
            group_id,
            self._groupfolders_permissions(permissions),
        )
        return {"success": bool(ok)}

    async def set_group_folder_quota(self, folder_id: int, quota: int) -> dict[str, bool]:
        """Set quota for group folder.

        Args:
            folder_id: Folder ID
            quota: Quota in bytes. ``-3`` for unlimited (legacy).

        """
        # Modular API treats None as unlimited; legacy used -3.
        api_quota: int | None = None if quota == -3 else quota
        await self._apis.groupfolders.set_quota(folder_id, api_quota)
        return {"success": True}

    async def rename_group_folder(
        self, folder_id: int, mountpoint: str
    ) -> dict[str, bool]:
        """Rename a group folder."""
        await self._apis.groupfolders.rename(folder_id, mountpoint)
        return {"success": True}

    # Legacy LDAP API
    async def create_ldap_config(self) -> dict[str, Any]:
        """Create a new LDAP configuration."""
        result = await self._apis.ldap.create()
        return result.data

    async def remove_ldap_config(self, id: str) -> None:
        """Remove the given LDAP configuration."""
        await self._apis.ldap.delete(id)

    async def get_ldap_config(self, id: str) -> dict[str, Any]:
        """Get an LDAP configuration."""
        result = await self._apis.ldap.get(id)
        return result.data

    async def set_ldap_config(self, id: str, config_data: dict[str, Any]) -> None:
        """Update the properties of a given LDAP configuration."""
        await self._apis.ldap.update(id, config_data)

    # Legacy NotificationManager API
    async def get_notifications(self) -> list[dict[str, Any]]:
        """Get user's notifications.

        Returns:
            List of notification dicts.

        """
        notifications = await self._apis.notifications.get_all()
        return [n.data for n in notifications]

    async def get_notification(self, not_id: int) -> dict[str, Any]:
        """Get a single notification.

        Args:
            not_id: Notification ID

        Returns:
            Notification data

        """
        notification = await self._apis.notifications.get(not_id)
        return notification.data

    async def remove_notifications(self) -> None:
        """Remove all of user's notifications."""
        await self._apis.notifications.clear()

    async def remove_notification(self, not_id: int) -> None:
        """Remove a single notification.

        Args:
            not_id: Notification ID

        """
        await self._apis.notifications.delete(not_id)

    # Legacy Shares API
    async def get_all_shares(self) -> list[dict[str, Any]]:
        """Return list of all shares."""
        response = await self._apis.shares._get()
        if isinstance(response, list):
            return [s.data if hasattr(s, "data") else s for s in response]
        return response

    async def search_sharees(
        self,
        item_type: str,
        lookup: bool = False,
        limit: int = 200,
        page: int = 1,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Search for people or groups to share things with.

        Arg order matches legacy: ``(item_type, lookup, limit, page, search)``.
        """
        return await self._apis.sharees.search_sharees(
            search=search,
            item_type=item_type,
            lookup=lookup,
            limit=limit,
            page=page,
        )

    async def get_file_shares(
        self,
        path: str,
        reshares: bool = False,
        subfiles: bool = False,
    ) -> list[dict[str, Any]]:
        """Return list of shares for given file/folder.

        Args:
            path: Path to file.
            reshares: Also list reshares.
            subfiles: List recursively if path is a folder.

        Returns:
            List of share dicts.

        """
        shares = await self._apis.shares.get_file_shares(path, reshares, subfiles)
        return [s.data for s in shares]

    async def get_share(self, share_id: int) -> dict[str, Any]:
        """Return information about a known share.

        Args:
            share_id: Share ID.

        Returns:
            Share data dict.

        """
        share = await self._apis.shares.get(share_id)
        return share.data

    async def create_share(  # noqa: D417, PLR0917
        self,
        path: str,
        share_type: int,
        permissions: int,
        share_with: str | dict[str, Any] | None = None,
        allow_public_upload: bool = False,
        password: str | None = None,
        expire_date: str | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        """Create a new share.

        Legacy order: ``(path, share_type, permissions, ...)``.

        Args:
            path: File to share.
            share_type: See ShareType enum.
            permissions: See SharePermission enum.
            share_with: Target of your sharing.
            allow_public_upload: Whether to allow public upload.
            password: Set a password on this share.
            expire_date: Expiration date (YYYY-MM-DD).
            note: Optional note to sharees.

        Returns:
            Share data dict.

        """
        if isinstance(share_type, ShareType):
            stype = share_type
        else:
            stype = ShareType(share_type)
        if isinstance(permissions, SharePermission):
            perms = permissions
        else:
            perms = SharePermission(permissions)
        expire: dt.date | None = None
        if isinstance(expire_date, dt.date) and not isinstance(expire_date, dt.datetime):
            expire = expire_date
        elif isinstance(expire_date, str):
            expire = dt.date.fromisoformat(expire_date)
        share = await self._apis.shares.create(
            path=path,
            permissions=perms,
            share_type=stype,
            share_with=share_with,
            allow_public_upload=allow_public_upload,
            password=password,
            expire_date=expire,
            note=note,
        )
        return share.data

    async def delete_share(self, share_id: int) -> None:
        """Delete an existing share.

        Args:
            share_id: The Share ID to delete.

        """
        await self._apis.shares.delete(share_id)

    async def update_share(  # noqa: D417, PLR0917
        self,
        share_id: int,
        permissions: int | None = None,
        password: str | None = None,
        allow_public_upload: bool | None = None,
        expire_date: str | None = None,
        note: str | None = None,
    ) -> list:
        """Update properties of an existing share.

        Legacy issued one OCS PUT per given field and returned the gathered list.

        Args:
            share_id: The share ID to update.
            permissions: New permissions.
            password: New password.
            allow_public_upload: Allow public uploads to shared folder.
            expire_date: Expiration date (YYYY-MM-DD).
            note: Note for this share.

        Returns:
            List of per-field update responses.

        """
        reqs = []
        if permissions is not None:
            perms = (
                permissions.value
                if isinstance(permissions, SharePermission)
                else permissions
            )
            reqs.append(
                self._apis.shares._put(path=f"/{share_id}", data={"permissions": perms})
            )
        if password:
            reqs.append(
                self._apis.shares._put(path=f"/{share_id}", data={"password": password})
            )
        if allow_public_upload is not None:
            reqs.append(
                self._apis.shares._put(
                    path=f"/{share_id}",
                    data={"publicUpload": str(allow_public_upload).lower()},
                )
            )
        if expire_date:
            reqs.append(
                self._apis.shares._put(
                    path=f"/{share_id}", data={"expireDate": expire_date}
                )
            )
        if note:
            reqs.append(self._apis.shares._put(path=f"/{share_id}", data={"note": note}))
        if not reqs:
            return []
        return list(await asyncio.gather(*reqs))

    # Legacy Status API
    @staticmethod
    def _status_clear_at(
        clear_at: dt.datetime | int | float | None,
    ) -> dt.datetime | None:
        if clear_at is None:
            return None
        if isinstance(clear_at, dt.datetime):
            return clear_at
        return dt.datetime.fromtimestamp(float(clear_at))

    async def get_status(self) -> dict[str, Any]:
        """Get current status."""
        result = await self._apis.status.get()
        return result.data

    async def set_status(self, status_type: str) -> dict[str, Any]:
        """Set user status.

        Args:
            status_type:
                One of: online, away, dnd, invisible, offline

        Returns:
            New status data

        """
        return await self._apis.status.set(StatusType[status_type])

    async def get_predefined_statuses(self) -> list[dict[str, Any]]:
        """Get list of predefined statuses."""
        statuses = await self._apis.status.get_predefined_statuses()
        return [s.data for s in statuses]

    async def choose_predefined_status(
        self,
        message_id: str | int,
        clear_at: dt.datetime | int | float | None = None,
    ) -> dict[str, Any]:
        """Choose from predefined status messages.

        Args:
            message_id:
                Message ID of the predefined status.

            clear_at:
                Unix timestamp (or datetime) at which to clear this status.

        Returns:
            New status description

        """
        predefined = PredefinedStatus({"id": message_id})
        return await self._apis.status.choose_predefined_status(
            predefined, self._status_clear_at(clear_at)
        )

    async def set_status_message(
        self,
        message: str,
        status_icon: str | None = None,
        clear_at: int | float | dt.datetime | None = None,
    ) -> dict[str, Any]:
        """Set a custom status message.

        Args:
            message: Your custom message
            status_icon: Emoji icon. Defaults to None.
            clear_at: Unix timestamp (or datetime) at which to clear this message.

        Returns:
            New status description

        """
        return await self._apis.status.set_message(
            message, status_icon, self._status_clear_at(clear_at)
        )

    async def clear_status_message(self) -> None:
        """Clear status message.

        Legacy returned the empty OCS DELETE body (None).
        """
        await self._apis.status.clear_message()

    async def get_all_user_statuses(
        self,
        limit: int | None = 100,
        offset: int | None = 0,
    ) -> list[dict[str, Any]]:
        """Get all user statuses."""
        statuses = await self._apis.status.get_all_user_statuses(
            limit=limit if limit is not None else 100,
            offset=offset if offset is not None else 0,
        )
        return [s.data for s in statuses]

    async def get_user_status(self, user: str) -> dict[str, Any]:
        """Get the status for a specific user."""
        status = await self._apis.status.get_user_status(user)
        return status.data

    # Legacy UserManager API
    async def user_autocomplete(
        self,
        search: str,
        item_type: str | None = None,
        item_id: str | None = None,
        sorter: str | None = None,
        share_types: list[ShareType] = [ShareType["user"]],
        limit: int = 25,
    ) -> list[dict[str, str]]:
        """Search for a user using incomplete information.

        Modular UsersApi has no autocomplete helper; call the OCS v2
        ``/core/autocomplete/get`` endpoint (legacy path) via the shares
        driver's OCS v2 client.
        """
        types = share_types if share_types is not None else [ShareType["user"]]
        share_types_values = [
            x.value if isinstance(x, ShareType) else int(x) for x in types
        ]
        # SharesApi is wired with OCS v2 (matches legacy /ocs/v2.php/...).
        return await self._apis.shares.driver.get(
            path="/core/autocomplete/get",
            data={
                "search": search,
                "itemType": item_type,
                "itemId": item_id,
                "sorter": sorter,
                "shareTypes[]": share_types_values,
                "limit": limit,
            },
        )

    async def create_user(  # noqa: PLR0917
        self,
        user_id: str,
        display_name: str,
        email: str,
        quota: int | str | None,
        language: str,
        groups: list[str] = [],
        subadmin: list[str] = [],
        password: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Nextcloud user.

        Args:
            user_id: New user ID
            display_name: User display Name (eg. "Your Name")
            email: E-mail Address
            quota: User quota, in bytes.  None for unlimited.
            language: User language
            groups: Groups user should be added to.
            subadmin: Groups user should be admin for.
            password: User password.

        Returns:
            User data dict.

        """
        user = await self._apis.users.create(
            user_id=user_id,
            display_name=display_name,
            email=email,
            language=language,
            quota=quota,
            groups=groups,
            subadmin=subadmin,
            password=password,
        )
        return user.data

    async def search_users(
        self,
        search: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[str]:
        """Search for users.

        Args:
            search: Search string
            limit: Results per request. Defaults to 100.
            offset: Paging offset. Defaults to 0.

        Returns:
            List of user ID matches.

        """
        return await self._apis.users.search(search, limit, offset)

    async def get_user(self, user_id: str | None = None) -> dict[str, Any]:
        """Get a valid user.

        Args:
            user_id: User ID. Defaults to current user if None.

        Returns:
            User description dict.

        """
        target = user_id if user_id is not None else self._nc.user
        user = await self._apis.users.get(target)
        return user.data

    async def get_users(self) -> list[str]:
        """Return all user IDs.

        Admin required.

        Returns:
            List of user IDs.

        """
        return await self._apis.users.get_all()

    async def update_user(
        self,
        user_id: str,
        new_data: dict[str, Any],
    ) -> list:
        """Update a user's information.

        Args:
            user_id: User ID
            new_data: New key/value pairs

        Returns:
            List of per-field OCS responses (legacy ``asyncio.gather``).

        """
        reqs = [self._apis.users._update_user(user_id, k, v) for k, v in new_data.items()]
        if not reqs:
            return []
        return list(await asyncio.gather(*reqs))

    async def get_user_editable_fields(self) -> list[str]:
        """Get user-editable fields.

        Returns:
            List of user-editable fields.

        """
        return await self._apis.users.get_editable_fields()

    async def disable_user(self, user_id: str) -> list[str]:
        """Disable user_id.

        Must be admin.

        Args:
            user_id: User ID

        Returns:
            Empty OCS 100 list (legacy ``ocs_query``).

        """
        await self._apis.users.disable(user_id)
        return []

    async def enable_user(self, user_id: str) -> list[str]:
        """Enable user_id.  Must be admin.

        Args:
            user_id: User ID

        Returns:
            Empty OCS 100 list (legacy ``ocs_query``).

        """
        await self._apis.users.enable(user_id)
        return []

    async def remove_user(self, user_id: str) -> list[str]:
        """Remove existing user_id.

        Args:
            user_id: User ID

        Returns:
            Empty OCS 100 list (legacy ``ocs_query``).

        """
        await self._apis.users.delete(user_id)
        return []

    async def get_user_groups(self, user_id: str | None = None) -> list[str]:
        """Get list of groups user_id belongs to.

        Args:
            user_id: User ID. Defaults to current user.

        Returns:
            List of group ids.

        """
        groups = await self._apis.users.get_group_membership(user_id)
        return [g.id for g in groups]

    async def add_user_to_group(self, user_id: str, group_id: str) -> list[str]:
        """Add user_id to group_id.

        Args:
            user_id: User ID
            group_id: Group ID

        Returns:
            Empty OCS 100 list (legacy ``ocs_query``).

        """
        await self._apis.users.add_to_group(user_id, group_id)
        return []

    async def remove_user_from_group(self, user_id: str, group_id: str) -> list[str]:
        """Remove user_id from group_id.

        Args:
            user_id: User ID
            group_id: Group Id

        Returns:
            Empty OCS 100 list (legacy ``ocs_query``).

        """
        await self._apis.users.remove_from_group(user_id, group_id)
        return []

    async def promote_user_to_subadmin(self, user_id: str, group_id: str) -> list[str]:
        """Make user_id a subadmin of group_id.

        Args:
            user_id: User ID
            group_id: Group ID

        Returns:
            Empty OCS 100 list (legacy ``ocs_query``).

        """
        await self._apis.users.promote_to_group_subadmin(user_id, group_id)
        return []

    async def demote_user_from_subadmin(self, user_id: str, group_id: str) -> list[str]:
        """Demote user_id from subadmin of group_id.

        Args:
            user_id: User ID
            group_id: Group ID

        Returns:
            Empty OCS 100 list (legacy ``ocs_query``).

        """
        await self._apis.users.demote_from_group_subadmin(user_id, group_id)
        return []

    async def get_user_subadmin_groups(self, user_id: str) -> list[str]:
        """Return list of groups of which user_id is subadmin.

        Args:
            user_id: User ID

        Returns:
            List of group ids.

        """
        groups = await self._apis.users.get_subadmin_groups(user_id)
        return [g.id for g in groups]

    async def resend_welcome_email(self, user_id: str) -> list[str]:
        """Re-send initial welcome e-mail to user_id.

        Args:
            user_id: User ID

        Returns:
            Empty OCS 100 list (legacy ``ocs_query``).

        """
        await self._apis.users.resend_welcome_email(user_id)
        return []

    # Legacy NextCloudTalkAPI
    @staticmethod
    def _talk_conversation_type(
        room_type: ConversationType | str | int,
    ) -> ConversationType:
        if isinstance(room_type, ConversationType):
            return room_type
        if isinstance(room_type, int):
            return ConversationType(room_type)
        return ConversationType[room_type]

    @staticmethod
    def _talk_notification_level(
        level: ConversationNotificationLevel | str | int,
    ) -> ConversationNotificationLevel:
        if isinstance(level, ConversationNotificationLevel):
            return level
        if isinstance(level, int):
            return ConversationNotificationLevel(level)
        return ConversationNotificationLevel[level]

    @staticmethod
    def _talk_call_notification_level(
        level: CallNotificationLevel | str | int,
    ) -> CallNotificationLevel:
        if isinstance(level, CallNotificationLevel):
            return level
        if isinstance(level, int):
            return CallNotificationLevel(level)
        if level in CallNotificationLevel.__members__:
            return CallNotificationLevel[level]
        # Legacy used NotificationLevel names for call notify; map best-effort.
        legacy_map = {
            "default": CallNotificationLevel.on,
            "always_notify": CallNotificationLevel.on,
            "notify_on_mention": CallNotificationLevel.on,
            "never_notify": CallNotificationLevel.off,
        }
        return legacy_map[level]

    @staticmethod
    def _talk_listable_scope(scope: ListableScope | str | int) -> ListableScope:
        if isinstance(scope, ListableScope):
            return scope
        if isinstance(scope, int):
            return ListableScope(scope)
        return ListableScope[scope]

    @staticmethod
    def _talk_read_only_state(
        state: ConversationReadOnlyState | int,
    ) -> ConversationReadOnlyState:
        if isinstance(state, ConversationReadOnlyState):
            return state
        return ConversationReadOnlyState(state)

    @staticmethod
    def _talk_participant_permissions(
        permissions: ParticipantPermissions | int,
    ) -> ParticipantPermissions:
        if isinstance(permissions, ParticipantPermissions):
            return permissions
        return ParticipantPermissions(permissions)

    @staticmethod
    def _talk_permission_mode(
        mode: ConversationPermissionMode | str,
    ) -> ConversationPermissionMode:
        if isinstance(mode, ConversationPermissionMode):
            return mode
        return ConversationPermissionMode(mode)

    @staticmethod
    def _talk_permission_action(mode: PermissionAction | str) -> PermissionAction | str:
        if isinstance(mode, PermissionAction):
            return mode
        if mode == "set":
            # Modular PermissionAction has add/remove only; callers handle "set".
            return "set"
        return PermissionAction(mode)

    @staticmethod
    def _talk_object_source(source: ObjectSources | str) -> ObjectSources:
        if isinstance(source, ObjectSources):
            return source
        return ObjectSources(source)

    @staticmethod
    def _talk_shared_item_type(metadata_type: SharedItemType | str) -> SharedItemType:
        if isinstance(metadata_type, SharedItemType):
            return metadata_type
        try:
            return SharedItemType(metadata_type)
        except ValueError:
            return SharedItemType[metadata_type]

    async def get_conversations(
        self,
        status_update: bool = False,
        include_status: bool = False,
    ) -> list[dict[str, Any]]:
        """Return list of user's conversations."""
        conversations = await self._apis.talk.conversations.get_all(
            status_update=status_update,
            include_status=include_status,
        )
        return [c.data for c in conversations]

    async def create_conversation(
        self,
        room_type: str,
        invite: str = "",
        room_name: str = "",
        source: str = "",
    ) -> dict[str, Any]:
        """Create a new conversation."""
        conversation = await self._apis.talk.conversations.create(
            room_type=self._talk_conversation_type(room_type),
            invite=invite,
            room_name=room_name,
            source=source,
        )
        return conversation.data

    async def get_conversation(self, room_token: str) -> dict[str, Any]:
        """Get a specific conversation."""
        conversation = await self._apis.talk.conversations.get(room_token)
        return conversation.data

    async def get_open_conversation_list(self) -> list[dict[str, Any]]:
        """Get list of open rooms."""
        conversations = await self._apis.talk.conversations.list_open()
        return [c.data for c in conversations]

    async def rename_conversation(self, token: str, new_name: str) -> dict[str, bool]:
        """Rename the room."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.rename(new_name)
        return {"success": True}

    async def remove_conversations(self, token: str) -> dict[str, bool]:
        """Delete the room."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.delete()
        return {"success": True}

    async def set_conversation_description(
        self, token: str, description: str
    ) -> dict[str, bool]:
        """Set description on room."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.set_description(description)
        return {"success": True}

    async def conversation_allow_guests(
        self, token: str, allow_guests: bool
    ) -> dict[str, bool]:
        """Allow or disallow guests in a conversation."""
        conversation = await self._apis.talk.conversations.get(token)
        if allow_guests:
            await conversation.allow_guests()
        else:
            await conversation.disallow_guests()
        return {"success": True}

    async def read_only(self, token: str, state: int) -> dict[str, bool]:
        """Set read-only for a conversation."""
        await self._apis.talk.conversations.read_only(
            token, self._talk_read_only_state(state)
        )
        return {"success": True}

    async def set_conversation_password(
        self, token: str, password: str
    ) -> dict[str, bool]:
        """Set password for a conversation."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.set_password(password)
        return {"success": True}

    async def add_conversation_to_favorites(self, token: str) -> dict[str, bool]:
        """Add conversation to favorites."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.add_to_favorites()
        return {"success": True}

    async def remove_conversation_from_favorites(self, token: str) -> dict[str, bool]:
        """Remove conversation from favorites."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.remove_from_favorites()
        return {"success": True}

    async def set_conversation_notification_level(
        self,
        token: str,
        notification_level: str,
    ) -> dict[str, bool]:
        """Set notification level."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.set_notification_level(
            self._talk_notification_level(notification_level)
        )
        return {"success": True}

    async def set_call_notification_level(
        self,
        token: str,
        notification_level: str,
    ) -> dict[str, bool]:
        """Set notification level for calls."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.set_call_notification_level(
            self._talk_call_notification_level(notification_level)
        )
        return {"success": True}

    async def set_participant_permissions(
        self,
        token: str,
        scope: str = "default",
        permissions: ParticipantPermissions | int = Permissions(0),
    ) -> dict[str, bool]:
        """Set default or call permissions for conversation attendees."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.set_default_permissions(
            permissions=self._talk_participant_permissions(permissions),
            mode=self._talk_permission_mode(scope),
        )
        return {"success": True}

    async def join_conversation(
        self,
        token: str,
        password: str | None,
        force: bool = True,
    ) -> dict[str, Any]:
        """Join a conversation (available for call and chat)."""
        return await self._apis.talk.participants.join(
            room_token=token, password=password, force=force
        )

    async def leave_conversation(self, token: str) -> dict[str, bool]:
        """Remove yourself from a conversation."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.leave()
        return {"success": True}

    async def invite_to_conversation(
        self,
        token: str,
        invitee: str,
        source: str = "users",
    ) -> int | None:
        """Invite a user/group/email/circle to this room.

        Modular add_* APIs do not return the optional new conversation type
        integer that legacy exposed; always returns None.
        """
        conversation = await self._apis.talk.conversations.get(token)
        src = self._talk_object_source(source)
        if src is ObjectSources.user:
            await conversation.add_user(invitee)
        elif src is ObjectSources.email:
            await conversation.add_email(invitee)
        elif src is ObjectSources.circle:
            await conversation.add_circle(invitee)
        else:
            # add_group expects a Group object; use participants API for groups/etc.
            await self._apis.talk.participants.add_to_conversation(
                room_token=token, invitee=invitee, source=src
            )
        return None

    async def get_conversation_participants(
        self,
        token: str,
        include_status: bool = False,
    ) -> list[dict[str, Any]]:
        """Return list of participants."""
        participants, _ = await self._apis.talk.participants.get_all(
            room_token=token, include_status=include_status
        )
        return [p.data for p in participants]

    async def send_to_conversation(
        self,
        token: str,
        message: str,
        reply_to: int = 0,
        display_name: str | None = None,
        reference_id: str | None = None,
        silent: bool = False,
    ) -> dict[str, Any]:
        """Send a new chat message."""
        conversation = await self._apis.talk.conversations.get(token)
        kwargs: dict[str, Any] = {
            "message": message,
            "reply_to": reply_to,
            "silent": silent,
        }
        if display_name is not None:
            kwargs["display_name"] = display_name
        if reference_id is not None:
            kwargs["reference_id"] = reference_id
        msg, _headers = await conversation.send(**kwargs)
        return msg.data

    async def set_conversation_scope(
        self, token: str, scope: str
    ) -> dict[str, bool] | None:
        """Change who can see the conversation."""
        conversation = await self._apis.talk.conversations.get(token)
        await conversation.set_scope(self._talk_listable_scope(scope))
        return {"success": True}

    async def set_conversation_permissions_for_participants(
        self,
        token: str,
        permissions: ParticipantPermissions | int,
        mode: str = "add",
    ) -> dict[str, bool]:
        """Set permissions for all attendees in a conversation.

        Modular API has no dedicated all-attendees helper; call the Talk
        attendees/permissions/all endpoint via ParticipantsApi._put.
        """
        perms = self._talk_participant_permissions(permissions)
        action = self._talk_permission_action(mode)
        mode_value = action.value if isinstance(action, PermissionAction) else action
        await self._apis.talk.participants._put(
            path=f"/room/{token}/attendees/permissions/all",
            data={"mode": mode_value, "permissions": int(perms)},
        )
        return {"success": True}

    async def set_conversation_guest_display_name(
        self,
        token: str,
        display_name: str,
    ) -> dict[str, bool]:
        """Set display name as a guest."""
        await self._apis.talk.participants.set_guest_display_name(token, display_name)
        return {"success": True}

    async def get_conversation_messages(
        self,
        token: str,
        look_into_future: bool = False,
        limit: int = 100,
        timeout: int = 30,
        last_known_message: int | None = None,
        last_common_read: int | None = None,
        set_read_marker: bool = True,
        include_last_known: bool = False,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Receive chat messages of a conversation.

        Legacy annotated List[Dict] but actually returned ``(messages, headers)``.
        """
        conversation = await self._apis.talk.conversations.get(token)
        kwargs: dict[str, Any] = {
            "look_into_future": look_into_future,
            "limit": limit,
            "timeout": timeout,
            "set_read_marker": set_read_marker,
            "include_last_known": include_last_known,
        }
        if last_known_message is not None:
            kwargs["last_known_message_id"] = last_known_message
        if last_common_read is not None:
            kwargs["last_common_read_id"] = last_common_read
        messages, headers = await conversation.get_messages(**kwargs)
        return [m.data for m in messages], headers

    async def send_rich_object_to_conversation(
        self,
        token: str,
        rich_object: NextcloudTalkRichObject,
        reference_id: str | None = None,
        actor_display_name: str = "Guest",
    ) -> dict[str, Any]:
        """Share a rich object to the chat."""
        conversation = await self._apis.talk.conversations.get(token)
        kwargs: dict[str, Any] = {
            "rich_object": rich_object,
            "actor_display_name": actor_display_name,
        }
        if reference_id is not None:
            kwargs["reference_id"] = reference_id
        msg, _headers = await conversation.send_rich_object(**kwargs)
        return msg.data

    async def clear_conversation_history(self, token: str) -> dict[str, Any]:
        """Clear chat history."""
        conversation = await self._apis.talk.conversations.get(token)
        message = await conversation.clear_history()
        return message.data

    async def get_conversation_autocomplete_suggestions(
        self,
        token: str,
        search: str,
        limit: int = 20,
        include_status: bool = False,
    ) -> list[dict[str, Any]]:
        """Get mention autocomplete suggestions."""
        conversation = await self._apis.talk.conversations.get(token)
        suggestions = await conversation.suggest_autocompletes(
            search=search, limit=limit, include_status=include_status
        )
        return [s.data for s in suggestions]

    async def share_file_to_conversation(
        self,
        token: str,
        path: str,
        reference_id: str | None = None,
        metadata_type: str = "comment",
    ) -> dict[str, Any] | int:
        """Share a file to the chat.

        Modular ``share_file`` returns share id (int); legacy returned share dict.
        """
        conversation = await self._apis.talk.conversations.get(token)
        metadata = ChatFileShareMetadata(
            message_type=self._talk_shared_item_type(metadata_type),
            caption="",
        )
        kwargs: dict[str, Any] = {"path": path, "metadata": metadata}
        if reference_id is not None:
            kwargs["reference_id"] = reference_id
        result = await conversation.share_file(**kwargs)
        if isinstance(result, tuple):
            result = result[0]
        if hasattr(result, "data"):
            return result.data
        return result

    async def remove_participant_from_conversation(
        self,
        token: str,
        attendee_id: int,
    ) -> dict[str, bool]:
        """Delete an attendee from conversation."""
        await self._apis.talk.participants.remove_from_conversation(token, attendee_id)
        return {"success": True}

    async def promote_conversation_participant(
        self,
        token: str,
        attendee_id: int,
    ) -> dict[str, bool]:
        """Promote a user or guest to moderator."""
        await self._apis.talk.participants.promote_to_moderator(token, attendee_id)
        return {"success": True}

    async def demote_conversation_participant(
        self,
        token: str,
        attendee_id: int,
    ) -> dict[str, bool]:
        """Demote a moderator to user or guest."""
        await self._apis.talk.participants.demote(token, attendee_id)
        return {"success": True}

    async def set_conversation_participant_permissions(
        self,
        token: str,
        attendee_id: int,
        permissions: ParticipantPermissions | int,
        mode: str = "add",
    ) -> dict[str, bool]:
        """Set permissions for an attendee."""
        perms = self._talk_participant_permissions(permissions)
        action = self._talk_permission_action(mode)
        if action == "set":
            # Modular PermissionAction lacks "set"; hit endpoint directly.
            await self._apis.talk.participants._put(
                path=f"/room/{token}/attendees/permissions",
                data={
                    "attendeeId": attendee_id,
                    "method": "set",
                    "permissions": int(perms),
                },
            )
        else:
            assert isinstance(action, PermissionAction)
            await self._apis.talk.participants.set_conversation_permissions(
                room_token=token,
                attendee_id=attendee_id,
                permissions=perms,
                mode=action,
            )
        return {"success": True}

    async def remove_conversation_message(
        self,
        token: str,
        message_id: int,
    ) -> dict[str, Any]:
        """Delete a chat message."""
        conversation = await self._apis.talk.conversations.get(token)
        message, _headers = await conversation.delete_message(message_id)
        return message.data

    async def mark_conversation_message_read(
        self,
        token: str,
        message_id: int,
    ) -> dict[str, Any]:
        """Mark chat as read.

        Legacy ``message_id`` maps to modular ``last_read_message_id``.
        """
        headers = await self._apis.talk.chat.mark_as_read(
            room_token=token, last_read_message_id=message_id
        )
        return headers or {"success": True}

    async def mark_conversation_message_unread(
        self,
        token: str,
        message_id: int,
    ) -> dict[str, Any]:
        """Mark chat as unread.

        Modular ``mark_as_unread`` takes only room_token; ``message_id`` is
        accepted for signature compatibility but ignored.
        """
        headers = await self._apis.talk.chat.mark_as_unread(room_token=token)
        return headers or {"success": True}

    async def get_shared_items_overview(
        self,
        token: str,
        limit: int = 10,
    ) -> Any:
        """List overview of items shared into a chat.

        Uses ChatApi._get for the overview payload shape (dict-by-type) that
        legacy returned; modular list_shared_items flattens to Message list.
        """
        response, _ = await self._apis.talk.chat._get(
            path=f"/chat/{token}/share/overview",
            data={"limit": limit},
        )
        return response

    # Legacy FileManager API
    async def list_files(
        self, path: str, properties: list[str] = []
    ) -> list[dict[str, Any]]:
        """Return a list of files at ``path``.

        Legacy annotated Dict but ``dav_query`` returned the DAV
        ``d:response`` list (or a single dict). Modular ``get_all`` always
        normalizes to a list of file dicts.
        """
        user_path = await self._apis.files.get_all(path, properties=properties)
        return [f.data for f in user_path._files]

    async def download_file(self, path: str) -> bytes:
        """Download the file at ``path``."""
        return await self._apis.files.download(path)

    async def upload_file(self, local_path: str, remote_path: str) -> None:
        """Upload a file."""
        await self._apis.files.upload(local_path, remote_path)

    async def upload_file_chunked(
        self, local_path: str, remote_path: str, chunk_size: int
    ) -> None:
        """Upload a large file in chunks."""
        await self._apis.files.upload_file_chunked(local_path, remote_path, chunk_size)

    async def create_folder(self, path: str, create_parents: bool = False) -> None:
        """Create a new folder/directory."""
        await self._apis.files.mkdir(path, create_parents=create_parents)

    async def create_folder_with_parents(self, path: str) -> None:
        """Create folder with parents (mkdir -p)."""
        await self._apis.files.mkdir_with_parents(path)

    async def delete(self, path: str) -> None:
        """Delete file or folder."""
        await self._apis.files.delete(path)

    async def move(self, source: str, dest: str, overwrite: bool = False) -> None:
        """Move a file or folder."""
        await self._apis.files.move(source, dest, overwrite=overwrite)

    async def copy(self, source: str, dest: str, overwrite: bool = False) -> None:
        """Copy a file or folder."""
        await self._apis.files.copy(source, dest, overwrite=overwrite)

    async def set_favorite(self, path: str) -> dict[str, Any]:
        """Set file/folder as a favorite."""
        result = await self._apis.files.set_favorite(path)
        return result.data

    async def remove_favorite(self, path: str) -> dict[str, Any]:
        """Remove file/folder as a favorite."""
        result = await self._apis.files.unset_favorite(path)
        return result.data

    async def get_favorites(self, path: str | None = "") -> list[dict[str, Any]]:
        """List favorites below given path."""
        favorites = await self._apis.files.get_favorites(path or "")
        return [f.data for f in favorites]

    async def get_trashbin(self) -> list[dict[str, Any]]:
        """Get items in the trash."""
        trash = await self._apis.files.get_trashbin()
        return [f.data for f in trash._files]

    async def empty_trashbin(self) -> None:
        """Empty the trash."""
        await self._apis.files.empty_trashbin()

    async def restore_from_trashbin(self, path: str) -> None:
        """Restore a file from the trash."""
        await self._apis.files.restore_trash(path)

    async def get_file_versions(self, file: str | int) -> list[dict[str, Any]]:
        """List of file versions.

        Legacy accepted a path string (or file id). Modular ``get_versions``
        needs a numeric file id; resolve path via ``get_all`` when needed.
        """
        if isinstance(file, int):
            file_id = file
        elif isinstance(file, str) and file.isdigit():
            file_id = int(file)
        else:
            path_obj = await self._apis.files.get_all(
                str(file), properties=["oc:fileid"], directory_only=True
            )
            file_id = int(path_obj.fileid)
        versions = await self._apis.files.get_versions(file_id)
        return [v.data for v in versions._files]

    async def restore_file_version(self, path: str) -> None:
        """Restore an old file version."""
        await self._apis.files.restore_version(path)

    async def get_groupfolder_acl(
        self, path: str, inherited: bool = False
    ) -> list[dict[str, Any]]:
        """Return groupfolder ACL rules set for ``path``."""
        return await self._apis.files.get_groupfolder_acl(path, inherited=inherited)

    async def set_groupfolder_acl(self, path: str, acls: list[dict[str, Any]]) -> None:
        """Apply groupfolder ACL rules to ``path``."""
        await self._apis.files.set_groupfolder_acl(path, acls)

    # Legacy LoginFlowV2 API
    async def login_flow_initiate(
        self, user_agent: str = f"nextcloud_async/{__VERSION__}"
    ) -> dict[str, Any]:
        """Initiate login flow v2.

        Temporarily applies ``user_agent`` on the modular client for this call.
        """
        prev = self._nc.user_agent
        if user_agent:
            self._nc.user_agent = user_agent
        try:
            return await self._apis.loginflow.initiate()
        finally:
            self._nc.user_agent = prev

    async def login_flow_wait_confirm(
        self, token: str, timeout: int = 60
    ) -> dict[str, Any]:
        """Wait for user to confirm application authorization."""
        return await self._apis.loginflow.wait_confirm(token, timeout=timeout)

    async def destroy_login_token(self) -> dict[str, bool]:
        """Delete an app password generated by Login Flow v2."""
        await self._apis.loginflow.destroy_token()
        return {"success": True}

    # Legacy Maps API
    async def get_map_favorites(self) -> list[dict[str, Any]]:
        """Get a list of map favorites."""
        favorites = await self._apis.maps.list_favorites()
        return [f.data for f in favorites]

    async def create_map_favorite(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a map favorite from a legacy data dict."""
        favorite = await self._apis.maps.add(**data)
        return favorite.data

    async def update_map_favorite(self, id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing map favorite from a legacy data dict."""
        favorite = await self._apis.maps.update(id=id, **data)
        return favorite.data

    async def remove_map_favorite(self, id: int) -> dict[str, bool]:
        """Remove a map favorite by id."""
        await self._apis.maps.delete(id)
        return {"success": True}

    # Legacy Wipe API
    async def get_wipe_status(self) -> bool:
        """Check for remote wipe flag."""
        return await self._apis.wipe.check()

    async def notify_wipe_status(self) -> dict[str, bool]:
        """Notify server that device has been wiped."""
        await self._apis.wipe.notify_wiped()
        return {"success": True}
