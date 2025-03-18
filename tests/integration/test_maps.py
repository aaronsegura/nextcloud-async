from typing import AsyncGenerator

import pytest
import pytest_asyncio

from nextcloud_async.api import MapFavorite, MapsApi
from nextcloud_async.exceptions import NextcloudNotFoundError

DATA = {
    "name": "Blueberry Hill Campground",
    "lat": 48.785526,
    "lng": -95.035892,
    "category": "Camping",
    "comment": "ALL THE BLUEBERRIES",
}


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def map_favorite(
    maps_api: MapsApi, network_blocked: bool
) -> AsyncGenerator[MapFavorite]:
    favorite = await maps_api.add(**DATA)
    yield favorite
    if not network_blocked:
        try:
            await favorite.delete()
        except NextcloudNotFoundError:
            pass


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestMaps:
    async def test_create_favorite(self, map_favorite: MapFavorite):
        assert isinstance(map_favorite, MapFavorite)
        assert map_favorite.latitude == DATA["lat"]
        assert map_favorite.longitude == DATA["lng"]
        assert map_favorite.name == DATA["name"]
        assert map_favorite.category == DATA["category"]
        assert map_favorite.comment == DATA["comment"]
        assert DATA["name"] in str(map_favorite)

    # Fixture map_favorite isn't directly accessed in this test, but it it required
    # to guarantee a favorite is in the system before running maps_api.list_favorites()
    #
    async def test_list_favorites(self, maps_api: MapsApi, map_favorite: MapFavorite):
        favorites = await maps_api.list_favorites()
        for fav in favorites:
            assert isinstance(fav, MapFavorite)

    async def test_update_favorite(self, maps_api: MapsApi, map_favorite: MapFavorite):
        new_data = {
            "name": "Palisades Reservoir",
            "lat": 43.250235495324,
            "lng": -111.10126018524,
            "comment": "Good t-mobile, no verizon.  Lake access.  Beautiful",
            "category": "Boondocking",
        }
        favorites = await maps_api.list_favorites()
        favorite = next(
            filter(
                lambda x: (x.lat, x.lng) == (map_favorite.lat, map_favorite.lng),
                favorites,
            )
        )

        await favorite.update(**new_data)
        assert isinstance(favorite, MapFavorite)
        assert favorite.lat == new_data["lat"]
        assert favorite.lng == new_data["lng"]
        assert favorite.name == new_data["name"]
        assert favorite.category == new_data["category"]
        assert favorite.comment == new_data["comment"]

    async def test_delete_favorite(self, maps_api: MapsApi):
        favorites = await maps_api.list_favorites()
        for favorite in favorites:
            if (favorite.lat, favorite.lng) == (DATA["lat"], DATA["lng"]):
                await favorite.delete()
