from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversations import Conversation

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

    async def get_interal_file_chat(
            self,
            file_id: int) -> 'Conversation':
        """Return conversation token for discussion of internal file.

        Args:
            file_id:
                ID of file

        Returns:
            Conversation
        """
        from .conversations import Conversations
        conversations = Conversations(self.api.client)
        response, _ = await self._get(path=f'/file/{file_id}')
        return await conversations.get(response)

    async def get_public_file_share_chat(
            self,
            share_token: str) -> 'Conversation':
        """Return conversationtoken for discussion of shared file.

        Args:
            share_token:
                Share token.

        Returns:
            Conversation token
        """
        from .conversations import Conversations
        conversations = Conversations(self.api.client)
        response, _ = await self._get(path=f'/publicshare/{share_token}')
        return await conversations.get(response['token'])

    async def create_password_request_conversation(
            self,
            share_token: str) -> Dict[str, Any]:
        """Create a conversation to request the password for a public share.

        Args:
            share_token:
                Share token

        Returns:
            Dictionary
                token:  The token of the conversation for this file
                name:   A technical name for the conversation
                displayName: The visual name of the conversation
        """
        response, _ = await self._post(
            path='/publicshareauth',
            data={'shareToken': share_token})
        return response
