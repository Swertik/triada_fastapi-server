import os

import pytest

from triada.schemas.models import Users  # Импортируем модель
from sqlalchemy.future import select


@pytest.mark.asyncio
async def test_create_user(db_session, setup_test_db):
    """Тест создания пользователя в тестовой БД"""

    # Создаём нового пользователя
    new_user = Users(user_id=5, user_name="Alice")
    db_session.add(new_user)

    # Проверяем, что он записан в БД
    stmt = select(Users).where(Users.user_name == "Alice")
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    print(result)

    assert user is not None
    assert user.user_name == "Alice"
    assert user.user_id == 5

