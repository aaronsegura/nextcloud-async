import datetime as dt

from enum import Enum, auto
from typing import Dict, Optional

from nextcloud_aio.exceptions import NextCloudAsyncException


class StatusType(Enum):
    online = auto()
    away = auto()
    dnd = auto()
    invisible = auto()
    offline = auto()


class OCSStatusAPI(object):

    async def get_status(self):
        return await self.ocs_query(
            method='GET',
            sub=r'/ocs/v2.php/apps/user_status/api/v1/user_status')

    async def set_status(self, status_type: StatusType):
        """Set user status."""
        return await self.ocs_query(
            method='PUT',
            sub=r'/ocs/v2.php/apps/user_status/api/v1/user_status/status',
            data={'statusType': status_type.name})

    def __validate_future_timestamp(self, ts: int) -> None:
        """Verify the given unix timestamp is valid and in the future."""
        if not ts:
            return

        try:
            clear_dt = dt.datetime.fromtimestamp(ts)
        except (TypeError, ValueError):
            raise NextCloudAsyncException('Invalid `clear_at`.  Should be unix timestamp.')

        now = dt.datetime.now()
        if clear_dt < now:
            raise NextCloudAsyncException('Invalid `clear_at`.  Should be in the future.')

    async def choose_status_message(
            self,
            message_id: int,
            clear_at: int):
        """Choose from predefined status messages."""
        self.__validate_future_timestamp(clear_at)
        return await self.ocs_query(
            method='PUT',
            sub=r'/ocs/v2.php/apps/user_status/api/v1/user_status/status/message/predefined',
            data={
                'messageId': message_id,
                'clearAt': clear_at
            })

    async def set_status_message(
            self,
            message: str,
            status_icon: Optional[str] = None,
            clear_at: Optional[int] = None):
        """Set a custom status message."""
        self.__validate_future_timestamp(clear_at)
        return await self.ocs_query(
            method='PUT',
            sub=r'/ocs/v2.php/apps/user_status/api/v1/user_status/message/custom',
            data={
                'message': message,
                'statusIcon': status_icon,
                'clearAt': clear_at})

    async def clear_status_message(self) -> Dict:
        """Clear status message."""
        return await self.ocs_query(
            method='DELETE',
            sub=r'/ocs/v2.php/apps/user_status/api/v1/user_status/message')

    async def get_predefined_statuses(self):
        """Get list of predefined statuses."""
        return await self.ocs_query(
            method='GET',
            sub=r'/ocs/v2.php/apps/user_status/api/v1/predefined_statuses')

    async def get_all_user_status(
            self,
            limit: Optional[int] = 100,
            offset: Optional[int] = 0):
        """Get all user statuses."""
        return await self.ocs_query(
            method='GET',
            sub=r'/ocs/v2.php/apps/user_status/api/v1/statuses')

    async def get_user_status(
            self,
            user: str):
        """Get the status for a specific user."""
        return await self.ocs_query(
            method='GET',
            sub=f'/ocs/v2.php/apps/user_status/api/v1/statuses/{user}')
