import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(autouse=True)
def magicmock(mocker) -> MagicMock:
    return mocker.MagicMock()


@pytest.fixture(autouse=True)
def asyncmock(mocker) -> AsyncMock:
    return mocker.AsyncMock()
