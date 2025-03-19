"""Implement Nextcloud Maps API.

https://github.com/nextcloud/maps/blob/master/openapi.yml

"""

from typing import NotRequired, TypedDict, Unpack

from nextcloud_async.api.mixins import NextcloudDataObject
from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudBaseDriver


class MapFavorite(NextcloudDataObject):
    _api: "MapsApi"

    def __str__(self) -> str:
        return f'<MapFavorite "{self.name}">'

    def __eq__(self, other: "MapFavorite") -> bool:
        return (self.name, self.lat, self.lng) == (other.name, other.lat, other.lng)

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
        await self._api.delete(self.id)
        self.data = {"name": "**deleted**"}

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
        response = await self._api.update(id=self.id, **kwargs)
        self.data = response.data


class MapsApi(NextcloudModule):
    """Interact with Nextcloud Maps API.

    Add/remove/edit/delete map favorites.
    """

    def __init__(
        self,
        base_driver: NextcloudBaseDriver,
        api_version: str = "1.0",
    ) -> None:
        self.stub = f"/apps/maps/api/{api_version}"
        self.driver = base_driver

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
        category: str | None = None,
        comment: str | None = None,
        extensions: str | None = None,
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
        category: str | None = None,
        comment: str | None = None,
        extensions: str | None = None,
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


def maps_api(client: NextcloudClient) -> MapsApi:
    """MapsApi factory."""
    base_driver = NextcloudBaseDriver(client)
    return MapsApi(base_driver)
