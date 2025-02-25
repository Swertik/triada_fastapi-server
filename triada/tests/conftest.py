import pytest
import pytest_asyncio
from starlette.testclient import TestClient
from triada.config.settings import TEST_DATABASE_URL
from triada.main import app
from triada.api.db_api import override_database, get_engine, get_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel


@pytest.hookimpl(tryfirst=True)
def pytest_assertrepr_compare(op, left, right):
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

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Создает тестовую базу данных и таблицы"""
    with override_database(TEST_DATABASE_URL):
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)  # Очищаем БД
            await conn.run_sync(SQLModel.metadata.create_all)  # Создаем схему
        yield
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)  # Очищаем после тестов

@pytest_asyncio.fixture
async def db_session():
    """Создаёт сессию БД для тестов и откатывает все изменения после каждого теста"""
    with override_database(TEST_DATABASE_URL):
        async_session = get_sessionmaker()
        async with async_session() as session:
            yield session
            await session.rollback()
            await session.close()
