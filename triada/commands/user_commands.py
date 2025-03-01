"""
Реализации команд для пользователей
"""
from datetime import datetime, timedelta
from sqlmodel import Session, select
from triada.api.vk_api import send_message
from triada.commands.base import BaseCommand, BaseDBCommand, BaseUserDBCommand, BaseUserCommand
from triada.config.settings import GROUP_ID
from triada.schemas.table_models import Battles, BattlesPlayers, Users


class HiddenActionCommand(BaseUserDBCommand):
    """Команда для обработки скрытых действий"""

    async def _execute_command(self, session) -> None:
        active_player = (await session.exec(select(BattlesPlayers).where(BattlesPlayers.user_id == self.peer_id and
                                                  BattlesPlayers.hidden_action == 'active'))).first()
        if not active_player:
            raise ValueError("Вы не можете сейчас отправить своё скрытое действие.")
        time_out = (await session.exec(select(BattlesPlayers).where(BattlesPlayers.link == self.link and
                                                             BattlesPlayers.time_out is not None))).first()
        battle_time_out = (await session.exec(select(Battles).where(Battles.link == self.link))).first()
        if time_out.time_out - battle_time_out.time_out - timedelta(hours=1) > datetime.now():
            raise ValueError("Время на предоставление скрытого действия уже истекло.")

        active_player.hidden_action = self.text


    async def _needs_commit(self) -> bool:
        return True

    async def _send_success_message(self) -> None:
        await send_message(self.peer_id, "Скрытое действие записано")


class MyBattlesCommand(BaseUserDBCommand):
    async def _execute_command(self, session):
        user_battles = (await session.exec(select(BattlesPlayers).where(BattlesPlayers.user_id == self.from_id))).all()
        print("\n"*5,user_battles, "\n"*5)
        if not user_battles:
            raise ValueError("Ваши бои:\n\nУ вас нет активных боёв.")

        self.text = "Ваши бои:\n\n" + "\n".join(f"https://vk.com/wall-{GROUP_ID}_{links.link}" for links in user_battles)


    async def _send_success_message(self) -> None:
        #TODO: Добавить нормальное сообщение
        await send_message(self.peer_id, self.text)


class BattlesCommand(BaseUserDBCommand):
    async def _execute_command(self, session):
        battles = (await session.exec(select(Battles).where(Battles.status != 'closed'))).all()

        if not battles:
            raise ValueError("Активные бои:\n\n Активных боёв на данный момент нет.")

        self.text = "Активные бои:\n\n" + "\n".join(f"https://vk.com/wall-{GROUP_ID}_{links.link}" for links in battles)

    async def _send_success_message(self) -> None:
        await send_message(self.peer_id, self.text)

class CommandsCommand(BaseUserCommand):
    async def _execute_command(self):
        self.text = "Команды:\n- мои бои\n- бои\n- команды"

    async def _send_success_message(self):
        await send_message(self.peer_id, self.text)

class MyStatCommand(BaseUserDBCommand):
    async def _execute_command(self, session):
        user = (await session.exec(select(Users).where(Users.user_id == self.from_id))).first()

        if not user:
            raise ValueError('Статистика игрока не найдена.')

        else:
            self.text = f"""\
Ваша статистика:

Количество боев: {sum([user.wins, user.technical_wins, user.loses, user.technical_loses])}
Количество побед: {user.wins}
Количество технических побед: {user.technical_wins}
Количество поражений: {user.loses}
Количество технических поражений: {user.technical_loses}
Ваш ММР: {user.mmr}
Фрагменты побед: {user.fragments_of_victories}
Фрагменты величия: {user.fragments_of_greatness}
Место в рейтинге: [В РАЗРАБОТКЕ]
"""

    async def _send_success_message(self):
        await send_message(self.peer_id, self.text)