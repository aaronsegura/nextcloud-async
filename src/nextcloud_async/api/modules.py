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
