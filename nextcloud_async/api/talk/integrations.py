from typing import Optional, Dict, Any

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule

class Integrations(NextcloudModule):
    """Nextcloud Talk Integrations API.

    https://nextcloud-talk.readthedocs.io/en/latest/integration/
    """

    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '1') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    async def get_interal_file_chat_token(
            self,
            file_id: int) -> str:
        response, _ = await self._get(path=f'/file/{file_id}')
        return response['token']

    async def get_public_file_share_chat_token(
            self,
            share_token: str) -> str:
        response, _ = await self._get(path=f'/publicshare/{share_token}')
        return response['token']

    async def create_password_request_conversation(
            self,
            share_token: str) -> Dict[str, Any]:
        response, _ = await self._post(
            path='/publicshareauth',
            data={'shareToken': share_token})
        return response
