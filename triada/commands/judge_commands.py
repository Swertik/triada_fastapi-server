"""
Реализации команд для судьи
"""
import base64
from typing import List, Tuple

from asyncpg.pgproto.pgproto import timedelta

from triada.api.db_api import get_sessionmaker
from triada.api.vk_api import send_message, send_comment, close_comments, open_comments
from triada.commands.base import BaseCommand, BaseDBCommand, BaseUserDBCommand, BattleStatusCommand
from triada.schemas.table_models import Battles, BattlesPlayers, Users
from sqlmodel import select
from triada.run.settings import JUDGE_CHAT_ID, GROUP_ID
from triada.utils.db_commands import process_add_time
from triada.utils.redis_client import redis_client
import pickle

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
        pass


    async def _send_success_message(self) -> None:
        await send_comment(self.link, self.text)
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
        await process_add_time(self.link, timedelta(hours=int(self.text)))


    async def _needs_commit(self) -> bool:
        return True

    async def _send_success_message(self) -> None:
        await send_comment(self.link, f"УВЕДОМЛЕНИЕ\n\nБой продлён на {self.text} часов.")
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

class GradeActivateCommand(BaseUserDBCommand):
    async def _execute_command(self, session) -> None:
        players = (await session.exec(select(BattlesPlayers).where(BattlesPlayers.link == self.link).order_by(BattlesPlayers.turn))).all()
        self.text = "Игроки:\n" + "\n".join([f"@id{i.user_id}({i.user_name})" for i in players])
        users = (await session.exec(select(Users).where(Users.user_id.in_([i.user_id for i in players])))).all()
        serialized_data = pickle.dumps(users)
        encoded_str = base64.b64encode(serialized_data).decode('utf-8')
        await redis_client.set(f"user:{self.from_id}:state", f"waiting for grade {self.link}")
        await redis_client.set(f"user:{self.from_id}:state:data", encoded_str)


    async def _send_success_message(self) -> None:
        await send_message(self.peer_id, self.text)


async def update_mmr(mmr, data, link):
    mmr: List = mmr.split('\n')
    data: Tuple[Users] = pickle.loads(base64.b64decode(data))
    if len(mmr) < len(data):
        await send_message(JUDGE_CHAT_ID, "Вы не указали достаточно информации!")
        return
    for i, user_mmr in enumerate(mmr):
        user_mmr = user_mmr.split(': ')
        user = data[i]
        match user_mmr[0].lower():
            case 'победа':
                user.wins += 1
            case 'поражение':
                user.losses += 1
            case 'техническая победа':
                user.technical_wins += 1
            case 'техническое поражение':
                user.technical_losses += 1
            case _:
                await send_message(JUDGE_CHAT_ID, "Вы не указали один из аргументов!")
                return
        user.mmr += int(user_mmr[1])
    await send_message(JUDGE_CHAT_ID, "Оценка успешно добавлена!")
    async with get_sessionmaker()() as session:
        session.add_all(data)
        await session.commit()
    await close_comments(link)
    return