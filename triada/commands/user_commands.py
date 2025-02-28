"""
Реализации команд для пользователей
"""
from datetime import datetime, timedelta
from sqlmodel import Session, select
from triada.api.vk_api import send_message
from triada.commands.base import BaseCommand, BaseDBCommand, BaseUserDBCommand
from triada.config.settings import GROUP_ID
from triada.schemas.table_models import Battles, BattlesPlayers


class HiddenActionCommand(BaseDBCommand):
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
        user_battles = (await session.exec(select(BattlesPlayers).where(BattlesPlayers.user_id == self.peer_id))).all()

        if not user_battles:
            raise ValueError("Ваши бои:\n\nУ вас нет активных боёв.")

        self.text = "Ваши бои:\n\n" + "\n".join(f"https://vk.com/wall-{GROUP_ID}_{links.link}" for links in user_battles)



    async def _send_success_message(self) -> None:
        #TODO: Добавить нормальное сообщение
        await send_message(self.peer_id, self.text)