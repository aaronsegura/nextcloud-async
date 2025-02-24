import asyncio
import httpx
import os

import pytest
import pytest_asyncio

import tempfile

from nextcloud_async import NextcloudClient
from nextcloud_async.api import Files
from nextcloud_async.exceptions import NextcloudError


from .constants import (
    NEXTCLOUD_VERSION,
    REMOTE_TEST_DIR_DEST,
    REMOTE_TEST_BASE_DIR,
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

@pytest.fixture
def temp_file():
    _, filename = tempfile.mkstemp('nextcloud-async-pytest', dir=tempfile.gettempdir())
    return filename

async def remove_remote_test_dir():
    # Remove remote testing environment.
    nc = NextcloudClient(ENDPOINT, USER, PASSWORD, httpx.AsyncClient())
    files_api = Files(nc)
    try:
        await files_api.delete(REMOTE_TEST_BASE_DIR)
    except NextcloudError:
        pass

async def create_remote_test_dirs():
    # Prep the test environment
    # User-defined fixtures do not work here.
    nc = NextcloudClient(ENDPOINT, USER, PASSWORD, httpx.AsyncClient())
    files_api = Files(nc)

    for dir in [REMOTE_TEST_BASE_DIR, REMOTE_TEST_DIR_DEST]:
        try:
            await files_api.mkdir(dir)
        except NextcloudError as e:
                if e.status_code != 405:  # noqa: PLR2004
                    raise

def pytest_sessionstart():
    # Remove remote testing directory for test_files:
    asyncio.run(remove_remote_test_dir())
    asyncio.run(create_remote_test_dirs())

def pytest_sessionfinish(session, exitstatus: int):  # noqa: ARG001
    # Clean up remote on successful run
    if exitstatus == 0:
        asyncio.run(remove_remote_test_dir())
