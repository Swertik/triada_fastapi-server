"""
Базовые интерфейсы для команд
"""
from abc import ABC, abstractmethod
import logging
from triada.api.db_api import engine
from sqlmodel import Session
from triada.api.vk_api import send_message

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
            if await self._needs_commit():
                with Session(engine) as session:
                    session.commit()
            await self._send_success_message()
        except Exception as e:
            text = f"Ошибка при выполнении команды {self.__class__.__name__}: {e}"
            logger.error(text)
            if await self._needs_commit():
                with Session(engine) as session:
                    session.rollback()
            await self._send_error_message(text)

    @abstractmethod
    async def _execute_command(self) -> None:
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