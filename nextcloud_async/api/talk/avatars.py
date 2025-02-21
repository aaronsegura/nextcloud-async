"""Nextcloud Talk Conversation Avatars API.

Requires capability: avatar

https://nextcloud-talk.readthedocs.io/en/latest/avatar/
"""
from typing import Optional

from nextcloud_async.driver import NextcloudTalkApi, NextcloudModule


class ConversationAvatars(NextcloudModule):
    def __init__(
            self,
            api: NextcloudTalkApi,
            api_version: str = '1') -> None:
        self.stub = f'/apps/spreed/api/v{api_version}'
        self.api: NextcloudTalkApi = api

    async def _validate_capability(self) -> None:
        await self.api.require_talk_feature('avatar')

    async def set_image(self, room_token:str, image_data: bytes) -> None:
        """Set conversations avatar.

        Args:
            room_token:
                Token of conversation

            image_data:
                Image data
        """
        await self._validate_capability()
        await self._post(
            path=f'/room/{room_token}/avatar',
            data={'file': image_data})

    async def set_emoji(
            self,
            room_token: str ,
            emoji: str,
            color: Optional[str] = None) -> None:
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
        await self._post(
            path=f'/room/{room_token}/avatar/emoji',
            data={
                'emoji': emoji,
                'color': color})

    async def delete(self, room_token: str) -> None:
        """Delete conversation avatar.

        To determine if the delete option should be presented to the user, it's
        recommended to check the isCustomAvatar property of Conversation object.

        Args:
            room_token:
                Token of conversation.
        """
        await self._validate_capability()
        await self._delete(path=f'/room/{room_token}/avatar')

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
            response = await self._get_raw(
                path=f'/room/{room_token}/avatar/dark')
        else:
            response = await self._get_raw(
                path=f'/room/{room_token}/avatar')

        return response.content

    async def get_federated(
            self,
            room_token: str,
            cloud_id: str,
            size: int,
            dark_mode: bool  = False) -> bytes:
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
        await self.api.require_talk_feature('avatar')
        await self.api.require_talk_feature('federated-v1')

        if dark_mode:
            response = await self.api.client.http_client.request(
                method='GET',
                url=f'{self.api.client.endpoint}/ocs/v2.php/apps/spreed/api/v1/proxy/{room_token}/user-avatar/{size}/dark',
                data={
                    'cloudId': cloud_id,
                    'size': size})
        else:
            response = await self.api.client.http_client.request(
                method='GET',
                url=f'{self.api.client.endpoint}/ocs/v2.php/apps/spreed/api/v1/proxy/{room_token}/user-avatar/{size}',
                data={
                    'cloudId': cloud_id,
                    'size': size})

        return response.content
