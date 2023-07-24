from dataclasses import asdict
from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
class TestEndpoints():
    async def test_raw_sql(self, mocker, result):
        session_mock = AsyncMock()
        session_begin_mock = MagicMock()
        session_mock.__aenter__.return_value = session_begin_mock

        async def async_magic():
            return result

        MagicMock.__await__ = lambda x: async_magic().__await__()
        mocker.patch('main.async_sessionmaker').return_value = MagicMock(
            return_value=session_mock)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/raw_sql")
            assert response.json() == [asdict(row) for row in result]
