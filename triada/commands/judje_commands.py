"""
Реализации команд для судьи
"""
from asyncpg.pgproto.pgproto import timedelta

from triada.api.vk_api import send_message, send_comment, close_comments, open_comments
from triada.commands.base import BaseCommand, BaseDBCommand, BaseUserDBCommand, BattleStatusCommand
from triada.schemas.table_models import Battles
from sqlmodel import select, text
from triada.config.settings import JUDGE_CHAT_ID, GROUP_ID
from triada.utils.db_commands import process_add_time

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


class CloseCommand(BattleStatusCommand):
    async def _send_success_message(self) -> None:
        await send_comment(self.link, "УВЕДОМЛЕНИЕ\n\nБой закрыт!")
        await send_message(JUDGE_CHAT_ID, 'Бой успешно закрыт!')

    async def command(self) -> None:
        await close_comments(self.link)

    async def status(self) -> str:
        return "closed"


class OpenCommand(BattleStatusCommand):
    async def _send_success_message(self) -> None:
        await send_comment(self.link, "УВЕДОМЛЕНИЕ\n\nБой открыт!")
        await send_message(JUDGE_CHAT_ID, 'Бой успешно открыт!')

    async def command(self) -> None:
        await open_comments(self.link)

    async def status(self) -> str:
        return "paused"


class PauseCommand(BattleStatusCommand):
    async def _send_success_message(self) -> None:
        await send_comment(self.link, "УВЕДОМЛЕНИЕ\n\nБой поставлен на паузу")
        await send_message(JUDGE_CHAT_ID, 'Бой успешно поставлен на паузу!')

    async def command(self) -> None:
        pass

    async def status(self) -> str:
        return "paused"


class RePauseCommand(BattleStatusCommand):
    async def _send_success_message(self) -> None:
        await send_comment(self.link, "УВЕДОМЛЕНИЕ\n\nБой снят с паузы")
        await send_message(JUDGE_CHAT_ID, 'Бой успешно снят с паузы!')

    async def command(self) -> None:
        pass

    async def status(self) -> str:
        return "active"


class ExtendCommand(BaseDBCommand):
    async def _execute_command(self, session) -> None:
        await process_add_time(self.link, timedelta(hours= int(self.text)))
        await send_comment(self.link, f"УВЕДОМЛЕНИЕ\n\nБой продлён на {self.text} часов.")

    async def _needs_commit(self) -> bool:
        return True

    async def _send_success_message(self) -> None:
        await send_message(JUDGE_CHAT_ID, 'В бою успешно проведено продление!')


class SuspectsCommand(BaseUserDBCommand):
    async def _execute_command(self, session) -> None:
        result = (await session.exec(select(Battles).where(Battles.judge_id == self.from_id))).all()
        self.text = "\n".join(f"https://vk.com/wall-{GROUP_ID}_{link.link}" for link in result)

    
    async def _send_success_message(self) -> None:
        await send_message(self.peer_id, f"Подсудимые:\n\n{self.text}")


class HelloCommand:
    def __init__(self, peer_id: int):
        self.peer_id = peer_id

    async def execute(self) -> None:
        await send_message(self.peer_id, 'Привет!')
