"""Nextcloud Talk Conversation Avatars API.

Requires capability: avatar

https://nextcloud-talk.readthedocs.io/en/latest/avatar/
"""

from typing import Any

import aiofile

from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.driver import NextcloudTalkDriver


class ConversationAvatarsApi(NextcloudModule):
    def __init__(self, driver: NextcloudTalkDriver, api_version: str = "1") -> None:
        self.stub = f"/apps/spreed/api/v{api_version}"
        self.driver: NextcloudTalkDriver = driver

    async def _validate_capability(self) -> None:
        await self.driver.require_feature("avatar")

    async def set_image(self, room_token: str, filename: str) -> dict[str, Any]:
        """Set conversations avatar.

        Args:
            room_token:
                Token of conversation

            filename:
                Image file name

        """
        await self._validate_capability()
        async with aiofile.async_open(filename, "rb") as fp:
            return await self._post(
                path=f"/room/{room_token}/avatar", file=await fp.read()
            )

    async def set_emoji(
        self, room_token: str, emoji: str, color: str | None = None
    ) -> dict[str, Any]:
        """Set emoji as avatar.

        Args:
            room_token:
                Token of conversation

            emoji:
                New emoji avatar

            color:
                HEX color code (6 times 0-9A-F) without the leading # character (omit to
                fallback to the default bright/dark mode icon background color)

        """
        await self._validate_capability()
        return await self._post(
            path=f"/room/{room_token}/avatar/emoji",
            data={"emoji": emoji, "color": color},
        )

    async def delete(self, room_token: str) -> dict[str, Any]:
        """Delete conversation avatar.

        To determine if the delete option should be presented to the user, it's
        recommended to check the isCustomAvatar property of Conversation object.

        Args:
            room_token:
                Token of conversation.

        """
        await self._validate_capability()
        return await self._delete(path=f"/room/{room_token}/avatar")

    async def get(self, room_token: str, dark_mode: bool = False) -> bytes:
        """Get conversations avatar (binary).

        Args:
            room_token:
                Token of conversation

            dark_mode:
                Whether to get Dark Mode version.

        Returns:
            Image data

        """
        await self._validate_capability()
        if dark_mode:
            response = await self._get_raw(path=f"/room/{room_token}/avatar/dark")
        else:
            response = await self._get_raw(path=f"/room/{room_token}/avatar")

        return response.content

    async def get_federated(
        self, room_token: str, cloud_id: str, size: int, dark_mode: bool = False
    ) -> bytes:
        """Get federated user avatar (binary).

        Args:
            room_token:
                Token of conversation

            cloud_id:
                Federation CloudID to get the avatar for

            size:
                Only 64 and 512 are supported

            dark_mode:
                Whether to get Dark Mode version.

        Returns:
            Image data

        """
        await self.driver.require_feature("avatar")
        await self.driver.require_feature("federated-v1")

        if dark_mode:
            response = await self.driver.client.http_client.request(
                method="GET",
                url=f"{self.driver.client.endpoint}/ocs/v2.php/apps/spreed/api/v1/proxy/{room_token}/user-avatar/{size}/dark",
                data={"cloudId": cloud_id, "size": size},
            )
        else:
            response = await self.driver.client.http_client.request(
                method="GET",
                url=f"{self.driver.client.endpoint}/ocs/v2.php/apps/spreed/api/v1/proxy/{room_token}/user-avatar/{size}",
                data={"cloudId": cloud_id, "size": size},
            )

        return response.content
