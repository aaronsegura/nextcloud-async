import aiofile
import httpx
import os

import pytest
import pytest_asyncio

import tempfile

from nextcloud_async import NextcloudClient
from nextcloud_async.api import Files
from nextcloud_async.exceptions import NextcloudError
from .test_files import TestFiles


from .constants import (
    NEXTCLOUD_VERSION,
    REMOTE_TEST_DIR_SRC,
    REMOTE_TEST_DIR_DEST,
    REMOTE_TEST_BASE_DIR,
    FILE_CONTENTS_ORIG,
    USER,
    PASSWORD,
    ENDPOINT)

@pytest.fixture(scope='module')
def vcr_config():
    return {
        # Add 'headers' to match_on defaults
        "match_on": ['method', 'scheme', 'host', 'port', 'path', 'query', 'headers'],

        # Write plain text responses to cassettes
        "decode_compressed_response": True}

@pytest.fixture(scope='module')
def vcr_cassette_dir(request):
    # Put all cassettes in vhs/{module}/{test}.yaml
    return os.path.join(
        f'tests/cassettes/nextcloud-{NEXTCLOUD_VERSION}', request.module.__name__)

@pytest_asyncio.fixture
async def nc():
    async with httpx.AsyncClient() as client:
        yield NextcloudClient(ENDPOINT, USER, PASSWORD, client)

@pytest_asyncio.fixture
async def temp_file():
    _, filename = tempfile.mkstemp('nextcloud-async-pytest', dir=tempfile.gettempdir())
    async with aiofile.async_open(filename, 'wb') as fp:
        await fp.write(FILE_CONTENTS_ORIG)
        yield filename
    os.unlink(filename)
