import pytest

from dataclasses import asdict
from unittest.mock import MagicMock
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
class TestEndpoints():
    async def test_raw_sql(self, mocker, result):
        session_mock = MagicMock()
        session_mock.__aenter__.return_value = MagicMock()

        async def async_func():
            return result

        MagicMock.__await__ = lambda x: async_func().__await__()
        mocker.patch('main.async_sessionmaker').return_value = MagicMock(
            return_value=session_mock)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/raw_sql")
            assert response.json() == [asdict(row) for row in result]
