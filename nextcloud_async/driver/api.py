from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Hashable

from nextcloud_async.client import NextcloudClient

class NextcloudHttpApi(ABC):
    """Base HTTP methods imported by different Nextcloud API drivers."""
    def __init__(self, client: NextcloudClient):
        self.client = client.http_client
        self.user = client.user
        self.password = client.password
        self.endpoint = client.endpoint
        self.user_agent = client.user_agent

    @abstractmethod
    async def request(
            self,
            method: str = 'GET',
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        ...

    async def get(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='GET', path=path, data=data, headers=headers)

    async def post(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='POST', path=path, data=data, headers=headers)

    async def put(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='PUT', path=path, data=data, headers=headers)

    async def delete(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='DELETE', path=path, data=data, headers=headers)

    async def propfind(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='PROPFIND', path=path, data=data, headers=headers)

    async def mkcol(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='MKCOL', path=path, data=data, headers=headers)

    async def move(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='MOVE', path=path, data=data, headers=headers)

    async def copy(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='MOVE', path=path, data=data, headers=headers)

    async def proppatch(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='PROPPATCH', path=path, data=data, headers=headers)

    async def report(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='REPORT', path=path, data=data, headers=headers)


class NextcloudModule(ABC):
    api: NextcloudHttpApi
    stub: str

    async def _get(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.get(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _post(
            self,
            data: Optional[Any] = None,
            path: str = '',
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.post(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _put(
            self,
            data: Optional[Any] = None,
            path: str = '',
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.put(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _delete(
            self,
            data: Optional[Any] = None,
            path: str = '',
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.delete(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _propfind(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.propfind(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _mkcol(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.mkcol(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _move(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.move(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _copy(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.copy(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _proppatch(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.proppatch(path=f'{self.stub}{path}', data=data, headers=headers)

    async def _report(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.report(path=f'{self.stub}{path}', data=data, headers=headers)