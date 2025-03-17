import json

import httpx
import pytest
from pytest_httpx import HTTPXMock

from nextcloud_async import NextcloudClient
from nextcloud_async.api import MapFavorite, Maps

from ...constants import EMPTY_RESPONSE, ENDPOINT, PASSWORD, USER

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
    client = NextcloudClient(ENDPOINT, USER, PASSWORD, http_client=httpx.AsyncClient())
    return Maps(client)


@pytest.fixture
def map_favorite(maps: Maps):
    return MapFavorite(_FAVORITE_DATA, maps)


@pytest.mark.asyncio
class TestMaps:
    async def test_mapfavorite_properties(self, map_favorite: MapFavorite):
        assert map_favorite.latitude == _FAVORITE_DATA["lat"]
        assert map_favorite.longitude == _FAVORITE_DATA["lng"]
        assert map_favorite.category == _FAVORITE_DATA["category"]

    async def test_str(self, map_favorite):
        assert f'<MapFavorite "{_FAVORITE_DATA["name"]}">' == str(map_favorite)

    async def test_map_favorite_delete(
        self, maps: Maps, map_favorite: MapFavorite, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200,
            content=EMPTY_RESPONSE,
            method="DELETE",
            url=f"{ENDPOINT}{maps.api.stub}{maps.stub}/favorites/{_FAVORITE_DATA['id']}",
        )
        await map_favorite.delete()
        httpx_mock.assert_all_responses_sent()

    async def test_map_favorite_update(
        self, maps: Maps, map_favorite: MapFavorite, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            200,
            content=bytes(json.dumps(_UPDATED_DATA), "utf-8"),
            method="PUT",
            url=f"{ENDPOINT}{maps.api.stub}{maps.stub}/favorites/{_FAVORITE_DATA['id']}",
        )
        await map_favorite.update(**_UPDATED_DATA)
        httpx_mock.assert_all_responses_sent()
        assert map_favorite.name == _UPDATED_DATA["name"]

    async def test_map_favorite_create(self, maps: Maps, httpx_mock: HTTPXMock):
        _data = _FAVORITE_DATA.copy()
        _data.pop("id")
        httpx_mock.add_response(
            200,
            content=bytes(json.dumps(_FAVORITE_DATA), "utf-8"),
            method="POST",
            url=f"{ENDPOINT}{maps.api.stub}{maps.stub}/favorites",
        )
        new_favorite = await maps.add(**_data)
        httpx_mock.assert_all_responses_sent()
        assert new_favorite.id == _FAVORITE_DATA["id"]

    async def test_list_favorites(self, maps: Maps, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            200,
            content=bytes(json.dumps([_FAVORITE_DATA]), "utf-8"),
            method="GET",
            url=f"{ENDPOINT}{maps.api.stub}{maps.stub}/favorites",
        )
        result = await maps.list_favorites()
        assert isinstance(result[0], MapFavorite)

        assert result[0].name == _FAVORITE_DATA["name"]
        httpx_mock.assert_all_responses_sent()
