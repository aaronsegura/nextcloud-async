"""
    https://nextcloud-talk.readthedocs.io/en/latest/poll/
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from nextcloud_async.driver import NextcloudModule, NextcloudTalkApi

from .constants import PollMode, PollStatus

@dataclass
class Poll:
    data: Dict[str, Any]
    talk_api: NextcloudTalkApi

    def __post_init__(self):
        self.api = Polls(self.talk_api)

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self):
        return f'<Talk Poll "{self.question}" from {self.actorId}>'

    def __repr__(self):
        return str(self)

    @property
    def status(self):
        return PollStatus(self.data['status']).name

    @property
    def result_mode(self):
        return PollMode(self.resultMode).name

    async def refresh(self):
        response = await self.api.get(room_token=self.token, poll_id=self.id)
        self.data = response.data

    async def vote(self, **kwargs) -> None:
        await self.api.vote(room_token=self.token, poll_id=self.id, **kwargs)

    async def close(self, **kwargs) -> None:
        await self.api.close(room_token=self.token, poll_id=self.id)


class Polls(NextcloudModule):
    """Interact with Nextcloud Talk Chat API."""

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: Optional[str] = '1'):
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
        response, _ = await self._get(
            path=f'/{room_token}/{poll_id}')
        response.update({'token': room_token})
        return Poll(response, self.api)

    async def list_drafts(
            self,
            room_token: str) -> List[Poll]:
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
        await self._post(
            path=f'/{room_token}/{poll_id}',
            data={'optionIds': votes})

    async def close(
            self,
            room_token: str,
            poll_id: int) -> None:
        await self._delete(
            path=f'/{room_token}/{poll_id}')
