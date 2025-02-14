"""Implement Nextcloud Maps API.

https://github.com/nextcloud/maps/blob/master/openapi.yml

"""

import json
import httpx

from typing import List, Hashable, Any, Dict

from nextcloud_async.client import NextcloudClient
from nextcloud_async.api.base import NextcloudBaseApi

class Maps:
    stub = '/index.php/apps/maps/api/1.0'

    """Interact with Nextcloud Maps API.

    Add/remove/edit/delete map favorites.
    """
    def __init__(
            self,
            client: NextcloudClient):
        self.api = NextcloudBaseApi(client)

    async def list_favorites(self) -> List[str]:
        """Get a list of map favorites.

        Returns
        -------
            list of favorites

        """
        response = await self.api.get(sub=f'{self.stub}/favorites')
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
        await self.api.delete(sub=f'{self.stub}/favorites/{id}')

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
        response = await self.api.put(
                        sub=f'{self.stub}/favorites/{id}',
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
                        sub=f'{self.stub}/favorites',
                        data=data)
        return json.loads(response.content.decode('utf-8'))
