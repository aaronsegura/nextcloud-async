from abc import ABC
from typing import Any, Awaitable, Callable

from nextcloud_async.exceptions import NextcloudForbiddenError


class NextcloudModule(ABC):
    api: Any
    stub: str

    async def _get(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.get(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _get_raw(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.get_raw(
            path=f"{self.stub}{path}",
            data=data,
            headers=headers,
        )

    async def _post(
        self,
        data: Any | None = None,
        path: str = "",
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.post(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _put(
        self,
        data: Any | None = None,
        path: str = "",
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.put(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _delete(
        self,
        data: Any | None = None,
        path: str = "",
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.delete(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _propfind(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.propfind(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _mkcol(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.mkcol(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _move(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.move(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _copy(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.copy(path=f"{self.stub}{path}", data=data, headers=headers)

    async def _proppatch(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.proppatch(
            path=f"{self.stub}{path}", data=data, headers=headers
        )

    async def _report(
        self,
        path: str = "",
        data: Any | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        return await self.api.report(
            path=f"{self.stub}{path}", data=data, headers=headers
        )


def password_confirmation_required(
    func: Callable[..., Awaitable],
) -> Callable[..., Awaitable]:
    """Wrap certain calls because of stupid Nextcloud API shenanigans.

    https://github.com/nextcloud/server/issues/51391

    This is an async decorator and can be used inside of NextcloudModule classes to
    wrap functions that require periodic password confirmations in the nextcloud API.
    If the wrapped function raises a 403 error with "confirmation" in the `reason` field,
    cookies will be cleared and the call will be tried again.  Any further exceptions
    (or exceptions other than 403/confirmation) are raised to the caller.

    ````
    @password_confirmation_required
    async def create(self, ...):
        ...
    ````

    Args:
        func:
            Function to be wrapped.

    """

    async def _wrapper(
        self: NextcloudModule, *args: Any, **kwargs: dict[Any, Any]
    ) -> Any:
        try:
            return await func(self, *args, **kwargs)
        except NextcloudForbiddenError as e:
            if "confirmation" in str(e):
                self.api.client.http_client.cookies.delete("oc_sessionPassphrase")
                return await func(self, *args, **kwargs)
            else:
                raise

    return _wrapper
