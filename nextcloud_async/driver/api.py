from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Hashable

from nextcloud_async.client import NextcloudClient

from nextcloud_async.exceptions import (
    NextcloudBadRequest,
    NextcloudForbidden,
    NextcloudNotModified,
    NextcloudUnauthorized,
    NextcloudDeviceWipeRequested,
    NextcloudNotFound,
    NextcloudTooManyRequests,
    NextcloudTalkConflict,
    NextcloudTalkPreconditionFailed,
    NextcloudNotCapable)


class NextcloudHttpApi(ABC):
    """Base HTTP methods imported by different Nextcloud API drivers."""
    def __init__(self, client: NextcloudClient):
        self.client = client

    @abstractmethod
    async def request(
            self,
            method: str = 'GET',
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        ...

    async def raw_request(
            self,
            method: str = 'GET',
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        ...

    async def raise_response_exception(self, status_code: int):
        from nextcloud_async.api import Wipe

        match status_code:
            case 304:
                raise NextcloudNotModified()
            case 400:
                raise NextcloudBadRequest()
            case 401:
                wipe = Wipe(self.client)
                wipe_status = await wipe.check()
                if wipe_status:
                    raise NextcloudDeviceWipeRequested()
                else:
                    raise NextcloudUnauthorized()
            case 403:
                wipe = Wipe(self.client)
                wipe_status = await wipe.check()
                if wipe_status:
                    raise NextcloudDeviceWipeRequested()
                else:
                    raise NextcloudForbidden()
            case 404:
                raise NextcloudNotFound()
            case 429:
                raise NextcloudTooManyRequests()
            case 409:
                raise NextcloudTalkConflict()
            case 412:
                raise NextcloudTalkPreconditionFailed()
            case 499:
                raise NextcloudNotCapable()
            case _:
                pass


    async def get(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.request(method='GET', path=path, data=data, headers=headers)

    async def get_raw(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.raw_request(method='GET', path=path, data=data, headers=headers)

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

    async def _get_raw(
            self,
            path: str = '',
            data: Optional[Any] = None,
            headers: Optional[Dict[Hashable, Any]] = {}) -> Any:
        return await self.api.get_raw(path=f'{self.stub}{path}', data=data, headers=headers)

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
