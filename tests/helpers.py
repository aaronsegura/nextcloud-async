import asyncio

from unittest import mock


class AsyncContextManager(mock.MagicMock):
    async def __aenter__(self, *args, **kwargs):
        return self.__enter__(*args, **kwargs)

    async def __aexit__(self, *args, **kwargs):
        return self.__exit__(*args, **kwargs)


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)
