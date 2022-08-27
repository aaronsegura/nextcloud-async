"""Implement Nextcloud Maps API.

https://github.com/nextcloud/maps/blob/master/openapi.yml

"""

import json


class Maps(object):
    """Interact with Nextcloud Maps API.

    Add/remove/edit/delete map favorites.
    """

    async def get_map_favorites(self) -> list:
        """Get a list of map favorites.

        Returns
        -------
            list of favorites

        """
        response = await self.request(
            method='GET',
            url=f'{self.endpoint}/index.php/apps/maps/api/1.0/favorites')
        return json.loads(response.content.decode('utf-8'))

    async def remove_map_favorite(self, id: int) -> str:
        """Remove a map favorite by Id.

        Args:
        ----
            id (int): ID of favorite to remove

        """
        return await self.request(
            method='DELETE',
            url=f'{self.endpoint}/index.php/apps/maps/api/1.0/favorites/{id}')

    async def update_map_favorite(self, id: int, data: dict) -> dict:
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
        response = await self.request(
            method='PUT',
            url=f'{self.endpoint}/index.php/apps/maps/api/1.0/favorites/{id}',
            data=data)
        return json.loads(response.content.decode('utf-8'))

    async def create_map_favorite(self, data: dict) -> dict:
        """Update an existing map favorite.

        Args
        ----
            data (dict): Dictionary describing new favorite
                Keys may be: ['name', 'lat', 'lng', 'category',
                'comment', 'extensions']

        Returns
        -------
            dict: Result of update

        """
        response = await self.request(
            method='POST',
            url=f'{self.endpoint}/index.php/apps/maps/api/1.0/favorites',
            data=data)
        return json.loads(response.content.decode('utf-8'))
