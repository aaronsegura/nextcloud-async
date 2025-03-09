"""Implement Nextcloud Maps API.

https://github.com/nextcloud/maps/blob/master/openapi.yml

"""

from typing import Optional, Awaitable, TypedDict, NotRequired, Unpack

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudModule, NextcloudBaseApi
from nextcloud_async.api.dataobject import NextcloudDataObject


class MapFavorite(NextcloudDataObject):

    self_api: "Maps"

    def __str__(self) -> str:
        return f'<MapFavorite "{self.name}">'

    def async_refresh(self) -> Awaitable:
        """No need to refresh this object."""
        ...

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
        await self.self_api.delete(self.id)

    class _UpdateArgs(TypedDict):
        name: NotRequired[str]
        lat: NotRequired[float]
        lng: NotRequired[float]
        category: NotRequired[str]
        comment: NotRequired[str]
        extensions: NotRequired[str]

    async def update(self, **kwargs: Unpack[_UpdateArgs]) -> None:  # noqa: D417
        """Update an existing map favorite.

        Args:
            name:
                Name of this locaion

            lat:
                Latitude

            lng:
                Longitude

            category:
                Category

            comment:
                Comment

            extensions:
                Not really sure /shrug

        """
        response = await self.self_api.update(id=self.id, **kwargs)
        self.data = response.data


class Maps(NextcloudModule):
    """Interact with Nextcloud Maps API.

    Add/remove/edit/delete map favorites.
    """

    def __init__(self, client: NextcloudClient, api_version: str = "1.0") -> None:
        self.stub = f"/apps/maps/api/{api_version}"
        self.api = NextcloudBaseApi(client)

    async def list_favorites(self) -> list[MapFavorite]:
        """Get a list of map favorites.

        Returns:
            list of favorites
        """
        response = await self._get(path="/favorites")
        return [MapFavorite(data, self) for data in response]

    async def delete(self, id: int) -> None:
        """Remove a map favorite by Id.

        Args:
            id: ID of favorite to remove
        """
        await self._delete(path=f"/favorites/{id}")
        self.data = {"deleted": True}

    async def update(
        self,
        id: int,
        name: str,
        lat: float,
        lng: float,
        category: Optional[str] = None,
        comment: Optional[str] = None,
        extensions: Optional[str] = None,
    ) -> MapFavorite:
        """Update an existing map favorite.

        Args:
            id:
                ID of favorite to update

            name:
                Name of this locaion

            lat:
                Latitude

            lng:
                Longitude

            category:
                Category

            comment:
                Comment

            extensions:
                Not really sure /shrug
        Returns:
            MapFavorite
        """
        data = {
            "name": name,
            "lat": lat,
            "lng": lng,
            "category": category,
            "comment": comment,
            "extensions": extensions,
        }
        response = await self._put(path=f"/favorites/{id}", data=data)

        return MapFavorite(response, self)

    async def add(
        self,
        name: str,
        lat: float,
        lng: float,
        category: Optional[str] = None,
        comment: Optional[str] = None,
        extensions: Optional[str] = None,
    ) -> MapFavorite:
        """Add a new map favorite.

        Args:
            name:
                Name of this locaion

            lat:
                Latitude

            lng:
                Longitude

            category:
                Category

            comment:
                Comment

            extensions:
                Not really sure /shrug

        Returns:
            New MapFavorite
        """
        data = {
            "name": name,
            "lat": lat,
            "lng": lng,
            "category": category,
            "comment": comment,
            "extensions": extensions,
        }
        response = await self._post(path="/favorites", data=data)
        return MapFavorite(response, self)
