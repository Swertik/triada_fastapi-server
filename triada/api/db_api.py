from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from triada.config.settings import DATABASE_URL, TEST_DATABASE_URL
from contextlib import contextmanager
import threading

# Используем thread-local storage для хранения текущего URL
_db_context = threading.local()
_db_context.url = DATABASE_URL

def get_db_url():
    """Возвращает текущий URL базы данных"""
    return getattr(_db_context, 'url', DATABASE_URL)

@contextmanager
def override_database(url: str):
    """Контекстный менеджер для временного переключения URL базы данных"""
    old_url = get_db_url()
    _db_context.url = url
    try:
        yield
    finally:
        _db_context.url = old_url

# Создаем движок динамически на основе текущего URL
def get_engine():
    return create_async_engine(get_db_url(), echo=True)

# Создаем фабрику сессий
def get_sessionmaker():
    engine = get_engine()
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

# Функция для получения сессии
async def get_session() -> AsyncSession:
    async_session = get_sessionmaker()
    async with async_session() as session:
        yield session

# Функция для инициализации базы данных
async def init_db():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)