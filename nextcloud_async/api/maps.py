"""Implement Nextcloud Maps API.

https://github.com/nextcloud/maps/blob/master/openapi.yml

"""

import json

from typing import List, Hashable, Any, Dict

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudBaseApi, NextcloudModule

class Maps(NextcloudModule):
    """Interact with Nextcloud Maps API.

    Add/remove/edit/delete map favorites.
    """
    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '1.0'):
        self.stub = f'/apps/maps/api/{api_version}'
        self.api = NextcloudBaseApi(client)

    async def list_favorites(self) -> List[str]:
        """Get a list of map favorites.

        Returns
        -------
            list of favorites

        """
        response = await self._get(path='/favorites')
        return json.loads(response.content.decode('utf-8'))

    async def delete_favorite(self, id: int) -> None:
        """Remove a map favorite by Id.

        Args:
        ----
            id (int): ID of favorite to remove

        Raises:
        -------
            Appropriate NextcloudException

        """
        await self._delete(path=f'/favorites/{id}')

    async def update_favorite(self, id: int, data: Dict[Hashable, Any]) -> Dict[Hashable, Any]:
        """Update an existing map favorite.

        Args
        ----
            id (int): ID of favorite to update

            data (dict): Dictionary describing new data to use
                Keys may be: ['name', 'lat', 'lng', 'category',
                'comment', 'extensions']

        Returns
        -------
            dict: Result of update

        """
        response = await self._put(
                        path=f'/favorites/{id}',
                        data=data)

        return json.loads(response.content.decode('utf-8'))

    async def add_favorite(self, data: Dict[Hashable, Any]) -> Dict[Hashable, Any]:
        """Add a new map favorite.

        Args
        ----
            data (dict): Dictionary describing new favorite
                Keys are: ['name', 'lat', 'lng', 'category',
                'comment', 'extensions']

        Returns
        -------
            dict: Result of update

        """
        response = await self.api.post(
                        path='/favorites',
                        data=data)
        return json.loads(response.content.decode('utf-8'))
