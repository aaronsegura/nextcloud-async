"""Interact with Nextcloud Status API.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-status-api.html
"""

import datetime as dt

from dataclasses import dataclass

from enum import Enum
from typing import Optional, Dict, Any, List

from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi
from nextcloud_async.client import NextcloudClient


class StatusType(Enum):
    """Status Types."""

    online = 'online'
    away = 'away'
    dnd = 'dnd'
    invisible = 'invisible'
    offline = 'offline'


@dataclass
class PredefinedStatus:
    data: Dict[str, Any]

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Predefined Status "{self.icon} {self.id}">'

    def __repr__(self):
        return str(self.data)



@dataclass
class MyStatus:
    data: Dict[str, Any]
    status_api: 'Status'

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<My Status {self.status} "{self.message}">'

    def __repr__(self):
        return str(self.data)


    async def set(self, *args, **kwargs) -> None:
        response = await self.status_api.set(*args, **kwargs)
        self.data = response

    async def set_predefined_status(self, *args, **kwargs) -> None:
        response = await self.status_api.choose_predefined_status(*args, **kwargs)
        self.data = response

    async def set_message(self, *args, **kwargs) -> None:
        response = await self.status_api.set_message(*args, **kwargs)
        self.data = response

    async def clear_message(self) -> None:
        await self.status_api.clear_message()
        self.message = ''


@dataclass
class UserStatus:
    data: Dict[str, Any]

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<User Status {self.status} "{self.message}">'

    def __repr__(self):
        return str(self.data)



class Status(NextcloudModule):
    """Manage a user's status on Nextcloud instances."""

    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '1'):
        self.stub = f'/apps/user_status/api/v{api_version}'
        self.api = NextcloudOcsApi(client, ocs_version = '2')

    async def get(self) -> MyStatus:
        """Get current status.

        Returns
        -------
            dict: Status description
        """
        response = await self._get('/user_status')
        return MyStatus(response, self)


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
            data={'statusType': status_type.value})

    async def get_predefined_statuses(self) -> List[PredefinedStatus]:
        """Get list of predefined statuses.

        Returns
        -------
            list: Predefined statuses
        """
        response = await self._get(path='/predefined_statuses')
        return [PredefinedStatus(data) for data in response]

    async def choose_predefined_status(
            self,
            status: PredefinedStatus,
            clear_at: Optional[dt.datetime] = None) -> Dict[str, Any]:
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
        data: Dict[str, int|str] = {'messageId': status.id}
        if clear_at:
            if dt.datetime.now() < clear_at:
                data.update({'clearAt': clear_at.strftime('%s')})
        response = await self._put(
            path='/user_status/message/predefined',
            data=data)
        return response

    async def set_message(
            self,
            message: str,
            status_icon: Optional[str] = None,
            clear_at: Optional[dt.datetime] = None) -> Dict[str, Any]:
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
        data: Dict[str, str] = {'message': message}
        if status_icon:
            data.update({'statusIcon': status_icon})
        if clear_at:
            if dt.datetime.now() < clear_at:
                data.update({'clearAt': clear_at.strftime('%s')})
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

    async def get_user_status(self, user: str) -> UserStatus:
        """Get the status for a specific user.

        Args
        ----
            user (str): User ID

        Returns
        -------
            dict: User status description
        """
        response = await self._get(path=f'/statuses/{user}')
        return UserStatus(response)
