"""Implement Nextcloud Maps API.

https://github.com/nextcloud/maps/blob/master/openapi.yml

"""

from dataclasses import dataclass

from typing import List, Any, Dict

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudBaseApi


@dataclass
class MapFavorite:
    data: Dict[str, Any]
    maps_api: 'Maps'

    def __getattr__(self, k: str) -> Any:
        return self.data[k]

    def __str__(self) -> str:
        return f'<MapFavorite "{self.name}">'

    def __repr__(self) -> str:
        return str(self.data)

    @property
    def latitude(self) -> float:
        """Alias for self.lat."""
        return self.lat

    @property
    def longitude(self) -> float:
        """Alias for self.lng."""
        return self.lng

    async def delete(self) -> None:
        """Delete this favorite."""
        await self.maps_api.delete(self.id)

    async def update(self, data: dict[str, str|float]) -> None:
        """Update an existing map favorite.

        Args:
            data: Dictionary describing new data to use
                Keys may be: ['name', 'lat', 'lng', 'category', 'comment', 'extensions']
        """
        response = await self.maps_api.update(id=self.id, data=data)
        self.data = response.data


class Maps(NextcloudModule):
    """Interact with Nextcloud Maps API.

    Add/remove/edit/delete map favorites.
    """
    def __init__(
            self,
            client: NextcloudClient,
            api_version: str = '1.0') -> None:
        self.stub = f'/apps/maps/api/{api_version}'
        self.api = NextcloudBaseApi(client)

    async def list(self) -> List[MapFavorite]:
        """Get a list of map favorites.

        Returns:
            list of favorites
        """
        response = await self._get(path='/favorites')
        return [MapFavorite(data, self) for data in response]

    async def delete(self, id: int) -> None:
        """Remove a map favorite by Id.

        Args:
        ----
            id: ID of favorite to remove
        """
        await self._delete(path=f'/favorites/{id}')
        self.data = {'deleted': True}

    async def update(self, id: int, data: Dict[str, str|float]) -> MapFavorite:
        """Update an existing map favorite.

        Args:
            id: ID of favorite to update

            data: Dictionary describing new data to use
                Keys may be: ['name', 'lat', 'lng', 'category', 'comment', 'extensions']

        Returns:
            MapFavorite
        """
        response = await self._put(
                        path=f'/favorites/{id}',
                        data=data)

        return MapFavorite(response, self)

    async def add(self, data: Dict[str, str|float]) -> MapFavorite:
        """Add a new map favorite.

        Args:
            data: Dictionary describing new favorite
                Keys are: ['name', 'lat', 'lng', 'category', 'comment', 'extensions']

        Returns:
            MapFavorite
        """
        response = await self._post(
                        path='/favorites',
                        data=data)
        return MapFavorite(response, self)
