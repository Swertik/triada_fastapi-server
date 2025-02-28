"""
Реализации команд для судьи
"""
from triada.api.vk_api import send_message, send_comment, close_comments, open_comments
from triada.commands.base import BaseCommand, BaseDBCommand, BaseUserDBCommand
from triada.schemas.table_models import Battles
from sqlmodel import select, text
from triada.config.settings import JUDGE_CHAT_ID, GROUP_ID

JUDGE_COMMANDS = [
    "вердикт",
    "закрыть",
    "открыть",
    "пауза",
    "снять паузу",
    "продлить",
    "подсудимые",]

class VerdictCommand(BaseCommand):
    async def _execute_command(self) -> None:
        # TODO: Добавить вложения
        await send_comment(self.link, self.text)

    async def _send_success_message(self) -> None:
        await send_message(self.peer_id, 'Комментарий в пост размещен!')


class CloseCommand(BaseCommand):
    async def _execute_command(self) -> None:
        await close_comments(self.link)

    async def _send_success_message(self) -> None:
        await send_message(self.peer_id, 'Пост закрыт!')


class OpenCommand(BaseCommand):
    async def _execute_command(self) -> None:
        await open_comments(self.link)

    async def _send_success_message(self) -> None:
        await send_message(self.peer_id, 'Пост открыт!')


class PauseCommand(BaseDBCommand):
    async def _execute_command(self, session) -> None:
        battle = (await session.exec(select(Battles).where(Battles.link == self.link))).first()
        battle.status = 'paused'
        session.add(battle)
        await session.commit()

    async def _needs_commit(self) -> bool:
        return True

    async def _send_success_message(self) -> None:
        await send_comment(self.link, "УВЕДОМЛЕНИЕ\n\nБой поставлен на паузу")
        await send_message(JUDGE_CHAT_ID, 'Бой успешно поставлен на паузу!')


class RePauseCommand(BaseDBCommand):
    async def _execute_command(self, session) -> None:
        battle = session.exec(select(Battles).where(Battles.link == self.link)).one()
        battle.status = 'active'
        session.add(battle)
        session.commit()

    async def _needs_commit(self) -> bool:
        return True
    
    async def _send_success_message(self) -> None:
        await send_comment(self.link, "УВЕДОМЛЕНИЕ\n\nБой снят с паузы")
        await send_message(JUDGE_CHAT_ID, 'Бой успешно снят с паузы!')


class ExtendCommand(BaseDBCommand):
    async def _execute_command(self, session) -> None:
        query = text("SELECT * FROM process_add_time(:link, :time)")
        #TODO: Разобраться с запросами к базе данных и переписать process add time в python
        result = session.exec(query, {"link": self.link, "time": self.text})
        result.fetchone()  # Получение результата
        await send_comment(self.link, f"УВЕДОМЛЕНИЕ\n\nБой продлён на {self.text} часов.")

    async def _needs_commit(self) -> bool:
        return True

    async def _send_success_message(self) -> None:
        await send_message(JUDGE_CHAT_ID, 'В бою успешно проведено продление!')


class SuspectsCommand(BaseUserDBCommand):

    async def _execute_command(self, session) -> None:
        result = session.exec(select(Battles).where(Battles.judge_id == self.link))
        links = result.fetchall()
        suspects = "\n".join(f"https://vk.com/wall-{GROUP_ID}_{link[0]}" for link in links)
        await send_message(self.peer_id, f"Подсудимые:\n\n{suspects}")
    
    async def _send_success_message(self) -> None:
        pass


class HelloCommand:
    def __init__(self, peer_id: int):
        self.peer_id = peer_id

    async def execute(self) -> None:
        await send_message(self.peer_id, 'Привет!')
