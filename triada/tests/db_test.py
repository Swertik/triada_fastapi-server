import pytest
from triada.schemas.table_models import Users  # Импортируем модель
from sqlalchemy.future import select


@pytest.mark.asyncio
async def test_create_user(db_session):
    """Тест создания пользователя в тестовой БД"""
    # Создаём нового пользователя
    new_user = Users(user_id=5, user_name="Alice")
    db_session.add(new_user)

    # Проверяем, что он записан в БД
    result = (await db_session.exec(select(Users).where(Users.user_name == "Alice")))
    user = result.scalars().first()
    print(result)

    assert user is not None
    assert user.user_name == "Alice"
    assert user.user_id == 5
