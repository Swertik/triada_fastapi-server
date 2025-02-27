from unittest.mock import AsyncMock
import pytest
import pytest_asyncio
from triada.config.settings import TEST_DATABASE_URL
from triada.main import app
from triada.api.db_api import override_database, get_engine, get_sessionmaker
from sqlmodel import SQLModel



@pytest.hookimpl(tryfirst=True)
def pytest_assertrepr_compare(left, right):
    if isinstance(left, list) and isinstance(right, list):
        def clean_token(call_obj):
            if isinstance(call_obj, tuple) and 'params' in call_obj[1]:
                call_obj[1]['params']['access_token'] = "<HIDDEN>"
            return call_obj

        left_clean = [clean_token(c) for c in left]
        right_clean = [clean_token(c) for c in right]

        return [
            "Comparison failed, but access_token are hidden:",
            f"  Left:  {left_clean}",
            f"  Right: {right_clean}"
        ]

app.dependency_overrides = {}


@pytest_asyncio.fixture
async def mock_vk_client():
    mock_response = AsyncMock()
    mock_response.json.return_value = {"response": 1234567}

    mock_client = AsyncMock()
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

    return mock_client


@pytest_asyncio.fixture(scope="session")
async def clear_db():
    """
    Подготавливает базу данных к работе
    """
    with override_database(TEST_DATABASE_URL):
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)  # Очистка перед тестами
            await conn.run_sync(SQLModel.metadata.create_all)  # Пересоздание схемы
        try:
            yield  # Тут выполняются тесты
        finally:
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.drop_all)  # Очистка после тестов


@pytest_asyncio.fixture
async def db_session():
    """Создаёт сессию БД для тестов и откатывает все изменения после каждого теста"""
    with override_database(TEST_DATABASE_URL):
        async_session = get_sessionmaker()
        async with async_session() as session:
            yield session
            await session.close()
