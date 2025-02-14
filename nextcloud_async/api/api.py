from importlib.metadata import version

from nextcloud_async.client import NextcloudClient

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Hashable


VERSION = version('nextcloud_async')
USER_AGENT = f'nextcloud_async/{VERSION}'


class NextcloudHttpApi(ABC):
    def __init__(self, client: NextcloudClient, user_agent: Optional[str] = USER_AGENT):
        self.client = client.http_client
        self.user = client.user
        self.password = client.password
        self.endpoint = client.endpoint
        self.user_agent = user_agent

    @abstractmethod
    async def request(
            self,
            method: str = 'GET',
            url: Optional[str] = None,
            sub: str = '',
            data: Optional[Dict[Hashable, Any]] = {},
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        ...



    async def get(
            self,
            url: Optional[str] = None,
            sub: str = '',
            data: Optional[Dict[Hashable, Any]] = {},
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='GET', url=url, sub=sub, data=data, headers=headers)

    async def post(
            self,
            url: Optional[str] = None,
            sub: str = '',
            data: Optional[Dict[Hashable, Any]] = {},
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='POST', url=url, sub=sub, data=data, headers=headers)

    async def put(
            self,
            url: Optional[str] = None,
            sub: str = '',
            data: Optional[Dict[Hashable, Any]] = {},
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='PUT', url=url, sub=sub, data=data, headers=headers)

    async def delete(
            self,
            url: Optional[str] = None,
            sub: str = '',
            data: Optional[Dict[Hashable, Any]] = {},
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='DELETE', url=url, sub=sub, data=data, headers=headers)
