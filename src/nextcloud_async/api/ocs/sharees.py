"""Implement Nextcloud Sharees API.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-sharee-api.html

Not Implemented:
    Federated share management
"""

from typing import Any, Dict, Optional

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudOcsApi


class ShareesApi(NextcloudModule):
    """Sharees interface."""

    def __init__(self, ocs_api: NextcloudOcsApi, api_version: str = "1") -> None:
        self.stub = f"/apps/files_sharing/api/v{api_version}"
        self.api = ocs_api

    async def search_sharees(
        self,
        search: Optional[str] = None,
        item_type: str = "file",
        lookup: bool = False,
        limit: int = 20,
        page: int = 1,
    ) -> dict[str, str]:
        """Get all sharees matching a search term.

        Args:
            item_type:
                Item type (`file`, `folder`, `calendar`, etc...)

            lookup:
                Whether to use global Nextcloud lookup service. Defaults to False.

            limit:
                How many results to return per request. Defaults to 200.

            page:
                Return this page of results. Defaults to 1.

            search:
                Search term. Defaults to None.

        Returns:
            Dictionary of exact and potential matches.
        """
        data: dict[str, Any] = {
            "search": search,
            "itemType": item_type,
            "perPage": limit,
            "page": page,
            "lookup": lookup,
        }
        return await self._get(path="/sharees", data=data)

    async def sharee_recommendations(self, item_type: str = "file") -> dict[str, str]:
        """Get sharees the sharer might want to share with.

        Args:
            item_type:
                `file`, `folder`, `calendar`, etc..

        Returns:
            Recommended sharees.
        """
        return await self._get(path="/sharees_recommended", data={"itemType": item_type})


def sharees_api(client: NextcloudClient) -> ShareesApi:
    """Factory for ShareesApi."""
    ocs_api = NextcloudOcsApi(client)
    return ShareesApi(ocs_api)
