"""Implement Nextcloud Shares/Sharee APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-sharee-api.html

Not Implemented:
    Federated share management
"""


from typing import Any, Dict

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi


class Sharees(NextcloudModule):
    """Manage local shares on Nextcloud instances."""
    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '1'):
        self.stub = f'/apps/files_sharing/api/v{api_version}'
        self.api = NextcloudOcsApi(client, ocs_version = '1')

    async def search_sharees(
            self,
            search: str = '',
            item_type: str = 'file',
            lookup: bool = False,
            limit: int = 20,
            page: int = 1):
        """Search for people or groups to share things with.

        Args
        ----
            item_type (str): Item type (`file`, `folder`, `calendar`, etc...)

            lookup (bool, optional): Whether to use global Nextcloud lookup service.
            Defaults to False.

            limit (int, optional): How many results to return per request. Defaults to 200.

            page (int, optional): Return this page of results. Defaults to 1.

            search (str, optional): Search term. Defaults to None.

        Returns
        -------
            Dictionary of exact and potential matches.

        """
        data: Dict[str, Any] = {
            'search': search,
            'itemType': item_type,
            'perPage': limit,
            'page': page,
            'lookup': lookup
        }
        return await self._get(path='/sharees', data=data)

    async def sharee_recommendations(self, item_type: str = 'file'):
        return await self._get(
            path='/sharees_recommended',
            data={'itemType': item_type})
