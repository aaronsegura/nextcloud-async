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

    def __str__(self) -> str:
        return f'<Predefined Status "{self.icon} {self.id}">'

    def __repr__(self) -> str:
        return str(self.data)



@dataclass
class MyStatus:
    data: Dict[str, Any]
    status_api: 'Status'

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<My Status {self.status} "{self.message}">'

    def __repr__(self) -> str:
        return str(self.data)

    async def set(self, status_type: StatusType) -> None:
        """Set user status.

        Args:
            status_type: See StatusType Enum
        """
        response = await self.status_api.set(status_type=status_type)
        self.data = response

    async def set_predefined_status(
            self,
            status: PredefinedStatus,
            clear_at: dt.datetime) -> None:
        """Choose from predefined status messages.

        Args:
            status:
                PredefinedStatus (see get_predefined_statuses())

            clear_at:
                datetime at which to clear this status.
        """
        response = await self.status_api.choose_predefined_status(
            status=status,
            clear_at=clear_at)
        self.data = response

    async def set_message(
            self,
            message: str,
            status_icon: str,
            clear_at: dt.datetime) -> None:
        """Set a custom status message.

        Args:
            message:
                Your custom message

            status_icon:
                Emoji icon. Defaults to None.

            clear_at:
                datetime at which to clear this message.
        """
        response = await self.status_api.set_message(
            message=message,
            status_icon=status_icon,
            clear_at=clear_at)
        self.data = response

    async def clear_message(self) -> None:
        """Clear my status message."""
        await self.status_api.clear_message()
        self.message = ''


@dataclass
class UserStatus:
    data: Dict[str, Any]

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<User Status {self.status} "{self.message}">'

    def __repr__(self) -> str:
        return str(self.data)


class Status(NextcloudModule):
    """Manage a user's status on Nextcloud instances."""

    def __init__(
            self,
            client: NextcloudClient,
            ocs_version: str = '2',
            api_version: str = '1') -> None:
        self.stub = f'/apps/user_status/api/v{api_version}'
        self.api = NextcloudOcsApi(client, ocs_version = ocs_version)

    async def get(self) -> MyStatus:
        """Get current status.

        Returns:
            dict: Status description
        """
        response = await self._get('/user_status')
        return MyStatus(response, self)


    async def set(self, status_type: StatusType) -> Dict[str, Any]:
        """Set user status.

        Args:
            status_type:
                See StatusType Enum

        Returns:
            New status data
        """
        return await self._put(
            path='/user_status/status',
            data={'statusType': status_type.value})

    async def get_predefined_statuses(self) -> List[PredefinedStatus]:
        """Get list of predefined statuses.

        Returns:
            PredefinedStatus list
        """
        response = await self._get(path='/predefined_statuses')
        return [PredefinedStatus(data) for data in response]

    async def choose_predefined_status(
            self,
            status: PredefinedStatus,
            clear_at: Optional[dt.datetime] = None) -> Dict[str, Any]:
        """Choose from predefined status messages.

        Args:
            status:
                PredefinedStatus (see get_predefined_statuses())

            clear_at:
                datetime at which to clear this status.

        Returns:
            dict: New status description
        """
        data: Dict[str, int|str] = {'messageId': status.id}
        if clear_at:
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

        Args:
            message: Your custom message

            status_icon: Emoji icon. Defaults to None.

            clear_at: datetime at which to clear this message.

        Returns:
            dict: New status description
        """
        data: Dict[str, str] = {'message': message}
        if status_icon:
            data.update({'statusIcon': status_icon})
        if clear_at:
            data.update({'clearAt': clear_at.strftime('%s')})
        return await self._put(
            path='/user_status/message/custom',
            data=data)

    async def clear_message(self) -> None:
        """Clear status message."""
        await self._delete(path=r'/user_status/message')

    async def get_all_user_statuses(
            self,
            limit: int = 100,
            offset: int = 0) -> list[UserStatus]:
        """Get all user statuses.

        Args:
            limit: Results per page. Defaults to 100.

            offset: Paging offset. Defaults to 0.

        Returns:
            list: User statuses
        """
        response = await self._get(
            path='/statuses',
            data={'limit': limit, 'offset': offset})
        return [UserStatus(data) for data in response]

    async def get_user_status(self, user: str) -> UserStatus:
        """Get the status for a specific user.

        Args:
            user (str): User ID

        Returns:
            dict: User status description
        """
        response = await self._get(path=f'/statuses/{user}')
        return UserStatus(response)
