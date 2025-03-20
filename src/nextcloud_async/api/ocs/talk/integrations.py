from typing import Any

from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.driver import NextcloudTalkDriver


class IntegrationsApi(NextcloudModule):
    """Nextcloud Talk Integrations API.

    https://nextcloud-talk.readthedocs.io/en/latest/integration/
    """

    def __init__(
        self,
        api: NextcloudTalkDriver,
        api_version: str = "1",
    ) -> None:
        self.stub = f"/apps/spreed/api/v{api_version}"
        self.driver: NextcloudTalkDriver = api

    async def get_internal_file_chat(self, file_id: int) -> str:
        """Return conversation token for discussion of internal file.

        Args:
            file_id:
                ID of file

        Returns:
            Conversation

        """
        response, _ = await self._get(path=f"/file/{file_id}")
        return response

    async def get_public_file_share_chat(self, share_token: str) -> str:
        """Return conversationtoken for discussion of shared file.

        Args:
            share_token:
                Share token.

        Returns:
            Conversation token

        """
        response, _ = await self._get(path=f"/publicshare/{share_token}")
        return response

    async def create_password_request_conversation(
        self, share_token: str
    ) -> dict[str, Any]:
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
            path="/publicshareauth", data={"shareToken": share_token}
        )
        return response
