"""
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/
"""

import httpx

from urllib.parse import urlencode
from typing import Dict, Optional


class NextCloudBaseAPI(object):
    """The Base API interface."""

    def __init__(
            self,
            client: httpx.AsyncClient,
            endpoint: str,
            user: str = '',
            password: str = ''):

        self.user = user
        self.password = password
        self.endpoint = endpoint
        self.client = client

    async def request(
            self,
            method: str = 'GET',
            url: str = None,
            sub: str = '',
            data: Optional[Dict[str, object]] = {},
            headers: Optional[Dict[str, object]] = {}) -> httpx.Response:

        if method.lower() == 'get':
            sub = f'{sub}?{urlencode(data)}'
            data = None

        return await self.client.request(
            method=method,
            auth=(self.user, self.password),
            url=f'{url}{sub}' if url else f'{self.endpoint}{sub}',
            data=data,
            headers=headers)
