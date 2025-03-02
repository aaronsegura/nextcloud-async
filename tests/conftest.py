import httpx
import os

import pytest
import pytest_asyncio

from nextcloud_async import NextcloudClient

from .constants import (
    NEXTCLOUD_VERSION,
    USER,
    PASSWORD,
    ENDPOINT)

@pytest.fixture
def vcr_config():
    return {
        # Add 'headers' to match_on defaults
        "match_on": ['method', 'scheme', 'host', 'port', 'path', 'query', 'headers'],

        # cookies will change between requests
        "filter_headers": ["cookie", "authorization"],

        # Write plain text responses to cassettes
        "decode_compressed_response": True}

@pytest.fixture
def vcr_cassette_dir(request):
    # Put all cassettes in vhs/{module}/{test}.yaml
    return os.path.join(
        f'tests/cassettes/nextcloud-{NEXTCLOUD_VERSION}', request.module.__name__)

@pytest_asyncio.fixture(scope='class', loop_scope='class')
async def nc():
    async with httpx.AsyncClient(timeout=30) as client:
        yield NextcloudClient(ENDPOINT, USER, PASSWORD, client)

