import asyncio
import datetime
from unittest.mock import AsyncMock
import pytest
import pytest_asyncio
from triada.config.settings import TEST_DATABASE_URL
from triada.main import app
from triada.api.db_api import override_database, get_engine, get_sessionmaker
from sqlmodel import SQLModel, select

from triada.schemas.table_models import BattlesPlayers, Battles, Users, Judges

print("pytest_assertrepr_compare is active!")


@pytest.hookimpl(tryfirst=True)
def pytest_assertrepr_compare(left, right):
    if isinstance(left, list):
        def clean_token(call_obj):
            if isinstance(call_obj, tuple) and 'params' in call_obj[1]:
                call_obj[1]['params']['access_token'] = "<HIDDEN>"
            return call_obj

        left_clean = [clean_token(c) for c in left]

        return [
            "Comparison failed, but access_token are hidden:",
            f"  Left:  {left_clean}",
            f"  Right: {right}"
        ]

app.dependency_overrides = {}


@pytest_asyncio.fixture
async def mock_vk_client_factory():
    def mock_vk_client():
        mock_response = AsyncMock()
        mock_response.json.return_value = {"response": 1234567}

        mock_client = AsyncMock()
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        return mock_client
    return mock_vk_client

@pytest_asyncio.fixture
async def db_session():
    """Создаёт сессию БД для тестов и откатывает все изменения после каждого теста"""
    with override_database(TEST_DATABASE_URL):
        async with get_sessionmaker()() as session:
            try:
                yield session
            finally:
                await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_db():
    with override_database(TEST_DATABASE_URL):
        async_session = get_sessionmaker()
        async with async_session() as session:
            new_battle = Battles(link=123, judge_id=2, time_out=datetime.timedelta(hours=24))

            new_users = [Users(user_id=1, user_name='Egor'),
                         Users(user_id=2, user_name='Asya'),
                         Users(user_id=3, user_name='Kiz')]
            new_users_battles = [BattlesPlayers(user_id=1, link=123, time_out=datetime.datetime.now(), character='1',
                                                universe='ff', user_name='Egor', turn=0),
                                 BattlesPlayers(user_id=2, link=123, character='2',universe='ff', user_name='Asya', turn=1),
                                 BattlesPlayers(user_id=3, link=123, character='3',universe='ff', user_name='Kiz', turn=2)]
            new_judges = [Judges(judge_id=456507851), Judges(judge_id=2, active_battles=1)]

            session.add_all(new_judges)
            session.add_all(new_users)
            session.add_all(new_users_battles)
            session.add(new_battle)
            await session.commit()
            yield
            await session.close()


@pytest_asyncio.fixture(scope="session",autouse=True)
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

