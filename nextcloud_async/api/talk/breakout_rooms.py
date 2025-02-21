from dataclasses import dataclass

from typing import Any, List, Tuple, TYPE_CHECKING, Dict

from nextcloud_async.driver import NextcloudModule, NextcloudTalkApi

if TYPE_CHECKING:
    from .conversations import Conversation

from .types import BreakoutRoomData, ConversationData
from .constants import BreakoutRoomAssignmentMode, BreakoutRoomStatus

@dataclass
class BreakoutRoom:
    data: BreakoutRoomData
    talk_api: NextcloudTalkApi

    def __post_init__(self) -> None:
        """Set up required external APIs."""
        from .conversations import Conversations
        self.api = BreakoutRooms(self.talk_api)
        self.conversations_api = Conversations(self.talk_api.client)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<Talk BreakoutRoom token={self.token}, "{self.name}"">'

    def __repr__(self) -> str:
        return str(self.data)

    @property
    def status(self) -> BreakoutRoomStatus:
        """Return status of breakout room.

        See constants.BreakoutRoomStatus for more info.

        Returns:
            Status of breakout room
        """
        return BreakoutRoomStatus(self.breakoutRoomStatus)

    @property
    def mode(self) -> BreakoutRoomAssignmentMode:
        """Returns BreakoutRoom mode.

        See constants.BreakoutRoomMode for mor info.

        Returns:
            BreakoutRoom mode.
        """
        return BreakoutRoomAssignmentMode(self.breakoutRoomMode)

    @property
    def is_breakout_room(self) -> bool:
        """Shortcut to allow quick determination of room type.

        Distinguishses between Conversation and BreakoutRoom.

        Returns:
            True
        """
        return True

    async def delete(self) -> None:
        """Delete this breakout room."""
        await self.conversations_api.delete(self.token)

    async def request_assistance(self) -> None:
        """Request moderator assistance to this breakout room."""
        await self.api.request_assistance(room_token=self.token)

    async def reset_request_assistance(self) -> None:
        """Reset request for moderator assistance."""
        await self.api.reset_request_assistance(room_token=self.token)

