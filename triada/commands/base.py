"""
Базовые интерфейсы для команд
"""
from abc import ABC, abstractmethod
import logging

from sqlmodel import select

from triada.api.db_api import get_sessionmaker
from triada.api.vk_api import send_message
from triada.schemas.table_models import Battles

logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """Базовый класс для всех команд"""

    def __init__(self, link: int, text: str, peer_id: int):
        self.link = int(link)
        self.text = text
        self.peer_id = peer_id

    async def execute(self) -> None:
        """
        Выполняет команду с обработкой ошибок
        """
        try:
            await self._execute_command()
            await self._send_success_message()
        except Exception as e:
            text = f"Ошибка при выполнении команды {self.__class__.__name__}: {e}"
            logger.error(text)
            await self._send_error_message(text)

    @abstractmethod
    async def _execute_command(self) -> None:
        """Реализация конкретной команды"""
        pass

    @abstractmethod
    async def _send_success_message(self) -> None:
        """Отправка сообщения об успехе"""
        pass

    async def _send_error_message(self, text: str) -> None:
        """Отправка сообщения об ошибке"""
        await send_message(self.peer_id, text)


class BaseDBCommand(ABC):
    """Базовый класс для всех команд"""
    
    def __init__(self, link: int, text: str, peer_id: int):
        self.link = link
        self.text = text
        self.peer_id = peer_id
        
    async def execute(self) -> None:
        """
        Выполняет команду с обработкой ошибок
        """
        async with get_sessionmaker()() as session:
            try:
                await self._execute_command(session)
                if await self._needs_commit():
                    await session.commit()
                await self._send_success_message()
            except Exception as e:
                text = f"Ошибка при выполнении команды {self.__class__.__name__}: {e}"
                logger.error(text)
                if await self._needs_commit():
                    await session.rollback()
                await self._send_error_message(text)

    @abstractmethod
    async def _execute_command(self, session) -> None:
        """Реализация конкретной команды"""
        pass

    async def _needs_commit(self) -> bool:
        """Требуется ли коммит транзакции"""
        return False

    @abstractmethod
    async def _send_success_message(self) -> None:
        """Отправка сообщения об успехе"""
        pass

    async def _send_error_message(self, text: str) -> None:
        """Отправка сообщения об ошибке"""
        await send_message(self.peer_id, text)


class BattleStatusCommand(BaseDBCommand):
    async def _execute_command(self, session) -> None:
        battle = (await session.exec(select(Battles).where(Battles.link == self.link))).first()
        battle.status = await self.status()
        await session.commit()
        await self.command()

    @abstractmethod
    async def _send_success_message(self) -> None:
        pass

    @abstractmethod
    async def status(self) -> None:
        pass

    @abstractmethod
    async def command(self) -> None:
        pass

class BaseUserDBCommand(ABC):
    """Базовый класс для команд с подключением к базе данных"""

    def __init__(self, peer_id: int, from_id: int, link: int = None) -> None:
        self.peer_id = peer_id
        self.from_id = from_id
        self.link = link

    async def execute(self) -> None:
        """
        Выполняет команду с обработкой ошибок
        """
        async with get_sessionmaker()() as session:
            try:
                await self._execute_command(session)
                if await self._needs_commit():
                    await session.commit()
                await self._send_success_message()
            except Exception as e:
                text = f"Ошибка: {e}"
                logger.error(text)
                if await self._needs_commit():
                    await session.rollback()
                await self._send_error_message(text)

    @abstractmethod
    async def _execute_command(self, session) -> None:
        """Реализация конкретной команды"""
        pass

    async def _needs_commit(self) -> bool:
        """Требуется ли коммит транзакции"""
        return False

    @abstractmethod
    async def _send_success_message(self) -> None:
        """Отправка сообщения об успехе"""
        pass

    async def _send_error_message(self, text: str) -> None:
        """Отправка сообщения об ошибке"""
        await send_message(self.peer_id, text)


class BaseUserCommand(ABC):
    """Базовый класс для всех команд"""

    def __init__(self, text: str, peer_id: int):
        self.text = text
        self.peer_id = peer_id

    async def execute(self) -> None:
        """
        Выполняет команду с обработкой ошибок
        """
        try:
            await self._execute_command()
            await self._send_success_message()
        except Exception as e:
            text = f"Ошибка при выполнении команды {self.__class__.__name__}: {e}"
            logger.error(text)
            await self._send_error_message(text)

    @abstractmethod
    async def _execute_command(self, session) -> None:
        """Реализация конкретной команды"""
        pass

    @abstractmethod
    async def _send_success_message(self) -> None:
        """Отправка сообщения об успехе"""
        pass

    async def _send_error_message(self, text: str) -> None:
        """Отправка сообщения об ошибке"""
        await send_message(self.peer_id, text)