import pytest

from unittest.mock import AsyncMock, call

from nextcloud_async.api import MapFavorite, MapsApi

_FAVORITE_DATA = {
    "id": 1,
    "name": "My Favorite",
    "lat": 0.0,
    "lng": 0.0,
    "category": "Testing",
}

_UPDATED_DATA = {
    "name": "My Updated Favorite",
    "lat": 30.487698,
    "lng": -95.124103,
    "category": "Camping",
}


@pytest.fixture
def maps():
    return MapsApi(AsyncMock())


@pytest.fixture
def map_favorite(maps: MapsApi):
    return MapFavorite(_FAVORITE_DATA, maps)


@pytest.mark.asyncio
class TestMapFavorites:
    async def test_mapfavorite_properties(self, map_favorite: MapFavorite):
        assert map_favorite.latitude == _FAVORITE_DATA["lat"]
        assert map_favorite.longitude == _FAVORITE_DATA["lng"]
        assert map_favorite.category == _FAVORITE_DATA["category"]

    async def test_str(self, map_favorite):
        assert f'<MapFavorite "{_FAVORITE_DATA["name"]}">' == str(map_favorite)

    async def test_map_favorite_delete(self, map_favorite: MapFavorite):
        await map_favorite.delete()
        expected = [
            call.delete(path="/apps/maps/api/1.0/favorites/1", data=None, headers=None)
        ]
        map_favorite._api.driver.assert_has_calls(expected)

    async def test_map_favorite_update(self, map_favorite: MapFavorite):
        await map_favorite.update(**_UPDATED_DATA)
        expected = [
            call.put(
                path="/apps/maps/api/1.0/favorites/1",
                data={
                    "name": _UPDATED_DATA["name"],
                    "lat": _UPDATED_DATA["lat"],
                    "lng": _UPDATED_DATA["lng"],
                    "category": _UPDATED_DATA["category"],
                    "comment": None,
                    "extensions": None,
                },
                headers=None,
            )
        ]
        map_favorite.self_api.api.assert_has_calls(expected)


@pytest.mark.asyncio
class TestMapsApi:
    async def test_map_favorite_create(self, maps: MapsApi):
        _data = _FAVORITE_DATA.copy()
        _data.pop("id")
        await maps.add(**_data)
        expected = [
            call.post(
                path="/apps/maps/api/1.0/favorites",
                data={
                    "name": _data["name"],
                    "lat": _data["lat"],
                    "lng": _data["lng"],
                    "category": _data["category"],
                    "comment": None,
                    "extensions": None,
                },
                headers=None,
            )
        ]
        maps.driver.assert_has_calls(expected)

    async def test_list_favorites(self, maps: MapsApi):
        await maps.list_favorites()
        expected = [
            call.get(path="/apps/maps/api/1.0/favorites", data=None, headers=None),
            call.get().__iter__(),
        ]
        maps.driver.assert_has_calls(expected)
