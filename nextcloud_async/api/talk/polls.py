"""Nextcloud Talk Polls API.

https://nextcloud-talk.readthedocs.io/en/latest/poll/
"""
from typing import List, Dict, Any
from dataclasses import dataclass

from nextcloud_async.driver import NextcloudModule, NextcloudTalkApi

from .constants import PollMode, PollStatus

@dataclass
class Poll:
    data: Dict[str, Any]
    talk_api: NextcloudTalkApi

    def __post_init__(self) -> None:
        self.api = Polls(self.talk_api)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<Talk Poll "{self.question}" from {self.actorId}>'

    def __repr__(self) -> str:
        return str(self.data)

    @property
    def status(self) -> PollStatus:
        """Return poll status.

        Returns:
            PollStatus
        """
        return PollStatus(self.data['status'])

    @status.setter
    def status(self, status: PollStatus) -> None:
        self.data['status'] = status.value

    @property
    def result_mode(self) -> PollMode:
        """Return poll mode.

        Returns:
            PollMode
        """
        return PollMode(self.resultMode)

    async def refresh(self) -> None:
        """Refresh status of poll."""
        response = await self.api.get(room_token=self.token, poll_id=self.id)
        self.data = response.data

    async def vote(self, votes: List[int]) -> None:
        """Vote on this poll.

        Args:
            votes:
                The option IDs the participant wants to vote for
        """
        await self.api.vote(room_token=self.token, poll_id=self.id, votes=votes)

    async def close(self) -> None:
        """Close this poll."""
        await self.api.close(room_token=self.token, poll_id=self.id)
        self.status = PollStatus.closed


class Polls(NextcloudModule):
    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '1') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}/poll'
        self.api: NextcloudTalkApi = api

    async def create(
            self,
            room_token: str,
            question: str,
            options: List[str],
            result_mode: PollMode,
            max_votes: int,
            draft: bool = False) -> Poll:
        """Create a poll in a conversation.

        Args:
            room_token:
                Token of conversation

            question:
                The poll topic

            options:
                Voting options

            result_mode:
                PollMode

            max_votes:
                Maximum amount of options a participant can vote for

            draft:
                Whether or not to save this poll as a draft

        Returns:
            Poll object
        """
        response, _ = await self._post(
            path=f'/{room_token}',
            data={
                'draft': draft,
                'question': question,
                'options': options,
                'resultMode': result_mode.value,
                'maxVotes': max_votes})
        response.update({'token': room_token})
        return Poll(response, self.api)

    async def edit_draft(
            self,
            room_token: str,
            question: str,
            options: List[str],
            result_mode: PollMode,
            max_votes: int) -> Poll:
        """Edit a draft poll in a conversation.

        Args:
            room_token:
                Token of conversation

            question:
                Poll topic

            options:
                Voting options

            result_mode:
                PollMode

            max_votes:
                Maximum amount of options a participant can vote for

        Returns:
            Poll object
        """
        await self.api.require_talk_feature('edit-draft-poll')
        response, _ = await self._post(
            path=f'/{room_token}',
            data={
                'question': question,
                'options': options,
                'resultMode': result_mode.value,
                'maxVotes': max_votes})
        response.update({'token': room_token})
        return Poll(response, self.api)

    async def get(
            self,
            room_token: str,
            poll_id: int) -> Poll:
        """Get state or result of a poll.

        Args:
            room_token:
                Token of conversation

            poll_id:
                Poll ID

        Returns:
            Poll object
        """
        response, _ = await self._get(
            path=f'/{room_token}/{poll_id}')
        response.update({'token': room_token})
        return Poll(response, self.api)

    async def list_drafts(
            self,
            room_token: str) -> List[Poll]:
        """Get a list of all poll drafts in a conversation.

        Args:
            room_token:
                Token of conversation.

        Returns:
            List of Poll objets
        """
        await self.api.require_talk_feature('talk-polls-drafts')
        response, _ = await self._get(
            path=f'/{room_token}/drafts')

        ret = []
        for data in response:
            data.update({'token': room_token})
            ret.append(Poll(data, self.api))
        return ret

    async def vote(
            self,
            room_token: str,
            poll_id: int,
            votes: List[int]) -> None:
        """Vote on a poll.

        Args:
            room_token:
                Token of conversation

            poll_id:
                Poll ID

            votes:
                The option IDs the participant wants to vote for
        """
        await self._post(
            path=f'/{room_token}/{poll_id}',
            data={'optionIds': votes})

    async def close(
            self,
            room_token: str,
            poll_id: int) -> None:
        """Close a poll.

        Args:
            room_token:
                Token of conversation

            poll_id:
                Poll ID
        """
        await self._delete(
            path=f'/{room_token}/{poll_id}')