class BreakoutRooms(NextcloudModule):
    """Nextcloud BreakoutRooms API.

    Requires capability: breakout-rooms-v1

    Group and public conversations can be used to host breakout rooms.

    * Only moderators can configure and remove breakout rooms
    * Only moderators can start and stop breakout rooms
    * Moderators in the parent conversation are added as moderators to all breakout rooms
    and remove from all on demotion

    https://nextcloud-talk.readthedocs.io/en/latest/breakout-rooms/

    Typical lifecycle of breakout rooms:
        * .configure()
        * .start()
        * Optionally:
            * .create_additional_room()
            * .delete_room()
            * .broadcast_message()
            * .reorganize_attendees()
        * .stop()
        * .remove()
    """
    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '1') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}/breakout-rooms'
        self.api: NextcloudTalkApi = api

    async def _validate_capability(self) -> None:
            await self.api.require_talk_feature('breakout-rooms-v1')

    def _create_rooms_by_type(
            self,
            rooms: List[ConversationData]) -> Tuple['Conversation', List[BreakoutRoom]]:
        from .conversations import Conversation
        parent_room: Conversation = Conversation(rooms[0], self.api)
        breakout_rooms: List[BreakoutRoom] = []

        for room in rooms:
            if hasattr(room, 'breakoutRoomStatus'):
                breakout_rooms.append(BreakoutRoom(room, self.api))
            else:
                parent_room = Conversation(room, self.api)

        return parent_room, breakout_rooms

    async def configure(
            self,
            room_token: str,
            mode: BreakoutRoomAssignmentMode,
            num_rooms: int,
            attendee_map: Dict[str, int]) -> Tuple['Conversation', List['BreakoutRoom']]:
        """Configure breakout rooms for Conversation.

        Args:
            room_token:
                Token of parent Conversation

            mode:
                Participant assignment mode

            num_rooms:
                Number of breakout rooms to create

            attendee_map:
                A Dict of {attendeeId: room_number} (0 based)
                Only considered when the mode is BreakoutRoomAssignmentMode.manual

        Returns:
            Parent room and all breakout rooms.
        """
        await self._validate_capability()
        response, _ = await self._post(
            path=f'/{room_token}',
            data={
                'mode': mode.value,
                'amount': num_rooms,
                'attendeeMap': attendee_map})
        return self._create_rooms_by_type(response)

    async def create_additional_room(self) -> None:
        """See talk.conversation.create_additional_breakout_room()."""
        raise NotImplementedError(
            'Use Conversation.create_additional_breakout_room() instead.')

    async def delete_room(self) -> None:
        """See talk.conversation.delete_breakout_room()."""
        raise NotImplementedError('Use Conversation.delete_breakout_room() instead.')

    async def remove(self, room_token: str) -> 'Conversation':
        """Remove breakout rooms from conversation.

        Args:
            room_token:
                Token of parent Conversation.

        Returns:
            Parent Conversation object
        """
        await self._validate_capability()
        return await self._delete(path=f'/{room_token}')

    async def start(self, room_token: str) -> Tuple['Conversation', List[BreakoutRoom]]:
        """Start breakout rooms.

        Args:
            room_token:
                Token of parent Conversation

        Returns:
            Parent room and all breakout rooms.
        """
        await self._validate_capability()
        response = await self._post(path=f'/{room_token}/rooms')
        return self._create_rooms_by_type(response)

    async def stop(self, room_token: str) -> Tuple['Conversation', List[BreakoutRoom]]:
        """Stop breakout rooms for a conversation.

        Args:
            room_token:
                Token of parent Conversation.

        Returns:
            Parent conversation and all breakout rooms.
        """
        await self._validate_capability()
        response = await self._delete(path=f'/{room_token}/rooms')
        return self._create_rooms_by_type(response)

    async def broadcast_message(self, room_token: str, message: str) -> None:
        """Broadcast message to all breakout rooms.

        Must be a moderator in parent Conversation.

        Args:
            room_token:
                Token of parent conversation

            message:
                Message to broadcast
        """
        await self._validate_capability()
        await self._post(
            path=f'/{room_token}/broadcast',
            data={
                'token': room_token,
                'message': message})

    async def reorganize_attendees(
            self,
            room_token: str,
            attendee_map: Dict[str, int]) -> Tuple['Conversation', List[BreakoutRoom]]:
        """Reorganize attendees in breakout rooms.

        Args:
            room_token:
                Token of parent Conversation

            attendee_map:
                A Dict of {attendeeId: room_number} (0 based)

        Returns:
            Parent conversation and all breakout rooms.
        """
        await self._validate_capability()
        response = await self._post(
            path=f'/{room_token}/attendees',
            data={'attendeeMap': attendee_map})
        return self._create_rooms_by_type(response)

    async def request_assistance(self, room_token: str) -> None:
        """Request assistance in a breakout room.

        Args:
            room_token:
                Token of breakout room
        """
        await self._validate_capability()
        await self._post(path=f'/{room_token}/request-assistance')

    async def reset_request_assistance(self, room_token: str) -> None:
        """Cancel a request for assistance.

        Args:
            room_token:
                Token of breakout room
        """
        await self._validate_capability()
        await self._delete(path=f'/{room_token}/request_assistance')

    async def switch_rooms(self, room_token: str, target: int) -> BreakoutRoom:
        """Switch breakout rooms.

        This endpoint allows participants to switch between breakout rooms when they are
        allowed to choose the breakout room and not are automatically or manually
        assigned by the moderator.

        Args:
            room_token:
                Token of parent conversation

            target:
                Token of new breakout room

        Returns:
            New breakout room.
        """
        await self._validate_capability()
        response = await self._post(
            path=f'/{room_token}/switch',
            data={'target': target})
        return BreakoutRoom(response, self.api)
