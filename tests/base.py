"""Credit: https://github.com/luffah/nextcloud-API"""
from .constants import ENDPOINT, USER, PASSWORD

import httpx

from unittest import TestCase

from nextcloud_async import NextcloudAsync


class BaseTestCase(TestCase):

    def setUp(self):
        self.ncc = NextcloudAsync(
            client=httpx.AsyncClient(),
            endpoint=ENDPOINT,
            user=USER,
            password=PASSWORD)
