"""Test Nextcloud Maps API."""

from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import USER, ENDPOINT, PASSWORD, EMPTY_200

import asyncio
import httpx

from unittest.mock import patch

ID = 4
LAT = 48.785526
LNG = -95.035892
NAME = "Blueberry Hill Campground"
COMMENT = "ALL THE BLUEBERRIES"

class MapsAPI(BaseTestCase):  # noqa: D101

    def test_get_favorites(self):  # noqa: D102
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=bytes('[]', 'utf-8'))) as mock:
            asyncio.run(self.ncc.get_map_favorites())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/index.php/apps/maps/api/1.0/favorites?',
                data=None,
                headers={})

    def test_create_favorite(self):  # noqa: D102
        json_response = bytes(
            '{"id":4,"name":"Blueberry Hill Campground","date_modifie'
            'd":1661549544,"date_created":1661549544,"lat":48.785526,"lng":-95.035'
            '892,"category":"Campgrounds","comment":"Blueberries!","extensions":null}',
            'utf-8')

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            data = {
                'name': NAME,
                'lat': LAT,
                'lng': LNG,
                'comment': COMMENT}
            asyncio.run(self.ncc.create_map_favorite(data))
            mock.assert_called_with(
                method='POST',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/index.php/apps/maps/api/1.0/favorites',
                data=data,
                headers={})

    def test_update_favorite(self):  # noqa: D102
        json_response = bytes(
            '{"id":4,"name":"Blueberry Hill Campground","date_modifie'
            'd":1661549544,"date_created":1661549544,"lat":48.785526,"lng":-95.035'
            '892,"category":"Campgrounds","comment":"Blueberries!","extensions":null}',
            'utf-8')

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            data = {
                'name': NAME,
                'lat': LAT,
                'lng': LNG,
                'comment': COMMENT}
            asyncio.run(self.ncc.update_map_favorite(ID, data))
            mock.assert_called_with(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/index.php/apps/maps/api/1.0/favorites/{ID}',
                data=data,
                headers={})

    def test_remove_favorite(self):  # noqa: D102
        json_response = bytes('"DELETED"', 'utf-8')

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.remove_map_favorite(ID))
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/index.php/apps/maps/api/1.0/favorites/{ID}',
                data={},
                headers={})
