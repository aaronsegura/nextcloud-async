"""Interact with Nextcloud Status API.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-status-api.html
"""

import datetime as dt

from enum import Enum
from typing import Optional, Union, Dict, Hashable, Any, cast

from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.client import NextcloudClient
from nextcloud_async.exceptions import NextcloudException


class StatusType(Enum):
    """Status Types."""

    online = 'online'
    away = 'away'
    dnd = 'dnd'
    invisible = 'invisible'
    offline = 'offline'


class Status(NextcloudModule):
    """Manage a user's status on Nextcloud instances."""

    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '1'):
        self.stub = f'/apps/user_status/api/v{api_version}'
        self.api = NextcloudOcsApi(client, ocs_version = '2')

    async def get(self):
        """Get current status.

        Returns
        -------
            dict: Status description

        """
        return await self._get('/user_status')

    async def set(self, status_type: StatusType):
        """Set user status.

        Args
        ----
            status_type (StatusType): See StatusType Enum

        Returns
        -------
            dict: New status description.

        """
        return await self._put(
            path='/user_status/status',
            data={'statusType': status_type.name})

    def __validate_future_timestamp(self, ts: Union[float, int]) -> None:
        """Verify the given unix timestamp is valid and in the future.

        Args
        ----
            ts (float or int): Timestamp

        Raises
        ------
            NextcloudException: Invalid timestamp or timestamp in the past

        """
        try:
            clear_dt = dt.datetime.fromtimestamp(ts)
        except (TypeError, ValueError):
            raise NextcloudException(status_code=406, reason='Invalid `clear_at`.  Should be unix timestamp.')

        now = dt.datetime.now()
        if clear_dt <= now:
            raise NextcloudException(status_code=406, reason='Invalid `clear_at`.  Should be in the future.')

    async def get_predefined_statuses(self):
        """Get list of predefined statuses.

        Returns
        -------
            list: Predefined statuses

        """
        return await self._get(path='/predefined_statuses')

    async def choose_predefined_status(
            self,
            message_id: int,
            clear_at: Union[int, None] = None) -> Dict[Hashable, Any]:
        """Choose from predefined status messages.

        Args
        ----
            message_id (int): Message ID (see get_predefined_statuses())

            clear_at (int, optional): Unix timestamp at which to clear this status. Defaults
            to None.

        Returns
        -------
            dict: New status description

        """
        data: Dict[Hashable, int] = {'messageId': message_id}
        if clear_at:
            self.__validate_future_timestamp(clear_at)
            data.update({'clearAt': clear_at})
        return await self._put(
            path='/user_status/message/predefined',
            data=data)

    async def set_message(
            self,
            message: str,
            status_icon: Optional[str] = None,
            clear_at: Optional[int] = None) -> Dict[Hashable, Any]:
        """Set a custom status message.

        Args
        ----
            message (str): Your custom message

            status_icon (str, optional): Emoji icon. Defaults to None.

            clear_at (int, optional): Unix timestamp at which to clear this message. Defaults
            to None.

        Returns
        -------
            dict: New status description

        """
        data: Dict[Hashable, str] = {'message': message}
        if status_icon:
            data.update({'statusIcon': status_icon})
        if clear_at:
            self.__validate_future_timestamp(clear_at)
            data.update(cast(Dict[Hashable, Any], {'clearAt': clear_at}))
        return await self._put(
            path='/user_status/message/custom',
            data=data)

    async def clear_message(self):
        """Clear status message.

        Returns
        -------
            Empty 200 Response

        """
        return await self._delete(path=r'/user_status/message')

    async def get_all_user_statuses(
            self,
            limit: Optional[int] = 100,
            offset: Optional[int] = 0):
        """Get all user statuses.

        Args
        ----
            limit (int, optional): Results per page. Defaults to 100.

            offset (int, optional): Paging offset. Defaults to 0.

        Returns
        -------
            list: User statuses

        """
        return await self._get(
            path='/statuses',
            data={'limit': limit, 'offset': offset})

    async def get_user_status(self, user: str):
        """Get the status for a specific user.

        Args
        ----
            user (str): User ID

        Returns
        -------
            dict: User status description

        """
        return await self._get(
            path=f'/statuses/{user}')
